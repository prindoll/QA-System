# GraphRAG QA (LangChain + Neo4j)

Hệ thống QA production-ready với GraphRAG, hỗ trợ:

- Hybrid Retrieval (Graph + Vector + Lexical)
- Multi-hop graph expansion
- Taxonomy-aware reasoning (`IS_A`, `PART_OF`)
- LLM abstraction layer (OpenAI/local/other)

## 1. Quick start

```bash
docker compose up -d
cp .env.example .env
pip install -e .
uvicorn app.main:app --reload --port 8000
```

## 2. API

- `GET /health`
- `POST /qa/ask`

Example request:

```json
{
  "query": "Sản phẩm A thuộc nhóm nào và liên quan đến thành phần nào?",
  "top_k": 12,
  "max_hops": 2
}
```

## 3. Ingestion pipeline

```bash
python -m scripts.bootstrap_neo4j
python -m scripts.run_ingestion --input data/raw/sample.txt --doc-id sample-doc-1
python -m scripts.backfill_embeddings
python -m scripts.run_graph_migration
```

## 4. Project layout

- `app/domain`: business logic + service orchestration
- `app/infrastructure`: adapters cho Neo4j, LLM, vector
- `app/processing`: extraction/normalize/indexing pipeline
- `app/api`: FastAPI routers/schemas

## 5. Notes

- Mặc định dùng OpenAI cho extraction + answer generation.
- Có thể đổi sang local model thông qua `LLM_PROVIDER` và adapter tương ứng.
