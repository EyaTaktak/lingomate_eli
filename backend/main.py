import os
import io
import base64
import logging
import uvicorn
from typing import List
from dotenv import load_dotenv

# Web & API
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# AI & Media
from gtts import gTTS
import speech_recognition as sr
from pydub import AudioSegment
from colorama import Fore, Back, Style, init

# Project Imports
from agents.orchestrator import run_pipeline
from tools.level_detector import detect_english_level

# Initialize Colorama and Logging
init(autoreset=True)
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LingoMate-API")

app = FastAPI(title="🤖 LingoMate AI - Hybrid Coach Engine")

# --- CONFIGURATION ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "https://lingomate-eli.onrender.com"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MODELS ---
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    text: str
    level: str = "A1"
    history: List[Message] = []

# --- ENDPOINTS ---

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Primary chat endpoint with real-time level detection and agentic orchestration.
    """
    try:
        user_text = request.text
        
        # 1. VISUAL LOGGING FOR DEMO
        print(f"\n{Fore.CYAN}{'='*20} INCOMING REQUEST {'='*20}")
        print(f"{Fore.YELLOW}💬 USER: {user_text}")

        # 2. LEVEL DETECTION
        # We detect level on every message to ensure the coach adapts dynamically
        detected_level = detect_english_level(user_text)
        print(f"{Fore.WHITE}{Back.GREEN} 🏆 DETECTED LEVEL: {detected_level} {Style.RESET_ALL}")

        # 3. ASYNC ORCHESTRATION
        # We await the pipeline which now handles Pedagogy, RAG, and Grammar
        response_text = await run_pipeline(user_text, detected_level)
        
        print(f"{Fore.MAGENTA}🤖 COACH: {response_text[:70]}...")
        print(f"{Fore.CYAN}{'='*58}\n")

        return {
            "response": response_text, 
            "detected_level": detected_level
        }
    except Exception as e:
        logger.error(f"Chat Error: {e}")
        raise HTTPException(status_code=500, detail="Internal AI Engine Error")

@app.post("/stt")
async def speech_to_text(audio: UploadFile = File(...)):
    """
    Converts speech to text using Google Speech Recognition and Pydub for audio conversion.
    """
    recognizer = sr.Recognizer()
    try:
        audio_bytes = await audio.read()
        audio_stream = io.BytesIO(audio_bytes)

        # Convert WebM/Ogg to WAV for compatibility
        audio_segment = AudioSegment.from_file(audio_stream)
        wav_io = io.BytesIO()
        audio_segment.export(wav_io, format="wav")
        wav_io.seek(0)

        with sr.AudioFile(wav_io) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data, language="en-US")
            print(f"{Fore.BLUE}🎙️ STT TRANSCRIPTION: {text}")
            return {"text": text}

    except Exception as e:
        logger.warning(f"STT Exception: {e}")
        return {"text": ""}

@app.get("/tts")
async def text_to_speech(text: str):
    """
    Converts text to speech and returns it as a Base64 string for the Angular frontend.
    """
    try:
        mp3_fp = io.BytesIO()
        tts = gTTS(text=text, lang='en')
        tts.write_to_fp(mp3_fp)
        
        mp3_fp.seek(0)
        audio_b64 = base64.b64encode(mp3_fp.read()).decode('utf-8')
        
        return {
            "text": text,
            "audio_base64": audio_b64
        }
    except Exception as e:
        logger.error(f"TTS Error: {e}")
        raise HTTPException(status_code=500, detail="Audio Generation Failed")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)