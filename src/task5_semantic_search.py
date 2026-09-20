"""
Task 5 — Semantic search.

Embed query bằng chính hàm của Task 4, query ChromaDB và đổi cosine distance
thành similarity. Output phải theo SearchResult, sort giảm dần và không quá top_k.
"""

from .task4_chunking_indexing import embed_texts, get_collection


def semantic_search(query: str, top_k: int = 10) -> list[dict]:
    """Trả về danh sách SearchResult theo độ tương đồng ngữ nghĩa (dense) giảm dần."""
    if not query.strip() or top_k <= 0:
        return []

    collection = get_collection()

    # Kiểm tra số lượng chunk nếu collection hỗ trợ .count()
    if hasattr(collection, "count"):
        try:
            total_items = collection.count()
            if total_items == 0:
                return []
            top_k = min(top_k, total_items)
        except Exception:
            pass

    query_vectors = embed_texts([query])
    if not query_vectors:
        return []

    query_vector = query_vectors[0]
    response = collection.query(
        query_embeddings=[query_vector],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    if not response or not response.get("ids") or not response["ids"][0]:
        return []

    results = []
    seen_ids = set()

    for item_id, content, metadata, distance in zip(
        response["ids"][0],
        response["documents"][0],
        response["metadatas"][0],
        response["distances"][0],
    ):
        if item_id in seen_ids:
            continue
        seen_ids.add(item_id)

        meta = dict(metadata or {})
        # Đảm bảo chunk_index có kiểu int
        if "chunk_index" in meta:
            meta["chunk_index"] = int(meta["chunk_index"])

        score = float(max(0.0, 1.0 - float(distance)))
        results.append({
            "id": item_id,
            "content": content,
            "score": score,
            "metadata": meta,
            "retrieval_method": "dense",
        })

    # Sắp xếp giảm dần theo điểm số similarity
    results.sort(key=lambda item: item["score"], reverse=True)
    return results[:top_k]


if __name__ == "__main__":
    for result in semantic_search("test query", top_k=3):
        print(result)
