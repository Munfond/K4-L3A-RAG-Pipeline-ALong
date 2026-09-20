"""
Task 4 — Chunking, embedding và indexing.

Hướng dẫn:
    1. Đọc toàn bộ Markdown trong data/standardized/.
    2. Chia văn bản bằng strategy đã chọn.
    3. Embed chunks bằng một provider duy nhất.
    4. Upsert vào ChromaDB với cosine distance.

Mỗi document/chunk phải theo docs/MODULE_CONTRACTS.md. ID cần ổn định để
chạy lại pipeline không tạo dữ liệu trùng. Task 5 phải dùng chung embed_texts().
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"
CHROMA_DIR = Path(__file__).parent.parent / "chroma_db"

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
CHUNKING_METHOD = "recursive"

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3")
COLLECTION_NAME = "rag_documents"

_model_cache = None


def _get_sentence_transformer():
    global _model_cache
    if _model_cache is None:
        from sentence_transformers import SentenceTransformer
        _model_cache = SentenceTransformer(EMBEDDING_MODEL)
    return _model_cache


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Tạo embedding cho danh sách chuỗi văn bản theo provider được cấu hình."""
    if not texts:
        return []

    provider = os.getenv("EMBEDDING_PROVIDER", "sentence_transformers").lower()

    if provider == "openai":
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        model_name = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
        response = client.embeddings.create(input=texts, model=model_name)
        return [item.embedding for item in response.data]

    elif provider == "gemini":
        from google import genai
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        model_name = os.getenv("EMBEDDING_MODEL", "text-embedding-004")
        vectors = []
        for text in texts:
            res = client.models.embed_content(model=model_name, contents=text)
            vectors.append(res.embedding.values)
        return vectors

    else:
        model = _get_sentence_transformer()
        embeddings = model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()


def get_collection():
    """Mở hoặc tạo Chroma collection dùng khoảng cách cosine."""
    import chromadb

    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def load_documents() -> list[dict]:
    """Đọc mọi file Markdown trong data/standardized/ và trả về danh sách Document theo contract."""
    documents = []
    if not STANDARDIZED_DIR.exists():
        return documents

    for path in sorted(STANDARDIZED_DIR.rglob("*.md")):
        if path.name.startswith("."):
            continue

        content = path.read_text(encoding="utf-8").strip()
        if not content:
            continue

        doc_type = "legal" if "legal" in path.parts else "news"
        title = path.stem
        url: str | None = None

        # Trích xuất Title và Source URL nếu có trong phần Header của Markdown
        for line in content.splitlines()[:10]:
            stripped = line.strip()
            if stripped.startswith("# ") and title == path.stem:
                parsed_title = stripped.replace("# ", "").strip()
                if parsed_title:
                    title = parsed_title
            elif stripped.startswith("**Source:**"):
                parsed_url = stripped.replace("**Source:**", "").strip()
                if parsed_url:
                    url = parsed_url

        documents.append({
            "id": path.relative_to(STANDARDIZED_DIR).as_posix(),
            "content": content,
            "metadata": {
                "source": path.name,
                "title": title,
                "doc_type": doc_type,
                "url": url,
            },
        })
    return documents


def chunk_documents(documents: list[dict]) -> list[dict]:
    """Chia nhỏ Document thành danh sách các Chunk có ID duy nhất và metadata hợp lệ."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
    )

    chunks = []
    for document in documents:
        split_texts = splitter.split_text(document["content"])
        for index, text in enumerate(split_texts):
            clean_text = text.strip()
            if not clean_text:
                continue
            chunk_metadata = dict(document["metadata"])
            chunk_metadata["chunk_index"] = index
            chunks.append({
                "id": f"{document['id']}::chunk-{index}",
                "content": clean_text,
                "metadata": chunk_metadata,
            })
    return chunks


def embed_chunks(chunks: list[dict], batch_size: int = 64) -> list[dict]:
    """Thêm embedding vector vào từng chunk."""
    if not chunks:
        return chunks

    texts = [chunk["content"] for chunk in chunks]
    all_embeddings: list[list[float]] = []

    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i + batch_size]
        batch_vectors = embed_texts(batch_texts)
        all_embeddings.extend(batch_vectors)

    for chunk, vector in zip(chunks, all_embeddings):
        chunk["embedding"] = vector
    return chunks


def index_to_vectorstore(chunks: list[dict]) -> None:
    """Upsert chunks vào ChromaDB collection."""
    if not chunks:
        print("Không có chunk nào để index.")
        return

    collection = get_collection()

    # ChromaDB metadata không hỗ trợ giá trị None nên chuyển None thành ""
    sanitized_metadatas = []
    for chunk in chunks:
        meta = dict(chunk["metadata"])
        if meta.get("url") is None:
            meta["url"] = ""
        sanitized_metadatas.append(meta)

    batch_size = 100
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        batch_meta = sanitized_metadatas[i:i + batch_size]
        collection.upsert(
            ids=[chunk["id"] for chunk in batch],
            documents=[chunk["content"] for chunk in batch],
            embeddings=[chunk["embedding"] for chunk in batch],
            metadatas=batch_meta,
        )


def run_pipeline() -> None:
    """Chạy toàn bộ quy trình: load -> chunk -> embed -> index."""
    print("1. Đang tải tài liệu Markdown...")
    documents = load_documents()
    print(f"-> Đã tải {len(documents)} tài liệu.")

    print("2. Đang phân đoạn (chunking)...")
    chunks = chunk_documents(documents)
    print(f"-> Đã tạo {len(chunks)} chunks.")

    print("3. Đang tạo embedding...")
    embedded_chunks = embed_chunks(chunks)

    print("4. Đang lưu trữ và đánh chỉ mục vào ChromaDB...")
    index_to_vectorstore(embedded_chunks)
    print(f"-> Hoàn tất đánh chỉ mục {len(embedded_chunks)} chunks vào ChromaDB!")


if __name__ == "__main__":
    run_pipeline()
