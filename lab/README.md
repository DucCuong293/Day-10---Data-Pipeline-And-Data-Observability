# Day 10 - Data Pipeline And Data Observability

Chao cac ban den voi bai lab Day 10.

Muc tieu cua bai nay la xay dung mot ETL pipeline nho nhung day du cho mot he thong RAG:

- Lay du lieu hoc thuat tu external source
- Lam sach va chuan hoa thanh cleaned dataset
- Tao embedding va nap vao ChromaDB
- Xay agent de tra loi cau hoi tren bo du lieu
- Danh gia chat luong cua agent truoc va sau khi du lieu bi corrupt
- Tao bao cao data quality, freshness, va metrics comparison

Trong folder `lab/`, mot so phan da duoc giu lai o muc "real code" de cac ban co the tham khao cach to chuc codebase:

- `src/day10_lab/retrieval/agent.py`
- `src/day10_lab/retrieval/llm.py`
- `src/day10_lab/retrieval/embeddings.py`
- `src/day10_lab/retrieval/index.py`
- `src/day10_lab/retrieval/qa.py`
- `src/day10_lab/evaluation/metrics.py`
- `src/day10_lab/core/config.py`
- `src/day10_lab/core/utils.py`

Nhung phan ETL, observability, test set, va pipeline orchestration duoc de o dang scaffold/pseudo-code de cac ban tu hoan thien.

Codebase duoc chia theo module:

- `core/`: config va utility dung chung
- `ingestion/`: load source, clean, corrupt data
- `retrieval/`: embeddings, vector store, LLM providers, agent
- `evaluation/`: test set va scoring
- `observability/`: quality checks, freshness, reports
- `pipelines/`: flow baseline va flow corruption
- `scripts/`: entrypoint de chay lab

Tai lieu huong dan:

- [Guide.md](Guide.md)
- [Rubric.md](Rubric.md)

Goi y cach bat dau:

```bash
uv sync
uv run python scripts/run_phase1.py
```

Neu code chua chay duoc, do la binh thuong. Cac ban can hoan thanh cac file pseudo-code truoc, sau do moi co the chay end-to-end.
