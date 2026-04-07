from pathlib import Path


def load_pdf(file_path: str) -> str:
    """Stub loader: replace by pypdf/pdfplumber in production."""
    path = Path(file_path)
    return path.read_text(encoding="utf-8")
