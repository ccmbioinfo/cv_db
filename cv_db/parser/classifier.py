from enum import Enum
from typing import Iterable

from vllm import LLM
from vllm import SamplingParams
from vllm.sampling_params import StructuredOutputsParams

from cv_db.parser.models import *

class SectionClassifier:
    def __init__(self, llm: LLM, temperature=0, max_tokens=128):
        self.llm=llm
        self.sampling_params = SamplingParams(
            temperature=0.0,
            max_tokens=128,  # headroom for {"section_type": "intellectual_property"} + any grammar whitespace
            structured_outputs=StructuredOutputsParams(
            json=SectionClassification.model_json_schema()))

    @staticmethod
    def _top_lines(text: str, n: int = 20) -> str:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return "\n".join(lines[:n])

    @staticmethod
    def _prompt(header: str | None, text: str) -> str:
        header = header or ""
        return f"""Classify this CV section into exactly one of the allowed categories.

Use the section heading and the supplied text. Choose the category that
best describes the actual content of the section.

Do not infer information that is not present.
Return only the category name.

Allowed categories:
contact_information
education
employment
award
publication
presentation
funding
teaching
supervision
peer_review
association
administration
intellectual_property
creative
media
profile

Section heading:
{header}

Section text:
{text}
"""

    def __call__(self, sections: Iterable[tuple[str | None, str]]) -> list[SectionClassification | None]:
        sections = list(sections)
        if not sections:
            return []

        headers = [s[0] for s in sections]
        texts = [self._top_lines(s[1]) for s in sections]

        # Batched chat conversations — llm.chat applies the model's chat template
        # per-conversation, which llm.generate does NOT do.
        conversations = [
            [{"role": "user", "content": self._prompt(header, text)}]
            for header, text in zip(headers, texts)
        ]

        outputs = self.llm.chat(
            conversations,
            sampling_params=self.sampling_params,
            use_tqdm=False,
        )

        results: list[SectionClassification | None] = []
        for out in outputs:
            raw = out.outputs[0].text
            try:
                results.append(SectionClassification.model_validate_json(raw))
            except ValueError:
                # Grammar guarantees syntactic validity but not that generation
                # completed before max_tokens — surface failures instead of
                # letting a bad record silently disappear.
                results.append(None)

        return results



