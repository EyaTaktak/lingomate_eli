import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from gtts import gTTS
import speech_recognition as sr
import uvicorn
import io
from pydub import AudioSegment
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
app = FastAPI(title="Hybrid English Coach API")
from agents.orchestrator import run_pipeline
from tools.level_detector import detect_english_level
# Charger les variables du fichier .env
load_dotenv()
# --- CONFIGURATION CORS ---
# On autorise Angular (port 4200) à communiquer avec FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200",
                   "https://lingomate-eli.onrender.com"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration API NVIDIA
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
LLM_API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"

# --- MODÈLES DE DONNÉES ---
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    text: str
    level: str = "A1"
    history: List[Message] = []

# --- LOGIQUE DE L'AGENT ---

def get_llm_response(user_text, level, history):
    return run_pipeline(user_text, level)

# --- ENDPOINTS API ---

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    user_text = request.text
    
    # 2. UTILISATION : Si le niveau est par défaut (A1), on tente de le détecter
    # ou on le détecte systématiquement pour ajuster le tir.
    detected_level = detect_english_level(user_text)
    response_text = get_llm_response(request.text, detected_level, request.history)
    return {"response": response_text}



@app.post("/stt")
async def speech_to_text(audio: UploadFile = File(...)):
    recognizer = sr.Recognizer()
    
    try:
        # 1. Lire les données brutes envoyées par le navigateur
        audio_bytes = await audio.read()
        audio_stream = io.BytesIO(audio_bytes)

        # 2. Conversion automatique (WebM/Ogg -> WAV) avec pydub
        # Cela règle l'erreur "Audio file could not be read"
        audio_segment = AudioSegment.from_file(audio_stream)
        
        # 3. Exporter en WAV dans un flux mémoire
        wav_io = io.BytesIO()
        audio_segment.export(wav_io, format="wav")
        wav_io.seek(0)

        # 4. Reconnaissance vocale
        with sr.AudioFile(wav_io) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data, language="en-US")
            print(f"--- Transcription : {text} ---") # Vérifie ton terminal Python !
            return {"text": text}

    except Exception as e:
        print(f"Détail erreur technique STT : {str(e)}")
        # On renvoie un texte vide pour ne pas bloquer l'interface
        return {"text": ""}

import base64
@app.get("/tts")
async def text_to_speech(text: str):
    try:
        # 1. Générer l'audio en mémoire vive au lieu d'un fichier temporaire
        mp3_fp = io.BytesIO()
        tts = gTTS(text=text, lang='en')
        tts.write_to_fp(mp3_fp)
        

        # Convertir en base64
        audio_b64 = base64.b64encode(mp3_fp.read()).decode('utf-8')
        # 2. Revenir au début du "fichier virtuel" pour la lecture
        mp3_fp.seek(0)
        
        # Retourner JSON : audio + texte
        return {
            "text": text,
            "audio_base64": audio_b64
        }

    except Exception as e:
        print(f"Erreur TTS: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)