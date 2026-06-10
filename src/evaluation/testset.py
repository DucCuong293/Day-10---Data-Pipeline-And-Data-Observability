from __future__ import annotations

from typing import Any

import pandas as pd


from core.utils import write_json, first_sentence

def build_test_set(df: pd.DataFrame, output_path) -> list[dict[str, Any]]:
    """Build evaluation test set from cleaned DataFrame and write to JSON."""
    if len(df) < 3:
        raise ValueError("DataFrame has too few documents to generate a representative test set (minimum 3 required).")
        
    sample_size = min(5, len(df))
    # Pick a spread of papers across the dataframe
    indices = [int(i * (len(df) - 1) / (sample_size - 1)) if sample_size > 1 else 0 for i in range(sample_size)]
    sample_df = df.iloc[indices]
    
    test_set = []
    q_id_counter = 1
    
    for _, row in sample_df.iterrows():
        title = row["title"]
        paper_id = row["paper_id"]
        
        # 1. Authors question
        test_set.append({
            "id": f"q_{q_id_counter:03d}",
            "question_type": "authors",
            "question": f"Who authored the paper '{title}'?",
            "ground_truth": row["authors_joined"],
            "ground_truth_doc_ids": [paper_id]
        })
        q_id_counter += 1
        
        # 2. Date question
        test_set.append({
            "id": f"q_{q_id_counter:03d}",
            "question_type": "date",
            "question": f"When was the paper '{title}' published?",
            "ground_truth": row["published"],
            "ground_truth_doc_ids": [paper_id]
        })
        q_id_counter += 1
        
        # 3. Categories question
        test_set.append({
            "id": f"q_{q_id_counter:03d}",
            "question_type": "categories",
            "question": f"What categories does the paper '{title}' belong to?",
            "ground_truth": row["categories_joined"],
            "ground_truth_doc_ids": [paper_id]
        })
        q_id_counter += 1
        
        # 4. Summary question
        test_set.append({
            "id": f"q_{q_id_counter:03d}",
            "question_type": "summary",
            "question": f"What is the main contribution or summary of the paper '{title}'?",
            "ground_truth": first_sentence(row["summary"]),
            "ground_truth_doc_ids": [paper_id]
        })
        q_id_counter += 1
        
    from pathlib import Path
    write_json(Path(output_path), test_set)
    return test_set

