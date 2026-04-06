# HOMEWORK2_agent_system.py
# Homework 2: AI Agent System with RAG and Tools (self-contained submission folder)
# Tim Fraser
#
# Run from this directory (homework2_submission/):
#   python3 HOMEWORK2_agent_system.py
#
# Requires: Ollama with model smollm2:1.7b, pip install -r requirements.txt
#
# Canonical copy also lives at: 08_function_calling/HOMEWORK2_agent_system.py
# This file uses RAG data from ./data/lab_custom_docs.txt next to this script.

# 0. SETUP ###################################

import json
import os

import pandas as pd

from functions import agent_run, df_as_text

MODEL = "smollm2:1.7b"

# RAG corpus shipped in this folder (submission bundle)
RAG_DOCUMENT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "lab_custom_docs.txt")

RAG_QUERY = "vector database"

# 1. RAG: SEARCH FUNCTION ###################################


def search_text_lines(query: str, document_path: str) -> dict:
    """
    Line-based keyword retrieval (case-insensitive substring per line).

    Returns a dict suitable for json.dumps() → LLM user message (LAB pattern).
    """
    if not os.path.isfile(document_path):
        return {
            "query": query,
            "document": os.path.basename(document_path),
            "matching_content": "",
            "num_lines": 0,
            "error": f"File not found: {document_path}",
        }

    with open(document_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    hits = [ln for ln in lines if query.lower() in ln.lower()]
    text = "\n".join(ln.rstrip("\n") for ln in hits)
    return {
        "query": query,
        "document": os.path.basename(document_path),
        "matching_content": text,
        "num_lines": len(hits),
    }


# 2. TOOL: DEPARTMENT METRICS #######

_METRICS_ROWS = [
    {"department": "Engineering", "quarter": "Q1", "headcount": 42, "budget_k": 1200, "projects_shipped": 7},
    {"department": "Engineering", "quarter": "Q2", "headcount": 45, "budget_k": 1280, "projects_shipped": 9},
    {"department": "Sales", "quarter": "Q1", "headcount": 18, "budget_k": 410, "projects_shipped": 0},
    {"department": "Sales", "quarter": "Q2", "headcount": 20, "budget_k": 455, "projects_shipped": 0},
    {"department": "Operations", "quarter": "Q1", "headcount": 30, "budget_k": 620, "projects_shipped": 12},
    {"department": "Operations", "quarter": "Q2", "headcount": 31, "budget_k": 640, "projects_shipped": 11},
]
METRICS_DF = pd.DataFrame(_METRICS_ROWS)


def get_department_metrics(department: str):
    """Return quarterly rows for one department (case-insensitive)."""
    if department is None or str(department).strip() == "":
        return pd.DataFrame()
    key = str(department).strip().lower()
    mask = METRICS_DF["department"].str.lower() == key
    return METRICS_DF.loc[mask].copy()


tool_get_department_metrics = {
    "type": "function",
    "function": {
        "name": "get_department_metrics",
        "description": (
            "Fetch quarterly headcount, budget (thousands USD), and projects shipped "
            "for a department: Engineering, Sales, or Operations."
        ),
        "parameters": {
            "type": "object",
            "required": ["department"],
            "properties": {
                "department": {
                    "type": "string",
                    "description": "Department name, e.g. Engineering",
                }
            },
        },
    },
}

# 3. THREE-AGENT PIPELINE ###################################


def run_homework2_system(rag_query: str = RAG_QUERY, metrics_department: str = "Engineering"):
    """
    Run Agent 1 (RAG), Agent 2 (tools), Agent 3 (merge). Prints labeled blocks for screenshots.
    """
    retrieval = search_text_lines(rag_query, RAG_DOCUMENT)
    retrieval_json = json.dumps(retrieval, indent=2)

    print("=== RAG retrieval (JSON passed to Agent 1) ===")
    print(retrieval_json)
    print()

    role_rag = (
        "You are a concise ML tutor. The user message is JSON with keys query, matching_content, num_lines. "
        "Explain the query topic using ONLY matching_content as evidence. "
        "If num_lines is 0, say no evidence was found. "
        "Do not repeat the full JSON. Use short markdown: a title and 2–4 sentences."
    )
    task_rag = (
        f"User focus topic: {rag_query}\n\n"
        f"Retrieved evidence as JSON:\n{retrieval_json}"
    )
    out_rag = agent_run(role=role_rag, task=task_rag, model=MODEL, output="text", tools=None)

    print("=== Agent 1 — RAG answer (grounded) ===")
    print(out_rag)
    print()

    role_tool = (
        "You are a data assistant. When asked for department metrics, you MUST call "
        "get_department_metrics with the department name. Do not invent numbers."
    )
    task_tool = f"Pull all quarterly metrics for the {metrics_department} department using the tool."
    tool_calls = agent_run(
        role=role_tool,
        task=task_tool,
        model=MODEL,
        output="tools",
        tools=[tool_get_department_metrics],
    )

    df_metrics = None
    if isinstance(tool_calls, list) and len(tool_calls) > 0:
        df_metrics = tool_calls[0].get("output")
    if not isinstance(df_metrics, pd.DataFrame) or df_metrics.empty:
        print("Note: no tool output from model; calling get_department_metrics directly.")
        df_metrics = get_department_metrics(metrics_department)

    metrics_table = df_as_text(df_metrics) if not df_metrics.empty else "(no metrics rows)"

    print("=== Agent 2 — tool output (markdown table) ===")
    print(metrics_table)
    print()

    role_merge = (
        "You are an integrator for an internal analytics briefing. "
        "You receive (A) a short note grounded in documentation about ML/RAG concepts and "
        "(B) a markdown table of quarterly department metrics. "
        "Produce markdown with sections: ## Summary, ## Linking concepts to the metrics, ## Recommendation. "
        "Be brief; do not contradict the table numbers."
    )
    task_merge = (
        f"## (A) Documentation-grounded note\n{out_rag}\n\n"
        f"## (B) Department metrics ({metrics_department})\n{metrics_table}\n"
    )
    out_merge = agent_run(role=role_merge, task=task_merge, model=MODEL, output="text", tools=None)

    print("=== Agent 3 — merged briefing ===")
    print(out_merge)

    return {"retrieval": retrieval, "rag_text": out_rag, "metrics_table": metrics_table, "merged": out_merge}


if __name__ == "__main__":
    run_homework2_system(rag_query=RAG_QUERY, metrics_department="Engineering")
