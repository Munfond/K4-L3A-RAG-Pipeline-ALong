import streamlit as st
from dotenv import load_dotenv


from src.task10_generation import generate_with_citation

load_dotenv()

st.set_page_config(
    page_title="IELTS Writing RAG Assistant",
    page_icon="✍️",
    layout="wide",
)

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.title("⚙️ Cấu hình RAG")
    st.caption("Trợ lý AI tra cứu tiêu chí chấm điểm, chiến lược và cấu trúc bài thi IELTS Writing.")
    top_k = st.slider("Số lượng chunks trích xuất (top-k):", 3, 10, 5)

st.title("✍️ IELTS Writing Assistant")
st.caption("Hỏi đáp dựa trên tài liệu chính sách, tiêu chí chấm điểm và bài viết chuyên sâu về IELTS Writing.")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sources"):
            with st.expander(f"📚 Trích dẫn nguồn ({message.get('retrieval_source', 'N/A')})"):
                for idx, src in enumerate(message["sources"], 1):
                    meta = src.get("metadata", {})
                    st.markdown(
                        f"**{idx}. {meta.get('title', 'Tài liệu')}** (Nguồn: `{meta.get('source', '')}` | "
                        f"Phương thức: `{src.get('retrieval_method', '')}` | Điểm: `{src.get('score', 0):.4f}`)"
                    )
                    st.text(src.get("content", ""))

query = st.chat_input("Nhập câu hỏi về IELTS Writing...")

if query:
    st.session_state.messages.append({"role": "user", "content": query})

    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        with st.spinner("Đang tìm kiếm tài liệu và sinh câu trả lời..."):
            result = generate_with_citation(query, top_k=top_k)
            answer = result.get("answer", "")
            sources = result.get("sources", [])
            retrieval_source = result.get("retrieval_source", "none")

        st.markdown(answer)

        if sources:
            with st.expander(f"📚 Trích dẫn nguồn ({retrieval_source})"):
                for idx, src in enumerate(sources, 1):
                    meta = src.get("metadata", {})
                    st.markdown(
                        f"**{idx}. {meta.get('title', 'Tài liệu')}** (Nguồn: `{meta.get('source', '')}` | "
                        f"Phương thức: `{src.get('retrieval_method', '')}` | Điểm: `{src.get('score', 0):.4f}`)"
                    )
                    st.text(src.get("content", ""))

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": sources,
        "retrieval_source": retrieval_source,
    })
