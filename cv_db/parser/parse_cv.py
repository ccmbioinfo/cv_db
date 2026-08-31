import os
import logging
from typing import Optional
from dataclasses import dataclass, field

import numpy as np
from paddleocr import PPStructureV3, PaddleOCRVL

from cv_db.parser.models import *

logger = logging.getLogger(__name__)

class SectionExtractor:
    def __init__(self, llm, sampling_params):
        self.llm = llm
        self.sampling_params = sampling_params

    def _get_model(self, section_class):
        model=EXTRACTION_MODELS[section_class]
        return model

    def _extract(self, section_class, section):
        model = self._get_model(section_class)
        prompt = model.get_prompt(section.header, section.text)
        conversation = [{"role": "user", "content": prompt}]
        output = self.llm.chat(
            [conversation],
            sampling_params=self.sampling_params,
            use_tqdm=False,
        )
        raw = output[0].outputs[0].text
        try:
            return model.model_validate_json(raw)
        except ValueError:
            logger.warning(
                "Failed to parse LLM output as JSON for section '%s': %s",
                section.header, raw
            )
            return None

    def __call__(self, sections):
        data=[]
        for section in sections:
            result = self._extract(section.section_class, section)
            data.append(result)
        return data


class SectionClassifier:
    def __init__(self, llm, sampling_params):
        self.llm = llm
        self.sampling_params = sampling_params

    def _top_lines(self, text, n=20):
        """Return the first n non-empty lines of text."""
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return lines[:n]

    def _prompt(self, header: str | None, text: str) -> str:
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

    # def _merge_sections(self, sections):
    #     """Merge sections with the same section_class into a single section."""
    #     types=list(set([section.section_class for section in sections]))
    #     same_sections={}
    #     for type in types:
    #         same_sections[type]=[]
    #
    #     for section in sections:
    #         type=section.section_clas
    #         same_sections[type].append(section)
    #
    #     for type, sections in same_sections.items():



    def __call__(self, sections):
        sections = list(sections)
        if not sections:
            return []

        headers = [s.header for s in sections]
        texts = [self._top_lines(s.text) for s in sections]

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
                logger.warning(
                    "Failed to parse LLM output as JSON: %s", raw
                )
                results.append(None)

        for section, result in zip(sections, results):
            section.section_class=result

        return sections

@dataclass
class _VisionPlaceholder:
    """Marks a spot in a page's event stream where a vision-labeled crop
    needs to be swapped in for its (deferred) VLM output."""
    batch_index: int
    raw_item_content: str  # kept only for debugging/fallback

@dataclass
class CVSection:
    header:str
    text:str
    section_class:Optional[CVSectionType]= None

class CVParser:
    def __init__(
        self,
        device: str | None = None,
        page_det_limit_side_len: int = 1536,
        crop_det_limit_side_len: int = 960,
        vision_batch_size: int = 8,
    ):
        """
        Args:
            device: e.g. "gpu:0" or "cpu". If None, auto-detects the same
                way the original code did. Passed to BOTH pipelines.
            page_det_limit_side_len: max side length for full-page text
                detection. Tune based on your smallest reliably-readable
                font size, not upward by default.
            crop_det_limit_side_len: max side length for the VLM pass on
                individual vision-labeled crops. Crops are smaller than
                full pages, so this should generally be smaller than
                page_det_limit_side_len, not equal to it.
            vision_batch_size: how many vision crops to send to
                vl_pipeline.predict() per batched call. Bounds VRAM use
                while still amortizing per-call overhead. Tune down if
                you see OOM, up if GPU utilization looks low.
        """
        self.page_det_limit_side_len = page_det_limit_side_len
        self.crop_det_limit_side_len = crop_det_limit_side_len
        self.vision_batch_size = vision_batch_size

        self.ocr_pipeline = PPStructureV3(
            engine="transformers",
            lang="en",
            use_table_recognition=False,
            use_formula_recognition=False,
            use_chart_recognition=False,
            use_seal_recognition=False,
            device="gpu",  # FIX: was hardcoded "gpu"; now honors
                                   # the resolved/passed-in device.
            use_doc_unwarping=False,
        )
        self.vl_pipeline = PaddleOCRVL(
            engine="transformers",
            use_doc_unwarping=False,
            use_chart_recognition=False,
            use_seal_recognition=False,
            format_block_content=True,
            use_doc_orientation_classify=False,
            device="gpu",  # FIX: was hardcoded "gpu"; now matches
                                   # ocr_pipeline's placement. Verify this
                                   # kwarg is honored in your installed
                                   # PaddleOCRVL version — see caveats below.
        )

    def _predict(self, file):
        if not os.path.exists(file):
            raise FileNotFoundError(f"File not found: {file}")
        return self.ocr_pipeline.predict(
            input=file,
            text_det_limit_side_len=self.page_det_limit_side_len,
            text_det_limit_type="max",
        )

    def _build_events(self, output):
        """Pass 1: walk every page in original order, deferring vision
        crops instead of resolving them immediately. Returns:
            page_events: list[list[event]] — one event list per page
            pending_crops: list[np.ndarray] — crops awaiting VLM inference,
                in the same order their placeholders were created
        """
        page_events = []
        pending_crops = []

        for i in range(len(output)):
            page = output[i]
            events = []
            for item in page["parsing_res_list"]:
                label = item.order_label
                if label == "vision":
                    arr = np.asarray(item.image["img"])
                    placeholder = _VisionPlaceholder(
                        batch_index=len(pending_crops),
                        raw_item_content=getattr(item, "content", ""),
                    )
                    pending_crops.append(arr)
                    events.append(("vision", placeholder))
                elif label == "paragraph_title":
                    events.append(("header", item.content))
                elif label == "sub_paragraph_title":
                    events.append(("sub_header", item.content))
                elif label == "normal_text":
                    events.append(("text", item.content))
                # any other label: silently skipped, same as original
            page_events.append(events)

        return page_events, pending_crops

    def _run_vl_batches(self, pending_crops):
        """Batched VLM inference over all collected crops, chunked to
        bound VRAM. Falls back to per-item calls within a chunk if the
        batched call fails (e.g. list input unsupported), and isolates
        failures of individual crops so one bad image doesn't abort the
        whole run."""
        results = [None] * len(pending_crops)
        bs = self.vision_batch_size

        for start in range(0, len(pending_crops), bs):
            chunk = pending_crops[start:start + bs]
            try:
                chunk_out = self.vl_pipeline.predict(
                    input=chunk,
                    text_det_limit_side_len=self.crop_det_limit_side_len,
                    text_det_limit_type="max",
                )
                chunk_out = list(chunk_out)
                if len(chunk_out) != len(chunk):
                    raise ValueError(
                        f"Batched VLM call returned {len(chunk_out)} "
                        f"results for {len(chunk)} inputs."
                    )
                for offset, res in enumerate(chunk_out):
                    results[start + offset] = res
            except Exception as e:
                logger.warning(
                    "Batched vl_pipeline.predict() failed for chunk "
                    "%d-%d (%s); falling back to per-item calls.",
                    start, start + len(chunk), e,
                )
                for offset, arr in enumerate(chunk):
                    # FIX: previously unguarded — a single bad crop would
                    # raise here and abort the entire (potentially
                    # >100-page) run. Now isolated per item, consistent
                    # with the "skip rather than fabricate" handling in
                    # _replay_events.
                    try:
                        single_out = self.vl_pipeline.predict(
                            input=arr,
                            text_det_limit_side_len=self.crop_det_limit_side_len,
                            text_det_limit_type="max",
                        )
                        results[start + offset] = list(single_out)[0]
                    except Exception as item_e:
                        logger.warning(
                            "Per-item vl_pipeline.predict() failed for "
                            "crop %d (%s); skipping.",
                            start + offset, item_e,
                        )
                        results[start + offset] = None

        return results

    def _replay_events(self, page_events, vl_results):
        """Pass 2: replay events in original order, resolving vision
        placeholders with real VLM output, and rebuild `sections` with
        the same header-tracking semantics as the original code."""
        sections = []
        # FIX: previously reinitialized inside the `for events in
        # page_events` loop, so header/sub_header silently reset to None
        # at every page boundary. A section (e.g. a multi-page
        # Publications list) whose header only appears on its first page
        # would then produce headerless/empty-keyed chunks for every
        # subsequent page. Now persists across the whole document.
        current_headers = {"header": None, "sub_header": None}

        for events in page_events:
            for kind, payload in events:
                if kind == "header":
                    current_headers["header"] = payload
                elif kind == "sub_header":
                    current_headers["sub_header"] = payload
                elif kind == "text":
                    key_parts = [current_headers["header"], current_headers["sub_header"]]
                    full_key = "|".join(p for p in key_parts if p is not None)
                    sections.append((full_key, payload))
                elif kind == "vision":
                    vision_output = vl_results[payload.batch_index]
                    if vision_output is None:
                        logger.warning(
                            "No VLM output for a vision crop; skipping."
                        )
                        continue
                    for sub_item in vision_output["parsing_res_list"]:
                        sub_label = sub_item.label
                        if sub_label == "paragraph_title":
                            current_headers["header"] = sub_item.content
                        elif sub_label == "sub_paragraph_title":
                            # Verify this label actually appears in your
                            # crop outputs — remove if it doesn't.
                            current_headers["sub_header"] = sub_item.content
                        elif sub_label in ("text", "table", "reference_content"):
                            key_parts = [current_headers["header"], current_headers["sub_header"]]
                            full_key = "|".join(p for p in key_parts if p is not None)
                            sections.append((full_key, sub_item.content))

        section_classes=[]
        for section in sections:
            s=CVSection(header=section[0], text=section[1])
            section_classes.append(s)

        return section_classes

    def _sections(self, output):
        page_events, pending_crops = self._build_events(output)
        vl_results = self._run_vl_batches(pending_crops) if pending_crops else []
        return self._replay_events(page_events, vl_results)

    def __call__(self, file):
        pipeline_out = self._predict(file)
        return self._sections(pipeline_out)