from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from support_utils.guardrails import GuardrailResult, input_guardrails


@dataclass
class Decision:
    action: str  # ANSWER, ESCALATE, BLOCK, FALLBACK
    reason: str
    intent: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


def classify_intent(issue: str) -> str:
    lower = issue.lower()
    if any(w in lower for w in ["refund", "charged twice", "duplicate charge", "payment failed"]):
        return "refund_or_billing"
    if any(w in lower for w in ["login", "password", "account"]):
        return "account_access"
    if any(w in lower for w in ["slow", "bug", "error", "crash"]):
        return "technical_support"
    return "general_support"


def policy_decision(issue: str) -> Decision:
    guardrail = input_guardrails(issue)
    if guardrail.action == "BLOCK":
        return Decision("BLOCK", guardrail.reason, None, guardrail.metadata)
    intent = classify_intent(issue)
    if intent == "refund_or_billing":
        return Decision(
            "ESCALATE",
            "Refund and billing decisions require human verification",
            intent,
            {"policy": "refund_requires_human_approval"},
        )
    return Decision("ANSWER", "Request can be answered by assistant", intent, {"policy": "standard_support"})


def fallback_response(issue: str, reason: str) -> Dict[str, Any]:
    return {
        "status": "fallback",
        "message": "I'm not able to complete that request directly, but I can route it to the right support path.",
        "reason": reason,
        "next_action": "send_to_support_queue",
    }


def escalation_response(issue: str, reason: str) -> Dict[str, Any]:
    return {
        "status": "escalated",
        "message": "This request requires human review. I'm escalating it to a support agent.",
        "reason": reason,
        "next_action": "human_review",
    }


def blocked_response(issue: str, reason: str) -> Dict[str, Any]:
    return {
        "status": "blocked",
        "message": "I can't process this request as written.",
        "reason": reason,
        "next_action": "ask_user_to_rephrase_without_sensitive_or_out_of_scope_content",
    }
