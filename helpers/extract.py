"""Extract book text with pdfminer.

pdfminer's newline count is what `wc -l` reports. Form-feed characters
between pages are not newlines, so they do not add lines.
"""

from pathlib import Path

import pdfminer.high_level


def extract_pdf_text(path: Path) -> str:
    """Return the plain text of a PDF."""
    return pdfminer.high_level.extract_text(str(Path(path)))


def write_pdf_text(pdf_path: Path, out_path: Path) -> Path:
    """Write extracted PDF text to ``out_path`` and return that path."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(extract_pdf_text(pdf_path), encoding="utf-8")
    return out_path


def write_pdf_directory(pdf_dir: Path, out_dir: Path) -> list[Path]:
    """Extract every PDF in ``pdf_dir`` to ``out_dir/<stem>.md``."""
    pdf_dir = Path(pdf_dir)
    out_dir = Path(out_dir)
    return [
        write_pdf_text(pdf_path, out_dir / f"{pdf_path.stem}.md")
        for pdf_path in sorted(pdf_dir.glob("*.pdf"))
    ]
