"""
Task 3 — Chuẩn hóa dữ liệu sang Markdown.

Hướng dẫn:
    1. Dùng MarkItDown để convert PDF/DOCX.
    2. Đọc JSON và giữ metadata ở đầu file Markdown.
    3. Giữ cấu trúc thư mục legal/ và news/.
    4. Không tạo file rỗng hoặc file trùng khi chạy lại.

Cài đặt:
    Dependency MarkItDown đã được khai báo trong pyproject.toml.
    
-> Hoặc dùng công cụ nào bạn quen khác Markitdown
"""
import json
from pathlib import Path
from markitdown import MarkItDown


LANDING_DIR = Path(__file__).parent.parent / "data" / "landing"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "standardized"


def _extract_text_docx(path: Path) -> str:
    """Trích xuất nội dung văn bản từ file DOCX bằng zipfile thuần Python."""
    import zipfile
    import xml.etree.ElementTree as ET

    try:
        with zipfile.ZipFile(path) as docx_zip:
            xml_content = docx_zip.read("word/document.xml")
        root = ET.fromstring(xml_content)
        paragraphs = []
        for p in root.iter():
            if p.tag.endswith("}p"):
                texts = [elem.text for elem in p.iter() if elem.tag.endswith("}t") and elem.text]
                if texts:
                    paragraphs.append("".join(texts))
        return "\n\n".join(paragraphs)
    except Exception as err:
        print(f"Lỗi fallback trích xuất DOCX {path.name}: {err}")
        return ""


def convert_legal_docs() -> None:
    """Chuyển đổi các tài liệu pháp lý/quy định (PDF, DOC, DOCX) sang Markdown."""
    legal_dir = LANDING_DIR / "legal"
    output_dir = OUTPUT_DIR / "legal"
    output_dir.mkdir(parents=True, exist_ok=True)

    if not legal_dir.exists():
        print(f"Thư mục không tồn tại: {legal_dir}")
        return

    converter = None
    try:
        converter = MarkItDown()
    except Exception:
        pass

    for path in sorted(legal_dir.iterdir()):
        if path.is_file() and not path.name.startswith(".") and path.suffix.lower() in {".pdf", ".doc", ".docx"}:
            try:
                print(f"Đang convert tài liệu: {path.name}...")
                text_content = ""
                if converter:
                    try:
                        result = converter.convert(str(path))
                        text_content = result.text_content or ""
                    except Exception:
                        text_content = ""

                # Fallback thuần Python cho file .docx nếu MarkItDown không có dependency
                if not text_content.strip() and path.suffix.lower() == ".docx":
                    text_content = _extract_text_docx(path)

                if not text_content.strip():
                    print(f"Cảnh báo: Nội dung rỗng sau khi convert {path.name}")
                    continue

                dest_file = output_dir / f"{path.stem}.md"
                dest_file.write_text(text_content.strip(), encoding="utf-8")
                print(f"-> Đã lưu: {dest_file}")
            except Exception as error:
                print(f"-> Lỗi khi convert {path.name}: {error}")


def convert_news_articles() -> None:
    """Chuyển đổi các bài viết/thông báo dạng JSON sang Markdown có kèm metadata."""
    news_dir = LANDING_DIR / "news"
    output_dir = OUTPUT_DIR / "news"
    output_dir.mkdir(parents=True, exist_ok=True)

    if not news_dir.exists():
        print(f"Thư mục không tồn tại: {news_dir}")
        return

    for path in sorted(news_dir.glob("*.json")):
        if not path.name.startswith("."):
            try:
                print(f"Đang convert bài viết: {path.name}...")
                data = json.loads(path.read_text(encoding="utf-8"))
                title = data.get("title", path.stem)
                url = data.get("url", "")
                date_crawled = data.get("date_crawled", "")
                content_markdown = data.get("content_markdown", "")

                header = (
                    f"# {title}\n\n"
                    f"**Source:** {url}\n\n"
                    f"**Crawled:** {date_crawled}\n\n---\n\n"
                )
                full_content = (header + content_markdown).strip()

                dest_file = output_dir / f"{path.stem}.md"
                dest_file.write_text(full_content, encoding="utf-8")
                print(f"-> Đã lưu: {dest_file}")
            except Exception as error:
                print(f"-> Lỗi khi convert {path.name}: {error}")


def convert_all() -> None:
    """Convert toàn bộ dữ liệu landing sang standardized."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    convert_legal_docs()
    convert_news_articles()
    print(f"\nHoàn tất chuẩn hóa Markdown tại: {OUTPUT_DIR}")


if __name__ == "__main__":
    convert_all()
