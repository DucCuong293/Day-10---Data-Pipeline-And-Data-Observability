# Guide

## Tong quan

Bai lab nay mo phong mot data pipeline nho cho he thong RAG. Cac ban se di qua 2 pha:

1. Xay baseline pipeline voi du lieu sach
2. Gia lap du lieu loi, do impact len agent, sau do repair va so sanh

## Buoc 1: Cai moi truong

1. Di chuyen vao folder `lab/`
2. Tao file `.env` neu can
3. Cai dependency:

```bash
uv sync
```

## Buoc 2: Hieu cau truc code

- `core/config.py`: noi chua path va settings
- `ingestion/crossref.py`: load du lieu raw tu source
- `ingestion/cleaning.py`: clean va tao bang du lieu
- `retrieval/index.py`: embedding + ChromaDB
- `retrieval/agent.py`: RAG agent
- `evaluation/metrics.py`: cham diem
- `observability/quality.py`: data quality va freshness
- `pipelines/phase1.py`: baseline flow
- `pipelines/corruption_flow.py`: corruption flow

## Buoc 3: Load raw data tu source

Can hoan thanh:

- `src/day10_lab/ingestion/crossref.py`

Yeu cau:

- Goi external source de lay danh sach paper
- Parse response thanh record schema nhat quan
- Luu raw response vao `data/raw/`
- Luu raw records da parse vao `data/raw/`

Sau khi xong, em nen tu tra loi:

- Source nao dang duoc dung?
- Query/filter la gi?
- Record schema gom nhung truong nao?

## Buoc 4: Lam sach du lieu

Can hoan thanh:

- `src/day10_lab/ingestion/cleaning.py`

Yeu cau:

- Remove record khong hop le
- Chuan hoa title, summary, authors, categories
- Tao cot `text_for_embedding`
- Tinh freshness fields nhu `published`, `age_days`
- Luu cleaned data vao `data/clean/`

## Buoc 5: Tao evaluation set

Can hoan thanh:

- `src/day10_lab/evaluation/testset.py`

Yeu cau:

- Tao bo cau hoi tu cleaned dataset
- Moi sample can co `question`, `ground_truth`, `ground_truth_doc_ids`, `question_type`

## Buoc 6: Tao embedding va vector store

Phan nay da co code tham khao o:

- `src/day10_lab/retrieval/embeddings.py`
- `src/day10_lab/retrieval/index.py`

Can doc ky:

- Cach dung `sentence-transformers/all-MiniLM-L6-v2`
- Cach tao collection trong ChromaDB
- Cach query top-k context

## Buoc 7: Cau hinh LLM provider

Phan nay da co code tham khao o:

- `src/day10_lab/retrieval/llm.py`

Provider can support:

- OpenAI
- Gemini
- Anthropic
- OpenRouter
- Ollama
- Custom OpenAI-compatible endpoint

Nhiem vu cua em:

- Doc code
- Hieu `LLM_PROVIDER`, `LLM_MODEL`, va cac API key duoc map nhu the nao

## Buoc 8: Chay agent

Phan agent da co code tham khao o:

- `src/day10_lab/retrieval/agent.py`
- `src/day10_lab/retrieval/qa.py`

Sau khi ETL va index xong, agent co the:

- Semantic search trong local corpus
- Lookup theo `paper_id` hoac exact title
- Tra loi cau hoi factual

## Buoc 9: Chay baseline pipeline

Can hoan thanh:

- `src/day10_lab/pipelines/phase1.py`

Pipeline baseline can:

1. Load/fetch raw records
2. Clean data
3. Build embedding index
4. Tao hoac load test set
5. Evaluate
6. Run data quality checks
7. Tao freshness report
8. Tao report markdown

Sau khi code xong, chay:

```bash
uv run python scripts/run_phase1.py
```

Can kiem tra output trong:

- `data/clean/`
- `data/embeddings/`
- `data/eval/`
- `data/results/`
- `data/quality/`
- `data/reports/`

## Buoc 10: Doc score

Can doc file:

- `data/results/baseline_metrics.json`

Chi so can quan tam:

- `retrieval_hit_rate`
- `mean_token_f1`
- `judge_accuracy`
- `mean_judge_score`
- `ragas`

## Buoc 11: Tao data quality report

Can hoan thanh:

- `src/day10_lab/observability/quality.py`
- `src/day10_lab/observability/reporting.py`

Yeu cau toi thieu:

- Data quality checks
- Freshness monitoring
- Markdown report

## Buoc 12: Corrupt du lieu

Can hoan thanh:

- `src/day10_lab/ingestion/corruption.py`
- `src/day10_lab/pipelines/corruption_flow.py`

Y tuong corruption:

- Xoa mot so latest records
- Blank summary
- Add noise vao summary
- Truncate title
- Lam stale publication date
- Add duplicate rows

## Buoc 13: Re-evaluate sau corruption

Flow corruption can:

1. Doc cleaned baseline
2. Tao corrupted dataset
3. Rebuild embedding
4. Evaluate tren test set cu
5. Run quality checks
6. Tao freshness report
7. Repair lai tu raw source
8. Evaluate lai lan nua
9. Tao comparison report

Chay:

```bash
uv run python scripts/run_corruption_flow.py
```

## Buoc 14: So sanh baseline, corrupted, repaired

Can so sanh:

- Retrieval hit rate
- Token F1
- Judge accuracy
- Mean judge score
- Data quality success/fail
- Freshness status

Muc tieu la chung minh:

- Du lieu xau lam giam performance cua agent
- Repair dung cach se phuc hoi performance

## Buoc 15: Tu review truoc khi nop

Checklist:

- Code co chia module ro rang khong?
- Raw/clean/eval/results duoc luu day du khong?
- Agent co chay duoc khong?
- Metrics co hop ly khong?
- Report markdown co doc duoc khong?
- Co chung minh duoc impact cua corruption khong?
