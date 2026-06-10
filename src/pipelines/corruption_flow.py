from __future__ import annotations


import pandas as pd
from pathlib import Path
from core.config import load_settings
from core.utils import now_utc, read_json, write_csv
from ingestion.crossref import load_raw_records
from ingestion.cleaning import build_clean_dataframe
from ingestion.corruption import corrupt_clean_dataframe
from retrieval.index import LocalEmbeddingIndex
from evaluation.metrics import evaluate_pipeline
from observability.quality import run_data_quality_checks, build_freshness_report
from observability.reporting import generate_corruption_report

def main() -> None:
    """Run corruption simulation, evaluation, repair, and comparison reporting."""
    print("Starting Phase 2 Corruption & Repair Pipeline...")
    
    # 1. Load settings
    settings = load_settings()
    
    # 2. Read baseline clean dataset and metrics
    clean_json_path = settings.paths.clean_json
    if not clean_json_path.exists():
        raise FileNotFoundError(f"Clean dataset not found at {clean_json_path}. Please run run_phase1.py first.")
    df_clean = pd.read_json(clean_json_path)
    print(f"Loaded {len(df_clean)} clean records from baseline.")
    
    baseline_metrics = read_json(settings.paths.baseline_metrics)
    
    # 3. Create corrupted dataset
    print("Simulating data corruption...")
    df_corrupted = corrupt_clean_dataframe(df_clean, settings.paths.corruption_log)
    print(f"Corrupted dataset contains {len(df_corrupted)} records.")
    
    # 4. Save corrupted artifacts
    df_corrupted.to_json(settings.paths.corrupted_clean_json, orient="records", indent=2)
    write_csv(df_corrupted, settings.paths.corrupted_clean_csv)
    
    # 5. Rebuild embedding index with corrupted data
    print("Building Chroma index for corrupted data...")
    index_corrupted = LocalEmbeddingIndex.build(df_corrupted, settings, settings.paths.corrupted_embeddings_json)
    
    # 6. Evaluate on corrupted index
    print("Evaluating corrupted RAG pipeline...")
    corrupted_bundle = evaluate_pipeline(
        settings=settings,
        index=index_corrupted,
        test_set_path=settings.paths.eval_testset,
        metrics_output_path=settings.paths.corrupted_metrics,
        answers_output_path=settings.paths.corrupted_answers
    )
    
    # 7. Run quality checks on corrupted data
    print("Running quality and freshness checks on corrupted data...")
    corrupted_quality = run_data_quality_checks(df_corrupted, settings, "corrupted_quality")
    corrupted_freshness = build_freshness_report(df_corrupted, settings, settings.paths.quality_dir / "freshness_report_corrupted.json")
    
    # 8. Repair data: reload clean raw records and clean them again
    print("Repairing data from raw snapshot...")
    raw_records = load_raw_records(settings.paths.raw_records_json)
    run_date = now_utc()
    df_repaired = build_clean_dataframe(raw_records, run_date)
    print(f"Repaired dataset contains {len(df_repaired)} clean records.")
    
    # Save repaired artifacts
    df_repaired.to_json(settings.paths.repaired_clean_json, orient="records", indent=2)
    write_csv(df_repaired, settings.paths.repaired_clean_csv)
    
    # 9. Rebuild embedding index with repaired data
    print("Building Chroma index for repaired data...")
    index_repaired = LocalEmbeddingIndex.build(df_repaired, settings, settings.paths.repaired_embeddings_json)
    
    # 10. Evaluate on repaired index
    print("Evaluating repaired RAG pipeline...")
    repaired_bundle = evaluate_pipeline(
        settings=settings,
        index=index_repaired,
        test_set_path=settings.paths.eval_testset,
        metrics_output_path=settings.paths.repaired_metrics,
        answers_output_path=settings.paths.repaired_answers
    )
    
    # 11. Run quality checks on repaired data
    print("Running quality and freshness checks on repaired data...")
    repaired_quality = run_data_quality_checks(df_repaired, settings, "repaired_quality")
    repaired_freshness = build_freshness_report(df_repaired, settings, settings.paths.quality_dir / "freshness_report_repaired.json")
    
    # 12. Create comparison report
    print("Generating corruption and recovery comparison report...")
    generate_corruption_report(
        report_path=settings.paths.comparison_report,
        baseline_metrics=baseline_metrics,
        corrupted_metrics=corrupted_bundle.summary,
        repaired_metrics=repaired_bundle.summary,
        corrupted_quality=corrupted_quality,
        repaired_quality=repaired_quality,
        corrupted_freshness=corrupted_freshness,
        repaired_freshness=repaired_freshness
    )
    
    print("Corruption & Repair pipeline completed successfully.")

