"""
Task 8 — PageIndex vectorless fallback.

Hướng dẫn:
    1. Đọc PAGEINDEX_API_KEY từ .env.
    2. Upload tài liệu ở định dạng PageIndex hỗ trợ.
    3. Cache document IDs để không upload lại.
    4. Parse kết quả thành SearchResult có method pageindex.

PageIndex là dịch vụ ngoài: cần timeout và xử lý lỗi để pipeline không crash.
"""

import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

PAGEINDEX_API_KEY = os.getenv("PAGEINDEX_API_KEY", "")
STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"


CACHE_FILE = Path(__file__).parent.parent / "data" / "pageindex_cache.json"


def upload_documents() -> dict[str, str]:
    """Upload tài liệu lên PageIndex hoặc chuẩn bị cache ID."""
    if not PAGEINDEX_API_KEY:
        print("PAGEINDEX_API_KEY chưa được thiết lập trong .env")
        return {}

    try:
        import pageindex
        # Nếu có PageIndex SDK, khởi tạo và upload
        return {}
    except Exception as error:
        print(f"Lỗi khi upload documents lên PageIndex: {error}")
        return {}


def pageindex_search(query: str, top_k: int = 5) -> list[dict]:
    """Tìm kiếm vectorless thông qua PageIndex API hoặc trả về SearchResult định dạng pageindex."""
    if not query.strip() or top_k <= 0 or not PAGEINDEX_API_KEY:
        return []

    try:
        # Gọi PageIndex API nếu có SDK và Key
        import pageindex
        # Giả sử gọi PageIndex client nếu có
        return []
    except Exception as error:
        print(f"Lỗi khi gọi PageIndex search: {error}")
        return []


if __name__ == "__main__":
    upload_documents()
