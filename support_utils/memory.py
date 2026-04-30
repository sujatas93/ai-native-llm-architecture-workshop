from __future__ import annotations

from datetime import datetime, UTC
from typing import Any, Dict, List

conversation_memory: List[Dict[str, Any]] = []


def remember(user_id: str, issue: str, assistant_response: str) -> None:
    conversation_memory.append({
        "timestamp": datetime.now(UTC).isoformat(),
        "user_id": user_id,
        "issue": issue,
        "assistant_response": assistant_response,
    })


def get_recent_memory(user_id: str, limit: int = 3) -> List[Dict[str, Any]]:
    return [m for m in conversation_memory if m["user_id"] == user_id][-limit:]


def format_memory(memories: List[Dict[str, Any]]) -> str:
    if not memories:
        return "No prior user history available."
    return "\n".join(
        f"- Previous issue: {m['issue']} | Response: {m['assistant_response'][:80]}"
        for m in memories
    )
