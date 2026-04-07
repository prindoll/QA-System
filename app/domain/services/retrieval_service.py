from app.domain.models.retrieval import RetrievalBundle
from app.infrastructure.retrieval.graph_expander import GraphExpander
from app.infrastructure.retrieval.hybrid_retriever import HybridRetriever


class RetrievalService:
    def __init__(self, hybrid_retriever: HybridRetriever, graph_expander: GraphExpander) -> None:
        self.hybrid_retriever = hybrid_retriever
        self.graph_expander = graph_expander

    def retrieve(self, query: str, top_k: int, max_hops: int) -> RetrievalBundle:
        seed_bundle = self.hybrid_retriever.retrieve(query=query, top_k=top_k)
        expanded = self.graph_expander.expand(seed_bundle=seed_bundle, max_hops=max_hops)
        return expanded
