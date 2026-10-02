import math
from typing import Iterable, Sequence
from vllm import LLM, SamplingParams
from vllm.sampling_params import StructuredOutputsParams

from cv_db.parser.models import *
from cv_db.parser.prompts import *


class SectionExtractor:
    def __init__(self, llm: LLM):
        self.llm = llm

    @staticmethod
    def _estimate_max_tokens(text: str, base_margin: int = 256, factor: float = 1.5) -> int:
        """
        Estimates required generation length based on input word count.

        Uses a heuristic of ~1.3 tokens per word, scaled by an expansion factor,
        plus a constant buffer for JSON schema overhead.
        """
        words = len(text.split())
        estimated_input_tokens = math.ceil(words * 1.3)
        return math.ceil(estimated_input_tokens * factor) + base_margin

    def _get_prompt(self, section_type: str, text: str) -> str:
        template = SECTION_PROMPTS.get(section_type, DEFAULT_PROMPT_TEMPLATE)
        return template.format(section_type=section_type, text=text)

    def _get_sampling_params(
            self,
            section_type: CVSectionType | str,
            text: str,
            temperature: float = 0.0
    ) -> SamplingParams:
        # Convert string to enum key if passed as string
        key = section_type.value if isinstance(section_type, CVSectionType) else section_type

        if key not in EXTRACTION_MODELS:
            raise ValueError(f"Unknown section type: {key}")

        model_cls = EXTRACTION_MODELS[key]
        max_tokens = self._estimate_max_tokens(text)

        return SamplingParams(
            temperature=temperature,
            max_tokens=max_tokens,
            structured_outputs=StructuredOutputsParams(
                json=model_cls.model_json_schema()
            )
        )

    def __call__(
            self,
            items: Sequence[tuple[CVSectionType | str, str]],
            temperature: float = 0.0
    ) -> list[dict | None]:
        if not items:
            return []

        conversations = []
        sampling_params_list = []

        for sec_type, text in items:
            key = sec_type.value if isinstance(sec_type, CVSectionType) else sec_type
            model_cls = EXTRACTION_MODELS[key]

            # Construct dynamic prompt based on section key
            prompt_content = self._get_prompt(key, text)
            conversations.append([{"role": "user", "content": prompt_content}])

            # Dynamic sampling parameters (per request)
            max_tokens = self._estimate_max_tokens(text)
            params = SamplingParams(
                temperature=temperature,
                max_tokens=max_tokens,
                structured_outputs=StructuredOutputsParams(
                    json=model_cls.model_json_schema()
                )
            )
            sampling_params_list.append(params)

        # Batch execution via vLLM chat API
        outputs = self.llm.chat(
            conversations,
            sampling_params=sampling_params_list,
            use_tqdm=False
        )

        results = []
        for (sec_type, _), out in zip(items, outputs):
            key = sec_type.value if isinstance(sec_type, CVSectionType) else sec_type
            model_cls = EXTRACTION_MODELS[key]
            raw_text = out.outputs[0].text

            try:
                parsed = model_cls.model_validate_json(raw_text)
                results.append(parsed)
            except ValueError:
                results.append(None)

        return results