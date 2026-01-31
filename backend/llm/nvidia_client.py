import os
import requests

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
LLM_API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"

def call_llm(messages, temperature=0.2):
    headers = {
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        LLM_API_URL,
        headers=headers,
        json={
            "model": "meta/llama-3.1-8b-instruct",
            "messages": messages,
            "temperature": temperature
        },
        timeout=20
    )

    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]
