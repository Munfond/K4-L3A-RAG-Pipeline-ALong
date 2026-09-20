# RAG evaluation results

## Run information

| Field                              | Value |
| ---------------------------------- | ----- |
| Evaluation date                    | 2026-09-20 |
| Framework and version              | Ragas 0.4.3, LangChain 1.4.2 |
| Evaluator model                    | gpt-4o-mini |
| Generator model                    | gpt-4o-mini |
| Embedding model                    | BAAI/bge-m3 |
| Corpus version/commit              | 42199f6 |
| Golden dataset size                | 15 Q&A pairs |
| `top_k`                            | 5 |
| Fallback threshold and calibration | 0.30 (Cosine similarity score) |

## Configurations

- **Config A — dense-only:** Semantic search thuần túy sử dụng ChromaDB vector store kết hợp embedding model BAAI/bge-m3, lấy top 5 chunks theo độ tương đồng cosine (use_reranking=False).
- **Config B — hybrid + RRF:** Kết hợp dense semantic search (ChromaDB) và sparse lexical search (BM25Okapi), sau đó tổng hợp bảng xếp hạng bằng Reciprocal Rank Fusion với hệ số k=60 (use_reranking=True).

Hai config phải dùng cùng golden dataset, generator, evaluator, prompt và `top_k`; chỉ thay retrieval strategy.

## Overall scores

| Metric            | Config A (Dense-only) | Config B (Hybrid + RRF) | Delta B−A |
| ----------------- | --------------------: | ----------------------: | --------: |
| Faithfulness      |                  0.84 |                    0.92 |     +0.08 |
| Answer relevance  |                  0.81 |                    0.89 |     +0.08 |
| Context recall    |                  0.78 |                    0.88 |     +0.10 |
| Context precision |                  0.75 |                    0.86 |     +0.11 |
| **Average**       |                 0.795 |                   0.888 |    +0.093 |

## A/B comparison

- Cấu hình tốt hơn: Cấu hình B (Hybrid + RRF) vượt trội rõ rệt so với Cấu hình A (Dense-only) trên cả 4 chỉ số đánh giá.
- Evidence: Context precision tăng từ 0.75 lên 0.86 (+0.11) và Context recall tăng từ 0.78 lên 0.88 (+0.10). Các truy vấn chứa từ khóa kỹ thuật hoặc thuật ngữ chuyên ngành (như "One Skill Retake", "compound adjectives", "although/despite") được BM25 bắt chính xác và đưa lên vị trí đầu qua RRF.
- Trade-off về latency/cost: Hybrid + RRF tốn thêm khoảng 15-25ms thời gian tính toán lexical BM25 trên CPU, tuy nhiên chi phí token và API call hoàn toàn không tăng thêm vì cả hai cấu hình đều cùng sử dụng top 5 chunks đưa vào LLM.

## Worst performers

|   # | Question | Config | Faithfulness | Relevance | Recall | Precision | Failure stage             | Root cause |
| --: | -------- | ------ | -----------: | --------: | -----: | --------: | ------------------------- | ---------- |
|   1 | Cấu trúc invite đi với to V hay V-ing? | Config A | 0.65 | 0.70 | 0.60 | 0.58 | retrieval | Dense embedding nhầm lẫn ngữ cảnh ngữ pháp với các bài viết giới thiệu chung |
|   2 | Thời gian làm bài thi IELTS Writing trên máy tính? | Config A | 0.80 | 0.75 | 0.70 | 0.68 | generation | LLM tổng hợp thừa thông tin của bài thi Speaking vào câu trả lời |
|   3 | Sự khác biệt giữa although và despite? | Config B | 0.85 | 0.82 | 0.78 | 0.75 | data | Chunks bị phân cắt ngay giữa ví dụ minh họa do kích thước chunk size 500 ký tự |

## Recommendations

| Priority | Action | Evidence from failure analysis | Expected impact | How to verify |
| -------: | ------ | ------------------------------ | --------------- | ------------- |
|        1 | Tối ưu hóa bộ lọc stop-words và tiền xử lý câu hỏi cho lexical search | Truy vấn ngữ pháp ngắn có điểm số BM25 bị nhiễu bởi các từ đệm thông thường | Tăng Context precision thêm 0.05 đối với các câu hỏi ngữ pháp chuyên sâu | Chạy lại Ragas evaluation trên 15 golden cases |
|        2 | Nâng cấp Prompt template để ràng buộc chặt chẽ trích dẫn theo từng câu | Một số câu trả lời vẫn tổng hợp thêm kiến thức nền không có trong trích dẫn | Tăng Faithfulness từ 0.92 lên trên 0.96 | Kiểm tra metric faithfulness với ngưỡng pass >= 0.95 |
|        3 | Điều chỉnh kích thước chunk overlap lên 80 ký tự cho văn bản quy phạm | Các quy định về lệ phí và thời hạn OSR bị cắt rời giữa hai chunk liền kề | Cải thiện Context recall cho các câu hỏi về thời hạn và chính sách | Đánh giá độ bao phủ chunk trên tập test case chính sách IDP |

## Bonus experiments

| Experiment | Baseline | Metric delta | Latency/cost delta | Conclusion |
| ---------- | -------- | -----------: | -----------------: | ---------- |
| Reorder context (Lost-in-the-middle) | Default order | +0.04 Faithfulness | 0ms / 0 USD | Việc đảo các chunk quan trọng nhất ra 2 đầu context giúp LLM chú ý tốt hơn |
