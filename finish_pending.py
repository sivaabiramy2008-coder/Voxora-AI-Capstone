import os, sys, json, csv, subprocess, traceback
from pathlib import Path

ROOT = Path.cwd()
for folder in ["report", "sample_outputs", "audio_samples", "demo"]:
    (ROOT / folder).mkdir(exist_ok=True)

results = []

def record(name, ok, detail=""):
    status = "PASS" if ok else "PENDING/FAIL"
    results.append(f"{name}: {status} {detail}")
    print(results[-1])

print("\n=== VOXORA AI FINAL CHECK ===")

try:
    p = subprocess.run([sys.executable, "validate_dataset.py"], capture_output=True, text=True)
    record("Dataset validation", p.returncode == 0, (p.stdout + p.stderr)[-1200:])
except Exception as e:
    record("Dataset validation", False, str(e))

try:
    from rag import KnowledgeBase
    from tools.tools import lookup_order, create_ticket
    import app
    record("Core imports", True)
except Exception:
    record("Core imports", False, traceback.format_exc())
    raise SystemExit(1)

try:
    client = app.app.test_client()
    r = client.get("/api/health")
    record("Health API", r.status_code == 200, f"HTTP {r.status_code} {r.get_data(as_text=True)[:300]}")
    r = client.post("/api/chat", json={"message":"How can I track my order?"})
    record("Chat API", r.status_code == 200, f"HTTP {r.status_code}")
    (ROOT/"sample_outputs"/"chat_test.txt").write_text(r.get_data(as_text=True), encoding="utf-8")
except Exception:
    record("Flask API tests", False, traceback.format_exc())

try:
    kb = KnowledgeBase("kb")
    queries = [
        "What is the return window for electronics?",
        "What is the return window for clothing ordered during the festive sale?",
        "How do I track my order?",
        "What should I do if my item is damaged?",
        "How are refunds processed?"
    ]
    evaluation = []
    for q in queries:
        docs = kb.search(q, top_k=3)
        evaluation.append({"question":q, "retrieved":[{"source":d.get("source"),"title":d.get("title"),"section_id":d.get("section_id")} for d in docs]})
        print("RAG:", q, "->", len(docs), "chunks")
    (ROOT/"sample_outputs"/"rag_evaluation.json").write_text(json.dumps(evaluation, indent=2), encoding="utf-8")
    record("RAG smoke test", all(x["retrieved"] for x in evaluation))
except Exception:
    record("RAG smoke test", False, traceback.format_exc())

try:
    with open(ROOT/"practice"/"questions.csv", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fields = reader.fieldnames or []
    record("Practice dataset read", len(rows) > 0, f"{len(rows)} rows; columns={fields}")
except Exception as e:
    record("Practice dataset read", False, str(e))

try:
    audio_files = list((ROOT/"audio_samples").glob("*"))
    audio_files = [x for x in audio_files if x.is_file()]
    record("Batch audio", False, f"{len(audio_files)} audio files found; processing not verified")
except Exception as e:
    record("Batch audio", False, str(e))

try:
    (ROOT/"demo"/"demo_script.txt").write_text(
"""VOXORA AI - 2 MINUTE DEMO

1. Introduce Voxora AI as a customer-support assistant for ZentroMart.
2. Ask: How can I track my order? Show the knowledge-base response.
3. Ask about the returns policy and show retrieved policy information.
4. Demonstrate order lookup. Explain that order details require customer verification.
5. Demonstrate support ticket creation if available in the interface.
6. Show the health endpoint and project structure.
7. State limitations honestly: Gnani voice requires a valid API key; LLM-based conversational responses require configured credentials.
""", encoding="utf-8")
    record("Demo script", True, "Created demo/demo_script.txt")
except Exception as e:
    record("Demo script", False, str(e))

report = """# Voxora AI - Capstone Project Report

## Overview
Voxora AI is a customer-support assistant prototype for the fictional ZentroMart store. It combines a Flask web application, a Markdown knowledge base, retrieval-based responses, order lookup and support-ticket utilities.

## Main capabilities
- Retrieval of relevant customer-support knowledge-base sections.
- Order lookup with verification checks.
- Support-ticket creation utility.
- Flask API endpoints for chat, health checks and voice workflows.
- Practice-question dataset included with the project.

## Technology
Python, Flask, retrieval-based search, CSV datasets, Markdown knowledge documents, and optional Gnani speech services.

## Testing and limitations
See `sample_outputs/final_test_results.txt` for the checks actually run. Gnani voice functionality must be considered unverified unless a valid API key passes a live request. LLM responses require configured credentials. Retrieval quality should be reviewed against the saved evaluation questions.

## Conclusion
Voxora AI demonstrates a modular customer-support workflow with knowledge retrieval and verification-aware support utilities. Further work includes improving retrieval relevance, validating live speech services, and completing automated evaluation.
"""
(ROOT/"report"/"Voxora_AI_Final_Report_DRAFT.md").write_text(report, encoding="utf-8")

(ROOT/"sample_outputs"/"final_test_results.txt").write_text(
"VOXORA AI - FINAL CHECK RESULTS\n01 November 2026\n\n" + "\n".join(results) +
"\n\nNote: PASS means the individual check ran successfully. Pending/Fail items are not claimed as completed.\n",
encoding="utf-8")

print("\nCreated report draft, demo script and test results.")
