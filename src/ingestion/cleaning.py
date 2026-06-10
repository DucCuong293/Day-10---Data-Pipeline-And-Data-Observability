from __future__ import annotations

from datetime import datetime

import pandas as pd

from ingestion.crossref import PaperRecord


from core.utils import normalize_whitespace, compact_join

def build_clean_dataframe(records: list[PaperRecord], run_date: datetime) -> pd.DataFrame:
    """Clean raw records and construct a clean DataFrame ready for embedding and QA."""
    cleaned_rows = []
    run_date_naive = run_date.replace(tzinfo=None)
    
    for record in records:
        paper_id = record.paper_id.strip()
        title = normalize_whitespace(record.title)
        summary = normalize_whitespace(record.summary)
        
        # Filter bad rows (must have paper_id, title length >= 5, and summary)
        if not paper_id or not title or len(title) < 5 or not summary:
            continue
            
        authors = [normalize_whitespace(a) for a in record.authors if a.strip()]
        if not authors:
            authors = ["Unknown Author"]
            
        categories = [normalize_whitespace(c) for c in record.categories if c.strip()]
        if not categories:
            categories = ["Uncategorized"]
            
        primary_category = normalize_whitespace(record.primary_category)
        if not primary_category:
            primary_category = categories[0]
            
        # Parse date and calculate age_days
        try:
            published_dt = pd.to_datetime(record.published, errors='coerce')
        except Exception:
            published_dt = pd.NaT
            
        if pd.notna(published_dt):
            published_dt_naive = published_dt.to_pydatetime().replace(tzinfo=None)
            age_days = (run_date_naive - published_dt_naive).days
        else:
            age_days = 9999
            
        authors_joined = compact_join(authors, ", ")
        categories_joined = compact_join(categories, ", ")
        summary_chars = len(summary)
        
        text_for_embedding = (
            f"Title: {title}\n"
            f"Authors: {authors_joined}\n"
            f"Categories: {categories_joined}\n"
            f"Summary: {summary}"
        )
        
        cleaned_rows.append({
            "paper_id": paper_id,
            "title": title,
            "summary": summary,
            "authors_joined": authors_joined,
            "categories_joined": categories_joined,
            "primary_category": primary_category,
            "published": record.published,
            "updated": record.updated,
            "abs_url": record.abs_url,
            "pdf_url": record.pdf_url,
            "comment": record.comment,
            "age_days": age_days,
            "summary_chars": summary_chars,
            "text_for_embedding": text_for_embedding
        })
        
    if not cleaned_rows:
        return pd.DataFrame()
        
    df = pd.DataFrame(cleaned_rows)
    
    # Drop duplicates
    df = df.drop_duplicates(subset=["paper_id"], keep="first")
    df = df.drop_duplicates(subset=["title"], keep="first")
    
    # Sort by published date descending
    df["published_temp"] = pd.to_datetime(df["published"], errors="coerce")
    df = df.sort_values(by="published_temp", ascending=False).drop(columns=["published_temp"])
    
    return df

