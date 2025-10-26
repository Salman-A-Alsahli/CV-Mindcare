"""CLI entrypoint for CV Mindcare."""
import argparse
from typing import List, Tuple
from cv_mindcare.sensors import run_noise_sampling, run_greenery_sampling, run_emotion_sampling
from cv_mindcare.core import summarize_findings, fallback_advice
from cv_mindcare.llm import load_llama, llama_respond, SYSTEM_PROMPT, LLAMA_DEFAULT


def interactive_chat_loop(llm, tok, system_prompt: str, history: List[Tuple[str, str]]):
    print("Type your message to continue chatting with the assistant. Type '/exit' to quit.")
    try:
        while True:
            user_msg = input("You: ").strip()
            if not user_msg:
                continue
            if user_msg.lower() in {"/exit", "exit", ":q"}:
                print("Goodbye! 👋")
                break
            reply = llama_respond(llm, tok, system_prompt, history, user_msg)
            print("Assistant:" + reply + "")
            history.append(("user", user_msg))
            history.append(("assistant", reply))
    except KeyboardInterrupt:
        print("Goodbye! 👋")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--camera", type=int, default=0, help="Webcam index (default 0)")
    ap.add_argument("--noise-samples", type=int, default=5, help="Number of noise samples")
    ap.add_argument("--emotion-seconds", type=int, default=15, help="Seconds to sample emotions")
    ap.add_argument("--model", type=str, default=LLAMA_DEFAULT, help="Model id for LLaMA chat")
    ap.add_argument("--mock", action="store_true", help="Skip sensors and use mock readings to get immediate advice from the model")
    args = ap.parse_args()

    if args.mock:
        print("[MOCK] Using sample readings to get direct LLaMA advice...")
        noise = {"available": True, "avg_db": 58.1, "classification": "Acceptable", "readings": [58.2, 57.9, 58.3]}
        green = {"available": True, "avg_green_pct": 7.6, "classification": "Moderate", "samples": 120}
        emo = {"available": True, "dominant_emotion": "neutral", "counts": {"happy": 4, "neutral": 9, "sad": 2, "angry": 1}}
    else:
        noise = run_noise_sampling(args.noise_samples)
        green = run_greenery_sampling(args.camera)
        emo = run_emotion_sampling(args.emotion_seconds, args.camera)

    summary = summarize_findings(noise, green, emo)
    print("================ SUMMARY ================")
    print(summary)
    print("========================================")

    # LLM or fallback
    try:
        llm, tok = load_llama(args.model)
    except Exception:
        llm = None
        tok = None

    if llm is None:
        print("[LLM] Could not load model — using built-in fallback advice.\n")
        print(fallback_advice(noise, green, emo))
        return

    history: List[Tuple[str, str]] = []
    initial_user = (
        f"Please review these measurements and give brief, actionable advice to improve my wellbeing.\n\n{summary}\n\n"
        "Keep it friendly and specific to the readings."
    )
    assistant_reply = llama_respond(llm, tok, SYSTEM_PROMPT, history, initial_user)
    print("\n===== Assistant (LLaMA) =====\n" + assistant_reply + "\n=============================\n")
    history.append(("user", initial_user))
    history.append(("assistant", assistant_reply))

    interactive_chat_loop(llm, tok, SYSTEM_PROMPT, history)


if __name__ == "__main__":
    main()
