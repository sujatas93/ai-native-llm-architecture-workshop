from __future__ import annotations

import json
import time
from dataclasses import asdict
from typing import Any, Dict

from support_utils.llm_client import call_llm
from support_utils.policy import policy_decision, blocked_response, escalation_response, fallback_response
from support_utils.retrieval import enhanced_retrieve
from support_utils.prompts import memory_aware_rag_prompt
from support_utils.memory import remember
from support_utils.guardrails import output_guardrails
from support_utils.response_parser import parse_json_response
from support_utils.tracing import log_trace, estimate_tokens
from support_utils.evaluation import evaluate_response, score_eval

_request_counter = 0


def next_request_id() -> str:
    global _request_counter
    _request_counter += 1
    return f"req_{_request_counter:04d}"


def final_ai_native_pipeline(user_id: str, issue: str, prompt_version: str = "v_final") -> Dict[str, Any]:
    request_id = next_request_id()
    start = time.time()

    log_trace(request_id, "input", "received_issue", {"issue": issue, "prompt_version": prompt_version})

    decision = policy_decision(issue)
    log_trace(request_id, "decisioning", "policy_decision", asdict(decision))

    if decision.action == "BLOCK":
        response = blocked_response(issue, decision.reason)
        log_trace(request_id, "response", "blocked_response", response)
        ev = evaluate_response(response)
        log_trace(request_id, "evaluation", "deterministic_eval", {"eval": ev, "score": score_eval(ev)})
        return response

    if decision.action == "ESCALATE":
        response = escalation_response(issue, decision.reason)
        remember(user_id, issue, response["message"])
        log_trace(request_id, "response", "escalation_response", response)
        ev = evaluate_response(response)
        log_trace(request_id, "evaluation", "deterministic_eval", {"eval": ev, "score": score_eval(ev)})
        return response

    docs = enhanced_retrieve(issue, top_k=2)
    log_trace(request_id, "retrieval", "retrieved_documents",
              {"doc_ids": [d["doc_id"] for d in docs], "scores": [d.get("final_score") for d in docs]})

    prompt = memory_aware_rag_prompt(user_id, issue, docs)
    log_trace(request_id, "prompt", "constructed_prompt",
              {"prompt_version": prompt_version, "prompt_chars": len(prompt),
               "estimated_prompt_tokens": estimate_tokens(prompt)})

    output_text = call_llm(prompt, temperature=0.2, force_json=True)
    log_trace(request_id, "llm", "generated_output",
              {"output_chars": len(output_text), "estimated_output_tokens": estimate_tokens(output_text),
               "output_preview": output_text[:300]})

    output_check = output_guardrails(output_text)
    log_trace(request_id, "guardrails", "output_guardrail_result", asdict(output_check))

    if output_check.action == "FALLBACK":
        response = fallback_response(issue, output_check.reason)
    elif output_check.action == "ESCALATE":
        response = escalation_response(issue, output_check.reason)
    else:
        parsed, error = parse_json_response(output_text)
        response = parsed if parsed else fallback_response(issue, error or "Unknown parse error")

    remember(user_id, issue, json.dumps(response))

    ev = evaluate_response(response)
    latency_ms = round((time.time() - start) * 1000, 2)
    log_trace(request_id, "evaluation", "deterministic_eval",
              {"eval": ev, "score": score_eval(ev), "latency_ms": latency_ms})

    return response
