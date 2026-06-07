"""Milestone 3 — Ingestion and chunking.

Loads the .txt documents collected in Milestone 2 and splits each one into
chunks. Documents in this corpus come in two shapes:

* Line-structured files where every line is a single cat fact
  (e.g. cat-facts.txt, 62-facts-about-cats.txt).
* Paragraph-structured files where facts are separated by a blank line, and a
  fact may span a heading line plus a body line
  (e.g. 30-cat-facts-you-didnt-know.txt, lets-get-purr-sonal-...txt).

chunk_document() detects which shape a document has and chunks accordingly.
"""

import re
from pathlib import Path
from typing import List

DOCUMENTS_DIR = Path(__file__).parent / "documents"

# Matches a blank line (a line that is empty or only whitespace) used as a
# separator between paragraphs.
_BLANK_LINE_SPLIT = re.compile(r"\n[ \t]*\n")


def load_document(file_name: str) -> str:
    """Load a .txt file from the documents/ folder and return its text content.

    Args:
        file_name: Name of the file inside documents/ (e.g. "cat-facts.txt").

    Returns:
        The full text content of the file.
    """
    file_path = DOCUMENTS_DIR / file_name
    return file_path.read_text(encoding="utf-8")


def chunk_document(document: str) -> List[str]:
    """Split a document into a list of chunks.

    If the document contains multiple paragraphs separated by a blank line,
    each paragraph becomes a chunk; otherwise each line becomes a chunk. Chunks
    that are blank or whitespace-only are ignored.

    Args:
        document: The raw text content of a document.

    Returns:
        A list of non-empty, whitespace-trimmed chunks.
    """
    blocks = _BLANK_LINE_SPLIT.split(document)
    paragraphs = [block for block in blocks if block.strip()]

    if len(paragraphs) > 1:
        # Paragraph-structured: each blank-line-separated block is one chunk.
        pieces = paragraphs
    else:
        # Line-structured: each line is one chunk.
        pieces = document.splitlines()

    return [piece.strip() for piece in pieces if piece.strip()]


if __name__ == "__main__":
    # Quick verification across every document in documents/.
    for path in sorted(DOCUMENTS_DIR.glob("*.txt")):
        text = load_document(path.name)
        chunks = chunk_document(text)
        mode = "paragraph" if len([b for b in _BLANK_LINE_SPLIT.split(text) if b.strip()]) > 1 else "line"
        print(f"{path.name}: {len(chunks)} chunks ({mode} mode)")
        if chunks:
            sample = chunks[0][:100] + ("..." if len(chunks[0]) > 100 else "")
            print(f"    e.g. {sample}")
