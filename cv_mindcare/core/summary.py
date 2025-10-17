"""Summary and fallback advice logic."""
from typing import Dict


def summarize_findings(noise: Dict, green: Dict, emo: Dict) -> str:
    lines = ["Here are the quick observations from your environment:"]
    if noise.get("available"):
        lines.append(f"- Noise: avg {noise['avg_db']} dB → {noise['classification']}")
    else:
        lines.append(f"- Noise: unavailable ({noise.get('reason', 'unknown')})")

    if green.get("available"):
        lines.append(f"- Greenery: avg {green['avg_green_pct']:.2f}% → {green['classification']}")
    else:
        lines.append(f"- Greenery: unavailable ({green.get('reason', 'unknown')})")

    if emo.get("available"):
        lines.append(f"- Emotion: dominant '{emo['dominant_emotion']}' over {sum(emo.get('counts', {}).values())} samples")
    else:
        lines.append(f"- Emotion: unavailable ({emo.get('reason', 'unknown')})")

    lines.append("- Air quality: skipped (sensor not connected yet)")
    return "\n".join(lines)


def fallback_advice(noise: Dict, green: Dict, emo: Dict) -> str:
    tips = []
    # Noise
    if noise.get("available"):
        n = noise.get("avg_db", 0)
        nc = noise.get("classification", "")
        if n >= 70 or nc == "Harmful":
            tips.append("Noise is very high. Use headphones with isolation, close doors/windows, and add soft furnishings or panels.")
        elif n >= 55 or nc in {"Stress Zone"}:
            tips.append("Noise is above the focus sweet spot. Reduce notifications, enable noise suppression, and distance noisy devices.")
        else:
            tips.append("Noise level looks fine for focus.")
    else:
        tips.append("Noise reading unavailable—if possible, retry with a working microphone.")

    # Greenery
    if green.get("available"):
        g = green.get("avg_green_pct", 0)
        if g < 5:
            tips.append("Greenery is low. Add a plant or two in your field of view or a green poster; target >12% coverage.")
        elif g < 12:
            tips.append("Greenery is moderate. One more plant can push you into the 'high' zone.")
        else:
            tips.append("Great greenery—keep plants healthy and visible.")
    else:
        tips.append("Greenery unavailable—check webcam permissions.")

    # Emotion
    if emo.get("available"):
        d = (emo.get("dominant_emotion") or "").lower()
        if d in {"sad", "angry", "fear"}:
            tips.append("Mood skews negative. Try a 2–3 minute reset: stand, shoulder rolls, 6 slow breaths (4s in, 6s out), then a 25-minute focus block.")
        elif d in {"neutral"}:
            tips.append("Mood is neutral. A short stretch and a clear 30-minute goal can boost engagement.")
        else:
            tips.append("Positive affect detected—nice! Keep short breaks to maintain it.")
    else:
        tips.append("Emotion unavailable—face not detected or camera blocked.")

    quick = [
        "Open a window or run a fan for 2 minutes to refresh air.",
        "Silence non-critical app notifications.",
        "Place a plant or green object within your eye line.",
    ]
    return (
        "\n===== Opinion & Advice (Fallback) =====\n"
        "Your environment has a few easy improvements. Here are the priorities:\n"
        + "\n- " + "\n- ".join(tips) +
        "\n\nQuick wins (next 10 minutes):\n- " + "\n- ".join(quick) +
        "\n=======================================\n"
    )
