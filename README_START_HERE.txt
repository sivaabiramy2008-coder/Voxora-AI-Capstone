VOXORA AI — COMPLETE CAPSTONE PROJECT
====================================

This is the single combined project folder. It includes the Flask chat app, UI, RAG knowledge base, all CSV data, practice questions/conversations, official offline tools, dataset validator, and the original capstone brief/dataset archives under references/.

IMPORTANT VOICE STATUS
----------------------
The browser demo supports microphone input and spoken replies using Chrome's built-in Web Speech APIs where available. The official Gnani STT WebSocket and streamed TTS APIs are NOT configured in this package because official API documentation/credentials were not provided. Do not describe Gnani integration as complete until it is implemented and tested.

RUN ON WINDOWS (PowerShell)
---------------------------
1. Extract this ZIP completely.
2. Open the extracted VoxoraAI_Capstone_Complete folder in File Explorer.
3. Click the address bar, type powershell, and press Enter.
4. Run these commands one at a time:

   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install -r requirements.txt
   Copy-Item .env.example .env
   python validate_dataset.py
   python app.py

5. Open this in Chrome:
   http://127.0.0.1:5000

If PowerShell blocks activation, use Command Prompt instead:
   py -m venv .venv
   .venv\Scripts\activate.bat
   python -m pip install -r requirements.txt
   copy .env.example .env
   python validate_dataset.py
   python app.py

TEST THE CHAT ONE MESSAGE AT A TIME
-----------------------------------
- What is your return policy?
- What does the warranty cover?
- How can I track my order?
- Then send a valid synthetic order ID from data/orders.csv and follow the identity verification instructions.
- I need to contact a human agent
- Then describe the issue in a separate message.

OPTIONAL LLM
------------
Open .env and add your own OPENAI_API_KEY if you want the optional OpenAI response path. The local retrieval fallback works without it. Never upload .env or secrets to GitHub.

CONTENTS
--------
app.py, rag.py                 Flask app and local retrieval
static/, templates/            Web interface and browser voice demo
kb/                            Company policies, FAQs and support docs
data/                          Synthetic CSV tables
practice/                      Questions and multi-turn examples
tools/                         Offline mock order lookup and ticket creation
validate_dataset.py            Dataset checks
references/                     Original capstone brief and source dataset ZIP

NOTES
-----
- All dataset customer/order records are synthetic.
- Order lookup must complete the simulated identity-verification flow before sharing order details.
- Ticket creation is a local CSV simulation, not a real company ticketing system.
- Gnani STT/TTS is pending official provider integration.
- Read README.md and README_PROJECT.md for the detailed project notes.
