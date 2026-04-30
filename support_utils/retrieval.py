from __future__ import annotations

from typing import Any, Dict, List

from support_utils.data import knowledge_base
from support_utils.response_parser import tokenize


def basic_retrieve(query: str, top_k: int = 2) -> List[Dict[str, Any]]:
    query_tokens = tokenize(query)
    scored = []
    for doc in knowledge_base:
        tokens = tokenize(doc["text"] + " " + " ".join(doc["tags"]) + " " + doc["title"])
        scored.append((len(query_tokens & tokens), doc))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [doc for score, doc in scored[:top_k] if score > 0]


def format_retrieved_context(docs: List[Dict[str, Any]]) -> str:
    if not docs:
        return "No relevant policy documents found."
    blocks = []
    for doc in docs:
        blocks.append(
            f"Document: {doc['title']}\n"
            f"Doc ID: {doc['doc_id']}\n"
            f"Freshness: {doc['freshness']}\n"
            f"Trust Score: {doc['trust_score']}\n"
            f"Content: {doc['text']}"
        )
    return "\n\n".join(blocks)


def enhanced_retrieve(query: str, top_k: int = 2) -> List[Dict[str, Any]]:
    query_tokens = tokenize(query)
    scored = []
    for doc in knowledge_base:
        tokens = tokenize(doc["text"] + " " + " ".join(doc["tags"]) + " " + doc["title"])
        lexical = len(query_tokens & tokens)
        freshness_boost = 1.0 if doc["freshness"] >= "2026-01-01" else 0.2
        final_score = lexical + doc["trust_score"] + freshness_boost
        scored.append({**doc, "lexical_score": lexical, "final_score": round(final_score, 3)})
    scored.sort(key=lambda d: d["final_score"], reverse=True)
    return scored[:top_k]
