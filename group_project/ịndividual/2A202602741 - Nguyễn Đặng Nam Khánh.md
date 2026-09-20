# Individual contribution report

---

## Thông tin

- Họ và tên: Nguyễn Đặng Nam Khánh
- Mã học viên: 2A202602741
- Nhóm: ALong
- Repository/branch: Munfond/K4-L3A-RAG-Pipeline-ALong/main

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| Task 10 — Generation | Cài đặt hàm reorder_for_llm, format_context, tích hợp LLM và cơ chế Safe Refusal | `src/task10_generation.py` | Done |
| Chatbot UI | Xây dựng giao diện Streamlit với khung chat và expander trích dẫn nguồn chi tiết | `app.py` | Done |
| Evaluation & Golden set | Xây dựng 15 test cases chuẩn và hoàn thành toàn bộ báo cáo phân tích A/B trong RESULT.md | `group_project/evaluation/golden_dataset.json`, `RESULT.md` | Done |

## Quyết định kỹ thuật quan trọng

1. **Quyết định:** Áp dụng thuật toán Reordering (đưa chunk thứ hạng cao ra đầu và cuối danh sách ngữ cảnh) trước khi đưa vào LLM.  
   **Lý do/evidence:** Hạn chế hiện tượng "Lost in the middle" (mô hình ngôn ngữ thường chỉ chú ý kỹ phần đầu và phần đuôi của context dài); thực nghiệm cho thấy Faithfulness tăng thêm 0.08 khi có reorder.  
   **Trade-off:** Thứ tự xuất hiện trong prompt bị xáo trộn nhẹ so với thứ hạng gốc của RRF.

2. **Quyết định:** Thiết lập cơ chế Safe Refusal nghiêm ngặt kết hợp Prompt ràng buộc trích dẫn theo từng tài liệu.  
   **Lý do/evidence:** Tránh việc chatbot bịa đặt thông tin (hallucination) trong các câu hỏi nhạy cảm về lệ phí, chính sách bảo lưu hoặc quy chế thi IELTS.  
   **Trade-off:** Đối với một số câu hỏi người dùng diễn đạt quá chung chung, hệ thống có thể thận trọng từ chối thay vì cố gắng suy đoán.

## Kiểm thử và kết quả

- Test hoặc query tôi đã dùng:
  - `pytest tests/test_contracts.py -k test_reorder_is_non_mutating_and_context_contains_source -v`
  - `pytest tests/test_contracts.py -k test_generation_result_validator_accepts_safe_refusal -v`
  - `pytest tests/test_acceptance.py -k test_golden_dataset_has_15_grounded_cases -v`
  - `pytest tests/test_acceptance.py -k test_evaluation_report_is_completed -v`
  - Khởi chạy trực tiếp `streamlit run app.py` để tương tác hội thoại thực tế.
- Kết quả trước/sau nếu có: Chatbot trả lời mượt mà, đầy đủ trích dẫn nguồn tài liệu; toàn bộ 20/20 test cases của bài lab đều pass 100%.
- Lỗi đã phát hiện và cách xử lý: Xử lý ngoại lệ trong `call_llm` để khi thiếu API key hoặc API lỗi mạng, ứng dụng vẫn trả về phản hồi an toàn chứ không bị crash màn hình trắng.

## Điều còn hạn chế

- Một hạn chế cụ thể của phần tôi làm: Giao diện Chatbot hiện tại mới hỗ trợ chat theo từng lượt (turn-by-turn độc lập), chưa lưu nhớ lịch sử ngữ cảnh nhiều vòng hội thoại (multi-turn conversation memory).
- Nếu có thêm thời gian, thay đổi đầu tiên tôi sẽ thực hiện: Bổ sung Conversation Summary Buffer Memory để chatbot nhớ câu hỏi trước của người dùng khi hỏi tiếp câu thứ hai.

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 20/09/2026
- Tên thành viên: Nguyễn Đặng Nam Khánh
