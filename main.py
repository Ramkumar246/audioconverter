from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
from googletrans import Translator
from gtts import gTTS
import speech_recognition as sr

app = FastAPI()

# Directory to store uploaded files
UPLOAD_DIR = "uploads"

origins = [
    "*" # Add more origins if necessary
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Function to translate text to Tamil using Google Translate
def translate_to_tamil(text):
    translator = Translator()
    translated_text = translator.translate(text, src='en', dest='ta')
    print("translated_text",translated_text)
    return translated_text.text

def recognize_speech(audio_file):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)
        # Use Google Web Speech API for speech recognition
        try:
            # Recognize the speech using Google Web Speech API
            text = recognizer.recognize_google(audio_data, language='en-US')
            return text
        except sr.UnknownValueError:
            print("Google Web Speech API could not understand the audio")
            return None
        except sr.RequestError as e:
            print("Could not request results from Google Web Speech API; {0}".format(e))
            return None

# Function to convert Tamil text to audio using Google Text-to-Speech
def text_to_speech_tamil(text, output_file):
    tts = gTTS(text=text, lang='ta')
    tts.save(output_file)

# Route to handle file upload and translation
@app.post("/translate/")
async def translate_audio(file: UploadFile = File(...)):
    try:
        # Create the uploads directory if it doesn't exist
        if not os.path.exists(UPLOAD_DIR):
            os.makedirs(UPLOAD_DIR)

        # Save the uploaded audio file
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Recognize speech from the uploaded audio file (implement this)
        english_text = recognize_speech(file_path)

        # Dummy text for demonstration
        # english_text = "This is a dummy English text."

        # Translate the English text to Tamil using Google Translate
        tamil_text = translate_to_tamil(english_text)
        print("tamil_text",tamil_text)
        output_audio_file = os.path.join(UPLOAD_DIR, "translated_audio.mp3")
        text_to_speech_tamil(tamil_text, output_audio_file)

        # Return the translated audio file
        return FileResponse(output_audio_file, media_type="audio/mp3")
        # Convert the translated Tamil text to audio (implement this)
        # output_audio_file = os.path.join(UPLOAD_DIR, "translated_audio.mp3")
        # text_to_speech_tamil(tamil_text, output_audio_file)


    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
