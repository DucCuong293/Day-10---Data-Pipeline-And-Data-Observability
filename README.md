# Day 10 - Data Pipeline and Data Observability for RAG System

Dự án này là lời giải hoàn chỉnh cho bài Lab Day 10 về **Xây dựng đường ống dữ liệu (ETL Pipeline)** và **Giám sát chất lượng dữ liệu (Data Observability)** cho hệ thống RAG (Retrieval-Augmented Generation). 

**Thông tin sinh viên:**
*   **Họ và tên:** Nguyễn Đức Cường
*   **Mã học viên:** 2A202600794
*   **Lớp:** VinUni AI20k
*   **Báo cáo chi tiết tiếng Việt:** [LAB_REPORT.md](LAB_REPORT.md)

---

## 1. Kiến trúc hệ thống & Quy trình thực hiện

Hệ thống mô phỏng một quy trình vòng đời dữ liệu khép kín cho RAG bao gồm:
1.  **Ingestion:** Thu thập tự động các bài báo khoa học liên quan đến RAG và Agentic AI từ API của Crossref ([crossref.py](src/ingestion/crossref.py)).
2.  **Cleaning:** Làm sạch nội dung, loại bỏ thẻ XML, khử trùng lặp và tính toán độ tươi mới dữ liệu [cleaning.py](src/ingestion/cleaning.py).
3.  **Indexing:** Nhúng dữ liệu (Embedding) và đẩy vào cơ sở dữ liệu Vector Store ChromaDB [index.py](src/retrieval/index.py).
4.  **Test Set:** Tự động sinh tập câu hỏi đánh giá ngữ cảnh [testset.py](src/evaluation/testset.py).
5.  **Observability:** Giám sát chất lượng dữ liệu thời gian thực thông qua 5 bài kiểm tra chất lượng (Data Quality Checks) và báo cáo độ trễ (Freshness Reports) [quality.py](src/observability/quality.py).
6.  **Corruption (Giả lập lỗi):** Mô phỏng các sự cố dữ liệu thực tế (mất tóm tắt, cắt ngắn tiêu đề, lỗi ký tự, trùng hàng) để đo lường mức độ suy giảm hiệu năng của Agent [corruption.py](src/ingestion/corruption.py).
7.  **Repair (Khôi phục):** Tự động kích hoạt cơ chế kéo dữ liệu thô sạch từ snapshot nguồn gốc để làm sạch và lập chỉ mục lại, phục hồi 100% hiệu năng.

---

## 2. Kết quả đo lường thực tế

Dưới đây là bảng so sánh hiệu năng của RAG Agent (đánh giá bằng OpenAI `gpt-4o-mini` làm LLM Judge) qua các pha khác nhau của dữ liệu:

| Chỉ số / Trạng thái | Baseline (Dữ liệu sạch) | Corrupted (Dữ liệu lỗi) | Repaired (Sau sửa lỗi) | Tác động của lỗi dữ liệu |
| :--- | :---: | :---: | :---: | :---: |
| **Tổng số bản ghi** | 23 | 21 | 23 | Bị mất 2 bản ghi |
| **Kiểm định DQ** | **PASSED** | **FAILED** | **PASSED** | Phát hiện lỗi chất lượng |
| **Độ mới (Freshness)**| **FRESH** | **STALE** | **FRESH** | Phát hiện dữ liệu cũ quá hạn |
| **Retrieval Hit Rate** | 100.0% | 80.0% | 100.0% | **Giảm 20.0%** |
| **Mean Token F1 Score** | 100.0% | 76.6% | 100.0% | **Giảm 23.4%** |
| **LLM Judge Accuracy** | 100.0% | 80.0% | 100.0% | **Giảm 20.0%** |
| **Điểm LLM Judge (1-5)** | 5.00 | 4.25 | 5.00 | **Giảm 0.75đ** |

### Biểu đồ so sánh hiệu năng trực quan:
![RAG Performance Comparison](data/reports/metrics_comparison.svg)

---

## 3. Cài đặt & Hướng dẫn sử dụng

### 3.1. Cài đặt môi trường
Đảm bảo bạn đã cài đặt `uv`. Chạy lệnh sau tại thư mục gốc dự án để tự động tạo môi trường ảo và tải dependencies:
```bash
uv sync --python 3.13
```

### 3.2. Cấu hình biến môi trường
Tạo file `.env` từ `.env.example` và điền khóa API OpenAI của bạn:
```env
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
OPENAI_API_KEY=sk-proj-...
```

### 3.3. Thực thi kịch bản
*   **Chạy Baseline Flow (Pha 1):** Thu thập dữ liệu sạch, lập chỉ mục, sinh tập kiểm thử và đánh giá ban đầu.
    ```bash
    uv run python script/run_phase1.py
    ```
    *Xem báo cáo tại:* [phase1_report.md](data/reports/phase1_report.md)

*   **Chạy Corruption & Repair Flow (Pha 2):** Giả lập dữ liệu lỗi, đánh giá chất lượng bị giảm, tự động chạy quy trình sửa lỗi và xuất báo cáo so sánh.
    ```bash
    uv run python script/run_corruption_flow.py
    ```
    *Xem báo cáo so sánh tại:* [corruption_report.md](data/reports/corruption_report.md)
