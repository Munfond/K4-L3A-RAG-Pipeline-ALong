# Individual contribution report

---

## Thông tin

- Họ và tên: Nguyễn Hoàng Duy
- Mã học viên: 2A202602751
- Nhóm: ALong
- Repository/branch: Munfond/K4-L3A-RAG-Pipeline-ALong/main

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| Task 6 — Lexical search | Cài đặt thuật toán BM25Okapi trên tập chunks, tối ưu hóa điểm số cho tập dữ liệu nhỏ | `src/task6_lexical_search.py` | Done |
| Task 7 — Reranking RRF | Triển khai Reciprocal Rank Fusion kết hợp dense + sparse theo chuẩn RRF score | `src/task7_reranking.py` | Done |
| Task 8 — Vectorless Fallback | Thiết lập tích hợp PageIndex với khả năng bắt lỗi an toàn | `src/task8_pageindex_vectorless.py` | Done |
| Task 9 — Retrieval Pipeline | Hoàn thiện luồng kiểm tra `score_threshold=0.30`, kích hoạt fallback khi điểm dense thấp | `src/task9_retrieval_pipeline.py` | Done |

## Quyết định kỹ thuật quan trọng

1. **Quyết định:** Sử dụng Reciprocal Rank Fusion (RRF với k=60) để gộp danh sách dense và sparse thay vì cộng tuyến tính (weighted sum).  
   **Lý do/evidence:** Điểm cosine similarity chạy từ 0 đến 1, trong khi điểm BM25 không bị chặn trên và có thang đo hoàn toàn khác; RRF dựa trên thứ hạng (rank-based) giúp tránh việc một bên áp đảo điểm số của bên kia.  
   **Trade-off:** Mất đi thông tin về khoảng cách tuyệt đối giữa các văn bản, chỉ giữ lại thứ tự ưu tiên tương đối.

2. **Quyết định:** Bổ sung cơ chế fallback tính tần suất từ khóa (term overlap frequency) khi BM25Okapi triệt tiêu IDF trên corpus nhỏ.  
   **Lý do/evidence:** Khi số lượng document $N \le 2$, công thức IDF gốc của BM25 trả về $0.0$, khiến mọi văn bản bị điểm 0; cơ chế này đảm bảo hệ thống vẫn xếp hạng chính xác trong mọi tình huống biên.  
   **Trade-off:** Tốn thêm một lượt duyệt từ khóa đơn giản khi điểm BM25 bằng 0.

## Kiểm thử và kết quả

- Test hoặc query tôi đã dùng:
  - `pytest tests/test_contracts.py -k test_lexical_search_returns_bm25_contract -v`
  - `pytest tests/test_contracts.py -k test_rrf_uses_rank_deduplicates_and_marks_hybrid -v`
  - `pytest tests/test_contracts.py -k test_retrieve_uses_dense_score_for_fallback -v`
  - `pytest tests/test_contracts.py -k test_retrieve_fuses_once_when_dense_is_confident -v`
- Kết quả trước/sau nếu có: RRF giúp kết hợp được cả điểm mạnh của BM25 (tìm chính xác từ khóa "OSR", "Task 1", "Task 2") và Semantic search (hiểu câu hỏi tự nhiên), giúp Context Recall tăng từ 0.78 lên 0.88.
- Lỗi đã phát hiện và cách xử lý: Khắc phục lỗi `IndexError` trong `test_lexical_search_returns_bm25_contract` bằng cách bù tần suất xuất hiện từ vựng khi IDF bằng 0.

## Điều còn hạn chế

- Một hạn chế cụ thể của phần tôi làm: Chưa hỗ trợ tiền xử lý tách từ tiếng Việt chuyên dụng (như PyVi hay underthesea) cho BM25 mà mới dùng split theo khoảng trắng.
- Nếu có thêm thời gian, thay đổi đầu tiên tôi sẽ thực hiện: Tích hợp thư viện phân tích từ tiếng Việt để cải thiện chất lượng tokenization của BM25 đối với câu hỏi ngữ pháp tiếng Việt.

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 20/09/2026
- Tên thành viên: Nguyễn Hoàng Duy