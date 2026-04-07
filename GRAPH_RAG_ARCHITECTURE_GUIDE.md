# GraphRAG QA Architecture Guide (Detailed)

Tài liệu này mô tả chi tiết kiến trúc GraphRAG QA đã được scaffold trong project, bao gồm:

- Kiến trúc tổng thể và vai trò từng module
- Pipeline ingest -> index -> retrieval -> answer
- Cách chạy hệ thống end-to-end
- Cách thay đổi LLM provider
- Best practices để tránh duplicate, tăng consistency, giảm hallucination

Tài liệu này độc lập với README.

## 1. Mục tiêu hệ thống

Hệ thống được thiết kế để hỗ trợ:

- Hybrid Retrieval: kết hợp graph context + vector search
- Multi-hop reasoning qua graph expansion
- Taxonomy-aware reasoning (`IS_A`, `PART_OF`)
- LLM abstraction để đổi provider (OpenAI -> local -> provider khác)
- Production-ready structure: tách business logic và infrastructure

## 2. Kiến trúc tổng thể

```text
[Client]
   -> [FastAPI /qa/ask]
   -> [AnswerService]
      -> [RetrievalService]
         -> [HybridRetriever]
            -> Vector search (Neo4j vector index)
            -> Graph seed retrieval (Cypher)
         -> [GraphExpander]
            -> Multi-hop traversal (RELATES_TO|IS_A|PART_OF)
      -> [LLM Adapter]
         -> OpenAI/local model
   -> [Answer + Citations + Graph paths]

Offline indexing:
[Raw Text]
   -> [SemanticChunker]
   -> [ExtractionEngine (LLM JSON extraction)]
   -> [OntologyMapper + EntityResolver]
   -> [GraphIndexer (Neo4j upsert)]
   -> [VectorIndexer (embedding -> Chunk.embedding)]
```

## 3. Project map và vai trò từng folder

- `app/api`: FastAPI routers, request/response schema
- `app/domain`: business models, ports, services (không phụ thuộc provider cụ thể)
- `app/infrastructure`: adapters thực thi cho Neo4j, OpenAI, retrieval
- `app/processing`: extraction, normalize, indexing pipeline
- `app/workers`: orchestration cho ingestion/reindex
- `scripts`: script khởi tạo index/constraint và chạy ingestion
- `tests`: unit/integration/e2e

## 4. Luồng dữ liệu chi tiết

### 4.1 Ingestion và Extraction

1. Tài liệu text được chunk bởi `SemanticChunker`.
2. Mỗi chunk được đưa vào `ExtractionEngine` với prompt extraction.
3. LLM trả về JSON chứa:
   - entities
   - relationships
   - multi_hop_paths
   - metadata chunk/doc

File chính:

- `app/processing/extraction/prompts.py`
- `app/processing/extraction/extractor.py`
- `app/processing/extraction/json_schema.py`

### 4.2 Normalize và Entity Resolution

1. `OntologyMapper` map về controlled vocabulary.
2. `EntityResolver` deduplicate entity theo key `canonical_name + entity_type`.
3. Generate `entity_id` và `relation_id` on-demand để upsert idempotent.

File chính:

- `app/processing/normalize/ontology_mapper.py`
- `app/processing/normalize/entity_resolver.py`

### 4.3 Graph upsert (Neo4j)

- Entity được MERGE theo `entity_id`.
- Relationship được MERGE theo `relation_id`.
- APOC được dùng để union aliases, tránh duplicate.

File chính:

- `app/infrastructure/graph/cypher_repository.py`
- `scripts/bootstrap_neo4j.py`

### 4.4 Vector indexing

- Chunk text được embed bằng OpenAI embedding model.
- Vector gắn vào property `Chunk.embedding`.
- Vector index: `chunk_embedding_index`.

File chính:

- `app/processing/indexing/vector_indexer.py`
- `app/infrastructure/vector/neo4j_vector_store.py`

### 4.5 Hybrid Retrieval + Graph Expansion

1. `HybridRetriever` lấy top-k từ vector index.
2. Chạy thêm graph seed retrieval bằng Cypher.
3. Score fusion hiện tại: `0.7 * vector + 0.3 * graph`.
4. `GraphExpander` mở rộng multi-hop từ seed entities.
5. Loc theo confidence threshold.

File chính:

- `app/infrastructure/retrieval/hybrid_retriever.py`
- `app/infrastructure/retrieval/graph_expander.py`

### 4.6 Answer generation

1. `AnswerService` tổng hợp context:
   - retrieved chunks
   - graph facts
   - graph paths
2. Gửi qua LLM adapter với response format JSON.
3. Trả về answer + citations + graph paths.

File chính:

- `app/domain/services/answer_service.py`
- `app/infrastructure/llm/factory.py`
- `app/infrastructure/llm/openai_adapter.py`
- `app/infrastructure/llm/local_vllm_adapter.py`

## 5. Hướng dẫn chạy hệ thống

## 5.1 Prerequisites

- Python 3.11+
- Docker + Docker Compose
- OpenAI API key (nếu dùng OpenAI)

## 5.2 Setup nhanh

```bash
docker compose up -d
cp .env.example .env
pip install -e .
python -m scripts.bootstrap_neo4j
```

Cập nhật `.env`:

```env
OPENAI_API_KEY=your_key
LLM_PROVIDER=openai
OPENAI_CHAT_MODEL=gpt-4.1-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

## 5.3 Ingest dữ liệu

Ví dụ tạo file input:

```bash
mkdir -p data/raw
cat > data/raw/sample.txt << 'EOF'
Sản phẩm A là một loại thiết bị y tế.
Thiết bị y tế là một nhóm con của thiết bị chăm sóc sức khỏe.
Sản phẩm A bao gồm cảm biến B.
EOF
```

Chạy ingestion:

```bash
python -m scripts.run_ingestion --input data/raw/sample.txt --doc-id sample-doc-1
```

Nếu cần backfill vector:

```bash
python -m scripts.backfill_embeddings
```

## 5.4 Chạy API QA

```bash
uvicorn app.main:app --reload --port 8000
```

Health check:

```bash
curl -s http://localhost:8000/health
```

Hỏi đáp:

```bash
curl -s -X POST http://localhost:8000/qa/ask \
  -H 'Content-Type: application/json' \
  -d '{
   "query": "Sản phẩm A thuộc nhóm nào và có thành phần gì?",
    "top_k": 12,
    "max_hops": 2
  }'
```

## 6. Cấu hình quan trọng

Trong `.env`:

- `RETRIEVAL_TOP_K`: số chunk lấy ban đầu
- `GRAPH_MAX_HOPS`: độ sâu traversal
- `GRAPH_NEIGHBOR_LIMIT`: số nhánh graph mỗi hop
- `GRAPH_RELEVANCE_THRESHOLD`: ngưỡng lọc graph facts confidence thấp

Khuyến nghị ban đầu:

- `RETRIEVAL_TOP_K=12`
- `GRAPH_MAX_HOPS=2`
- `GRAPH_NEIGHBOR_LIMIT=8`
- `GRAPH_RELEVANCE_THRESHOLD=0.45`

## 7. Thay đổi LLM provider

Hệ thống đã có abstraction layer:

- Port: `app/domain/ports/llm_port.py`
- Factory: `app/infrastructure/llm/factory.py`

Đổi sang local vLLM:

1. Set `.env`:

```env
LLM_PROVIDER=local_vllm
```

2. Triển khai endpoint local theo OpenAI-compatible API.
3. Điều chỉnh endpoint/model trong `LocalVLLMAdapter` nếu cần.

## 8. Data consistency, duplicate, hallucination

### 8.1 Tránh duplicate entity

- Dùng `EntityResolver` trước khi graph upsert.
- MERGE theo `entity_id` và quản lý aliases.
- Sau này có thể bổ sung fuzzy resolver + human review queue.

### 8.2 Data consistency

- Constraint và index được tạo trong `bootstrap_neo4j`.
- Ingestion theo hướng idempotent: ingest lại không tạo node/edge duplicate nếu id giống nhau.

### 8.3 Giảm hallucination

- Prompt answer ép JSON và grounded context only.
- Bắt buộc citation theo chunk/doc.
- Nếu không đủ context, trả lời không đủ dữ liệu.

## 9. Vấn đề thường gặp và cách xử lý

### Lỗi vector index trong Neo4j

- Đảm bảo đã chạy `python -m scripts.bootstrap_neo4j`.
- Kiểm tra embedding dimensions khớp model đang dùng.

### Lỗi kết nối Neo4j

- Kiểm tra `docker compose ps`.
- Kiểm tra `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` trong `.env`.

### LLM trả về JSON lỗi

- Giảm `temperature` về 0.
- Tăng độ rõ schema/prompt extraction.
- Thêm retry + JSON repair (next step nên bổ sung).

## 10. Lộ trình nâng cấp production tiếp theo

- Thêm BM25 (Elasticsearch/Postgres FTS) vào score fusion.
- Thêm reranker (cross-encoder) sau retrieval.
- Thêm queue ingestion (Celery/RQ/Kafka).
- Thêm observability đầy đủ (Prometheus + tracing).
- Thêm evaluation pipeline (faithfulness/groundedness).

---

Nếu bạn muốn, bước tiếp theo mình có thể viết thêm:

- `OPERATIONS_RUNBOOK.md` (monitoring, SLO, alerting)
- `DEPLOYMENT_GUIDE.md` (Docker/K8s/CI-CD)
- `EVALUATION_GUIDE.md` (dataset và metric đánh giá QA)
