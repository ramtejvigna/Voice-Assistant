from flask import Flask, request, jsonify
from flask_cors import CORS
import pygame
import speech_recognition as sr
from googletrans import Translator
from gtts import gTTS
import os
import time
import google.generativeai as genai

genai.configure(api_key="AIzaSyCW3Zz4xkIiaj7YIFpml-KNK58KsJyekaA")
model = genai.GenerativeModel('gemini-1.5-flash')

app = Flask(__name__)

# Update CORS configuration to allow specific origins and handle preflight
cors = CORS(app)

# Supported languages
supported_languages = ['en', 'te', 'hi']
translator = Translator()

# Function to convert text to speech and play it
def speak(text, language):
    language_codes = {
        'en': 'en',  # English
        'te': 'te',  # Telugu
        'hi': 'hi'   # Hindi
    }

    if language not in language_codes:
        language = 'en'  # Fallback to English if language is not supported

    tts = gTTS(text=text, lang=language_codes[language])
    audio_file = "temp.mp3"
    tts.save(audio_file)

    pygame.mixer.init()
    pygame.mixer.music.load(audio_file)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        time.sleep(0.1)

    pygame.mixer.music.stop()
    pygame.mixer.quit()

@app.route('/getResponse', methods=['GET', 'OPTIONS'])
def getResponse():
    if request.method == 'OPTIONS':
        # Handle preflight request by returning OK status for CORS
        return jsonify({'message': 'Preflight request successful'}), 200

    try:
        language = request.args.get('language', 'en')
        page = request.args.get('page')

        if language not in supported_languages:
            return jsonify({"error": "Unsupported language"}), 400

        if page == 'home':
            response_text = 'Welcome to the Dashboard.'
        elif page == 'employees':
            response_text = 'Welcome to the Employees section.'
        elif page == 'customers':
            response_text = 'Welcome to the Customers section.'
        elif page == 'tasks':
            response_text = 'Welcome to the Task Management section.'
        elif page == 'babyDatabase':
            response_text = 'Welcome to the Baby Database section.'
        elif page == 'work-day':
            response_text = 'Welcome to the Work Day Calculation section.'
        elif page == 'leave':
            response_text = 'Welcome to the Leave Management section.'
        elif page == 'reports':
            response_text = 'Welcome to the Reports section.'
        elif page == 'salaries':
            response_text = 'Welcome to the Salaries section.'
        elif page == 'expenses':
            response_text = 'Welcome to the Expenses section.'
        elif page == 'customize':
            response_text = 'Welcome to the Customization section.'
        elif page == 'settings':
            response_text = 'Welcome to the Settings section.'
        else:
            response_text = 'Welcome to the application.'

        try:
            response_translated = translator.translate(response_text, src='en', dest=language)
            if response_translated and response_translated.text:
                response_translated = response_translated.text
            else:
                response_translated = response_text
        except Exception as e:
            print(f"Translation error: {e}")
            response_translated = response_text

        speak(response_translated, language)

        return jsonify({
            'message': response_translated
        }), 200

    except Exception as e:
        print("Error is:", e)
        return jsonify({"error": str(e)}), 500

@app.route('/callRoutes', methods=['GET'])
def callRoutes():
    try:
        # Get the language from the request (default to English)
        language = request.args.get('language', 'en')

        # Use the speech_recognition library to capture and convert speech to text
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening...")
            audio = recognizer.listen(source)

        try:
            # Recognize speech (convert speech to text)
            if language == 'en':
                transcript = recognizer.recognize_google(audio, language='en-US')
            elif language == 'te':
                transcript = recognizer.recognize_google(audio, language='te-IN')
            elif language == 'hi':
                transcript = recognizer.recognize_google(audio, language='hi-IN')
            else:
                return jsonify({"error": "Unsupported language"}), 400

            # Translate the transcript to English (if not already in English)
            if language != 'en':
                transcript = translator.translate(transcript, src=language, dest='en').text

            # Prompt for the generative model to respond based on the transcript
            prompt = f"I have these sections in my Sidebar, ['Home', 'Employees', 'Customers', 'Task Management', 'Baby Database', 'Work Day Calculation', 'Leave Management', 'Reports', 'Salaries', 'Expenses', 'Customization', 'Settings'].\nHome - Shows the user dashboard\nEmployees - Manage employees\nCustomers - Manage customers\nTask Management - Manage tasks\nBaby Database - Manage baby data\nWork Day Calculation - Calculate work days\nLeave Management - Manage leaves\nReports - View reports\nSalaries - Manage salaries\nExpenses - Manage expenses\nCustomization - Customize settings\nSettings - Manage settings\nBased on the given user transcript '{transcript}', select one of the sections where the user should navigate and provide that as output. The output should be like 'Home'. That's it, No other text should be present"

            # Use the generative model to generate content based on the prompt
            response = model.generate_content(prompt)
            generated_content = response.candidates[0].content.parts[0].text

            # Return the generated content as JSON
            return jsonify({"description": generated_content})

        except sr.UnknownValueError:
            return jsonify({"error": "Could not understand audio"}), 500
        except sr.RequestError as e:
            return jsonify({"error": f"Speech recognition error: {e}"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)