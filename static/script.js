const recordButton = document.getElementById("record");
const chatbox = document.getElementById("chatbox");

let mediaRecorder;
let audioChunks = [];

recordButton.addEventListener("click", async () => {
    if (!mediaRecorder || mediaRecorder.state === "inactive") {
        startRecording();
    } else {
        stopRecording();
    }
});

async function startRecording() {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    audioChunks = [];

    mediaRecorder.ondataavailable = event => {
        audioChunks.push(event.data);
    };

    mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunks, { type: "audio/wav" });
        sendAudio(audioBlob);
    };

    mediaRecorder.start();
    recordButton.textContent = "⏹️ Arrêter";
}

function stopRecording() {
    if (mediaRecorder) {
        mediaRecorder.stop();
        recordButton.textContent = "🎤 Parler";
    }
}

async function sendAudio(audioBlob) {
    const formData = new FormData();
    formData.append("audio", audioBlob, "audio.wav");

    addMessage("Utilisateur : (Envoi audio...)", "user");

    try {
        const response = await fetch("/predict", {
            method: "POST",
            body: formData
        });

        const data = await response.json();
        addMessage("Assistant : " + data.text, "bot");
    } catch (error) {
        addMessage("Assistant : Erreur de reconnaissance vocale.", "bot");
    }
}

function addMessage(text, sender) {
    const messageDiv = document.createElement("div");
    messageDiv.classList.add("message", sender);
    messageDiv.textContent = text;
    chatbox.appendChild(messageDiv);
    chatbox.scrollTop = chatbox.scrollHeight;
}
