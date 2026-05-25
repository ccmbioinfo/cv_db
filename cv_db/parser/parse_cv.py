from dataclasses import dataclass
from typing import Optional

import warnings
import os
import json

import pdfplumber
import torch

from cv_db.parser.prompts import *

@dataclass
class CVSection:
    section_type: str
    section_content: str
    parsed_content:dict

@dataclass
class CV:
    file:str
    raw_lines:list[str]
    cleaned_lines:list[str]
    fonts:dict
    sections: list[CVSection]

    @classmethod
    def from_db(cls, id):
        """
        creates a CV object from a database id
        """
        pass

    def to_db(self):
        """
        upload the cv to the database assuming all the sections are correct, they would need to be checked and coerced
        """
        pass


class ExtractSections:
    def __init__(self, model, tokenizer):
        """
        init for the class this takes a full AutoModelForCausalLM model and a tokenizer, if you are using quantization (you should)
        do this outside the model and then pass it to the class
        """
        self.model = model
        self.tokenizer = tokenizer
        self.device="cuda" if torch.cuda.is_available() else "cpu"

    def identify_section(self, cv:CV, max_include):
        """
        this takes the sections identified via parsed sections and returns a label for all the sections
        for extra robustness we are also inclund max_include tokens from the section body. This improves things quite a bit

        returns the same cv but there is a new key in the sections that shows what kind of section it is
        """
        for header, content in cv.sections.items():
            to_include = max_include if len(content) > max_include else len(content)
            if len(content) > 0:
                chunk_content = "\n".join(content[:to_include])
            else:
                chunk_content = ""
            prompt = classifiction_prompt.format(header=header, chunk_content=chunk_content)

            messages = [
                {"role": "system",
                 "content": "You are an expert assistant, you goal is to provided structued information from unstructured CV chunks. For a given chunk below indentify the section that it belongs to"},
                {"role": "user", "content": prompt},
            ]

            input_ids = self.tokenizer.apply_chat_template(
                messages,
                tokenize=True,
                add_generation_prompt=True,
                return_tensors="pt",
            ).to(self.model.device)

            with torch.inference_mode():
                output = self.model.generate(**input_ids, max_new_tokens=15, eos_token_id=self.tokenizer.eos_token_id,
                                        do_sample=False)
            gen_ids = output[0][input_ids["input_ids"].shape[-1]:]
            decoded = self.tokenizer.decode(gen_ids, skip_special_tokens=True)

            cv.sections[header]["section_type"]=decoded
        return cv

    def extract_section_info(self, section_type:str, section_content:list[str], prompt_dict):
        """
        for a given section and an accompanying prompt from the prompt dict create a structured output, I am not relying
        on returning a proper json, I have given up on that but I will try to parse it later after the model runs with a whole
        bunch of fallbacks see below.
        """
        prompt=prompt_dict[section_type]

        chunk = "\n".join(section_content)
        max_tokens = self._estimate_tokens(chunk) * 5  # we are returning all the information *and* json structure

        messages = [
            {"role": "system", "content": sys_extraction_prompt},
            {"role": "user", "content": f"{prompt} \n {extraction_prompts["rules"]} {chunk}"},
        ]
        input_ids = self.tokenizer.apply_chat_template(
            messages,
            tokenize=True,
            add_generation_prompt=True,
            return_tensors="pt",
        ).to(self.model.device)

        with torch.inference_mode():
            output = self.model.generate(**input_ids, max_new_tokens=max_tokens * 5, eos_token_id=self.tokenizer.eos_token_id,
                                    do_sample=False)
        gen_ids = output[0][input_ids["input_ids"].shape[-1]:]
        decoded = self.tokenizer.decode(gen_ids, skip_special_tokens=True)
        return decoded

    def to_json(self, decoded):
        """this is not done yet, this is the part I need help, you can test this with a few different models and may be
        ask a smaller second model to convert it to proper json"""
        pass


    def _estimate_tokens(self, chunk):
        """
        estimate the number of tokens we will need to return to save on processing time, this takes the section that
        is being processed
        """

        chunk = chunk.replace("\n", " ")
        length = len(chunk.split(" "))
        return length


class CV_Parser:
    def __init__(self, file):
        if not file.endswith(".pdf"):
            raise NotImplementedError("Only pdfs are supported currently")
        else:
            self.file = file

    def read_file(self):
        """
        take a pdf and get all the text and font information from it. This will be used to determine what's a header and what is
        not.
        It will return a list of lines (a line in the file) and metadata like page average font size etc.
        """
        if not os.path.exists(self.file):
            raise FileNotFoundError(f"File not found: {self.file}")

        structured_lines = []

        LINE_MERGE_TOL = 3  # same visual line
        BLANK_LINE_GAP = 12  # vertical gap => blank line

        with pdfplumber.open(self.file) as pdf:
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

    def get_fonts(self):
        """
        process the lines above to produce aggregate metadata about font information, this will then be used as follows
        1. Most abundant font size is the body text
        2. largest and smallest ones are removed because they are massive Curriculum Vitae and the confidential stuff at the bottom
        3. The remaining largest is a header (these are I'm hoping are the main sections)
        4. Everything else is a subheader

        returns a dictionary of headers and subheaders as the key and the rest of the text as a value, these will be used to
        a. identify sections
        b. once identified return structured parsed information.
        """
        if not self.structured_lines:
            raise ValueError("You need to run read_file() first")
        font_sizes = [item["size"] for item in self.structured_lines if item["size"] is not None]
        to_rem = [min(font_sizes),
                  max(font_sizes)]  # min contains the header and the footer and the max just says Curriculum Vitae
        font_sizes = list(set([item for item in font_sizes if item not in to_rem]))
        size_dict = {}
        for size in font_sizes:
            size_dict[size] = 0

        for line in self.structured_lines:
            if line["size"] not in font_sizes:
                continue
            else:
                size_dict[line["size"]] = size_dict[line["size"]] + 1

        header_val = max(size_dict)
        text_val = max(size_dict, key=size_dict.get)
        subheaders = [k for k in size_dict if k != header_val and k != text_val]
        font_sizes = {text_val: "text",
                      header_val: "header"}
        for item in subheaders:
            font_sizes[item] = "sub_header"
        return font_sizes

    def get_cleaned_lines(self, raw_lines, fonts):
        return [item for item in raw_lines if item["size"] in list(fonts.keys())]

    def get_sections(self, cleaned_lines, fonts):
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




