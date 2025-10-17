"""LLM helpers for Ollama / local LLaMA-style models."""
from typing import List, Tuple
import requests
import json

LLAMA_DEFAULT = "llama2:7b-chat"

SYSTEM_PROMPT = (
    "You are a supportive wellbeing assistant. You will be given observations "
    "about the user's environment (noise, greenery, emotions, air quality). "
    "Explain the results in simple terms, give concise, practical tips, and keep a positive tone."
)


def load_llama(model_name: str = LLAMA_DEFAULT):
    # For now this is a light wrapper returning the model identifier.
    print(f"[LLM] Using local Ollama model: {model_name}")
    return model_name, None


def format_prompt(system: str, history: List[Tuple[str, str]], user_msg: str) -> str:
    sep = "\n\n"
    prompt = f"[SYSTEM]\n{system}{sep}"
    for (role, msg) in history:
        if role == "user":
            prompt += f"[USER]\n{msg}{sep}"
        else:
            prompt += f"[ASSISTANT]\n{msg}{sep}"
    prompt += f"[USER]\n{user_msg}{sep}[ASSISTANT]\n"
    return prompt


def llama_respond(model_name, _tok, system: str, history: List[Tuple[str, str]], user_msg: str, max_new_tokens: int = 300):
    prompt = format_prompt(system, history, user_msg)
    try:
        r = requests.post(
            "http://localhost:11434/api/generate",
            headers={"Content-Type": "application/json"},
            data=json.dumps({
                "model": model_name,
                "prompt": prompt,
                "stream": False
            })
        )
        if r.status_code == 200:
            data = r.json()
            return data.get("response", "").strip()
        else:
            return f"[Error] Ollama returned status {r.status_code}: {r.text}"
    except Exception as e:
        return f"[Error] Failed to connect to Ollama: {e}"
