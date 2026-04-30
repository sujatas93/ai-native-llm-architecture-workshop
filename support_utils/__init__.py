"""
support package — re-exports all public symbols so notebooks can continue
to use `from support_utils import ...` via the thin shim, or import directly:

    from support.guardrails import GuardrailResult
    from support.llm_client import call_llm
"""
from support_utils.llm_client import (
    USE_REAL_LLM, OPENAI_MODEL, GEMINI_MODEL, gemini_client, call_llm,
)
from support_utils.data import customer_issues, primary_issue, knowledge_base
from support_utils.response_parser import (
    REQUIRED_FIELDS, VALID_CATEGORIES, VALID_URGENCY,
    tokenize, parse_json_response, validate_support_schema,
)
from support_utils.retrieval import basic_retrieve, format_retrieved_context, enhanced_retrieve
from support_utils.memory import conversation_memory, remember, get_recent_memory, format_memory
from support_utils.prompts import (
    structured_support_prompt, nshot_support_prompt,
    rag_support_prompt, memory_aware_rag_prompt,
)
from support_utils.guardrails import (
    FORBIDDEN_CLAIMS, GuardrailResult,
    contains_pii, is_prompt_injection, is_in_domain,
    input_guardrails, output_guardrails,
)
from support_utils.policy import (
    Decision, classify_intent, policy_decision,
    fallback_response, escalation_response, blocked_response,
)
from support_utils.tracing import (
    TRACE_LOGS, estimate_tokens, log_trace, view_traces, print_traces,
)
from support_utils.evaluation import (
    JUDGE_RUBRIC, evaluate_response, score_eval, llm_judge_prompt,
)
from support_utils.pipeline import next_request_id, final_ai_native_pipeline

__all__ = [
    "USE_REAL_LLM", "OPENAI_MODEL", "GEMINI_MODEL", "gemini_client", "call_llm",
    "customer_issues", "primary_issue", "knowledge_base",
    "REQUIRED_FIELDS", "VALID_CATEGORIES", "VALID_URGENCY",
    "tokenize", "parse_json_response", "validate_support_schema",
    "basic_retrieve", "format_retrieved_context", "enhanced_retrieve",
    "conversation_memory", "remember", "get_recent_memory", "format_memory",
    "structured_support_prompt", "nshot_support_prompt",
    "rag_support_prompt", "memory_aware_rag_prompt",
    "FORBIDDEN_CLAIMS", "GuardrailResult",
    "contains_pii", "is_prompt_injection", "is_in_domain",
    "input_guardrails", "output_guardrails",
    "Decision", "classify_intent", "policy_decision",
    "fallback_response", "escalation_response", "blocked_response",
    "TRACE_LOGS", "estimate_tokens", "log_trace", "view_traces", "print_traces",
    "JUDGE_RUBRIC", "evaluate_response", "score_eval", "llm_judge_prompt",
    "next_request_id", "final_ai_native_pipeline",
]
