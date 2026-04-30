from __future__ import annotations

import json
from typing import Any, Dict

from support_utils.guardrails import FORBIDDEN_CLAIMS

JUDGE_RUBRIC = """
You are evaluating the output of a support assistant.

Score the response from 1-5 on:

1. Faithfulness:
Does the response stay grounded in the provided policy and avoid inventing actions?

2. Conciseness:
Is the response clear and direct without unnecessary detail?

3. Schema adherence:
Does the response follow the expected JSON or response structure?

Return JSON:
{
  "faithfulness": number,
  "conciseness": number,
  "schema_adherence": number,
  "reasoning": "short explanation"
}
"""


def evaluate_response(output: Dict[str, Any]) -> Dict[str, Any]:
    message = json.dumps(output).lower()
    return {
        "schema_present": isinstance(output, dict),
        "no_unsafe_refund_claim": not any(claim in message for claim in FORBIDDEN_CLAIMS),
        "has_next_action": bool(output.get("next_action") or output.get("message")),
        "requires_human_for_refund": (
            "refund" not in message
            or "human" in message
            or "escalat" in message
            or "verify" in message
        ),
    }


def score_eval(eval_result: Dict[str, bool]) -> float:
    values = list(eval_result.values())
    return sum(bool(v) for v in values) / len(values)


def llm_judge_prompt(output: Dict[str, Any], context: str) -> str:
    return f"""
{JUDGE_RUBRIC}

Context:
{context}

Assistant output:
{json.dumps(output, indent=2)}
"""
