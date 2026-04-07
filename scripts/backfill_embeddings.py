from app.workers.reindex_worker import reindex_all_chunks


if __name__ == "__main__":
    reindex_all_chunks()
    print("Backfill embeddings done.")
