"""
Task 2 — Crawl bài viết/thông báo về IELTS Writing.
"""

import asyncio
from datetime import datetime
import json
from pathlib import Path
from crawl4ai import AsyncWebCrawler

DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "news"

ARTICLE_URLS = [
    "https://ielts.idp.com/vietnam/about/news-and-articles/article-computer-delivered-ielts",
    "https://ielts.idp.com/vietnam/about/news-and-articles/article-compound-adjectives",
    "https://ielts.idp.com/vietnam/about/news-and-articles/article-choose-to-v-or-v-ing",
    "https://ielts.idp.com/vietnam/about/news-and-articles/article-although-despite-in-spite-of",
    "https://ielts.idp.com/vietnam/about/news-and-articles/article-invite-to-v-or-ving",
]


async def crawl_article(crawler: AsyncWebCrawler, url: str) -> dict:
    """Crawl một URL và trích xuất url, title, date_crawled, content_markdown."""
    result = await crawler.arun(url=url)
    
    # Lấy title từ metadata hoặc thẻ tiêu đề
    title = (result.metadata or {}).get("title") or "IELTS Writing Guide"
    
    # Crawl4AI cung cấp sẵn markdown qua result.markdown
    markdown_content = result.markdown or ""
    
    if not markdown_content.strip():
        raise ValueError(f"No content returned for {url}")

    return {
        "url": url,
        "title": title.strip(),
        "date_crawled": datetime.now().isoformat(),
        "content_markdown": markdown_content.strip(),
    }


async def crawl_all() -> None:
    """Crawl toàn bộ danh sách URL và lưu thành các file JSON riêng biệt."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    async with AsyncWebCrawler() as crawler:
        for index, url in enumerate(ARTICLE_URLS, 1):
            try:
                print(f"[{index}/{len(ARTICLE_URLS)}] Crawling: {url}...")
                article = await crawl_article(crawler, url)
                
                output = DATA_DIR / f"article_{index:02d}.json"
                output.write_text(
                    json.dumps(article, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
                print(f"-> Đã lưu: {output}")
            except Exception as error:
                print(f"-> Thất bại: {url} — {error}")


if __name__ == "__main__":
    asyncio.run(crawl_all())
