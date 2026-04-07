class QdrantStore:
    """Placeholder adapter for external vector DB integration."""

    def __init__(self, endpoint: str, collection_name: str) -> None:
        self.endpoint = endpoint
        self.collection_name = collection_name

    def similarity_search(self, query: str, k: int) -> list[dict]:
        raise NotImplementedError("Implement Qdrant retrieval for large-scale deployment")
