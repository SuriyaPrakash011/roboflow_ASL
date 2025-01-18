from flask import Flask, request, jsonify, render_template
import os
import cv2
import requests
from googletrans import Translator
import pyttsx3
import threading

app = Flask(__name__)
API_URL = "https://detect.roboflow.com/american-sign-language-letters-uyjf7/1"
API_KEY = "ZzG3dGxZiRZnI7TcGJnr"
translator = Translator()
engine = pyttsx3.init()

def speak_text(text, lang):
    engine.setProperty('voice', lang)
    engine.say(text)
    engine.runAndWait()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    if "images" not in request.files or "language" not in request.form:
        return jsonify({"error": "Missing files or language"}), 400

    files = request.files.getlist("images")
    language = request.form["language"]
    image_folder = "uploaded_images"
    os.makedirs(image_folder, exist_ok=True)

    predicted_word = ""
    for file in files:
        file_path = os.path.join(image_folder, file.filename)
        file.save(file_path)
        image = cv2.imread(file_path)
        _, buffer = cv2.imencode(".jpg", image)
        response = requests.post(API_URL, params={"api_key": API_KEY}, files={"file": buffer.tobytes()})
        if response.status_code == 200:
            result = response.json()
            if result.get("predictions"):
                predicted_letter = result["predictions"][0]["class"]
                predicted_word += predicted_letter

    translation = translator.translate(predicted_word, dest=language).text
    threading.Thread(target=speak_text, args=(translation, language)).start()

    return jsonify({"predicted_word": predicted_word, "translation": translation})

if __name__ == "__main__":
    app.run(debug=True)
