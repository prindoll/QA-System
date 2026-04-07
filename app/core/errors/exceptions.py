class GraphRAGError(Exception):
    """Base exception for GraphRAG domain failures."""


class RetrievalError(GraphRAGError):
    """Raised when retrieval pipeline fails."""


class ExtractionError(GraphRAGError):
    """Raised when extraction pipeline fails."""
