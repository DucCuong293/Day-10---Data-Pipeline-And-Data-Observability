# Phase 1 - Baseline Data Pipeline Report

This report summarizes the baseline performance and data observability metrics for the RAG scholarly paper pipeline.

## 1. Source Summary
- **Source API:** Crossref REST API
- **Query:** `agentic retrieval augmented generation large language model`
- **Filter:** `from-pub-date:2025-12-12,has-abstract:true`
- **Max Results Configured:** 24
- **Total Records Ingested:** 24

## 2. Data Quality & Freshness
- **Data Quality Check Status:** PASSED
- **Total Cleaned Records:** 23
- **Missing Paper IDs:** 0
- **Duplicate Paper IDs:** 0
- **Missing Titles:** 0
- **Average Summary Length:** 1807.0 characters
- **Short Summaries (<30 chars):** 0
- **Freshness Status:** FRESH
- **Latest Publication Date:** 2026-06-02
- **Oldest Publication Date:** 2025-12-19
- **Stale Records (> threshold):** 0

## 3. RAG Retrieval & Q&A Performance Metrics
- **Total Test Samples:** 20
- **Retrieval Hit Rate:** 100.0%
- **Mean Token F1 Score:** 100.0%
- **LLM Judge Accuracy:** 100.0%
- **Mean Judge Score (1-5):** 5.00 / 5.0

---
Report generated at: 2026-06-10T07:59:41.980414+00:00