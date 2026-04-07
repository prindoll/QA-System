# GraphRAG QA Architecture

## Overview

Raw Text
-> LLM Information Extraction
-> Normalize + Ontology Mapping
-> Neo4j Graph Upsert
-> Embedding Indexing
-> Hybrid Retrieval
-> Graph Expansion (multi-hop)
-> LLM Answer Generation

## Hybrid Scoring

FinalScore = 0.7 * VectorScore + 0.3 * GraphScore

(BM25 score can be added in `app/infrastructure/retrieval/hybrid_retriever.py`)

## Key files

- Extraction prompt/schema:
  - `app/processing/extraction/prompts.py`
  - `app/processing/extraction/json_schema.py`
- Neo4j upsert:
  - `app/infrastructure/graph/cypher_repository.py`
- Hybrid retrieval:
  - `app/infrastructure/retrieval/hybrid_retriever.py`
- Multi-hop expansion:
  - `app/infrastructure/retrieval/graph_expander.py`
- LLM abstraction:
  - `app/domain/ports/llm_port.py`
  - `app/infrastructure/llm/factory.py`

## Scalability notes

- Use async worker queue for ingestion at scale.
- Use external vector DB adapter (`qdrant_store.py`) when chunk volume grows.
- Keep idempotent upsert and entity resolution to avoid duplicates.
