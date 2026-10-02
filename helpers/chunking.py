"""Chunk a Markdown book with gitsource and save the chunks."""

import json
from pathlib import Path

from gitsource import chunk_documents

try:
    from prepare import prepare_markdown
except ImportError:
    from helpers.prepare import prepare_markdown

PREPARED_DOCS = Path(__file__).resolve().parent.parent / "prepared_docs"


def chunk_markdown(
    path: Path,
    size: int = 2000,
    step: int = 1000,
    out_dir: Path = PREPARED_DOCS,
) -> int:
    """Chunk one Markdown file, write the chunks to ``prepared_docs``, and return the count.

    ``size`` and ``step`` are counts of non-empty lines. The written file is
    ``prepared_docs/<stem>.json`` and contains the list returned by
    ``gitsource.chunk_documents``.
    """
    path = Path(path)
    document = prepare_markdown(path)
    chunks = chunk_documents([document], size=size, step=step)

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    destination = out_dir / f"{path.stem}.json"
    destination.write_text(
        json.dumps(chunks, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return len(chunks)
