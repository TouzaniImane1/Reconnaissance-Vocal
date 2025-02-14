import os
import subprocess
import webbrowser
import json
from flask import Flask, request, jsonify, render_template
import numpy as np
import librosa
import soundfile as sf
from sklearn.mixture import GaussianMixture
import speech_recognition as sr

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_FOLDER = os.path.join(BASE_DIR, "static")

if not os.path.exists(AUDIO_FOLDER):
    os.makedirs(AUDIO_FOLDER)

# Liste des commandes reconnues
commandes = {
    "ouvre youtube": lambda: webbrowser.open("https://www.youtube.com"),
    "recherche": lambda query: webbrowser.open(f"https://www.google.com/search?q={query}"),
    "ouvre gmail": lambda: webbrowser.open("https://mail.google.com"),
    "ouvre calculatrice": lambda: subprocess.run("calc.exe", shell=True),
}

def convert_to_wav(input_path, output_path):
    """ Convertit un fichier audio en WAV """
    try:
        subprocess.run([
            "ffmpeg", "-y", "-i", input_path, 
            "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", output_path
        ], check=True)
        return output_path
    except subprocess.CalledProcessError:
        return None

def recognize_speech(audio_path):
    """ Transcrit la parole en texte """
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)

    try:
        texte = recognizer.recognize_google(audio, language="fr-FR").lower()
        print(f"Commande reconnue : {texte}")
        return texte
    except sr.UnknownValueError:
        return "Je n'ai pas compris"
    except sr.RequestError:
        return "Erreur avec le service de reconnaissance"

def execute_command(texte):
    """ Exécute une commande selon la parole reconnue """
    for cmd, action in commandes.items():
        if texte.startswith(cmd):
            if cmd == "recherche":
                query = texte.replace("recherche", "").strip()
                action(query)  # Recherche sur Google
            else:
                action()  # Ouvre une application/site web
            return f"{cmd}"

    return "Commande non reconnue"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    if "audio" not in request.files:
        return jsonify({"error": "Aucun fichier audio reçu"}), 400

    audio_file = request.files["audio"]
    file_path = os.path.join(AUDIO_FOLDER, "audio.wav")
    audio_file.save(file_path)

    fixed_audio_path = os.path.join(AUDIO_FOLDER, "audio_fixed.wav")
    if convert_to_wav(file_path, fixed_audio_path):
        texte_reconnu = recognize_speech(fixed_audio_path)
        resultat = execute_command(texte_reconnu)
    else:
        resultat = "Erreur dans la conversion audio"

    return jsonify({"text": texte_reconnu, "result": resultat})

if __name__ == "__main__":
    app.run(debug=True)
