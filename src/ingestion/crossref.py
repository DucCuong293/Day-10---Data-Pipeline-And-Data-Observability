from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from core.config import Settings


@dataclass(frozen=True)
class PaperRecord:
    paper_id: str
    title: str
    summary: str
    authors: list[str]
    categories: list[str]
    primary_category: str
    published: str
    updated: str
    abs_url: str
    pdf_url: str
    comment: str


import re
import requests
import time
from core.utils import read_json, write_json, normalize_whitespace

def parse_crossref_payload(payload: dict) -> list[PaperRecord]:
    """Parse Crossref payload into a list of PaperRecord objects."""
    items = payload.get("message", {}).get("items", [])
    records = []
    for item in items:
        paper_id = item.get("DOI", "").strip()
        if not paper_id:
            continue
            
        titles = item.get("title", [])
        title = normalize_whitespace(titles[0]) if titles else "Untitled"
        if not title:
            title = "Untitled"
            
        abstract = item.get("abstract", "")
        summary = re.sub(r"<[^>]+>", "", abstract).strip()
        summary = normalize_whitespace(summary)
        
        authors = []
        for author_dict in item.get("author", []):
            given = author_dict.get("given", "").strip()
            family = author_dict.get("family", "").strip()
            name = f"{given} {family}".strip()
            if name:
                authors.append(name)
        if not authors:
            authors = ["Unknown Author"]
            
        categories = item.get("subject", [])
        if not categories:
            categories = ["Uncategorized"]
        primary_category = categories[0]
        
        def extract_date(field_name):
            date_info = item.get(field_name) or {}
            date_parts = date_info.get("date-parts", [[None]])[0]
            if len(date_parts) >= 3 and all(x is not None for x in date_parts[:3]):
                return f"{date_parts[0]:04d}-{date_parts[1]:02d}-{date_parts[2]:02d}"
            elif len(date_parts) >= 2 and all(x is not None for x in date_parts[:2]):
                return f"{date_parts[0]:04d}-{date_parts[1]:02d}-01"
            elif len(date_parts) >= 1 and date_parts[0] is not None:
                return f"{date_parts[0]:04d}-01-01"
            return None

        published = None
        for f in ["published-print", "published-online", "published", "issued"]:
            published = extract_date(f)
            if published:
                break
        if not published:
            created_info = item.get("created") or {}
            date_time_str = created_info.get("date-time")
            if date_time_str:
                published = date_time_str.split("T")[0]
        if not published:
            published = "2026-01-01"
            
        updated = None
        created_info = item.get("created") or {}
        date_time_str = created_info.get("date-time")
        if date_time_str:
            updated = date_time_str.split("T")[0]
        if not updated:
            updated = published
            
        abs_url = item.get("URL", "")
        pdf_url = ""
        links = item.get("link", [])
        for link in links:
            if "pdf" in link.get("content-type", "") or "pdf" in link.get("URL", ""):
                pdf_url = link.get("URL", "")
                break
        if not pdf_url and links:
            pdf_url = links[0].get("URL", "")
            
        comment = item.get("publisher", "")
        
        records.append(
            PaperRecord(
                paper_id=paper_id,
                title=title,
                summary=summary,
                authors=authors,
                categories=categories,
                primary_category=primary_category,
                published=published,
                updated=updated,
                abs_url=abs_url,
                pdf_url=pdf_url,
                comment=comment
            )
        )
    return records


def fetch_source_records(settings: Settings) -> list[PaperRecord]:
    """Fetch raw records from Crossref API, save them, and parse them."""
    url = "https://api.crossref.org/works"
    params = {
        "query": settings.source_query,
        "filter": settings.source_filter,
        "rows": settings.max_results
    }
    
    max_retries = 3
    delay = 2
    response_data = None
    
    for attempt in range(max_retries):
        try:
            r = requests.get(url, params=params, timeout=15)
            if r.status_code in (429, 503):
                print(f"Crossref API returned {r.status_code}, retrying in {delay}s...")
                time.sleep(delay)
                delay *= 2
                continue
            r.raise_for_status()
            response_data = r.json()
            break
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"Failed to fetch from Crossref API: {e}. Trying to load local cache if exists...")
                try:
                    response_data = read_json(settings.paths.raw_api_response)
                    break
                except Exception:
                    raise e
            time.sleep(delay)
            delay *= 2
            
    if response_data is None:
        raise RuntimeError("Failed to fetch from API and no cached response available.")
        
    write_json(settings.paths.raw_api_response, response_data)
    
    records = parse_crossref_payload(response_data)
    
    serialized = []
    for r in records:
        serialized.append({
            "paper_id": r.paper_id,
            "title": r.title,
            "summary": r.summary,
            "authors": r.authors,
            "categories": r.categories,
            "primary_category": r.primary_category,
            "published": r.published,
            "updated": r.updated,
            "abs_url": r.abs_url,
            "pdf_url": r.pdf_url,
            "comment": r.comment
        })
    write_json(settings.paths.raw_records_json, serialized)
    
    return records


def load_raw_records(path: Path) -> list[PaperRecord]:
    """Load PaperRecord list from raw records JSON snapshot."""
    payload = read_json(path)
    records = []
    for item in payload:
        records.append(
            PaperRecord(
                paper_id=item["paper_id"],
                title=item["title"],
                summary=item["summary"],
                authors=item["authors"],
                categories=item["categories"],
                primary_category=item["primary_category"],
                published=item["published"],
                updated=item["updated"],
                abs_url=item["abs_url"],
                pdf_url=item["pdf_url"],
                comment=item["comment"]
            )
        )
    return records

