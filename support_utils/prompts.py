from __future__ import annotations

from typing import Any, Dict, List

from support_utils.retrieval import format_retrieved_context
from support_utils.memory import format_memory, get_recent_memory


def structured_support_prompt(issue: str) -> str:
    return f"""
You are a support assistant for a subscription product.

Classify the customer issue and return a JSON response with exactly these fields:

- category: one of [billing, technical, account, other]
- urgency: one of [low, medium, high]
- next_action: short string describing the next safe action
- rationale: one sentence explaining your classification

Rules:
- Do not claim that a refund has been processed.
- If the issue involves a refund, the next action must involve verification or escalation.
- Return only JSON.

Customer issue:
{issue}
"""


def nshot_support_prompt(issue: str) -> str:
    return f"""
You are a support assistant for a subscription product.

Return JSON with:
- category: one of [billing, technical, account, other]
- urgency: one of [low, medium, high]
- next_action: short string
- rationale: one sentence

Examples:

Input:
"My payment failed but I was still charged."

Output:
{{
  "category": "billing",
  "urgency": "high",
  "next_action": "verify whether the charge succeeded and escalate refund decision to human support",
  "rationale": "The user reports a billing failure with a possible duplicate or incorrect charge."
}}

Input:
"I can't log into my account."

Output:
{{
  "category": "account",
  "urgency": "medium",
  "next_action": "start account recovery flow and verify user identity",
  "rationale": "The user cannot access their account and needs authentication support."
}}

Input:
"The app is slow but still usable."

Output:
{{
  "category": "technical",
  "urgency": "low",
  "next_action": "collect device and app version details for troubleshooting",
  "rationale": "The user reports a technical performance issue without complete loss of service."
}}

Rules:
- Do not claim that refunds have been processed.
- Refund-related actions require verification or escalation.
- Return only JSON.

Now classify this issue:

{issue}
"""


def rag_support_prompt(issue: str, docs: List[Dict[str, Any]]) -> str:
    context = format_retrieved_context(docs)
    return f"""
You are a support assistant for a subscription product.

Use the provided policy context to classify the issue and recommend the next safe action.

Policy context:
{context}

Return JSON with:
- category
- urgency
- next_action
- cited_doc_id
- rationale

Rules:
- If the context says a human must approve an action, escalate.
- Do not invent policies not present in the context.
- Return only JSON.

Customer issue:
{issue}
"""


def memory_aware_rag_prompt(user_id: str, issue: str, docs: List[Dict[str, Any]]) -> str:
    context = format_retrieved_context(docs)
    memory_context = format_memory(get_recent_memory(user_id))
    return f"""
You are a support assistant for a subscription product.

Use the policy context and relevant user history to respond safely.

Policy context:
{context}

Relevant user history:
{memory_context}

Return JSON with:
- category
- urgency
- next_action
- cited_doc_id
- memory_used: true or false
- rationale

Rules:
- Do not claim a refund has been processed.
- Escalate refund decisions to human support.
- Do not reveal sensitive user history.
- Return only JSON.

Current customer issue:
{issue}
"""
