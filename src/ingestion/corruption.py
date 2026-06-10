from __future__ import annotations

import pandas as pd


from pathlib import Path
from core.utils import write_json

def corrupt_clean_dataframe(df: pd.DataFrame, output_log_path) -> pd.DataFrame:
    """Simulate various data corruption scenarios on the clean DataFrame and log changes."""
    if len(df) == 0:
        return df.copy()
        
    corrupted_df = df.copy()
    corruption_log = {
        "dropped_records": [],
        "blanked_summaries": [],
        "noisy_summaries": [],
        "truncated_titles": [],
        "stale_dates": [],
        "duplicated_rows": []
    }
    
    # 1. Drop some latest records (first 20% of records or at least 2 records)
    drop_count = max(2, len(corrupted_df) // 5)
    dropped_papers = corrupted_df.iloc[:drop_count]
    for _, row in dropped_papers.iterrows():
        corruption_log["dropped_records"].append({
            "paper_id": row["paper_id"],
            "title": row["title"]
        })
    corrupted_df = corrupted_df.iloc[drop_count:].copy().reset_index(drop=True)
    
    # 2. Blank summary of some rows (set to empty string for 2 rows)
    blank_indices = [0, min(1, len(corrupted_df) - 1)]
    for idx in blank_indices:
        if idx < len(corrupted_df):
            paper_id = corrupted_df.loc[idx, "paper_id"]
            orig_summary = corrupted_df.loc[idx, "summary"]
            corrupted_df.loc[idx, "summary"] = ""
            corruption_log["blanked_summaries"].append({
                "paper_id": paper_id,
                "original_summary": orig_summary
            })
            
    # 3. Inject noise into summary (for 2 rows starting from index 2)
    noise_indices = [min(2, len(corrupted_df) - 1), min(3, len(corrupted_df) - 1)]
    noise_indices = list(set(noise_indices))
    for idx in noise_indices:
        if idx < len(corrupted_df):
            paper_id = corrupted_df.loc[idx, "paper_id"]
            orig_summary = corrupted_df.loc[idx, "summary"]
            corrupted_df.loc[idx, "summary"] = "SYSTEM ERROR 404: DATA CORRUPTED " + orig_summary + " Lorem ipsum dolor sit amet."
            corruption_log["noisy_summaries"].append({
                "paper_id": paper_id,
                "original_summary": orig_summary
            })
            
    # 4. Make title truncated (for 2 rows starting from index 4)
    trunc_indices = [min(4, len(corrupted_df) - 1), min(5, len(corrupted_df) - 1)]
    trunc_indices = list(set(trunc_indices))
    for idx in trunc_indices:
        if idx < len(corrupted_df):
            paper_id = corrupted_df.loc[idx, "paper_id"]
            orig_title = corrupted_df.loc[idx, "title"]
            corrupted_df.loc[idx, "title"] = orig_title[:15] + "..."
            corruption_log["truncated_titles"].append({
                "paper_id": paper_id,
                "original_title": orig_title,
                "corrupted_title": corrupted_df.loc[idx, "title"]
            })
            
    # 5. Make published date stale (for 2 rows starting from index 6)
    stale_indices = [min(6, len(corrupted_df) - 1), min(7, len(corrupted_df) - 1)]
    stale_indices = list(set(stale_indices))
    for idx in stale_indices:
        if idx < len(corrupted_df):
            paper_id = corrupted_df.loc[idx, "paper_id"]
            orig_date = corrupted_df.loc[idx, "published"]
            corrupted_df.loc[idx, "published"] = "2010-01-01"
            corrupted_df.loc[idx, "age_days"] = 6000
            corruption_log["stale_dates"].append({
                "paper_id": paper_id,
                "original_published": orig_date
            })
            
    # 6. Add duplicate rows (duplicate the first row 2 times)
    if len(corrupted_df) > 0:
        dup_row = corrupted_df.iloc[[0]]
        corrupted_df = pd.concat([corrupted_df, dup_row, dup_row], ignore_index=True)
        corruption_log["duplicated_rows"].append({
            "paper_id": dup_row.iloc[0]["paper_id"],
            "title": dup_row.iloc[0]["title"]
        })
        
    # 7. Rebuild text_for_embedding with the corrupted texts
    for idx, row in corrupted_df.iterrows():
        title = row["title"]
        authors = row["authors_joined"]
        categories = row["categories_joined"]
        summary = row["summary"]
        corrupted_df.loc[idx, "text_for_embedding"] = (
            f"Title: {title}\n"
            f"Authors: {authors}\n"
            f"Categories: {categories}\n"
            f"Summary: {summary}"
        )
        corrupted_df.loc[idx, "summary_chars"] = len(summary)
        
    # 8. Save corruption log
    write_json(Path(output_log_path), corruption_log)
    
    return corrupted_df

