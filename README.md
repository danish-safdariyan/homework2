# Homework 2 — submission bundle (Git-friendly)

This folder holds everything needed to **run** and **link** Homework 2 (“AI Agent System with RAG and Tools”) in one place for your instructor or your `.docx` GitHub links.

## Contents

| File / folder | Role |
|---------------|------|
| `HOMEWORK2_agent_system.py` | Main pipeline: RAG → tool-calling agent → merging agent |
| `functions.py` | `agent_run`, `agent`, `df_as_text` (Ollama chat + tools) |
| `data/lab_custom_docs.txt` | RAG corpus (line-based retrieval) |
| `requirements.txt` | Python dependencies |

## Setup

1. Install Python packages: `pip install -r requirements.txt`
2. Install [Ollama](https://ollama.com) and pull the model: `ollama pull smollm2:1.7b`
3. Start Ollama (usually listens on `http://127.0.0.1:11434`)

## Run

From **this** directory:

```bash
cd homework2_submission
python3 HOMEWORK2_agent_system.py
```

Use the printed sections for **screenshots** (RAG JSON + Agent 1, Agent 2 table, Agent 3 merge).

## GitHub links for your `.docx`

After you push, use URLs like (replace `USER` / `REPO` / branch):

- `https://github.com/USER/REPO/blob/main/homework2_submission/HOMEWORK2_agent_system.py`
- `https://github.com/USER/REPO/blob/main/homework2_submission/functions.py`
- `https://github.com/USER/REPO/blob/main/homework2_submission/data/lab_custom_docs.txt`

The course repo also keeps copies under `08_function_calling/` and `07_rag/data/`; this folder is the **single bundle** for submission.

## Tool reference (documentation)

| Tool name | Purpose | Parameters | Returns |
|-----------|---------|------------|---------|
| `get_department_metrics` | Quarterly metrics for a department | `department` (string) | `pandas.DataFrame` |

RAG: `search_text_lines()` scans `data/lab_custom_docs.txt` line-by-line (case-insensitive substring) and builds JSON with `matching_content` and `num_lines`.
# homework2
