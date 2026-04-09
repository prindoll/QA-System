from app.workers.reindex_worker import count_chunks_missing_embeddings, reindex_missing_chunks
from scripts.backfill_mentions import backfill_mentions
from scripts.migrate_taxonomy_relationships import migrate_relates_to_predicate_to_typed


def main() -> None:
    taxonomy_stats = migrate_relates_to_predicate_to_typed()
    mention_rows = backfill_mentions()

    missing_before = count_chunks_missing_embeddings()
    reindexed = 0
    if missing_before > 0:
        reindexed = reindex_missing_chunks()

    print(
        "Graph migration completed: "
        f"IS_A={taxonomy_stats.get('IS_A', 0)}, "
        f"PART_OF={taxonomy_stats.get('PART_OF', 0)}, "
        f"MENTIONED_IN_ROWS={mention_rows}, "
        f"MISSING_EMBEDDINGS_BEFORE={missing_before}, "
        f"REINDEXED={reindexed}"
    )


if __name__ == "__main__":
    main()
