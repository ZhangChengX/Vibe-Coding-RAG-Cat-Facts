"""Milestone 2 — Collect dataset.

Crawls cat-fact web pages, keeps only the main article content (dropping
headers, footers, navigation menus, and sidebars), and saves each page's
text as a .txt file in the documents/ folder.
"""

import re
from pathlib import Path
from typing import List, Optional

import trafilatura

DOCUMENTS_DIR = Path(__file__).parent / "documents"


def _extract_main_content(downloaded: str) -> Optional[str]:
    """Extract only the main content from already-downloaded page HTML."""
    text = trafilatura.extract(
        downloaded,
        include_comments=False,
        include_tables=False,
        no_fallback=False,
    )
    return text.strip() if text else None


def collect(url: str) -> Optional[str]:
    """Crawl the main textual content of a web page.

    Uses trafilatura to download the page and extract only the main content,
    discarding boilerplate such as the header, footer, navigation menu, and
    sidebar. Returns the collected text, or None if the page could not be
    fetched or no main content was found.
    """
    downloaded = trafilatura.fetch_url(url)
    if downloaded is None:
        print(f"  ! Could not download: {url}")
        return None

    text = _extract_main_content(downloaded)
    if not text:
        print(f"  ! No main content extracted: {url}")
    return text


def _slugify(title: str) -> str:
    """Turn a page title into a safe lowercase file-name stem."""
    slug = title.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)   # drop punctuation
    slug = re.sub(r"[\s_-]+", "-", slug)   # collapse whitespace to hyphens
    slug = slug.strip("-")
    return slug or "untitled"


def generate_dataset(urls: List[str]) -> None:
    """Collect every URL and save its text into documents/ as a .txt file.

    The first URL is skipped because its text already exists in the folder as
    cat-facts.txt. The file name for each saved page is derived from the page
    title.
    """
    DOCUMENTS_DIR.mkdir(exist_ok=True)

    # Ignore the first URL — its text already lives in documents/cat-facts.txt.
    for url in urls[1:]:
        print(f"Collecting: {url}")
        downloaded = trafilatura.fetch_url(url)
        if downloaded is None:
            print(f"  ! Could not download: {url}")
            continue

        text = _extract_main_content(downloaded)
        if not text:
            print(f"  ! No main content extracted: {url}")
            continue

        metadata = trafilatura.extract_metadata(downloaded)
        title = metadata.title if metadata and metadata.title else None
        stem = _slugify(title) if title else _slugify(url.rstrip("/").split("/")[-1])
        out_path = DOCUMENTS_DIR / f"{stem}.txt"

        out_path.write_text(text, encoding="utf-8")
        print(f"  -> saved {out_path.name} ({len(text)} chars)")


# URLs from the Documents section of planning.md (source #1 first).
URLS = [
    "https://huggingface.co/ngxson/demo_simple_rag_py/resolve/main/cat-facts.txt",
    "https://cvillecatcare.com/veterinary-topics/101-amazing-cat-facts-fun-trivia-about-your-feline-friend/",
    "https://www.discoverwildlife.com/animal-facts/mammals/cat-facts",
    "https://www.bjsrawpetfood.com/blogs/all/fascinating-cat-facts-you-didn-t-know",
    "https://www.mygavet.com/services/cats/blog/50-cat-facts-you-probably-didnt-know",
    "https://www.animalfriends.co.uk/cat/cat-blog/cat-facts/",
    "https://www.goodhousekeeping.com/life/pets/g69020271/shocking-facts-about-cats-you-never-knew/",
    "https://petventuresbook.com/blogs/blog/20-interesting-cat-facts",
    "https://www.nekocatcafe.com/blog/62-facts-about-cats",
    "https://www.aaha.org/resources/lets-get-purr-sonal-interesting-facts-about-cats/",
]


if __name__ == "__main__":
    generate_dataset(URLS)
