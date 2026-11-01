const input = document.getElementById('message');
const send = document.getElementById('send');
const messages = document.getElementById('messages');
const welcome = document.getElementById('welcome');
const mic = document.getElementById('mic');
const voiceStatus = document.getElementById('voiceStatus');

let recorder = null;
let recordedChunks = [];
let isListening = false;

function add(role, text) {
    if (welcome) welcome.style.display = 'none';

    const row = document.createElement('div');
    row.className = 'msg ' + role;

    const content = document.createElement('div');
    content.className = 'content';
    content.textContent = text;

    row.appendChild(content);
    messages.appendChild(row);

    const chatArea = document.getElementById('chatArea');
    if (chatArea) chatArea.scrollTop = chatArea.scrollHeight;
}

async function speak(text) {
    try {
        const response = await fetch('/api/voice/speak', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({text})
        });

        if (!response.ok) throw new Error('Gnani TTS failed');

        const audioBlob = await response.blob();
        const audioUrl = URL.createObjectURL(audioBlob);
        const audio = new Audio(audioUrl);

        audio.onended = () => URL.revokeObjectURL(audioUrl);
        await audio.play();
    } catch (error) {
        voiceStatus.textContent = 'Voice playback failed. You can still read the reply.';
    }
}

async function sendText(text) {
    text = (text || input.value).trim();
    if (!text) return;

    input.value = '';
    send.disabled = true;
    add('user', text);

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({message: text})
        });

        const data = await response.json();
        if (!response.ok) throw new Error(data.error || 'Chat failed');

        const reply = data.reply || 'No response received.';
        add('assistant', reply);
        await speak(reply);
    } catch (error) {
        add('assistant', 'Unable to connect. Please check the server.');
    } finally {
        send.disabled = false;
        input.focus();
    }
}

async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({audio: true});

        recordedChunks = [];
        recorder = new MediaRecorder(stream);

        recorder.ondataavailable = event => {
            if (event.data.size > 0) recordedChunks.push(event.data);
        };

        recorder.onstop = async () => {
            stream.getTracks().forEach(track => track.stop());

            const audioBlob = new Blob(recordedChunks, {
                type: recorder.mimeType
            });

            const extension = recorder.mimeType.includes('ogg') ? 'ogg' : 'webm';
            const formData = new FormData();
            formData.append('audio', audioBlob, 'recording.' + extension);

            voiceStatus.textContent = 'Sending audio to Gnani...';

            try {
                const response = await fetch('/api/voice/transcribe', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();
                if (!response.ok) throw new Error(data.error || 'Transcription failed');

                voiceStatus.textContent = 'Recognized: ' + data.text;
                await sendText(data.text);
            } catch (error) {
                voiceStatus.textContent = error.message;
            }
        };

        recorder.start();
        isListening = true;
        mic.textContent = '■';
        mic.classList.add('listening');
        voiceStatus.textContent = 'Listening... Click the mic again to stop.';
    } catch (error) {
        voiceStatus.textContent = 'Microphone access failed. Allow microphone permission.';
    }
}

mic.addEventListener('click', () => {
    if (isListening && recorder && recorder.state === 'recording') {
        recorder.stop();
        isListening = false;
        mic.textContent = '🎙';
        mic.classList.remove('listening');
        voiceStatus.textContent = 'Processing your voice...';
    } else {
        startRecording();
    }
});

send.addEventListener('click', () => sendText());

input.addEventListener('keydown', event => {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendText();
    }
});

document.querySelectorAll('[data-prompt]').forEach(button => {
    button.addEventListener('click', () => sendText(button.dataset.prompt));
});

document.getElementById('newChat').addEventListener('click', async () => {
    await fetch('/api/new-chat', {method: 'POST'});
    messages.innerHTML = '';
    if (welcome) welcome.style.display = 'block';
    input.value = '';
    voiceStatus.textContent = 'Gnani voice support ready.';
});

document.getElementById('theme').addEventListener('click', () => {
    document.body.classList.toggle('light');
});

input.addEventListener('input', () => {
    input.style.height = 'auto';
    input.style.height = Math.min(input.scrollHeight, 130) + 'px';
});