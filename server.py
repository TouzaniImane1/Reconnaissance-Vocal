import os
import subprocess
from flask import Flask, request, jsonify, render_template
import numpy as np
import librosa
import soundfile as sf
from sklearn.mixture import GaussianMixture

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_FOLDER = os.path.join(BASE_DIR, "static")

# Assure-toi que le dossier 'static' existe
if not os.path.exists(AUDIO_FOLDER):
    os.makedirs(AUDIO_FOLDER)
from pydub import AudioSegment

def convert_to_wav_pydub(input_path, output_path):
    """ Convertit un fichier audio en WAV avec pydub """
    try:
        audio = AudioSegment.from_file(input_path)
        audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)  # 16kHz, mono, 16-bit
        audio.export(output_path, format="wav")
        print(f"Conversion réussie avec pydub : {input_path} → {output_path}")
        return output_path
    except Exception as e:
        print(f"Erreur de conversion avec pydub : {e}")
        return None

def convert_to_wav(input_path, output_path):
    """ Convertit un fichier audio en WAV """
    try:
        subprocess.run([
            "ffmpeg", "-y", "-i", input_path, 
            "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", output_path
        ], check=True)
        print(f"Conversion réussie : {input_path} → {output_path}")
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de la conversion de {input_path} : {e}")
        return None


def recognize_speech(audio_path):
    try:
        # Tentative de lecture avec soundfile
        try:
            y, sr = sf.read(audio_path)
        except RuntimeError:
            print("Soundfile a échoué, tentative avec librosa...")
            y, sr = librosa.load(audio_path, sr=None)

        if len(y) == 0:
            raise ValueError("Le fichier audio est vide ou corrompu")

        # Extraction des MFCC
        features = np.mean(librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13).T, axis=0)

        # Modèle GMM fictif
        model = GaussianMixture(n_components=3, covariance_type='diag')
        model.fit(features.reshape(-1, 1))

        return "Commande reconnue (exemple)"
    
    except Exception as e:
        print(f"Erreur de traitement audio : {str(e)}")
        return "Erreur dans l'enregistrement audio"

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
    file_path = "static/audio_fixed.wav"



    if os.path.exists(file_path):
        print(f"Fichier audio reçu et sauvegardé : {file_path}")

        # Vérifier et convertir si nécessaire
        fixed_audio_path = os.path.join(AUDIO_FOLDER, "audio_fixed.wav")
        if convert_to_wav(file_path, fixed_audio_path):
            result_text = recognize_speech(fixed_audio_path)
        else:
            result_text = "Erreur dans la conversion audio"

    else:
        print(f"Erreur : le fichier n'a pas été sauvegardé à {file_path}")
        result_text = "Erreur dans l'enregistrement audio"

    return jsonify({"text": result_text})

if __name__ == "__main__":
    app.run(debug=True)
