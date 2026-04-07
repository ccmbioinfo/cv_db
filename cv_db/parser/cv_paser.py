import warnings
import os
from functools import cached_property, lru_cache
import json

import outlines
import pdfplumber
from accelerate.test_utils.examples import clean_lines
from doc2pdf import convert
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

from cv_db.parser.cv_structure import *

def normalize_string(x):
    if not isinstance(x, str):
        return x
    if len(x) >= 2 and x[0] == x[-1] and x[0] in ("'", '"'):
        return x[1:-1]
    return x


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

    def identify_section(self, header, chunk):
        prompt = f"""
You are classifying sections of an academic CV.

Use the HEADER as the primary signal.

Definitions:
- education: degrees, training, academic qualifications
- employment: positions and appointments
- award: honors and distinctions
- publication: journal articles, books
- presentation: talks and posters
- research: research projects
- funding: grants
- supervision: mentoring students
- administration: committees, leadership
- association: memberships
- peer_review: reviewing journals/grants
- intellectual_property: patents
- creative: creative work
- media: interviews
- contact_information: phone, email, address
- profile: ONLY narrative personal statements

Rules:
- If HEADER is clear → ignore content
- If list-like or contains dates → NOT profile
- Profile must be narrative text only
- Prefer specific category over profile
- If unsure → unknown
            
            HEADER (most important):
            {header}
            ---------
            CONTENT (not as important, use if header is unclear):
            {chunk}
        """

        section_class = self.model(
            prompt,
            SectionClassification
        )

        return section_class

    def extract_section_info(self, chunk, header, section_type):

        schema = SECTION_TYPE_TO_SCHEMA.get(section_type)
        if schema is None:
            return None


        prompt = f"""
        Extract structured data from this CV section.

        Rules:
        - Do NOT fabricate information
        - Use null if missing
        - Dates must remain as strings (e.g., "Jul 2015", "2015-Present")
        - Do NOT convert to full dates
        - Do NOT guess fields
        - Preserve multiple entries

        SECTION TYPE: {section_type}

        HEADER:
        {header}

        CONTENT:
        {chunk}
        """

        try:
            results = self.model(
                prompt,
                schema,
                max_new_tokens=5000
            )
            return results
        except Exception as e:
            print(e)

@dataclass
class ParsedCV:
    file: str
    raw_lines: Optional[List] = None
    fonts: Optional[List] = None
    cleaned_lines: Optional[List] = None
    sections: Optional[dict] = None
    extracted_info: Optional[List] = None

class CVParser:
    def __init__(self, extractor: SectionExtractor):
        self.extractor=extractor

    def _read_file(self, path):
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")

        if path.endswith(".pdf"):
            return path
        elif path.endswith(".docx"):
            warnings.warn("Converting DOCX to PDF. This may take a while.")
            new_path=path.replace("docx", "pdf")
            convert(path, new_path)
        else:
            raise NotImplementedError("Unsupported file format. Only PDF and DOCX are supported.")

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

    def _get_fonts(self, raw_lines):
        font_sizes = [item["size"] for item in raw_lines]
        to_rem = [min(font_sizes),
                  max(font_sizes)]  # min contains the header and the footer and the max just says Curriculum Vitae
        font_sizes = list(set([item for item in font_sizes if item not in to_rem]))
        font_sizes.sort()
        font_sizes = {font_sizes[0]: "text",
                      font_sizes[1]: "sub_header2",
                      font_sizes[2]: "sub_header1",
                      font_sizes[3]: "header"}
        return font_sizes

    def _get_cleaned_lines(self, raw_lines, fonts):
        return [item for item in raw_lines if item["size"] in list(fonts.keys())]

    def _get_sections(self, cleaned_lines, fonts):
        sections = {}
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
                if full_key not in sections:
                    sections[full_key] = []
                sections[full_key].append(content)

        return sections

    def _extract_info(self, sections):
        extracted_sections = []
        for section_header, section_text in self.sections.items():
            section_text = "\n".join(section_text)
            section_type = self.extractor.identify_section(section_header, section_text)
            section_type = json.loads(section_type)["section_type"]
            section_info = self.extractor.extract_section_info(section_text, section_header, section_type)
            extracted_sections.append(section_info)

        return extracted_sections


    def process(self, file_path, extract=True):
        raw_lines=self.read(file_path)
        fonts=self._get_fonts(raw_lines)
        clean_lines=self._get_cleaned_lines(raw_lines, fonts)
        sections=self._get_sections(clean_lines, fonts)
        if extract:
            info=self._extract_info(sections)
        else:
            info=None

        cv = ParsedCV(file=file_path,
                      raw_lines=raw_lines,
                      fonts=fonts,
                      cleaned_lines=clean_lines,
                      sections=sections,
                      extracted_info=info)
        return cv

