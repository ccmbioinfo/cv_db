import re
from typing import Any, Dict, List, Optional, Union
import requests

from cv_db.parser.models import PublicationItem, FundingItem


class OpenAlexSearch:
    def __init__(self,api_key):
        self.api_key = api_key
        self.base_url = "https://api.openalex.org/works"

    @staticmethod
    def _clean_grant_number(grant_num: Optional[str]) -> Optional[str]:
        """Clean CV grant number artifacts (e.g. 'Grant # R01-CA123456' -> 'R01CA123456')."""
        if not grant_num:
            return None
        cleaned = re.sub(
            r"(?i)^(grant|award|protocol)\s*(number|no|#|\.)*:?\s*", "", grant_num
        ).strip()
        return cleaned if cleaned else None

    @staticmethod
    def _extract_year(date_str: Optional[str]) -> Optional[int]:
        """Extract 4-digit year from arbitrary date strings (e.g., '2021-2025')."""
        if not date_str:
            return None
        match = re.search(r"\b(19|20)\d{2}\b", str(date_str))
        return int(match.group(0)) if match else None

    @staticmethod
    def clean_grant_number(grant_num: Optional[str]) -> Optional[str]:
        """Clean CV grant number artifacts (e.g. 'Grant # R01-CA123456' -> 'R01CA123456')."""
        if not grant_num:
            return None
        cleaned = re.sub(
            r"(?i)^(grant|award|protocol)\s*(number|no|#|\.)*:?\s*", "", grant_num
        ).strip()
        return cleaned if cleaned else None

    @staticmethod
    def _clean_string(val):
        if not val:
            return None
        cleaned = re.sub(r"[^\w\s]", "", val)
        return " ".join(cleaned.split())


    def search_publication(self, pub:PublicationItem):
        # 1. Pre-filter short-circuit: skip network requests for unpublished works
        if pub.published is False or pub.submitted is True:
            return None

        cleaned_title = self._clean_string(pub.title)
        params: Dict[str, Any] = {
            "per_page": 1,
            "api_key": self.api_key,
        }

        # we have to have a title otherwise we cannot search so I'm not initiaing an empty list
        filters= [f"title.search:{cleaned_title}"]
        #just using the first author here
        if pub.authors and len(pub.authors) > 0:
            first_author = self._clean_string(pub.authors[0])
            if first_author:
                filters.append(f"raw_author_name.search:{first_author}")

        if pub.venue:
            filters.append(f"primary_location.source.raw_source_name.search:{pub.venue}")

        params["filter"] = ",".join(filters)

        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            results = response.json().get("results", [])

            if results:
                return results[0]
        except requests.RequestException:
            return None

    def search_openalex_grant(self, funding: FundingItem):
        """

        :param funding:
        :return:
        """
        # 1. Pre-filter short-circuit
        if funding.declined is True:
            return None

        params: Dict[str, Any] = {
            "per_page": 1,
        }

        filters=[]

        grant_num = self._clean_grant_number(funding.grant_number)
        start_year = self._extract_year(funding.start)

        if grant_num:
            filters = [f"funder_award_id:{grant_num}"]
            if start_year:
                filters.append(f"start_year:{start_year}")

        if len(filters) > 0:
            params["filter"] = ",".join(filters)

        try:
            resp = requests.get(self.base_url, params=params)
            resp.raise_for_status()
            results = resp.json().get("results", [])
            if results:
                return results[0]
        except requests.RequestException:
            pass

        return None



