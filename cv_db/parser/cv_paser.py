from dataclasses import dataclass
import os

import pandas as pd



from cv_db.parser.utils import *

@dataclass(frozen=True)
class CV:
    pass



class CvParser:
    def __init__(self):
        pass


    def parse(self, path):
        pass

    def insert(self, cv, database):
        pass


import re
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM


@dataclass
class CVSection:
    """Represents a parsed CV section with its content"""
    section_name: str
    raw_content: str
    structured_data: Optional[Dict[str, Any]] = None


class UofTCVParser:
    """
    Parser for University of Toronto CV documents.
    Uses a local LLM (Llama 3.1 8B) for structured information extraction.
    """

    def __init__(self, model_path: str, model_kwargs: Optional[Dict[str, Any]] = None, tokenizer_kwargs: Optional[Dict[str, Any]] = None,
                 section_patterns: Optional[List[str]] = None):
        """
        Constructor for the class, just load the model and get ready to parse
        :param model_path: path for the model, you can also use a huggingface name if you want
        :param model_kwargs: dict of arguments for the model
        :param tokenizer_kwargs: dict of arguments for the tokenizer
        """
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_name = model_path
        self.tokenizer = AutoTokenizer.from_pretrained(model_path, **tokenizer_kwargs)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.bfloat16,
            device_map="auto",
            low_cpu_mem_usage=True,
            **model_kwargs
        )

    def parse(self, cv_text: str) -> Dict[str, Any]:
        """
        parse the cv
        :param cv_text: a long string that contains the extracted cv text
        :return: a dict with all the sections
        """
        # Extract biographical info from header
        biographical_info = self._extract_biographical_info(cv_text)

        # Split CV into sections
        sections = self._split_into_sections(cv_text)

        # Parse each section
        parsed_data = {
            "biographical_info": biographical_info,
            "sections": {}
        }

        for section in sections:
            print(f"Parsing section: {section.section_name}")
            structured = self._extract_section_data(section)
            parsed_data["sections"][section.section_name] = structured

        return parsed_data

    def _extract_biographical_info(self, cv_text: str) -> Dict[str, Any]:
        """
        extract biographical information
        :param cv_text: cv text
        :return: a dict of personal information
        """
        # Take first 2000 characters which should contain biographical info
        header = cv_text[:2000]

        prompt = self._build_extraction_prompt(
            section_type="biographical_information",
            content=header,
            schema={
                "name": "Full name of the person",
                "title": "Professional title",
                "email": "Email address(es)",
                "phone": "Phone number(s)",
                "office_address": "Office address",
                "department": "Department name",
                "institution": "Institution/Organization"
            }
        )

        return self._query_llm(prompt)

    def _split_into_sections(self, cv_text: str) -> List[CVSection]:
        """Split CV text into major sections"""
        sections = []

        # Find all section headers and their positions
        section_matches = []
        for pattern in self.SECTION_PATTERNS:
            for match in re.finditer(pattern, cv_text, re.IGNORECASE):
                section_matches.append((match.start(), match.group()))

        # Sort by position
        section_matches.sort(key=lambda x: x[0])

        # Extract content between sections
        for i, (start_pos, header) in enumerate(section_matches):
            # Normalize section name
            section_name = self._normalize_section_name(header)

            # Get end position (start of next section or end of document)
            end_pos = section_matches[i + 1][0] if i + 1 < len(section_matches) else len(cv_text)

            # Extract content
            content = cv_text[start_pos:end_pos].strip()

            sections.append(CVSection(
                section_name=section_name,
                raw_content=content
            ))

        return sections

    def _normalize_section_name(self, header: str) -> str:
        """Normalize section header to a clean name"""
        # Remove numbers and special characters
        name = re.sub(r'^[0-9A-Z]+\.\s*', '', header)
        return name.strip().lower().replace(' ', '_')

    def _extract_section_data(self, section: CVSection) -> Dict[str, Any]:
        """Extract structured data from a CV section using LLM"""
        # Define schema based on section type
        schema = self._get_section_schema(section.section_name)

        if not schema:
            return {"raw_content": section.raw_content}

        # Build extraction prompt
        prompt = self._build_extraction_prompt(
            section_type=section.section_name,
            content=section.raw_content[:4000],  # Limit to avoid context overflow
            schema=schema
        )

        # Extract structured data
        return self._query_llm(prompt)

    def _get_section_schema(self, section_name: str) -> Optional[Dict[str, str]]:
        """Return the expected schema for a given section"""
        schemas = {
            "education": {
                "degrees": [
                    {
                        "dates": "Start and end dates",
                        "qualification": "Degree name",
                        "department": "Department",
                        "institution": "Institution name",
                        "location": "City, Province/State, Country",
                        "supervisors": "Supervisor names"
                    }
                ],
                "postgraduate_training": [
                    {
                        "dates": "Start and end dates",
                        "title": "Training title",
                        "specialization": "Specialization",
                        "institution": "Institution name",
                        "supervisors": "Supervisor names"
                    }
                ],
                "certifications": [
                    {
                        "dates": "Start and end dates",
                        "title": "Certification title",
                        "specialty": "Specialty area",
                        "institution": "Issuing institution",
                        "license_number": "License or membership number"
                    }
                ]
            },
            "employment": {
                "current_appointments": [
                    {
                        "dates": "Start and end dates",
                        "position": "Position/office held",
                        "department": "Department",
                        "division": "Division",
                        "faculty": "Faculty",
                        "institution": "Institution",
                        "location": "City, Province, Country",
                        "description": "Description of role"
                    }
                ],
                "previous_appointments": [
                    {
                        "dates": "Start and end dates",
                        "position": "Position/office held",
                        "department": "Department",
                        "institution": "Institution",
                        "location": "City, Province, Country"
                    }
                ]
            },
            "honours_and_career_awards": {
                "research_awards": {
                    "international": [self._award_schema()],
                    "national": [self._award_schema()],
                    "provincial": [self._award_schema()],
                    "local": [self._award_schema()]
                },
                "teaching_awards": {
                    "international": [self._award_schema()],
                    "national": [self._award_schema()],
                    "provincial": [self._award_schema()],
                    "local": [self._award_schema()]
                }
            },
            "publications": {
                "most_significant": [self._publication_schema()],
                "peer_reviewed_journal_articles": [self._publication_schema()],
                "books": [self._publication_schema()],
                "book_chapters": [self._publication_schema()],
                "submitted": [self._publication_schema()],
                "in_preparation": [self._publication_schema()]
            },
            "research_funding": {
                "peer_reviewed_grants": [
                    {
                        "dates": "Start and end dates",
                        "role": "Role (PI, Co-I, etc)",
                        "grant_name": "Name of grant",
                        "funding_source": "Funding organization",
                        "program": "Funding program name",
                        "grant_number": "Grant/account number",
                        "principal_investigator": "PI name",
                        "collaborators": "Collaborator names",
                        "amount": "Total amount",
                        "currency": "Currency",
                        "status": "funded/declined"
                    }
                ],
                "non_peer_reviewed_grants": [
                    {
                        "dates": "Start and end dates",
                        "role": "Role",
                        "grant_name": "Name of grant",
                        "funding_source": "Funding organization",
                        "amount": "Total amount",
                        "status": "funded/declined"
                    }
                ]
            },
            "presentations_and_special_lectures": {
                "international": [self._presentation_schema()],
                "national": [self._presentation_schema()],
                "provincial": [self._presentation_schema()],
                "local": [self._presentation_schema()]
            },
            "research_supervision": {
                "primary_supervision": [
                    {
                        "dates": "Start and end dates",
                        "role": "Supervisory role",
                        "supervisee_name": "Student/trainee name",
                        "program": "Graduate unit/program",
                        "position": "Supervisee position",
                        "thesis_title": "Research project title",
                        "completed_year": "Year completed (if applicable)"
                    }
                ],
                "committee_member": [
                    {
                        "dates": "Start and end dates",
                        "role": "Committee role",
                        "student_name": "Student name",
                        "program": "Graduate unit/program",
                        "thesis_title": "Thesis title"
                    }
                ]
            }
        }

        return schemas.get(section_name)

    def _award_schema(self) -> Dict[str, str]:
        """Common schema for awards"""
        return {
            "dates": "Start and end dates",
            "award_name": "Name of award",
            "role": "Role",
            "organization": "Awarding organization",
            "location": "City, Province/State, Country",
            "amount": "Award amount",
            "status": "awarded/nominated",
            "description": "Description"
        }

    def _publication_schema(self) -> Dict[str, str]:
        """Common schema for publications"""
        return {
            "authors": "List of authors (highlight CV holder)",
            "title": "Publication title",
            "journal_or_book": "Journal name or book title",
            "publication_date": "Year Month Day",
            "volume": "Volume number",
            "issue": "Issue number",
            "pages": "Page range",
            "url": "URL if available",
            "status": "published/in press/submitted",
            "impact_factor": "Impact factor if available",
            "trainee_publication": "Is this a trainee publication (yes/no)"
        }

    def _presentation_schema(self) -> Dict[str, str]:
        """Common schema for presentations"""
        return {
            "date": "Presentation date",
            "role": "Presentation role",
            "title": "Presentation title",
            "event": "Conference/event name",
            "location": "City, Province/State, Country",
            "presenters": "List of presenters",
            "type": "invited/abstract/poster/media"
        }

    def _build_extraction_prompt(self, section_type: str, content: str, schema: Dict[str, Any]) -> str:
        """Build a prompt for the LLM to extract structured data"""
        schema_str = json.dumps(schema, indent=2)

        prompt = f"""You are a precise information extraction system. Extract structured data from the following CV section.

Section Type: {section_type}

Expected Schema:
{schema_str}

CV Content:
{content}

Instructions:
1. Extract ALL relevant information matching the schema
2. Return ONLY valid JSON matching the schema structure
3. Use null for missing values
4. For dates, preserve the original format
5. For lists, extract all items found
6. Be precise and accurate - do not invent information

Return the extracted data as JSON:"""

        return prompt

    def _query_llm(self, prompt: str) -> Dict[str, Any]:
        """Query the LLM and parse JSON response"""
        messages = [
            {"role": "system",
             "content": "You are a precise data extraction assistant. Always respond with valid JSON only."},
            {"role": "user", "content": prompt}
        ]

        inputs = self.tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            return_tensors="pt"
        ).to(self.device)

        # Generate response
        with torch.no_grad():
            outputs = self.model.generate(
                inputs,
                max_new_tokens=2048,
                temperature=0.1,  # Low temperature for consistency
                do_sample=False,
                pad_token_id=self.tokenizer.eos_token_id
            )

        # Decode response
        response = self.tokenizer.decode(outputs[0][inputs.shape[1]:], skip_special_tokens=True)

        # Extract JSON from response
        try:
            # Try to find JSON block
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)
            else:
                return {"raw_response": response, "parsing_error": "No JSON found"}
        except json.JSONDecodeError as e:
            return {"raw_response": response, "parsing_error": str(e)}

    def save_to_json(self, parsed_data: Dict[str, Any], output_path: str):
        """Save parsed CV data to JSON file"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(parsed_data, f, indent=2, ensure_ascii=False)


