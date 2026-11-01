import csv, json
from pathlib import Path
from app import app

with open("practice/questions.csv", encoding="utf-8-sig", newline="") as f:
    rows = list(csv.DictReader(f))

client = app.test_client()
results = []

for i, row in enumerate(rows, 1):
    question = row.get("question", "").strip()
    if not question:
        continue
    response = client.post("/api/chat", json={"message": question})
    results.append({
        "id": row.get("id"),
        "question": question,
        "http_status": response.status_code,
        "response": response.get_json(silent=True) or response.get_data(as_text=True)
    })
    print(f"{i}/{len(rows)} - HTTP {response.status_code}")

Path("sample_outputs/practice_evaluation.json").write_text(
    json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8"
)
print(f"\nSaved {len(results)} question responses. This is response testing, not accuracy scoring.")
