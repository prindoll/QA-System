EXTRACTION_SYSTEM_PROMPT = """
You are an information extraction engine.
Return strictly valid JSON only.
Rules:
1) Extract entities, relationships, and attributes.
2) Capture taxonomy links using relation_type in [IS_A, PART_OF, RELATES_TO].
3) Include multi-hop paths if chain evidence appears in the text.
4) Every relationship must include evidence_text copied from source.
5) Never invent unsupported facts. Lower confidence if uncertain.
""".strip()


def build_extraction_user_prompt(text: str, doc_id: str, chunk_id: str) -> str:
    return f"""
Document ID: {doc_id}
Chunk ID: {chunk_id}

TEXT:
{text}

Return JSON now.
""".strip()
