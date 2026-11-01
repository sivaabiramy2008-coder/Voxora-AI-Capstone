import os, re, sys
from pathlib import Path
from flask import Flask, render_template, request, jsonify, session
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")

from tools import lookup_order, create_ticket
from rag import KnowledgeBase

from gnani.stt import GnaniSTTClient
from gnani.tts import GnaniTTSClient

GNANI_API_KEY = os.getenv("GNANI_API_KEY")

stt_client = GnaniSTTClient(api_key=GNANI_API_KEY) if GNANI_API_KEY else None
tts_client = GnaniTTSClient(api_key=GNANI_API_KEY) if GNANI_API_KEY else None

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "replace-this-for-local-demo")
kb = KnowledgeBase(ROOT / "kb")
REFERENCE_DATE = "20 October 2026"

def get_state():
    return session.get("support_state", {})

def set_state(state):
    session["support_state"] = state

def extract_order_id(text):
    # Dataset order IDs are digits; preserve them as strings.
    m = re.search(r"(?:order\s*(?:id|number|#)?\s*[:#-]?\s*)(\d{6,12})", text, re.I)
    if m:
        return m.group(1)
    m = re.search(r"\b(\d{8})\b", text)
    return m.group(1) if m else None

def is_verification_value(text):
    s = text.strip()
    return bool(re.fullmatch(r"\d{4}|\d{6}", s))

def route_order(message, state):
    low = message.lower()
    # If an order lookup is pending, accept only a standalone 4/6 digit proof.
    pending = state.get("pending_order_id")
    if pending and is_verification_value(message):
        result = lookup_order(pending, verification_value=message.strip())
        attempts = int(state.get("verification_attempts", 0))
        if result.get("verified") and result.get("found"):
            state.pop("pending_order_id", None)
            state.pop("verification_attempts", None)
            set_state(state)
            items = result.get("items", [])
            item_names = []
            for item in items:
                item_names.append(f"{item.get('quantity', 1)} × SKU {item.get('sku', 'unknown')}")
            details = [
                f"Order ID: {result.get('order_id')}",
                f"Status: {result.get('status', 'Not recorded')}",
                f"Order date: {result.get('placed_at', 'Not recorded')}",
                f"Total: ₹{result.get('total_inr', 'Not recorded')}",
            ]
            if result.get("estimated_delivery"):
                details.append(f"Estimated delivery: {result['estimated_delivery']}")
            if result.get("refund_status"):
                details.append(f"Refund status: {result['refund_status']}")
            if item_names:
                details.append("Items: " + ", ".join(item_names))
            return "Verification successful. Here are the available order details:\n" + "\n".join(details)
        if attempts >= 1:
            state.pop("pending_order_id", None)
            state.pop("verification_attempts", None)
            set_state(state)
            return "I couldn't verify those details after the allowed retry. For your privacy, I can't share order information. I can create a support handover if you describe the issue."
        state["verification_attempts"] = attempts + 1
        set_state(state)
        return "That verification value didn't match. You may try once more with either the last 4 digits of the registered phone number OR the 6-digit delivery pincode. Please don't send both."
    if any(x in low for x in ["track my order", "where is my order", "order status", "check my order", "track order"]):
        oid = extract_order_id(message)
        if not oid:
            state["awaiting_order_id"] = True
            set_state(state)
            return "I can help check an order. Please send your order ID first."
        state["pending_order_id"] = oid
        state["verification_attempts"] = 0
        set_state(state)
        lookup_order(oid)  # Unverified call intentionally reveals no private data.
        return f"Before I share any details for order {oid}, I need to verify you. Please provide either the last 4 digits of the registered phone number OR the 6-digit delivery pincode. I won't reveal the expected value."
    if state.get("awaiting_order_id"):
        oid = extract_order_id(message) or (message.strip() if re.fullmatch(r"\d{6,12}", message.strip()) else None)
        if oid:
            state["awaiting_order_id"] = False
            state["pending_order_id"] = oid
            state["verification_attempts"] = 0
            set_state(state)
            lookup_order(oid)
            return f"Before I share any details for order {oid}, please verify with either the last 4 digits of the registered phone number OR the 6-digit delivery pincode."
    return None

def route_ticket(message, state):
    low = message.lower()
    if state.get("awaiting_ticket_details"):
        if len(message.strip()) < 20:
            return "Please describe the issue in a little more detail so I can prepare a useful handover."
        result = create_ticket(
            summary=f"Customer requested support handover. Issue reported: {message.strip()}",
            order_id=state.get("ticket_order_id"),
            reason=state.get("ticket_reason", "general_support"),
            intent=state.get("ticket_reason", "general_support"),
        )
        state.pop("awaiting_ticket_details", None)
        state.pop("ticket_order_id", None)
        state.pop("ticket_reason", None)
        set_state(state)
        if result.get("created") is True:
            return f"Your support handover has been created. Ticket ID: {result['ticket_id']}. A human support colleague can review the issue."
        return "I couldn't create the support handover just now. Please try again with a clearer description."
    if any(x in low for x in ["create a ticket", "raise a ticket", "contact human", "talk to support", "human agent", "escalate"]):
        state["awaiting_ticket_details"] = True
        state["ticket_reason"] = "customer_requested_handover"
        set_state(state)
        return "I can prepare a support handover. Please describe the issue and include the order ID if relevant. Don't include your password or payment credentials."
    return None

def answer(message, history):
    state = get_state()
    tool_reply = route_order(message, state)
    if tool_reply:
        return tool_reply
    tool_reply = route_ticket(message, state)
    if tool_reply:
        return tool_reply

    docs = kb.search(message, top_k=4)
    if not docs:
        return "I couldn't find a reliable answer in the current ZentroMart documents. I don't want to guess. You can rephrase your question or ask me to prepare a support handover."

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    context = "\n\n".join(f"Source: {d['source']} | Section: {d.get('section_id') or 'not identified'}\n{d['text']}" for d in docs)
    if api_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            prior = "\n".join(
                f"{'Customer' if m.get('role') == 'user' else 'Voxora'}: {m.get('content','')}"
                for m in history[-8:]
            )
            response = client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                temperature=0.15,
                messages=[
                    {"role":"system","content":
                     f"You are Voxora AI, ZentroMart's customer support assistant. Dataset reference date is {REFERENCE_DATE}; use it for date-dependent answers. "
                     "Answer only from supplied retrieved documents. Prioritize current effective policies; ignore superseded policies and marketing copy if they conflict with authoritative policy. "
                     "Never invent facts or claim actions happened unless the connected tool confirmed them. If evidence is missing or contradictory, say so and offer human handover. "
                     "Never reveal verification secrets. Keep customer answers clear and concise."},
                    {"role":"user","content":f"Retrieved context:\n{context}\n\nRecent conversation:\n{prior}\n\nCustomer message:\n{message}\n\nGive a grounded answer and include source section IDs when available."}
                ]
            )
            answer_text = response.choices[0].message.content
            if answer_text:
                return answer_text
        except Exception:
            pass

    snippets = "\n\n".join(f"• {d['text']}" for d in docs[:3])
    return "I found these relevant notes in the ZentroMart knowledge base:\n\n" + snippets + "\n\nI can give a more conversational answer when an LLM API key is configured. Please verify policy details against the cited source sections."

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    payload = request.get_json(silent=True) or {}
    message = str(payload.get("message", "")).strip()
    if not message:
        return jsonify({"error": "Please enter a message."}), 400
    history = session.get("history", [])
    reply = answer(message, history)
    history.extend([{"role":"user","content":message},{"role":"assistant","content":reply}])
    session["history"] = history[-16:]
    return jsonify({"reply": reply})

@app.route("/api/new-chat", methods=["POST"])
def new_chat():
    session.clear()
    return jsonify({"ok": True})

@app.route("/api/health")
def health():
    return jsonify({"status":"ok", "indexed_chunks":len(kb.chunks), "reference_date":REFERENCE_DATE,
                    "voice":"not configured until official Gnani WebSocket details are added"})


@app.route("/api/voice/transcribe", methods=["POST"])
def transcribe():
    if not stt_client:
        return jsonify({"error": "Gnani API key is not configured."}), 503

    audio = request.files.get("audio")
    if not audio:
        return jsonify({"error": "No audio file received."}), 400

    audio_bytes = audio.read()
    if not audio_bytes:
        return jsonify({"error": "Audio file is empty."}), 400

    try:
        result = stt_client.transcribe_bytes(
            audio_bytes,
            filename=audio.filename or "audio.wav",
            language_code="en-IN"
        )

        transcript = (
            result.get("text")
            or result.get("transcript")
            or result.get("transcription")
            or ""
        ).strip()

        if not transcript:
            return jsonify({
                "error": "No speech detected.",
                "provider_response": result
            }), 422

        return jsonify({"text": transcript})

    except Exception:
        app.logger.exception("Gnani STT failed")
        return jsonify({"error": "Speech recognition failed. Please try again."}), 502


@app.route("/api/voice/speak", methods=["POST"])
def speak():
    if not tts_client:
        return jsonify({"error": "Gnani API key is not configured."}), 503

    payload = request.get_json(silent=True) or {}
    text = str(payload.get("text", "")).strip()

    if not text:
        return jsonify({"error": "Text is required."}), 400

    try:
        audio_bytes = tts_client.synthesize(
            text,
            voice="Kaveri",
            model="timbre-v2.5",
            language="en-IN"
        )

        from flask import Response
        return Response(
            audio_bytes,
            mimetype="audio/wav",
            headers={"Content-Disposition": "inline; filename=voxora-reply.wav"}
        )

    except Exception:
        app.logger.exception("Gnani TTS failed")
        return jsonify({"error": "Speech generation failed. Please try again."}), 502


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
