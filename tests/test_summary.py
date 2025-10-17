from cv_mindcare.core.summary import summarize_findings, fallback_advice


def test_summarize_all_unavailable():
    noise = {"available": False, "reason": "no mic"}
    green = {"available": False, "reason": "no cam"}
    emo = {"available": False, "reason": "no face"}
    s = summarize_findings(noise, green, emo)
    assert "Noise: unavailable" in s
    assert "Greenery: unavailable" in s
    assert "Emotion: unavailable" in s


def test_fallback_contains_quick_wins():
    noise = {"available": False}
    green = {"available": False}
    emo = {"available": False}
    fb = fallback_advice(noise, green, emo)
    assert "Quick wins" in fb
