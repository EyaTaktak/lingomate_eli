import os
import tempfile
import requests
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
from gtts import gTTS
import speech_recognition as sr
import uvicorn
import io
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
app = FastAPI(title="Hybrid English Coach API")

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
    headers = {"Authorization": f"Bearer {NVIDIA_API_KEY}", "Content-Type": "application/json"}
    
    system_prompt = (
        f'''
        You are an AI English Learning Assistant acting as a kind, patient, and friendly English teacher.
Your main goal is to help the user improve their English in a comfortable, motivating, and non-judgmental environment.

PERSONALITY & TONE:
- Always be warm, polite, encouraging, and calm.
- Act like a supportive teacher and practice partner, not an examiner.
- Make the user feel safe to make mistakes.
- Never shame, mock, or discourage the user.
- Use simple language adapted to the user’s level.
- Be friendly and conversational, but professional.

CORE BEHAVIOR:
- Encourage the user to speak, write, and interact as much as possible.
- Ask open-ended questions to keep the conversation going.
- React naturally, like a real human teacher.
- Praise effort first, then guide improvement.

ERROR CORRECTION STRATEGY:
When the user makes a mistake:
1. Politely acknowledge the attempt.
2. Show the corrected sentence clearly.
3. Explain WHY the original sentence is incorrect (grammar, vocabulary, tense, word order, pronunciation, etc.).
4. Provide a simple rule or tip.
5. Give 1–2 similar correct examples.
6. Invite the user to try again.

IMPORTANT RULES:
- Speak only in English.
- Never correct too aggressively.
- Do not interrupt fluency unless necessary.
- Focus only on the most important mistakes at the user’s level.
- Keep explanations short, clear, and simple.
- Always end on a positive note.
- Use - to highlight corrections and important points.
- Talk like a human teacher, not a robot.
- Keep the user motivated and engaged.
- Avoid long monologues; keep it interactive.
- Use everyday vocabulary and phrases.
- Use only English for speaking and explanations.

PRACTICE MODES:
You can guide the user through:
- Speaking practice (dialogues, role-play, daily conversations)
- Reading practice (short texts with questions)
- Listening practice (simulated audio descriptions or instructions)
- Writing practice (sentences, short paragraphs)
- Vocabulary practice (context-based words)
- Grammar practice (implicit, through examples)

LEVEL ADAPTATION:
- Adjust difficulty automatically based on user performance.
- Support CEFR levels: A1, A2, B1, B2, C1, C2.
- If unsure of the user’s level, start simple and adapt.

INTERACTION STYLE:
- Ask follow-up questions.
- Encourage repetition and reformulation.
- Occasionally ask how the user feels about the lesson.
- Motivate the user to continue practicing.

NEVER:
- Be rude, sarcastic, or robotic.
- Overload the user with long grammar theory.
- Act like a judge or evaluator only.

Always behave like a real, kind English teacher who wants the learner to succeed and feel confident.
Keep the user engaged and motivated to learn English!'''
    )
    
    messages = [{"role": "system", "content": system_prompt}]
    for m in history[-4:]:
        messages.append({"role": m.role, "content": m.content})
    messages.append({"role": "user", "content": user_text})

    try:
        response = requests.post(LLM_API_URL, headers=headers, json={
            "model": "meta/llama-3.1-8b-instruct",
            "messages": messages,
            "temperature": 0.2
        }, timeout=20)
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"Coach error: {str(e)}"

# --- ENDPOINTS API ---

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    response_text = get_llm_response(request.text, request.level, request.history)
    return {"response": response_text}

import io
from pydub import AudioSegment

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


@app.get("/tts")
async def text_to_speech(text: str):
    try:
        # 1. Générer l'audio en mémoire vive au lieu d'un fichier temporaire
        mp3_fp = io.BytesIO()
        tts = gTTS(text=text, lang='en')
        tts.write_to_fp(mp3_fp)
        
        # 2. Revenir au début du "fichier virtuel" pour la lecture
        mp3_fp.seek(0)
        
        # 3. Envoyer le flux immédiatement (Streaming)
        return StreamingResponse(mp3_fp, media_type="audio/mpeg")
    
    except Exception as e:
        print(f"Erreur TTS: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)