from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict

from support_utils.response_parser import tokenize, parse_json_response

FORBIDDEN_CLAIMS = [
    "refund processed",
    "processed your refund",
    "approved your refund",
    "refund has been approved",
]


@dataclass
class GuardrailResult:
    allowed: bool
    reason: str
    action: str  # ALLOW, BLOCK, ESCALATE, FALLBACK
    metadata: Dict[str, Any]


def contains_pii(text: str) -> bool:
    patterns = [r"\b\d{3}-\d{2}-\d{4}\b", r"\b\d{16}\b"]
    return any(re.search(p, text) for p in patterns) or "ssn" in text.lower()


def is_prompt_injection(text: str) -> bool:
    phrases = [
        "ignore previous instructions", "ignore all instructions",
        "developer message", "system prompt", "jailbreak", "bypass policy",
    ]
    return any(p in text.lower() for p in phrases)


def is_in_domain(text: str) -> bool:
    domain_keywords = {
        "charge", "charged", "billing", "refund", "subscription", "payment",
        "login", "account", "app", "slow", "password", "invoice",
    }
    return bool(tokenize(text) & domain_keywords)


def input_guardrails(issue: str) -> GuardrailResult:
    if contains_pii(issue):
        return GuardrailResult(False, "PII detected in user input", "BLOCK", {"guardrail": "pii_filter"})
    if is_prompt_injection(issue):
        return GuardrailResult(False, "Prompt injection attempt detected", "BLOCK", {"guardrail": "prompt_injection"})
    if not is_in_domain(issue):
        return GuardrailResult(False, "Request is outside support assistant domain", "BLOCK", {"guardrail": "domain_check"})
    return GuardrailResult(True, "Input passed guardrails", "ALLOW", {"guardrail": "input_guardrails"})


def output_guardrails(output: str) -> GuardrailResult:
    lower = output.lower()
    if any(claim in lower for claim in FORBIDDEN_CLAIMS):
        return GuardrailResult(
            False, "Output claims refund was processed or approved",
            "ESCALATE", {"guardrail": "unsafe_refund_claim"},
        )
    parsed, error = parse_json_response(output)
    if error:
        return GuardrailResult(False, "Output is not valid JSON", "FALLBACK",
                               {"guardrail": "json_validation", "error": error})
    if not isinstance(parsed, dict):
        return GuardrailResult(False, "Output JSON is not an object", "FALLBACK",
                               {"guardrail": "json_object_validation"})
    return GuardrailResult(True, "Output passed guardrails", "ALLOW", {"guardrail": "output_guardrails"})
