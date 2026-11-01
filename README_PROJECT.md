# Voxora AI — Dataset-integrated capstone starter

This project uses the uploaded `Capstone_Project_Dataset_FTTT_2026` synthetic dataset.

## Run on Windows PowerShell
Open PowerShell inside this `VoxoraAI_Capstone` folder and run one line at a time:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python validate_dataset.py
python app.py
```

Open `http://127.0.0.1:5000`.

## Test ideas
- `What is the return policy?`
- `What does the warranty cover?`
- `How can I track my order?`
- Then provide an order ID from the synthetic dataset and follow the identity-verification prompt. Use only the matching synthetic phone suffix or delivery pincode.
- `I need to contact a human agent` then describe the issue in the next message.

## What is integrated
- All provided `kb/*.md` company documents
- All supplied CSV data, practice questions/conversations and dataset validation script
- The dataset's official offline mock tools for identity-checked order lookup and ticket creation
- Local section-oriented keyword retrieval, with an optional LLM via `OPENAI_API_KEY`
- Responsive Voxora AI chat interface, new chat and theme toggle
- Browser microphone input and spoken replies using Chrome Web Speech APIs (demo fallback; not Gnani STT/TTS)

## Important limits before submission
- The included RAG is a simple local retrieval baseline, not a vector database. Validate answers against `practice/questions.csv` and improve retrieval as needed.
- The microphone and spoken response UI now work through Chrome browser speech services as a demo fallback. This is NOT the required Gnani STT/TTS integration. To satisfy the Gnani requirement, obtain credentials from Gnani and replace the browser fallback with the official Gnani STT WebSocket and TTS streaming APIs. Never place API keys in frontend JavaScript or commit them to GitHub.
- Test the conversation agent against `practice/conversations.csv`, especially verification retries, ticket creation, policy conflicts and unknown answers.
- The mock identity-check tool is synthetic and not secure enough for real customers.
- Use the dataset's fixed reference date: 20 October 2026 for date-dependent logic.
- Do not commit `.env` or secrets to GitHub.
