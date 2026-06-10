from __future__ import annotations

from typing import Any

import pandas as pd

from core.config import Settings


from pathlib import Path
from core.utils import write_json

def run_data_quality_checks(df: pd.DataFrame, settings: Settings, report_name: str) -> dict[str, Any]:
    """Run data quality checks on the papers DataFrame and save to quality dir."""
    total_rows = len(df)
    
    missing_paper_ids = int(df["paper_id"].isna().sum()) if total_rows > 0 else 0
    duplicate_paper_ids = int(df.duplicated(subset=["paper_id"]).sum()) if total_rows > 0 else 0
    missing_titles = int(df["title"].isna().sum()) if total_rows > 0 else 0
    
    avg_summary_chars = float(df["summary_chars"].mean()) if total_rows > 0 and "summary_chars" in df.columns else 0.0
    too_short_summaries = int((df["summary_chars"] < 30).sum()) if total_rows > 0 and "summary_chars" in df.columns else 0
    
    stale_rows = int((df["age_days"] > settings.freshness_threshold_days).sum()) if total_rows > 0 and "age_days" in df.columns else 0
    
    passed_row_count = total_rows >= 3
    passed_unique_ids = duplicate_paper_ids == 0 and missing_paper_ids == 0
    passed_no_null_titles = missing_titles == 0
    passed_summary_length = too_short_summaries == 0
    passed_freshness = stale_rows == 0
    
    all_passed = bool(passed_row_count and passed_unique_ids and passed_no_null_titles and passed_summary_length and passed_freshness)
    
    report = {
        "report_name": report_name,
        "total_rows": total_rows,
        "missing_paper_ids": missing_paper_ids,
        "duplicate_paper_ids": duplicate_paper_ids,
        "missing_titles": missing_titles,
        "avg_summary_chars": avg_summary_chars,
        "too_short_summaries": too_short_summaries,
        "stale_rows": stale_rows,
        "passed_checks": {
            "row_count": bool(passed_row_count),
            "unique_ids": bool(passed_unique_ids),
            "no_null_titles": bool(passed_no_null_titles),
            "summary_length": bool(passed_summary_length),
            "freshness": bool(passed_freshness)
        },
        "all_passed": all_passed
    }
    
    out_dir = settings.paths.quality_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    report_file = out_dir / f"{report_name}.json"
    write_json(report_file, report)
    
    return report


def build_freshness_report(df: pd.DataFrame, settings: Settings, report_path) -> dict[str, Any]:
    """Assess freshness metrics of the dataset and save freshness report."""
    if len(df) == 0:
        report = {
            "latest_published": "N/A",
            "oldest_published": "N/A",
            "stale_rows": 0,
            "total_rows": 0,
            "is_fresh": False
        }
    else:
        latest_published = str(df["published"].max())
        oldest_published = str(df["published"].min())
        stale_rows = int((df["age_days"] > settings.freshness_threshold_days).sum())
        total_rows = len(df)
        is_fresh = stale_rows == 0
        
        report = {
            "latest_published": latest_published,
            "oldest_published": oldest_published,
            "stale_rows": stale_rows,
            "total_rows": total_rows,
            "is_fresh": bool(is_fresh),
        }
        
    write_json(Path(report_path), report)
    return report

