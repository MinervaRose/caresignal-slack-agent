from __future__ import annotations

from collections import defaultdict
from typing import Any

from .models import CareSignal

# V0.2 design principle:
# Prefer a small number of high-quality care signals over noisy over-detection.
# CareSignal detects interaction patterns, not identities or diagnoses.

HELP_QUESTION_PATTERNS = [
    "can someone help",
    "anyone help",
    "how do i",
    "where is",
    "where are",
    "what do i",
    "can someone explain",
    "does anyone know",
]

BLOCKER_PATTERNS = [
    "i'm stuck",
    "i am stuck",
    "blocked",
    "i can't",
    "i cannot",
    "can't find",
    "cannot find",
    "not working",
    "invalid token",
    "error",
]

OVERLOAD_PATTERNS = [
    "overwhelmed",
    "too many messages",
    "can't keep up",
    "cannot keep up",
    "lost in the thread",
    "lost in the messages",
    "confused by the thread",
    "don't know what i actually need to read",
    "do not know what i actually need to read",
    "might quit",
]

FOLLOWUP_PROMISE_PATTERNS = [
    "i will post",
    "i'll post",
    "i will send",
    "i'll send",
    "i will share",
    "i'll share",
    "tomorrow",
    "later",
    "follow up",
]

QUIET_CONTRIBUTION_PATTERNS = [
    "i suggested",
    "maybe we could",
    "could we pin",
    "i think we could",
    "for what it's worth",
]

ANSWER_PATTERNS = [
    "try ",
    "fixed",
    "solved",
    "answer",
    "here is",
    "here's",
    "link",
    "checklist",
    "you do not need",
]

PRIORITY_RANK = {"high": 3, "medium": 2, "low": 1}
KIND_RANK = {
    "Overload signal": 5,
    "Unresolved blocker": 4,
    "Buried question": 3,
    "Follow-up gap": 2,
    "Quiet voice": 1,
}


def _text(message: dict[str, Any]) -> str:
    return str(message.get("text", "")).strip()


def _lower(message: dict[str, Any]) -> str:
    return _text(message).lower()


def _thread_id(message: dict[str, Any]) -> str:
    return str(message.get("thread_id") or message.get("ts") or "unknown-thread")


def _user(message: dict[str, Any]) -> str:
    return str(message.get("user") or "unknown")


def _has_any(text: str, patterns: list[str]) -> bool:
    return any(pattern in text for pattern in patterns)


def _looks_like_direct_help_request(text: str) -> bool:
    return _has_any(text, HELP_QUESTION_PATTERNS)


def _looks_like_blocker(text: str) -> bool:
    # Avoid treating general phrases such as "setup errors" in a suggestion as a blocker.
    return _has_any(text, BLOCKER_PATTERNS) and not (
        "i suggested" in text or "maybe we could" in text or "could we pin" in text
    )


def _looks_like_answer(text: str) -> bool:
    return _has_any(text, ANSWER_PATTERNS)


def _has_reply_after(messages_in_thread: list[dict[str, Any]], message: dict[str, Any]) -> bool:
    try:
        index = messages_in_thread.index(message)
    except ValueError:
        return False
    return any(_looks_like_answer(_lower(reply)) for reply in messages_in_thread[index + 1 :])


def _make_signal(kind: str, priority: str, message: dict[str, Any]) -> CareSignal:
    user = _user(message)
    thread_id = _thread_id(message)
    evidence = _text(message)

    if kind == "Overload signal":
        return CareSignal(
            kind=kind,
            priority="high",
            user=user,
            thread_id=thread_id,
            evidence=evidence,
            why_it_matters="The conversation volume or thread complexity may be making participation harder.",
            next_kind_action="Offer a calm summary and reduce the number of required next steps.",
            suggested_action="Assign follow-up",
            rts_query=f"messages around overload confusion in thread {thread_id}",
        )

    if kind == "Unresolved blocker":
        return CareSignal(
            kind=kind,
            priority="high",
            user=user,
            thread_id=thread_id,
            evidence=evidence,
            why_it_matters="The participant may be unable to continue without targeted help.",
            next_kind_action="Check whether the blocker is resolved; offer one concrete next step.",
            suggested_action="Assign follow-up",
            rts_query=f"messages around blocker error help request in thread {thread_id}",
        )

    if kind == "Buried question":
        return CareSignal(
            kind=kind,
            priority="high",
            user=user,
            thread_id=thread_id,
            evidence=evidence,
            why_it_matters="A direct request for help appears to have no clear answer in the thread.",
            next_kind_action="Answer directly in-thread or assign a human follow-up.",
            suggested_action="Assign follow-up",
            rts_query=f"unanswered question context in thread {thread_id}",
        )

    if kind == "Follow-up gap":
        return CareSignal(
            kind=kind,
            priority="medium",
            user=user,
            thread_id=thread_id,
            evidence=evidence,
            why_it_matters="A promised resource or action may need closure so participants know what to expect.",
            next_kind_action="Confirm whether the promised follow-up has been completed.",
            suggested_action="Needs context",
            rts_query=f"follow up promised resource checklist thread {thread_id}",
        )

    return CareSignal(
        kind="Quiet voice",
        priority="medium",
        user=user,
        thread_id=thread_id,
        evidence=evidence,
        why_it_matters="A potentially useful contribution appears to have received little or no response.",
        next_kind_action="Acknowledge the contribution or decide whether it should be resurfaced.",
        suggested_action="Needs context",
        rts_query=f"quiet contribution no response thread {thread_id}",
    )


def _candidate_signals_for_message(
    message: dict[str, Any],
    messages_in_thread: list[dict[str, Any]],
) -> list[CareSignal]:
    text = _lower(message)
    candidates: list[CareSignal] = []
    answered_after = _has_reply_after(messages_in_thread, message)
    has_later_messages = len(messages_in_thread) > messages_in_thread.index(message) + 1 if message in messages_in_thread else False

    if _has_any(text, OVERLOAD_PATTERNS):
        candidates.append(_make_signal("Overload signal", "high", message))

    if _looks_like_blocker(text) and not answered_after:
        candidates.append(_make_signal("Unresolved blocker", "high", message))

    if _looks_like_direct_help_request(text) and not answered_after:
        # If the same message is already a blocker, do not also emit a buried question.
        if not any(signal.kind == "Unresolved blocker" for signal in candidates):
            candidates.append(_make_signal("Buried question", "high", message))

    if _has_any(text, FOLLOWUP_PROMISE_PATTERNS):
        candidates.append(_make_signal("Follow-up gap", "medium", message))

    if _has_any(text, QUIET_CONTRIBUTION_PATTERNS) and not has_later_messages:
        candidates.append(_make_signal("Quiet voice", "medium", message))

    return candidates


def _best_signal(candidates: list[CareSignal]) -> CareSignal | None:
    if not candidates:
        return None
    return sorted(
        candidates,
        key=lambda signal: (PRIORITY_RANK[signal.priority], KIND_RANK.get(signal.kind, 0)),
        reverse=True,
    )[0]


def _dedupe_by_thread(signals: list[CareSignal]) -> list[CareSignal]:
    best_by_thread: dict[str, CareSignal] = {}
    for signal in signals:
        current = best_by_thread.get(signal.thread_id)
        if current is None:
            best_by_thread[signal.thread_id] = signal
            continue
        if (PRIORITY_RANK[signal.priority], KIND_RANK.get(signal.kind, 0)) > (
            PRIORITY_RANK[current.priority],
            KIND_RANK.get(current.kind, 0),
        ):
            best_by_thread[signal.thread_id] = signal
    return list(best_by_thread.values())


def detect_signals(messages: list[dict[str, Any]], *, max_signals: int = 5) -> list[CareSignal]:
    """Detect support-gap patterns in Slack-like messages.

    V0.2 is intentionally selective: one primary signal per message/thread, capped for
    Slack readability. It detects patterns, not identities or diagnoses.
    """
    messages_by_thread: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for message in messages:
        messages_by_thread[_thread_id(message)].append(message)

    raw_signals: list[CareSignal] = []
    for message in messages:
        thread_messages = messages_by_thread[_thread_id(message)]
        best = _best_signal(_candidate_signals_for_message(message, thread_messages))
        if best is not None:
            raw_signals.append(best)

    deduped = _dedupe_by_thread(raw_signals)
    ranked = sorted(
        deduped,
        key=lambda signal: (PRIORITY_RANK[signal.priority], KIND_RANK.get(signal.kind, 0)),
        reverse=True,
    )
    return ranked[:max_signals]
