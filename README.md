# AI-Native Software Architecture
### O'Reilly Course — Designing Reliable LLM Systems as End-to-End Pipelines

---

## 1. Jupyter Setup

### Option A — PyCharm / IntelliJ (recommended)

**Prerequisites:** PyCharm Professional (Community edition does not support Jupyter).

1. Open the project folder in PyCharm.
2. Create a virtual environment:
   - Go to **Settings → Project → Python Interpreter → Add Interpreter → Add Local Interpreter**
   - Choose **Virtualenv**, set location to `.venv` inside the project root, and select a Python 3.10+ base interpreter.
3. Install dependencies:
   ```
   pip install jupyter google-cloud-aiplatform google-auth python-dotenv openai
   ```
4. Open any `section_0*.ipynb` file — PyCharm will detect it as a Jupyter notebook and offer to start the Jupyter server automatically.
5. Select the `.venv` kernel from the kernel picker in the top-right of the notebook editor.
6. Run cells with **Shift+Enter** or the ▶ Run All button.

> **Tip:** If PyCharm asks to trust the notebook, click **Trust**. Notebooks from this repo are safe to run locally.

### Option B — JupyterLab (browser)

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install jupyterlab google-cloud-aiplatform google-auth python-dotenv openai
jupyter lab
```

Open any `section_0*.ipynb` from the file browser.

---

## 2. Credentials — `.env` file

Create a file named `.env` in the project root (it is already in `.gitignore`).

```dotenv
# ── Vertex AI / Gemini (primary LLM) ───────────────────────────────────────
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
VERTEX_LOCATION=us-central1
GEMINI_MODEL=gemini-2.5-pro

# ── OpenAI (fallback LLM) ───────────────────────────────────────────────────
OPENAI_API_KEY=sk-...
```

### Authenticating with Vertex AI

**Application Default Credentials (local dev — simpler):**
```bash
gcloud auth application-default login
```
Leave `GOOGLE_APPLICATION_CREDENTIALS` blank in `.env`.

### Toggling demo mode vs real LLM

Each notebook has a dedicated toggle cell near the top:

```python
import support
support.USE_REAL_LLM = True   # False = fast deterministic mock (no credentials needed)
```

Changing this cell and re-running it takes effect immediately — no kernel restart required.

---

## 3. Notebook structure

The course material is split into six focused notebooks. Each notebook imports shared infrastructure from the `support/` package and only shows the code relevant to its section.

| Notebook | Section | What you build |
|---|---|---|
| `section_01_naive_patterns.ipynb` | Why Traditional Patterns Break | A naive single-prompt assistant; observe variability and failure modes |
| `section_02_input_behavior.ipynb` | Input & Behavior Patterns | Structured prompts, output contracts, N-shot examples, prompt versioning |
| `section_03_retrieval_knowledge.ipynb` | Retrieval & Knowledge Patterns | Keyword retrieval, RAG prompts, freshness/trust scoring, conversation memory |
| `section_04_governance.ipynb` | Decisioning, Fallbacks & Governance | Input guardrails, intent classification, policy decision layer, output guardrails |
| `section_05_observability.ipynb` | Monitoring & Observability | In-memory tracing, deterministic evaluation, LLM-as-a-judge rubric |
| `section_06_pipeline.ipynb` | Closing the Loop | Compose all layers into a single end-to-end pipeline; inspect traces |

### Shared code — the `support/` package

Notebooks import shared infrastructure from `support/`. You can also import directly from submodules:

```
support/
├── llm_client.py       # call_llm(), USE_REAL_LLM, Gemini/OpenAI init
├── data.py             # customer_issues, knowledge_base
├── response_parser.py  # parse_json_response(), validate_support_schema(), tokenize()
├── retrieval.py        # basic_retrieve(), enhanced_retrieve(), format_retrieved_context()
├── memory.py           # conversation_memory, remember(), get_recent_memory()
├── prompts.py          # structured_support_prompt(), nshot_support_prompt(), rag_support_prompt()
├── guardrails.py       # GuardrailResult, input_guardrails(), output_guardrails(), FORBIDDEN_CLAIMS
├── policy.py           # Decision, policy_decision(), escalation/fallback/blocked responses
├── tracing.py          # TRACE_LOGS, log_trace(), view_traces(), print_traces()
├── evaluation.py       # evaluate_response(), score_eval(), JUDGE_RUBRIC, llm_judge_prompt()
└── pipeline.py         # final_ai_native_pipeline()
```

`support_utils.py` at the project root re-exports everything from the package for backward compatibility.

### Running order

The notebooks are designed to be run in order (01 → 06), but each is self-contained and can be run independently. The `support/` package provides all shared state; nothing is carried over between notebook kernels.
