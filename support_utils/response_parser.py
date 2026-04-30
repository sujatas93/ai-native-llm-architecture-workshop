from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional, Tuple

REQUIRED_FIELDS = {"category", "urgency", "next_action", "rationale"}
VALID_CATEGORIES = {"billing", "technical", "account", "other"}
VALID_URGENCY    = {"low", "medium", "high"}


def tokenize(text: str) -> set:
    return set(re.findall(r"[a-zA-Z_]+", text.lower()))


def parse_json_response(response: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    try:
        return json.loads(response), None
    except json.JSONDecodeError as e:
        return None, f"Invalid JSON: {e}"


def validate_support_schema(data: Dict[str, Any]) -> List[str]:
    errors = []
    missing = REQUIRED_FIELDS - set(data.keys())
    if missing:
        errors.append(f"Missing required fields: {sorted(missing)}")
    if data.get("category") not in VALID_CATEGORIES:
        errors.append(f"Invalid category: {data.get('category')}")
    if data.get("urgency") not in VALID_URGENCY:
        errors.append(f"Invalid urgency: {data.get('urgency')}")
    if not isinstance(data.get("next_action"), str) or not data.get("next_action"):
        errors.append("next_action must be a non-empty string")
    if not isinstance(data.get("rationale"), str) or not data.get("rationale"):
        errors.append("rationale must be a non-empty string")
    return errors
