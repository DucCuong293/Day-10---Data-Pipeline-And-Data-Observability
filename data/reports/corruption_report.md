# Data Pipeline Observability - Data Corruption & Recovery Report

This report evaluates the impact of data corruption on RAG performance and verifies the effectiveness of the recovery pipeline.

## 1. Metric Comparison Summary

The table below contrasts the RAG system metrics and data quality indicators across the three lifecycle phases:

| Indicator / Metric | Baseline (Clean) | Corrupted (Lỗi) | Repaired (Đã sửa) | Impact of Corruption |
| :--- | :---: | :---: | :---: | :---: |
| **Total Cleaned Records** | 23 | 21 | 23 | -2 rows |
| **Data Quality Check** | PASSED | FAILED | PASSED | Failed Quality Check |
| **Freshness Check** | FRESH | STALE | FRESH | Stale Data Detected |
| **Retrieval Hit Rate** | 100.0% | 80.0% | 100.0% | -20.0% Drop |
| **Mean Token F1 Score** | 100.0% | 76.6% | 100.0% | -23.4% Drop |
| **LLM Judge Accuracy** | 100.0% | 80.0% | 100.0% | -20.0% Drop |
| **Mean Judge Score (1-5)** | 5.00 | 4.25 | 5.00 | -0.75 Drop |

![Metrics Comparison Plot](metrics_comparison.svg)

## 2. Key Observations and Analysis

### Impact of Data Corruption on RAG Performance
- **Retrieval Hit Rate degradation:** When summaries were corrupted, titles truncated, or latest papers dropped, the embedding matching in ChromaDB was severely impacted. The retrieval hit rate fell by **20.0%**.
- **Answer Quality Drop:** The mean Token F1 score fell by **23.4%** and the LLM Judge accuracy fell by **20.0%**. This clearly demonstrates that corrupt data (e.g. truncated titles or blank/noisy summaries) prevents the RAG agent from locating the correct context and answering questions accurately.

### Effectiveness of the Repair Pipeline
- **Quality Restoration:** Re-running the ingestion from the clean raw records restored the data quality checks to **PASSED** and freshness checks to **FRESH**.
- **Performance Recovery:** After reconstructing the index with clean repaired data, the retrieval hit rate recovered by **+20.0%** and LLM Judge accuracy recovered by **+20.0%** (returning to baseline levels).

## 3. Data Observability Recommendations
1. **Enable active data quality checking** at the ingestion boundaries to block malformed titles or blank summaries.
2. **Monitor freshness metrics** continuously to detect stale document corpuses.
3. **Automate the repair pipeline** to reload from source archives when an anomaly is triggered by the quality gate.