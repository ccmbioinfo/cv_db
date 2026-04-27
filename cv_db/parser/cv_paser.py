import warnings
import os
import json

import outlines
import pdfplumber
from doc2pdf import convert
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from sentence_transformers import SentenceTransformer

from cv_db.parser.cv_structure import *

def normalize_string(x):
    if not isinstance(x, str):
        return x
    if len(x) >= 2 and x[0] == x[-1] and x[0] in ("'", '"'):
        return x[1:-1]
    return x

model_name="mistralai/Mistral-7B-Instruct-v0.3"
#quant_config=BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
#                                bnb_4bit_compute_dtype=torch.float16,
#                                bnb_4bit_use_double_quant=True)
#llm=AutoModelForCausalLM.from_pretrained(model_name, quantization_config=quant_config, device_map="auto")
#tokenizer = AutoTokenizer.from_pretrained(model_name)
#outlines_model=outlines.from_transformers(llm, tokenizer)

sentence_transformer_model = SentenceTransformer("Qwen/Qwen3-Embedding-4B")


class SectionExtractor:
    def __init__(self, outlines_model=model_name, sentence_transformer_model=sentence_transformer_model):
        self.outlines=outlines_model
        self.sentence_transformer=sentence_transformer_model

    def identify_section(self, headers):
        sections=[
            ("education", "degrees, training, academic qualifications, certifications"),
            ("employment", "positions and appointments, current and past"),
            ("award", "honors and distinctions but not certifications for research, leadership or teaching"),
            ("publication", "journal articles, letters, short articles, books, book chapters peer reviewed and not peer reviewed"),
            ("presentation", "invited or applied talks, posters and abstracts"),
            ("funding", "grants, peer reviewed and non peer reviewed"),
            ("supervision", "mentoring students, graduate, undergraduate and/or medical students"),
            ("administration", "committees, leadership administrative activities, not including associations but in organizational positions"),
            ("association", "memberships to professional associations past and present"),
            ("peer_review", "peer reviewing activities journals/grants, not items that get peer reviewed by others"),
            ("intellectual_property", "patents and trademarks"),
            ("creative", "creative work such as professional innovations or contributions to professional practices"),
            ("media", "interviews in news, radio, press or other media outlets"),
            ("contact_information", "phone, email, office address"),
            ("profile", "ONLY narrative personal statements that describes philosophy, values and vision in research teaching and professional practice")
        ]
        query_embeddings = self.sentence_transformer.encode(headers, prompt_name="query")
        document_embeddings = self.sentence_transformer.encode([item[1] for item in sections])
        similarity = self.sentence_transformer.similarity(query_embeddings, document_embeddings)
        items=torch.argmax(similarity, dim=1).tolist()
        section_class=[sections[item][0] for item in items]
        return section_class

    def extract_section_info(self, chunk, section_type):
        section_length=len(" ".join(chunk).split(" "))
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

        CONTENT:
        {chunk}
        """

        try:
            results = self.model(
                prompt,
                schema,
                max_new_tokens=section_length*5
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
            new_path = path
        elif path.endswith(".docx"):
            warnings.warn("Converting DOCX to PDF. This may take a while.")
            new_path = path.replace(".docx", ".pdf")
            convert(path, new_path)
        else:
            raise NotImplementedError("Unsupported file format. Only PDF and DOCX are supported.")

        structured_lines = []

        LINE_MERGE_TOL = 3  # same visual line
        BLANK_LINE_GAP = 12  # vertical gap => blank line

        with pdfplumber.open(new_path) as pdf:
            for page in pdf.pages:
                words = page.extract_words(
                    extra_attrs=["fontname", "size", "page_number", "top"]
                )

                if not words:
                    structured_lines.append({
                        "text": "",
                        "size": None,
                        "is_bold": False,
                        "starting_page": page.page_number,
                    })
                    continue

                lines = []
                current_line = [words[0]]

                for w in words[1:]:
                    prev = current_line[-1]

                    if abs(w["top"] - prev["top"]) < LINE_MERGE_TOL:
                        current_line.append(w)
                    else:
                        lines.append(current_line)

                        # infer blank line from vertical gap
                        if (w["top"] - prev["top"]) > BLANK_LINE_GAP:
                            lines.append(None)  # represents blank line

                        current_line = [w]

                lines.append(current_line)

                for line in lines:
                    if line is None:
                        structured_lines.append({
                            "text": "",
                            "size": None,
                            "is_bold": False,
                            "starting_page": page.page_number,
                        })
                        continue

                    text = " ".join(w["text"] for w in line)
                    avg_size = sum(w["size"] for w in line) / len(line)
                    is_bold = any("bold" in w["fontname"].lower() for w in line)
                    page_number = min(w["page_number"] for w in line)

                    structured_lines.append({
                        "text": text,
                        "size": round(avg_size),
                        "is_bold": is_bold,
                        "starting_page": page_number,
                    })

        return structured_lines

    def _get_fonts(self, raw_lines):
        font_sizes = [item["size"] for item in raw_lines if item["size"] is not None]
        to_rem = [min(font_sizes),
                  max(font_sizes)]  # min contains the header and the footer and the max just says Curriculum Vitae
        font_sizes = list(set([item for item in font_sizes if item not in to_rem]))
        size_dict = {}
        for size in font_sizes:
            size_dict[size]=0

        for line in raw_lines:
            if line["size"] not in font_sizes:
                continue
            else:
                size_dict[line["size"]] = size_dict[line["size"]] + 1
                
        header_val=max(size_dict)
        text_val=max(size_dict, key=size_dict.get)
        subheaders=[k for k in size_dict if k != header_val and k!=text_val]
        font_sizes = {text_val: "text",
                      header_val: "header"}
        for item in subheaders:
            font_sizes[item]="sub_header"
        return font_sizes

    def _get_cleaned_lines(self, raw_lines, fonts):
        return [item for item in raw_lines if item["size"] in list(fonts.keys())]

    def _get_sections(self, cleaned_lines, fonts):
        sections = {}
        # State tracking
        current_headers = {
            "header": None,
            "sub_header": None,
        }

        for line in cleaned_lines:
            label = fonts[line["size"]]  # Assuming "size" contains the classification label
            content = line["text"].strip()

            if label == "header":
                current_headers["header"] = content
                current_headers["sub_header"] = None

            elif label == "sub_header":
                current_headers["sub_header"] = content

            elif label == "text":
                # Build the key dynamically based on what headers are currently active
                key_parts = [
                    current_headers["header"],
                    current_headers["sub_header"]
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
        raw_lines=self._read_file(file_path)
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

