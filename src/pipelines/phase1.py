from __future__ import annotations


import json
from pathlib import Path
from core.config import load_settings
from core.utils import now_utc, write_csv, write_json
from ingestion.crossref import fetch_source_records, load_raw_records
from ingestion.cleaning import build_clean_dataframe
from retrieval.index import LocalEmbeddingIndex
from evaluation.testset import build_test_set
from evaluation.metrics import evaluate_pipeline
from observability.quality import run_data_quality_checks, build_freshness_report
from observability.reporting import generate_phase1_report
from retrieval.qa import answer_question

def main() -> None:
    """Run baseline pipeline end-to-end."""
    print("Starting Phase 1 Baseline Pipeline...")
    
    # 1. Load settings
    settings = load_settings()
    
    # 2. Load or fetch raw records
    raw_records_path = settings.paths.raw_records_json
    if settings.refresh_source or not raw_records_path.exists():
        print("Fetching raw papers from Crossref API...")
        records = fetch_source_records(settings)
    else:
        print("Loading cached raw papers from disk...")
        records = load_raw_records(raw_records_path)
        
    print(f"Total raw records loaded: {len(records)}")
    
    # 3. Clean data
    run_date = now_utc()
    df_clean = build_clean_dataframe(records, run_date)
    print(f"Total cleaned papers: {len(df_clean)}")
    
    # 4. Save clean CSV/JSON
    df_clean.to_json(settings.paths.clean_json, orient="records", indent=2)
    write_csv(df_clean, settings.paths.clean_csv)
    
    # 5. Build Chroma index
    print("Building Chroma index...")
    index = LocalEmbeddingIndex.build(df_clean, settings, settings.paths.embeddings_json)
    
    # 6. Create or load evaluation set
    eval_path = settings.paths.eval_testset
    if settings.refresh_test_set or not eval_path.exists():
        print("Generating new evaluation test set...")
        test_set = build_test_set(df_clean, eval_path)
    else:
        print("Loading cached evaluation test set...")
        with open(eval_path, "r", encoding="utf-8") as f:
            test_set = json.load(f)
            
    print(f"Total test questions: {len(test_set)}")
    
    # 7. Evaluate
    print("Evaluating baseline pipeline...")
    bundle = evaluate_pipeline(
        settings=settings,
        index=index,
        test_set_path=eval_path,
        metrics_output_path=settings.paths.baseline_metrics,
        answers_output_path=settings.paths.baseline_answers
    )
    
    # 8. Run quality checks and freshness report
    print("Running quality and freshness checks...")
    quality = run_data_quality_checks(df_clean, settings, "baseline_quality")
    freshness = build_freshness_report(df_clean, settings, settings.paths.freshness_report)
    
    # 9. Create markdown report
    print("Generating baseline markdown report...")
    source_summary = {
        "source_api": settings.source_api,
        "source_query": settings.source_query,
        "source_filter": settings.source_filter,
        "max_results": settings.max_results,
        "total_ingested": len(records)
    }
    generate_phase1_report(
        report_path=settings.paths.baseline_report,
        source_summary=source_summary,
        metrics=bundle.summary,
        quality=quality,
        freshness=freshness
    )
    
    # 10. Demo agent on some sample questions and save answers
    print("Running agent demo questions...")
    demo_questions = [
        "Who authored the first paper?",
        "When was the latest paper published?",
        "What categories are covered by the corpus?"
    ]
    demo_answers = []
    for q in demo_questions[:3]:
        ans_res = answer_question(q, settings=settings, index=index)
        demo_answers.append({
            "question": q,
            "answer": ans_res.answer,
            "retrieved_titles": ans_res.retrieved_titles
        })
    write_json(settings.paths.demo_answers, demo_answers)
    
    print("Baseline pipeline completed successfully.")

