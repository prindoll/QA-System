# Báo Cáo Hình Thức Index DB Trong Ứng Dụng QA GraphRAG
## Tập trung dữ liệu Multi-hop và Taxonomy

- Dự án: GraphRAG QA (Neo4j + Vector Index)
- Mục tiêu: tăng độ đúng truy vấn nhiều bước và truy vấn phân loại
- Phạm vi: luồng ingest/index, migration, và tiêu chí vận hành

---

# 1. Bài toán nghiệp vụ

- Dữ liệu có quan hệ nhiều bước (multi-hop): A -> B -> C
- Dữ liệu có quan hệ taxonomy: `IS_A`, `PART_OF`, `RELATES_TO`
- QA cần:
1. Truy xuất đúng đoạn văn bản liên quan
2. Mở rộng ngữ cảnh theo graph path
3. Có citation theo `chunk_id` và `source_doc_id`

---

# 2. Kiến trúc index hiện tại (sau nâng cấp)

- DB chính: Neo4j (lưu graph + vector)
- Node:
1. `Entity`
2. `Chunk`
- Relationship:
1. `MENTIONED_IN` (Entity -> Chunk)
2. `IS_A`
3. `PART_OF`
4. `RELATES_TO`
- Vector: `Chunk.embedding` + vector index `chunk_embedding_index`

---

# 3. Schema và ràng buộc quan trọng

- Uniqueness:
1. `Entity.entity_id`
2. `Chunk.chunk_id`
3. `relation_id` cho từng loại cạnh: `RELATES_TO`, `IS_A`, `PART_OF`
- Index:
1. `entity_canonical_name`
2. vector index cosine, dimension 1536
- Kết quả: đảm bảo idempotent khi ingest lại

---

# 4. Luồng ingest/index end-to-end

1. Input text -> `SemanticChunker` sinh `chunk_id`, `source_doc_id`, `text`
2. Mỗi chunk -> extraction JSON (entities + relationships)
3. Normalize:
   - map taxonomy về `IS_A|PART_OF|RELATES_TO`
   - resolve entity, sinh `entity_id/relation_id` ổn định
4. Graph index:
   - `upsert_entities`
   - `upsert_mentions` (`Entity-[:MENTIONED_IN]->Chunk`)
   - `upsert_relationships` theo typed edge
5. Vector index:
   - batch embedding bằng `embed_documents`
   - ghi vào `Chunk.embedding`

---

# 5. Điểm mới cho Multi-hop và Taxonomy

- Trước đây:
1. Nhiều quan hệ bị gom vào `RELATES_TO` + `predicate`
2. Thiếu `MENTIONED_IN` làm graph seed yếu
- Hiện tại:
1. Quan hệ taxonomy được lưu thành cạnh thật (`IS_A`, `PART_OF`)
2. `MENTIONED_IN` được tạo ngay trong ingest
3. `source_chunk_id` gắn vào quan hệ để truy vết bằng chứng

---

# 6. Luồng migration dữ liệu cũ

- Script tổng: `python -m scripts.run_graph_migration`
- Các bước:
1. Migrate cạnh `RELATES_TO` cũ có `predicate IS_A/PART_OF` -> typed edge
2. Backfill `MENTIONED_IN` từ `source_chunk_id`
3. Kiểm tra chunk thiếu embedding và reindex phần thiếu
- Mục tiêu: không mất dữ liệu cũ, không tạo duplicate

---

# 7. Cách retrieval tận dụng index

- Seed retrieval:
1. Vector search trên `chunk_embedding_index`
2. Graph seed từ `(:Entity)-[:MENTIONED_IN]->(:Chunk)`
- Graph expansion:
1. Traverse `[:RELATES_TO|IS_A|PART_OF*1..max_hops]`
2. Tính confidence theo path
3. Lọc theo ngưỡng relevance
- Score fusion: vector + graph để xếp hạng chunk

---

# 8. Ví dụ truy vấn multi-hop taxonomy

- Dữ liệu:
1. `Laptop IS_A Computer`
2. `Computer PART_OF IT_System`
3. `GPU RELATES_TO Laptop`
- Câu hỏi:
  "GPU thuộc nhóm nào và liên quan tới hệ thống nào?"
- Kỳ vọng:
1. Seed từ chunk chứa `GPU`, `Laptop`
2. Mở rộng graph qua `IS_A` và `PART_OF`
3. Trả lời có citation đúng theo chunk/doc

---

# 9. KPI báo cáo vận hành index

- KPI chất lượng:
1. Tỷ lệ câu hỏi multi-hop trả lời đúng có citation
2. Tỷ lệ truy vấn taxonomy trả đúng quan hệ `IS_A/PART_OF`
- KPI dữ liệu:
1. Số `Chunk`, `Entity`, `MENTIONED_IN`, `IS_A`, `PART_OF`, `RELATES_TO`
2. Tỷ lệ chunk có embedding
- KPI hiệu năng:
1. Thời gian ingest / 1 tài liệu
2. Chi phí embedding / 1k chunk

---

# 10. Checklist kiểm thử và nghiệm thu

- Functional:
1. Ingest xong có đủ `Entity`, `Chunk`, `MENTIONED_IN`
2. Có path multi-hop không rỗng trên bộ dữ liệu mẫu
3. Ingest lại không nhân bản node/edge
- Operational:
1. Migration chạy một lần thành công
2. Không còn chunk thiếu embedding sau backfill
3. API `/qa/ask` không đổi interface

---

# 11. Rủi ro và kiểm soát

- Rủi ro:
1. Extraction trả quan hệ sai type
2. Dữ liệu cũ thiếu `source_chunk_id` nên backfill mention không đủ
3. Khối lượng chunk lớn làm tăng thời gian embedding
- Kiểm soát:
1. Enforce relation type trong normalize/repository
2. Báo cáo số lượng record migrate/backfill
3. Dùng batch embedding và theo dõi throughput

---

# 12. Kế hoạch triển khai production

1. `python -m scripts.bootstrap_neo4j`
2. Chạy migration: `python -m scripts.run_graph_migration`
3. Chạy ingest mới cho dữ liệu phát sinh
4. Theo dõi KPI 1-2 tuần, hiệu chỉnh threshold retrieval

---

# 13. Thông điệp chốt

- Hình thức index hiện tại đã phù hợp hơn cho dữ liệu multi-hop + taxonomy
- Điểm cốt lõi là:
1. typed edges (`IS_A`, `PART_OF`, `RELATES_TO`)
2. liên kết chứng cứ `MENTIONED_IN`
3. vector + graph chạy đồng bộ
- Hướng tiếp theo: tối ưu chất lượng extraction và quan sát KPI theo domain
