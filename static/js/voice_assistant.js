/* ==========================================================================
   ReVahan AI Voice Assistant - Client Controller
   Web Speech API (SpeechRecognition + SpeechSynthesis) & Conversational ML Interface
   ========================================================================== */

document.addEventListener('DOMContentLoaded', function () {
    initVoiceAssistant();
});

function initVoiceAssistant() {
    const voiceFab = document.getElementById('voiceFab');
    const voicePanel = document.getElementById('voicePanel');
    const voicePanelOverlay = document.getElementById('voicePanelOverlay');
    const voiceCloseBtn = document.getElementById('voiceCloseBtn');
    const voiceMuteBtn = document.getElementById('voiceMuteBtn');
    const voiceMuteIcon = document.getElementById('voiceMuteIcon');
    const voiceMicBtn = document.getElementById('voiceMicBtn');
    const voiceMicIcon = document.getElementById('voiceMicIcon');
    const voiceTextInput = document.getElementById('voiceTextInput');
    const voiceSendBtn = document.getElementById('voiceSendBtn');
    const voiceChatMessages = document.getElementById('voiceChatMessages');
    const voiceStatusText = document.getElementById('voiceStatusText');
    const voiceWaveform = document.getElementById('voiceWaveform');
    const quickChips = document.querySelectorAll('.voice-chip');

    if (!voiceFab || !voicePanel) return;

    let isListening = false;
    let isSpeaking = false;
    let isMuted = localStorage.getItem('revahan_voice_muted') === 'true';
    let recognition = null;
    let speechSynth = window.speechSynthesis;

    // Apply mute state
    updateMuteUI();

    // Check Web Speech Recognition support
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-IN'; // Indian English dialect

        recognition.onstart = function () {
            isListening = true;
            voiceMicBtn.classList.add('recording');
            voiceWaveform.classList.add('active');
            voiceStatusText.textContent = "Listening... Speak clearly now";
            voiceStatusText.classList.add('text-warning');
        };

        recognition.onresult = function (event) {
            const transcript = event.results[0][0].transcript;
            console.log("Transcribed speech:", transcript);
            handleUserQuery(transcript);
        };

        recognition.onerror = function (event) {
            console.warn("Speech recognition error:", event.error);
            stopListening();
            if (event.error === 'not-allowed') {
                voiceStatusText.textContent = "Microphone access blocked. Please allow permission or type below.";
            } else {
                voiceStatusText.textContent = "Ready. Tap microphone to speak.";
            }
        };

        recognition.onend = function () {
            stopListening();
        };
    } else {
        voiceStatusText.textContent = "Voice recognition not supported in this browser. You can type below!";
    }

    // Toggle Panel Open/Close
    voiceFab.addEventListener('click', toggleVoicePanel);
    voiceCloseBtn.addEventListener('click', closeVoicePanel);
    voicePanelOverlay.addEventListener('click', closeVoicePanel);

    function toggleVoicePanel() {
        const isOpen = voicePanel.classList.contains('active');
        if (isOpen) {
            closeVoicePanel();
        } else {
            openVoicePanel();
        }
    }

    function openVoicePanel() {
        voicePanel.classList.add('active');
        voicePanelOverlay.classList.add('active');
        voiceTextInput.focus();
        scrollToBottom();
    }

    function closeVoicePanel() {
        voicePanel.classList.remove('active');
        voicePanelOverlay.classList.remove('active');
        stopListening();
        stopSpeaking();
    }

    // Toggle Mute
    voiceMuteBtn.addEventListener('click', function () {
        isMuted = !isMuted;
        localStorage.setItem('revahan_voice_muted', isMuted);
        updateMuteUI();
        if (isMuted) stopSpeaking();
    });

    function updateMuteUI() {
        if (!voiceMuteIcon) return;
        if (isMuted) {
            voiceMuteIcon.className = 'bi bi-volume-mute-fill text-danger';
            voiceMuteBtn.title = "Unmute Voice Speech";
        } else {
            voiceMuteIcon.className = 'bi bi-volume-up-fill text-success';
            voiceMuteBtn.title = "Mute Voice Speech";
        }
    }

    // Microphone Toggle
    voiceMicBtn.addEventListener('click', function () {
        if (!recognition) {
            alert("Speech recognition is not supported in this browser. Please use Google Chrome or Edge.");
            return;
        }
        if (isListening) {
            stopListening();
        } else {
            startListening();
        }
    });

    function startListening() {
        stopSpeaking();
        try {
            recognition.start();
        } catch (e) {
            console.error("Recognition start error:", e);
        }
    }

    function stopListening() {
        isListening = false;
        voiceMicBtn.classList.remove('recording');
        if (!isSpeaking) {
            voiceWaveform.classList.remove('active');
            voiceStatusText.textContent = "Ready. Tap microphone to speak or type.";
            voiceStatusText.classList.remove('text-warning');
        }
    }

    // Text Input Submit
    voiceSendBtn.addEventListener('click', sendTextMessage);
    voiceTextInput.addEventListener('keypress', function (e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            sendTextMessage();
        }
    });

    function sendTextMessage() {
        const text = voiceTextInput.value.trim();
        if (!text) return;
        voiceTextInput.value = '';
        handleUserQuery(text);
    }

    // Quick Chips click
    quickChips.forEach(chip => {
        chip.addEventListener('click', function () {
            const query = this.getAttribute('data-query');
            if (query) {
                handleUserQuery(query);
            }
        });
    });

    // Core Handler: Process User Query via Backend API
    function handleUserQuery(query) {
        stopListening();
        appendUserMessage(query);

        voiceStatusText.textContent = "Thinking & computing Machine Learning valuation...";
        voiceWaveform.classList.add('active');

        // Call Flask Backend
        fetch('/api/voice-assistant', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: query })
        })
        .then(response => response.json())
        .then(data => {
            voiceStatusText.textContent = "Ready. Ask another question or speak.";
            voiceStatusText.classList.remove('text-warning');
            voiceWaveform.classList.remove('active');

            appendBotMessage(data);

            // Speak response if not muted
            if (!isMuted && data.spoken_text) {
                speakText(data.spoken_text);
            }
        })
        .catch(err => {
            console.error("Voice assistant API error:", err);
            voiceStatusText.textContent = "Communication error. Please check server.";
            voiceWaveform.classList.remove('active');
            appendBotMessage({
                text: "⚠️ Sorry, I could not connect to the valuation backend. Please make sure your server is running.",
                action: 'error'
            });
        });
    }

    // Text-to-Speech Engine
    function speakText(text) {
        if (!speechSynth || isMuted) return;

        speechSynth.cancel(); // Cancel any ongoing speech
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 1.0;
        utterance.pitch = 1.1; // Smooth natural feminine pitch
        utterance.lang = 'en-IN';

        // Select a natural female English voice if available
        const voices = speechSynth.getVoices();
        const femaleVoice = voices.find(v => 
            (v.name.toLowerCase().includes('female') || 
             v.name.toLowerCase().includes('zira') || 
             v.name.toLowerCase().includes('heera') || 
             v.name.toLowerCase().includes('samantha') || 
             v.name.toLowerCase().includes('karen') ||
             v.name.toLowerCase().includes('veena') ||
             v.name.toLowerCase().includes('priya') ||
             v.name.toLowerCase().includes('neerja') ||
             v.name.toLowerCase().includes('aria')) &&
            (v.lang.startsWith('en'))
        );
        const fallbackVoice = voices.find(v => v.lang.includes('en-IN') || v.lang.includes('en-GB') || v.lang.startsWith('en'));
        if (femaleVoice) {
            utterance.voice = femaleVoice;
        } else if (fallbackVoice) {
            utterance.voice = fallbackVoice;
        }

        utterance.onstart = function () {
            isSpeaking = true;
            voiceWaveform.classList.add('active');
            voiceStatusText.textContent = "Speaking...";
        };

        utterance.onend = function () {
            stopSpeaking();
        };

        utterance.onerror = function () {
            stopSpeaking();
        };

        speechSynth.speak(utterance);
    }

    function stopSpeaking() {
        if (speechSynth) speechSynth.cancel();
        isSpeaking = false;
        if (!isListening) {
            voiceWaveform.classList.remove('active');
            voiceStatusText.textContent = "Ready. Tap microphone to speak.";
        }
    }

    // Append Messages to Dialogue Box
    function appendUserMessage(text) {
        const div = document.createElement('div');
        div.className = 'voice-bubble user';
        div.innerHTML = `<div class="bubble-content">${escapeHTML(text)}</div>`;
        voiceChatMessages.appendChild(div);
        scrollToBottom();
    }

    function appendBotMessage(data) {
        const div = document.createElement('div');
        div.className = 'voice-bubble bot';

        let html = '';
        if (data.action === 'prediction') {
            html += `
                <div class="bubble-content">
                    <div class="d-flex align-items-center gap-1 mb-2">
                        <span class="badge bg-primary px-2 py-1" style="font-size: 0.72rem;">ML VALUATION #${data.prediction_id}</span>
                        <span class="badge bg-dark border border-warning text-warning" style="font-size: 0.72rem;">${escapeHTML(data.year)} ${escapeHTML(data.brand)}</span>
                    </div>
                    <div class="voice-price-callout">
                        <small class="text-secondary d-block" style="font-size: 0.75rem;">ESTIMATED FAIR RESALE VALUE</small>
                        <h4 class="fw-bold mb-0 text-warning">₹ ${escapeHTML(data.price_formatted)}</h4>
                        <small class="text-info fw-bold">~ ${escapeHTML(data.price_lakhs)}</small>
                    </div>
                    <div class="p-2 rounded mt-2 mb-2 bg-surface border border-secondary border-opacity-25" style="font-size: 0.8rem;">
                        <i class="bi bi-arrows-expand me-1 text-warning"></i> Range: <strong>₹ ${escapeHTML(data.price_min)}</strong> &ndash; <strong>₹ ${escapeHTML(data.price_max)}</strong>
                    </div>
                    <div class="d-flex gap-2 mt-2">
                        <a href="${data.result_url}" class="btn btn-sm btn-primary-custom flex-fill py-1" style="font-size: 0.8rem;">
                            <i class="bi bi-eye-fill me-1"></i> Full Result
                        </a>
                        <a href="${data.report_url}" class="btn btn-sm btn-outline-custom flex-fill py-1" style="font-size: 0.8rem;">
                            <i class="bi bi-file-earmark-pdf-fill me-1"></i> PDF Report
                        </a>
                    </div>
                </div>
            `;
        } else {
            // General text with markdown-style linebreaks
            const formattedText = escapeHTML(data.text)
                .replace(/\n/g, '<br>')
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                .replace(/\*(.*?)\*/g, '<em>$1</em>');
            html = `<div class="bubble-content">${formattedText}</div>`;
        }

        div.innerHTML = html;
        voiceChatMessages.appendChild(div);
        scrollToBottom();
    }

    function scrollToBottom() {
        voiceChatMessages.scrollTop = voiceChatMessages.scrollHeight;
    }

    function escapeHTML(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }
}
