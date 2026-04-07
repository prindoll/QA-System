from pathlib import Path


def load_html(file_path: str) -> str:
    path = Path(file_path)
    return path.read_text(encoding="utf-8")
