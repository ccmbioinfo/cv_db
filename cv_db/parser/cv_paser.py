import warnings
import os
from functools import cached_property, lru_cache

import outlines
import pdfplumber
from doc2pdf import convert
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

from cv_db.parser.cv_structure import *

class SectionExtractor:
    def __init__(self, model_name, tokenizer_kwargs=None, model_kwargs=None, quant_kwargs=None):
        if tokenizer_kwargs is not None:
            tokenizer=AutoTokenizer.from_pretrained(model_name, **tokenizer_kwargs)
        else:
            tokenizer = AutoTokenizer.from_pretrained(model_name)

        if quant_kwargs is not None:
            quant_config=BitsAndBytesConfig(**quant_kwargs)
            if model_kwargs is not None:
                llm=AutoModelForCausalLM.from_pretrained(model_name, **model_kwargs, quantization_config=quant_config)
            else:
                llm = AutoModelForCausalLM.from_pretrained(model_name)
        else:
            if model_kwargs is not None:
                llm=AutoModelForCausalLM.from_pretrained(model_name, **model_kwargs)
            else:
                llm = AutoModelForCausalLM.from_pretrained(model_name)

        self.model=outlines.from_transformers(llm, tokenizer)

    def identify_section(self, chunk):
        prompt = f"""
        You are classifying a section of an academic CV.

        Decide what kind of CV content this is, based on its substance.
        Only choose ONE section type.

        If the content does not clearly match a category, choose "unknown".

        CV section text:
        ----------------
        {chunk}
        """

        classify_section = self.model(
            prompt,
            SectionClassification
        )

        return classify_section(prompt)

    def extract_section_info(self, chunk, section_type):
        schema = SECTION_TYPE_TO_SCHEMA.get(section_type)
        if schema is None:
            return None

        return self.model(
            f"""
        Extract all relevant information from the following CV section.
        Return structured data only.

        CV section:
        -----------
        {chunk}
        """,
            schema,
        )

@dataclass
class ParsedCV:
    @lru_cache(maxsize=None, typed=False)
    def file(self, path):
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")

        if path.endswith(".pdf"):
            return path
        elif path.endswith(".docx"):
            warnings.warn("Converting DOCX to PDF. This may take a while.")
            new_path=path.replace("docx", "pdf")
            convert(path, new_path)
            return new_path
        else:
            raise NotImplementedError("Unsupported file format. Only PDF and DOCX are supported.")

    @cached_property
    def raw_lines(self):
        structured_lines = []
        with pdfplumber.open(self.file) as pdf:
            for page in pdf.pages:
                words = page.extract_words(extra_attrs=["fontname", "size", "page_number", "top"])
                if not words:
                    continue

                lines = []
                current_line = [words[0]]
                for w in words[1:]:
                    if abs(w['top'] - current_line[-1]['top']) < 3:
                        current_line.append(w)
                    else:
                        lines.append(current_line)
                        current_line = [w]
                lines.append(current_line)

                for line in lines:
                    text = " ".join([w['text'] for w in line])
                    # Determine styling: UofT headers are typically larger or Bold
                    avg_size = sum([w['size'] for w in line]) / len(line)
                    is_bold = any("bold" in w['fontname'].lower() for w in line)
                    page_number = min(w["page_number"] for w in line)
                    structured_lines.append({
                        "text": text,
                        "size": round(avg_size),
                        "is_bold": is_bold,
                        "starting_page": page_number,
                        # "pos": line["top"]

                    })
        return structured_lines

    @cached_property
    def fonts(self):
        font_sizes = [item["size"] for item in self.raw_lines]
        to_rem = [min(font_sizes),
                  max(font_sizes)]  # min contains the header and the footer and the max just says Curriculum Vitae
        font_sizes = list(set([item for item in font_sizes if item not in to_rem]))
        font_sizes.sort()
        font_sizes = {font_sizes[0]: "text",
                      font_sizes[1]: "sub_header2",
                      font_sizes[2]: "sub_header1",
                      font_sizes[3]: "header"}
        return font_sizes

    @cached_property
    def cleaned_lines(self):
        return [item for item in self.raw_lines if item["size"] in list(self.fonts.keys())]

    @cached_property
    def sections(self):
        structured_data = {}

        # State tracking
        current_headers = {
            "header": None,
            "sub_header1": None,
            "sub_header2": None
        }

        for line in self.cleaned_lines:
            label = self.fonts[line["size"]]  # Assuming "size" contains the classification label
            content = line["text"].strip()

            if label == "header":
                current_headers["header"] = content
                current_headers["sub_header1"] = None
                current_headers["sub_header2"] = None

            elif label == "sub_header1":
                current_headers["sub_header1"] = content
                current_headers["sub_header2"] = None

            elif label == "sub_header2":
                current_headers["sub_header2"] = content

            elif label == "text":
                # Build the key dynamically based on what headers are currently active
                key_parts = [
                    current_headers["header"],
                    current_headers["sub_header1"],
                    current_headers["sub_header2"]
                ]

                # Filter out None values and join
                full_key = "|".join([part for part in key_parts if part is not None])

                # Initialize list if key doesn't exist, then append text
                if full_key not in structured_data:
                    structured_data[full_key] = []
                structured_data[full_key].append(content)

        return structured_data

    parsed_sections: dict = None

    @lru_cache(maxsize=None)
    def extracted_sections(self, extractor:SectionExtractor):
        extracted_sections=[]
        for section_header, section_text in self.sections.items():
            section_content="\n".join([section_header, section_text])
            section_type=extractor.identify_section(section_content)
            section_info=extractor.extract_section_info(section_content, section_type)
            extracted_sections.append(section_info)





