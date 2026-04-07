from langchain_openai import OpenAIEmbeddings

from app.infrastructure.graph.neo4j_client import Neo4jClient


class VectorIndexer:
	def __init__(self, neo4j_client: Neo4jClient, embedding_model: str) -> None:
		self.neo4j = neo4j_client
		self.embeddings = OpenAIEmbeddings(model=embedding_model)

	def index_chunks(self, chunks: list[dict]) -> None:
		for chunk in chunks:
			vector = self.embeddings.embed_query(chunk["text"])
			cypher = """
			MERGE (c:Chunk {chunk_id: $chunk_id})
			ON CREATE SET
			  c.source_doc_id = $source_doc_id,
			  c.text = $text,
			  c.created_at = datetime()
			ON MATCH SET
			  c.text = $text,
			  c.updated_at = datetime()
			SET c.embedding = $embedding
			"""
			self.neo4j.query(
				cypher,
				{
					"chunk_id": chunk["chunk_id"],
					"source_doc_id": chunk.get("source_doc_id", ""),
					"text": chunk["text"],
					"embedding": vector,
				},
			)
