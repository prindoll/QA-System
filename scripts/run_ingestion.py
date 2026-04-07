import argparse
from pathlib import Path

from app.workers.ingest_worker import run_ingest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to raw text file")
    parser.add_argument("--doc-id", required=True)
    args = parser.parse_args()

    text = Path(args.input).read_text(encoding="utf-8")
    run_ingest(text=text, doc_id=args.doc_id)
    print(f"Ingestion completed for doc_id={args.doc_id}")


if __name__ == "__main__":
    main()
