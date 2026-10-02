"""Load chunked books from prepared_docs and fit a minsearch index."""

import json
from pathlib import Path

from minsearch import Index

PREPARED_DOCS = Path(__file__).resolve().parent.parent / "prepared_docs"
SKIP_FILES = {"thinkpython2.json"}


def load_chunks(directory: Path = PREPARED_DOCS) -> list[dict]:
    """Load every chunk list in ``directory``."""
    chunks = []
    for path in sorted(Path(directory).glob("*.json")):
        if path.name in SKIP_FILES:
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            chunks.extend(data)
        else:
            chunks.append(data)
    return chunks


def prepare_documents(chunks: list[dict]) -> list[dict]:
    """Copy chunks and turn each ``content`` list into a single string."""
    documents = []
    for chunk in chunks:
        document = dict(chunk)
        content = document["content"]
        if isinstance(content, list):
            document["content"] = "\n".join(content)
        documents.append(document)
    return documents


def build_index(directory: Path = PREPARED_DOCS) -> Index:
    """Fit a minsearch index on the chunks in ``prepared_docs``."""
    documents = prepare_documents(load_chunks(directory))
    index = Index(text_fields=["content"], keyword_fields=["source"])
    index.fit(documents)
    return index


def index_chunks(directory: Path = PREPARED_DOCS) -> int:
    """Index every chunk in ``prepared_docs`` and print how many were indexed."""
    index = build_index(directory)
    indexed = len(index.docs)
    print(indexed)
    return indexed


def search(term: str, num_results: int = 5, directory: Path = PREPARED_DOCS) -> list[dict]:
    """Search the chunk index. Each result includes the source book."""
    index = build_index(directory)
    return index.search(term, num_results=num_results)


if __name__ == "__main__":
    index_chunks()
