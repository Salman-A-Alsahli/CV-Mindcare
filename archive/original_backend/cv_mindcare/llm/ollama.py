"""LLM helpers for Ollama / local LLaMA-style models."""
from typing import List, Tuple
import requests
import json

LLAMA_DEFAULT = "llama2:7b-chat"

SYSTEM_PROMPT = (
    "You are a supportive, long-term wellbeing assistant. You will be given a JSON object with two keys:"
    " current_readings and historical_summary.\n\n"
    "First, analyze the current_readings to give immediate, actionable advice.\n\n"
    "Next, use the historical_summary to add a personalized touch. Compare the current situation to past trends."
    " For example, if the current emotion is unusual, mention it. If a negative pattern is emerging (e.g., noise is"
    " consistently high at particular times), gently point it out and offer a long-term strategy.\n\n"
    "Your goal is to be a consistent companion that remembers the user's history and helps them see patterns in their"
    " wellbeing over time."
)


def create_context_for_ai(current_readings: dict, days: int = 30, include_json: bool = False):
    """Build a combined context payload using live readings + historical analysis.

    Args:
        current_readings: dict with keys like dominant_emotion, avg_db, noise_classification, avg_green_pct
        days: how many days of history to consider
        include_json: if True, also return a JSON string under the key 'json'

    Returns:
        A dict with keys 'current_readings' and 'historical_summary'.
    """
    try:
        from cv_mindcare import database_manager as dbm
    except Exception:
        dbm = None

    historical_summary = {
        "most_frequent_emotion": None,
        "noisiest_time_of_day": None,
        "insight": None,
    }

    if dbm is not None:
        try:
            df = dbm.get_session_history(days)
            analysis = dbm.analyze_and_rank_trends(df)

            most = analysis.get("emotions_rank", {}).get("most_common")
            noisy_cat = analysis.get("noisy_time_category", {}).get("category")
            greenery = analysis.get("greenery_insights", {})

            # Simple synthesized insight
            insight = None
            pos = greenery.get("avg_green_happy_neutral")
            neg = greenery.get("avg_green_sad_angry")
            if pos is not None and neg is not None:
                if pos > neg:
                    insight = (
                        "Higher greenery levels historically correlate with more frequent 'happy' or 'neutral' emotions."
                    )
                elif neg > pos:
                    insight = (
                        "Lower greenery levels historically correlate with more frequent 'sad' or 'angry' emotions."
                    )
                else:
                    insight = "No clear correlation between greenery levels and dominant emotions was found."
            else:
                # Fallback insight based on noise trends
                if noisy_cat:
                    insight = f"Noise tends to be higher in the {noisy_cat}, consider targeted changes then."

            historical_summary = {
                "most_frequent_emotion": most,
                "noisiest_time_of_day": noisy_cat,
                "insight": insight,
            }
        except Exception:
            # If anything fails, return a minimal historical summary
            pass

    payload = {"current_readings": current_readings, "historical_summary": historical_summary}
    if include_json:
        try:
            payload_json = json.dumps(payload)
        except Exception:
            payload_json = None
        payload["json"] = payload_json

    return payload


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
