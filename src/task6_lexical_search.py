"""
Task 6 — Lexical search bằng BM25.

Dùng cùng corpus chunks với Task 5. BM25 phù hợp với từ khóa chính xác, mã tài
liệu và tên riêng. Output phải theo SearchResult và sort score giảm dần.
"""


CORPUS: list[dict] = []


def load_corpus() -> list[dict]:
    """Tải corpus từ Task 4 nếu CORPUS chưa có dữ liệu."""
    global CORPUS
    if not CORPUS:
        try:
            from .task4_chunking_indexing import chunk_documents, load_documents
            documents = load_documents()
            CORPUS = chunk_documents(documents)
        except Exception:
            try:
                from src.task4_chunking_indexing import chunk_documents, load_documents
                documents = load_documents()
                CORPUS = chunk_documents(documents)
            except Exception:
                CORPUS = []
    return CORPUS


def build_bm25_index(corpus: list[dict]):
    """Tạo BM25 index từ danh sách corpus chunks."""
    if not corpus:
        return None
    from rank_bm25 import BM25Okapi
    tokenized = [item["content"].lower().split() for item in corpus]
    return BM25Okapi(tokenized)


def lexical_search(query: str, top_k: int = 10) -> list[dict]:
    """Trả về danh sách SearchResult theo thuật toán BM25 sắp xếp theo score giảm dần."""
    if not query.strip() or top_k <= 0:
        return []

    corpus = CORPUS if CORPUS else load_corpus()
    if not corpus:
        return []

    query_tokens = query.lower().split()
    if not query_tokens:
        return []

    bm25 = build_bm25_index(corpus)
    if bm25 is None:
        return []

    import numpy as np

    scores = [float(s) for s in bm25.get_scores(query_tokens)]

    # Với corpus cực nhỏ (N <= 2), IDF trong BM25Okapi có thể bằng 0.
    # Bổ sung tần suất xuất hiện từ khóa để đảm bảo thứ hạng chính xác.
    max_s = max(scores) if scores else 0.0
    if max_s <= 0.0:
        for i, item in enumerate(corpus):
            content_lower = item.get("content", "").lower()
            overlap = sum(content_lower.count(token) for token in query_tokens)
            scores[i] = float(overlap)

    indices = np.argsort(scores)[::-1]

    results = []
    seen_ids = set()

    for idx in indices:
        item = corpus[idx]
        if item["id"] in seen_ids:
            continue
        seen_ids.add(item["id"])

        meta = dict(item.get("metadata", {}))
        if "chunk_index" in meta:
            meta["chunk_index"] = int(meta["chunk_index"])

        score = float(max(0.0, scores[idx]))
        results.append({
            "id": item["id"],
            "content": item["content"],
            "score": score,
            "metadata": meta,
            "retrieval_method": "bm25",
        })
        if len(results) >= top_k:
            break

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]


if __name__ == "__main__":
    for result in lexical_search("test query", top_k=3):
        print(result)
