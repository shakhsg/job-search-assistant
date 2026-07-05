import csv
import io
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from app.extensions import db
from app.repositories import JobRepository
from app.services.parser import JobDescriptionParser
from app.services.scoring import MatchingEngine
from app.utils.security import UnsafeURLError, validate_outbound_url
from app.utils.text import compact_whitespace


class JobIngestionService:
    def __init__(self, config: dict) -> None:
        self.config = config
        self.parser = JobDescriptionParser()
        self.matching_engine = MatchingEngine()

    def create_manual_job(self, user, payload: dict):
        job_payload = self._build_job_payload(payload)
        job = JobRepository.upsert(user.id, job_payload)
        self._score_if_possible(user, job)
        return job

    def ingest_link(self, user, source_url: str):
        self._ensure_remote_fetch_enabled()
        safe_url = validate_outbound_url(source_url)
        response = requests.get(
            safe_url,
            timeout=self.config["HTTP_TIMEOUT_SECONDS"],
            headers={"User-Agent": "JobCopilot/1.0"},
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        title = compact_whitespace(
            (soup.find("meta", property="og:title") or {}).get("content")
            or (soup.title.string if soup.title and soup.title.string else "")
        )
        description = soup.get_text("\n", strip=True)
        host = (urlparse(safe_url).hostname or "").replace("www.", "")

        job = JobRepository.upsert(
            user.id,
            self._build_job_payload(
                {
                    "source_type": "link",
                    "source_url": safe_url,
                    "application_url": safe_url,
                    "company": host.split(".")[0].replace("-", " ").title(),
                    "title": title or "Imported from link",
                    "description_raw": description[:20000],
                }
            ),
        )
        self._score_if_possible(user, job)
        return job

    def ingest_csv(self, user, uploaded_file) -> int:
        decoded = uploaded_file.read().decode("utf-8-sig")
        rows = list(csv.DictReader(io.StringIO(decoded)))
        if len(rows) > self.config["CSV_MAX_ROWS"]:
            raise ValueError(f"CSV is limited to {self.config['CSV_MAX_ROWS']} rows.")

        for row in rows:
            payload = {
                "source_type": "csv",
                "provider_name": "",
                "external_id": row.get("external_id", ""),
                "source_url": row.get("source_url") or row.get("url") or "",
                "application_url": row.get("application_url") or row.get("apply_url") or "",
                "company": row.get("company", ""),
                "title": row.get("title", ""),
                "location": row.get("location", ""),
                "employment_type": row.get("employment_type", ""),
                "compensation": row.get("compensation", ""),
                "description_raw": row.get("description", ""),
            }
            job = JobRepository.upsert(user.id, self._build_job_payload(payload))
            self._score_if_possible(user, job)
        return len(rows)

    def ingest_api(self, user, provider_name: str, endpoint_url: str) -> int:
        self._ensure_remote_fetch_enabled()
        allowed_hosts = self.config.get("ALLOWED_API_HOSTS", [])
        if not allowed_hosts:
            raise UnsafeURLError("Add ALLOWED_API_HOSTS before using API ingestion.")

        safe_url = validate_outbound_url(endpoint_url, allowed_hosts=allowed_hosts, allowed_schemes=("https",))
        response = requests.get(
            safe_url,
            timeout=self.config["HTTP_TIMEOUT_SECONDS"],
            headers={"User-Agent": "JobCopilot/1.0"},
        )
        response.raise_for_status()
        payload = response.json()
        jobs = self._normalize_api_jobs(provider_name, payload)

        for item in jobs:
            job = JobRepository.upsert(user.id, self._build_job_payload(item))
            self._score_if_possible(user, job)
        return len(jobs)

    def refresh_job(self, user, job) -> None:
        job.parsed_data = self.parser.parse(job.description_raw or "", job.title)
        self._score_if_possible(user, job, commit=False)
        db.session.add(job)
        db.session.commit()

    def _build_job_payload(self, payload: dict) -> dict:
        description = payload.get("description_raw", "") or ""
        title = payload.get("title", "") or ""
        parsed_data = self.parser.parse(description, title)
        return {
            "source_type": payload.get("source_type", "manual"),
            "provider_name": payload.get("provider_name", ""),
            "external_id": payload.get("external_id", ""),
            "source_url": payload.get("source_url", ""),
            "application_url": payload.get("application_url", ""),
            "company": payload.get("company", "").strip(),
            "title": title.strip(),
            "location": payload.get("location", "").strip() or parsed_data.get("work_mode", ""),
            "employment_type": payload.get("employment_type", "").strip(),
            "compensation": payload.get("compensation", "").strip(),
            "description_raw": description.strip(),
            "parsed_data": parsed_data,
        }

    def _normalize_api_jobs(self, provider_name: str, payload) -> list[dict]:
        if provider_name == "greenhouse":
            items = payload.get("jobs", payload if isinstance(payload, list) else [])
            return [
                {
                    "source_type": "api",
                    "provider_name": "greenhouse",
                    "external_id": str(item.get("id", "")),
                    "source_url": item.get("absolute_url", ""),
                    "application_url": item.get("absolute_url", ""),
                    "company": item.get("company", "") or "Greenhouse Source",
                    "title": item.get("title", ""),
                    "location": (item.get("location") or {}).get("name", "") if isinstance(item.get("location"), dict) else "",
                    "description_raw": item.get("content", "") or item.get("description", ""),
                }
                for item in items
            ]

        if provider_name == "lever":
            items = payload if isinstance(payload, list) else payload.get("jobs", [])
            return [
                {
                    "source_type": "api",
                    "provider_name": "lever",
                    "external_id": str(item.get("id", "")),
                    "source_url": item.get("hostedUrl", ""),
                    "application_url": item.get("applyUrl", "") or item.get("hostedUrl", ""),
                    "company": item.get("company", "") or "Lever Source",
                    "title": item.get("text", ""),
                    "location": (item.get("categories") or {}).get("location", "") if isinstance(item.get("categories"), dict) else "",
                    "description_raw": item.get("descriptionPlain", "") or item.get("description", ""),
                }
                for item in items
            ]

        items = payload.get("jobs", payload if isinstance(payload, list) else [])
        return [
            {
                "source_type": "api",
                "provider_name": "generic_json",
                "external_id": str(item.get("id", "")),
                "source_url": item.get("source_url") or item.get("url") or "",
                "application_url": item.get("application_url") or item.get("apply_url") or item.get("url") or "",
                "company": item.get("company", ""),
                "title": item.get("title", ""),
                "location": item.get("location", ""),
                "employment_type": item.get("employment_type", ""),
                "compensation": item.get("compensation", ""),
                "description_raw": item.get("description", ""),
            }
            for item in items
        ]

    def _ensure_remote_fetch_enabled(self) -> None:
        if not self.config.get("REMOTE_FETCH_ENABLED", False):
            raise ValueError("Remote fetching is disabled by configuration.")

    def _score_if_possible(self, user, job, *, commit: bool = True) -> None:
        if user.profile:
            self.matching_engine.refresh_job(user.profile, job, commit=False)
        if commit:
            db.session.add(job)
            db.session.commit()
