# Homework 2 — AI Agent System with RAG and Tools


## Contents

| File / folder | Role |
|---------------|------|
| `HOMEWORK2_agent_system.py` | Main pipeline: RAG → tool-calling agent → merging agent |
| `functions.py` | `agent_run`, `agent`, `df_as_text` (Ollama chat + tools) |
| `data/lab_custom_docs.txt` | RAG corpus (line-based retrieval) |
| `requirements.txt` | Python dependencies |

---

## System architecture

The system is implemented in `HOMEWORK2_agent_system.py` and runs as a **linear three-agent pipeline**:

### Retrieval (programmatic, not an LLM)

The script calls `search_text_lines()` on a text file and builds a JSON retrieval payload (`query`, `document`, `matching_content`, `num_lines`). This is the RAG retrieval step.

### Agent 1 — RAG / grounded explainer

- **Role:** Concise ML tutor; explain using only retrieved evidence.
- **Input:** The retrieval JSON plus the focus topic (`RAG_QUERY`).
- **Output:** A brief explanation grounded in `matching_content`.

### Agent 2 — Tool / metrics fetcher

- **Role:** Data assistant that must call `get_department_metrics`.
- **Mechanism:** `agent_run(..., output="tools", tools=[tool_get_department_metrics])`. Python executes the tool and stores the result on the tool call; the script converts the returned `pandas.DataFrame` to a markdown table via `df_as_text()`.

### Agent 3 — Integrator / briefing writer

- **Role:** Merge documentation-grounded text with tabular metrics.
- **Input:** Agent 1’s text and Agent 2’s markdown table.
- **Output:** Markdown with sections **Summary**, **Linking concepts to the metrics**, and **Recommendation**.

**Workflow summary:** Retrieve → explain (RAG) → tool-call metrics → merge into one report.

---

## RAG data source

- **File (this repo):** `data/lab_custom_docs.txt` (resolved next to `HOMEWORK2_agent_system.py` via `RAG_DOCUMENT`).
- **Content:** Plain text; each line is a separate entry (ML/RAG-related notes).
- **Search function:** `search_text_lines(query, document_path)`
  - Reads the file as lines.
  - Keeps every line where `query.lower()` appears as a substring of the line (case-insensitive).
  - Returns a dictionary: `query`, `document` (basename), `matching_content` (joined matching lines), `num_lines`.
  - If the path is missing: empty content and an `error` field.
- **LLM connection:** The dict is `json.dumps(..., indent=2)` and embedded in the user/task content for Agent 1.

---

## Tool functions

| Tool name | Purpose | Parameters | Returns |
|-----------|---------|------------|---------|
| `get_department_metrics` | Quarterly rows for one department from an in-memory metrics table | `department` (string, required) — e.g. `"Engineering"`, `"Sales"`, `"Operations"` (matching is case-insensitive) | `pandas.DataFrame` with columns: `department`, `quarter`, `headcount`, `budget_k`, `projects_shipped`. Empty DataFrame if the name is blank or unknown. |

The LLM sees this tool through `tool_get_department_metrics` (Ollama-style metadata: `type`, `function.name`, `function.description`, `function.parameters`).

---

## Technical details

- **Language / entry point:** Python 3; run `HOMEWORK2_agent_system.py`.
- **LLM runtime:** Ollama (local).
- **Default model:** `smollm2:1.7b` (`MODEL` in the script).
- **HTTP API:** `functions.py` POSTs to `{OLLAMA_HOST}/api/chat` (default `http://localhost:11434`). Override with environment variable **`OLLAMA_HOST`** (full base URL, no trailing slash) or **`OLLAMA_PORT`** (used only when `OLLAMA_HOST` is unset).
- **API keys:** None (no cloud LLM). RAG file is local; metrics are in-memory (`_METRICS_ROWS` / `METRICS_DF`).
- **Key packages:** `pandas`, `requests`, `tabulate` (for `DataFrame.to_markdown`).
- **Important project files (this repo):**
  - `HOMEWORK2_agent_system.py` — main pipeline
  - `functions.py` — `agent_run`, `agent`, `df_as_text`
  - `data/lab_custom_docs.txt` — RAG corpus
- **Reliability:** If the model does not return a tool call, the script falls back to `get_department_metrics(...)` and may print: `Note: no tool output from model; calling get_department_metrics directly.`

---

## Setup

1. Install Python packages: `pip install -r requirements.txt` (use a venv if your course recommends it).
2. Install and start [Ollama](https://ollama.com) and pull the model: `ollama pull smollm2:1.7b`
3. Ensure Ollama responds at your configured host (default `http://127.0.0.1:11434`).

---

## Run

From the directory that contains `HOMEWORK2_agent_system.py` (clone of this repo or this folder):

```bash
python3 HOMEWORK2_agent_system.py
```

**Expected output:** Labeled terminal sections — RAG retrieval JSON, Agent 1 answer, Agent 2 markdown table, Agent 3 merged briefing — suitable for screenshots.

