"""
Task 1 — Thu thập tài liệu chính sách/quy định.

Hướng dẫn:
    1. Chọn chủ đề của nhóm.
    2. Tìm tối thiểu 3 tài liệu PDF/DOCX từ nguồn công khai.
    3. Lưu file gốc vào data/landing/legal/.
    4. Đặt tên không dấu và thể hiện đúng nội dung.

Ví dụ tài liệu: học phí, học bổng, ký túc xá, quy trình đăng ký.
Nếu website chặn crawler, hãy chọn nguồn công khai khác; không vượt WAF.
"""

from pathlib import Path


DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "legal"


def setup_directory() -> None:
    """Tạo thư mục lưu tài liệu gốc."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Ready: {DATA_DIR}")


def download_documents() -> list[Path]:
    """Kiểm tra và thu thập tối thiểu 3 tài liệu PDF/DOCX từ nguồn công khai vào data/landing/legal/."""
    setup_directory()

    # Danh sách các tài liệu hiện có trong thư mục
    existing_files = [
        p for p in DATA_DIR.iterdir()
        if p.is_file() and not p.name.startswith(".") and p.suffix.lower() in {".pdf", ".doc", ".docx"}
    ]

    if len(existing_files) >= 3:
        print(f"Đã có {len(existing_files)} tài liệu hợp lệ trong {DATA_DIR}:")
        for f in existing_files:
            print(f" - {f.name} ({f.stat().st_size / 1024:.1f} KB)")
        return existing_files

    # Nếu chưa có đủ file, có thể tải thêm từ các nguồn công khai
    import requests

    sources = {
        "ielts_guide.pdf": "https://www.cambridgeenglish.org/images/ielts-information-for-candidates-english-uk.pdf",
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    downloaded = list(existing_files)
    for filename, url in sources.items():
        dest = DATA_DIR / filename
        if not dest.exists():
            try:
                print(f"Đang tải {filename} từ {url}...")
                response = requests.get(url, headers=headers, timeout=30)
                response.raise_for_status()
                dest.write_bytes(response.content)
                print(f"-> Đã lưu: {dest}")
                downloaded.append(dest)
            except Exception as error:
                print(f"-> Không thể tải {filename}: {error}")

    return downloaded


if __name__ == "__main__":
    download_documents()
