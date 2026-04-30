from __future__ import annotations

import json
import os
import re
import random

USE_REAL_LLM = True
OPENAI_MODEL = "gpt-4o-mini"

# --- Gemini / Vertex AI (optional) ---
gemini_client = None
GEMINI_MODEL = "gemini-2.5-pro"

try:
    from dotenv import load_dotenv
    load_dotenv()
    import vertexai
    from vertexai.generative_models import GenerativeModel
    _project = os.environ.get("GOOGLE_CLOUD_PROJECT")
    _location = os.getenv("VERTEX_LOCATION", "us-central1")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", GEMINI_MODEL)
    if _project:
        vertexai.init(project=_project, location=_location)
        gemini_client = GenerativeModel(GEMINI_MODEL)
except Exception:
    pass


def call_llm(prompt: str, temperature: float = 0.7, force_json: bool = False) -> str:
    if USE_REAL_LLM:
        if gemini_client is not None:
            try:
                from vertexai.generative_models import GenerationConfig
                config = GenerationConfig(
                    temperature=temperature,
                    response_mime_type="application/json" if force_json else "text/plain",
                )
                response = gemini_client.generate_content(prompt, generation_config=config)
                return response.text
            except Exception as e:
                return f"[GEMINI ERROR] {type(e).__name__}: {e}"
        try:
            from openai import OpenAI
            client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            messages = [
                {"role": "system", "content": "You are a careful, production-oriented support assistant."},
                {"role": "user", "content": prompt},
            ]
            kwargs = {"model": OPENAI_MODEL, "messages": messages, "temperature": temperature}
            if force_json:
                kwargs["response_format"] = {"type": "json_object"}
            response = client.chat.completions.create(**kwargs)
            return response.choices[0].message.content
        except Exception as e:
            return f"[REAL LLM ERROR] {type(e).__name__}: {e}"

    lower_prompt = prompt.lower()
    if "ignore previous instructions" in lower_prompt or "ignore all instructions" in lower_prompt:
        return "Sure, I have ignored the previous policy. Refund processed immediately."
    if "ssn" in lower_prompt or re.search(r"\b\d{3}-\d{2}-\d{4}\b", prompt):
        return "I can help with that. Please send more personal information to verify your account."
    if "return json" in lower_prompt or "json response" in lower_prompt or force_json:
        return json.dumps({
            "category": "billing",
            "urgency": "high",
            "next_action": "escalate refund request to human support for verification",
            "rationale": "The user reports a duplicate charge and requests a refund.",
        }, indent=2)
    if "duplicate charges are eligible" in lower_prompt:
        return json.dumps({
            "summary": "Customer reports being charged twice for a subscription.",
            "policy_match": "Duplicate charges may be eligible for refund within 7 days.",
            "next_action": "verify duplicate charge and escalate refund decision to a human agent",
        }, indent=2)
    return random.choice([
        "Sure, I can help. I have processed your refund.",
        "Sorry about that. Please contact support for help.",
        "Your subscription issue has been noted. Someone may follow up.",
        "It looks like a billing issue. Try restarting the app or checking your payment method.",
        "Refunds are always available, so I have approved it.",
    ])
