from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import speech_recognition as sr
from googletrans import Translator
from gtts import gTTS
import os

app = Flask(__name__)
cors = CORS(app)

# Supported languages
supported_languages = ['en', 'te', 'hi']
translator = Translator()

# Function to convert text to speech and save it as an audio file
def save_speech(text, language, filename="response.mp3"):
    language_codes = {
        'en': 'en',
        'te': 'te',
        'hi': 'hi'
    }
    if language not in language_codes:
        language = 'en'

    tts = gTTS(text=text, lang=language_codes[language])
    tts.save(filename)
    return filename

@app.route('/getResponse', methods=['GET', 'OPTIONS'])
def getResponse():
    if request.method == 'OPTIONS':
        return jsonify({'message': 'Preflight request successful'}), 200

    try:
        language = request.args.get('language', 'en')
        page = request.args.get('page')

        if language not in supported_languages:
            return jsonify({"error": "Unsupported language"}), 400

        # Map page names to responses
        page_responses = {
            'home': 'Welcome to the Dashboard.',
            'employees': 'Welcome to the Employees section.',
            'customers': 'Welcome to the Customers section.',
            'tasks': 'Welcome to the Task Management section.',
            'babyDatabase': 'Welcome to the Baby Database section.',
            'work-day': 'Welcome to the Work Day Calculation section.',
            'leave': 'Welcome to the Leave Management section.',
            'reports': 'Welcome to the Reports section.',
            'salaries': 'Welcome to the Salaries section.',
            'expenses': 'Welcome to the Expenses section.',
            'customize': 'Welcome to the Customization section.',
            'settings': 'Welcome to the Settings section.'
        }
        
        response_text = page_responses.get(page, 'Welcome to the application.')

        try:
            response_translated = translator.translate(response_text, src='en', dest=language).text
        except Exception as e:
            print(f"Translation error: {e}")
            response_translated = response_text

        audio_file = save_speech(response_translated, language)
        return send_file(audio_file, mimetype="audio/mp3")

    except Exception as e:
        print("Error is:", e)
        return jsonify({"error": str(e)}), 500

@app.route('/callRoutes', methods=['GET'])
def callRoutes():
    try:
        language = request.args.get('language', 'en')

        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening...")
            audio = recognizer.listen(source)

        try:
            # Recognize speech based on language selection
            transcript = recognizer.recognize_google(audio, language=f"{language}-IN")

            # Translate the transcript if not in English
            if language != 'en':
                transcript = translator.translate(transcript, src=language, dest='en').text

            # Return the transcribed voice text directly
            return jsonify({"transcript": transcript})

        except sr.UnknownValueError:
            return jsonify({"error": "Could not understand audio"}), 500
        except sr.RequestError as e:
            return jsonify({"error": f"Speech recognition error: {e}"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500
