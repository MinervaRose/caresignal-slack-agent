from src.caresignal_core.signals import detect_signals


def test_detects_overload_signal():
    messages = [{"thread_id": "t1", "user": "Sam", "text": "I am overwhelmed by all these messages."}]
    signals = detect_signals(messages)
    assert any(signal.kind == "Overload signal" for signal in signals)


def test_detects_unresolved_blocker():
    messages = [{"thread_id": "t1", "user": "Ana", "text": "I am stuck with an invalid token error."}]
    signals = detect_signals(messages)
    assert any(signal.kind == "Unresolved blocker" for signal in signals)


def test_suggestion_is_quiet_voice_not_blocker():
    messages = [{"thread_id": "t1", "user": "Mei", "text": "I suggested a small checklist for setup errors above, maybe we could pin it?"}]
    signals = detect_signals(messages)
    kinds = {signal.kind for signal in signals}
    assert "Quiet voice" in kinds
    assert "Unresolved blocker" not in kinds
    assert "Buried question" not in kinds


def test_answered_thread_is_not_flagged_as_buried_question():
    messages = [
        {"thread_id": "t1", "user": "Owen", "text": "Can someone explain whether we submit the demo URL or the GitHub repo?"},
        {"thread_id": "t1", "user": "Nora", "text": "Good question, I will post a clear submission checklist tomorrow."},
    ]
    signals = detect_signals(messages)
    assert not any(signal.kind == "Buried question" for signal in signals)
