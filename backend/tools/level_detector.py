import os
import requests
from langchain.tools import tool
from pydantic import BaseModel, Field

class LevelDetectionInput(BaseModel):
    text: str = Field(description="The user's English text to be analyzed for proficiency level.")

@tool("level_detector", args_schema=LevelDetectionInput)
def detect_english_level(text: str) -> str:
    """Analyzes text to determine the CEFR English level (A1-C2)."""
    
    api_key = os.getenv("NVIDIA_API_KEY")
    url = "https://integrate.api.nvidia.com/v1/chat/completions"
    
    prompt = f"""Analyze the following English text and determine the CEFR level (A1, A2, B1, B2, C1, or C2). 
    Consider grammar, vocabulary, and sentence structure.
    Return ONLY the level code (e.g., 'B1').
    Text: {text}"""

    payload = {
        "model": "nvidia/llama-3.1-405b-instruct", # Ou votre modèle configuré
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1
    }
    
    headers = {"Authorization": f"Bearer {api_key}"}
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        res_json = response.json()
        # On extrait juste le niveau (ex: "B2")
        level = res_json['choices'][0]['message']['content'].strip()
        return level
    except Exception:
        return "A1" # Niveau par défaut en cas d'erreur