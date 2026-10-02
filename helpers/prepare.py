"""Turn Markdown books into source/content dictionaries for chunking."""

import json
from pathlib import Path


def prepare_markdown(path: Path, out_dir: Path | None = None) -> dict:
    """Read one Markdown file and drop blank lines.

    Returns a dictionary with ``source`` (the filename) and ``content``
    (non-empty lines). When ``out_dir`` is set, also writes
    ``out_dir/<stem>.json``.
    """
    path = Path(path)
    lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    document = {"source": path.name, "content": lines}

    if out_dir is not None:
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        destination = out_dir / f"{path.stem}.json"
        destination.write_text(
            json.dumps(document, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    return document


def prepare_directory(books_dir: Path, out_dir: Path) -> list[dict]:
    """Prepare every Markdown file in ``books_dir`` into ``out_dir``."""
    books_dir = Path(books_dir)
    return [
        prepare_markdown(path, out_dir)
        for path in sorted(books_dir.glob("*.md"))
    ]


if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent
    documents = prepare_directory(root / "books_text", root / "prepared_docs")
    for document in documents:
        print(f"{document['source']}: {len(document['content'])} lines")
