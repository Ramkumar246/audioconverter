from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
from googletrans import Translator
from gtts import gTTS
import speech_recognition as sr
from pydub import AudioSegment
from pydantic import BaseModel

app = FastAPI()

# Directory to store uploaded files
UPLOAD_DIR = "uploads"

class TextInput(BaseModel):
    text: str

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

def convert_to_wav(input_file, output_file):
    print("input_file",input_file)
    print("output_file",output_file)
    try:
        # Load the audio file
        audio = AudioSegment.from_file(input_file)

        # Convert to WAV format
        audio.export(output_file, format="wav")

        return True
    except Exception as e:
        print(f"Error converting to WAV: {e}")
        return False


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

        # Determine the file extension
        file_ext = os.path.splitext(file_path)[1].lower()

        # Convert to WAV if the uploaded file is not already in WAV format
        if file_ext != ".wav":
            wav_file_path = os.path.splitext(file_path)[0] + ".wav"
            if not convert_to_wav(file_path, wav_file_path):
                raise HTTPException(status_code=500, detail="Error converting to WAV")
            file_path = wav_file_path

        # Recognize speech from the uploaded audio file (implement this)
        english_text = recognize_speech(file_path)

        # Translate the English text to Tamil using Google Translate
        tamil_text = translate_to_tamil(english_text)

        # Convert the translated Tamil text to audio
        output_audio_file = os.path.join(UPLOAD_DIR, "translated_audio.mp3")
        text_to_speech_tamil(tamil_text, output_audio_file)
        response = FileResponse(output_audio_file, media_type="audio/mp3")
        print("audio_",type(response))
        # Return the translated audio file
        return FileResponse(output_audio_file, media_type="audio/mp3")

    except HTTPException as http_exception:
        raise http_exception
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.post("/translate_text/")
async def translate_text(input_text: TextInput):
    try:
        # Translate the input text to Tamil using Google Translate
        tamil_text = translate_to_tamil(input_text.text)

        # Convert the translated Tamil text to audio
        output_text_audio_file = os.path.join(UPLOAD_DIR, "translated_text.mp3")
        text_to_speech_tamil(tamil_text, output_text_audio_file)

        # Return the translated audio file
        response = FileResponse(output_text_audio_file, media_type="audio/mp3")
        print("text_response",type(response))
        return response
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")