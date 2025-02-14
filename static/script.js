document.addEventListener("DOMContentLoaded", function() {
    const recordButton = document.getElementById("record");
    const chatBox = document.getElementById("chat-box");

    function addMessage(text, sender) {
        const messageDiv = document.createElement("div");
        messageDiv.classList.add("message", sender);
        messageDiv.textContent = text;
        chatBox.appendChild(messageDiv);
        chatBox.scrollTop = chatBox.scrollHeight; // Auto-scroll
    }

    recordButton.addEventListener("click", function() {
        let constraints = { audio: true };
        navigator.mediaDevices.getUserMedia(constraints).then(function(stream) {
            const mediaRecorder = new MediaRecorder(stream);
            let chunks = [];

            mediaRecorder.ondataavailable = function(event) {
                chunks.push(event.data);
            };

            mediaRecorder.onstop = function() {
                addMessage("Utilisateur : (Envoi audio...)", "user");

                const audioBlob = new Blob(chunks, { type: "audio/wav" });
                const formData = new FormData();
                formData.append("audio", audioBlob, "recorded_audio.wav");

                fetch("/predict", {
                    method: "POST",
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    addMessage(`Assistant : ${data.text}`, "assistant");
                    addMessage(`Exécution : ${data.result}`, "assistant");
                })
                .catch(error => console.error("Erreur :", error));
            };

            mediaRecorder.start();
            setTimeout(() => {
                mediaRecorder.stop();
            }, 4000);
        }).catch(function(error) {
            console.error("Erreur d'accès au micro :", error);
        });
    });
});
