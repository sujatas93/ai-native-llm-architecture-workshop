from __future__ import annotations

from datetime import datetime, UTC
from typing import Any, Dict, List, Optional

TRACE_LOGS: List[Dict[str, Any]] = []


def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def log_trace(request_id: str, stage: str, event: str, payload: Dict[str, Any]) -> None:
    TRACE_LOGS.append({
        "timestamp": datetime.now(UTC).isoformat(),
        "request_id": request_id,
        "stage": stage,
        "event": event,
        "payload": payload,
    })


def view_traces(request_id: Optional[str] = None) -> List[Dict[str, Any]]:
    rows = TRACE_LOGS if request_id is None else [r for r in TRACE_LOGS if r["request_id"] == request_id]
    return rows


def print_traces(request_id: Optional[str] = None) -> None:
    for r in view_traces(request_id):
        print(f"\n\U0001f9fe [{r['timestamp']}]")
        print(f"Request: {r['request_id']}")
        print(f"Stage: {r['stage']} | Event: {r['event']}")
        print(f"Payload: {r['payload']}")
