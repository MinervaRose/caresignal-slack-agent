"""Slack context retrieval and message normalization for CareSignal.

V0.6 keeps two retrieval paths cleanly separated:
- channel-history retrieval via `conversations.history`, already working in V0.5;
- RTS retrieval via `assistant.search.context`, introduced in V0.6.

Both paths normalize Slack messages into the same compact CareSignal shape so
signal detection stays independent from Slack API details.
"""

from __future__ import annotations

import re
from typing import Any

from slack_sdk.errors import SlackApiError

DEMO_LINE_RE = re.compile(r"^\*(?P<user>[^*]+)\*\s*·\s*`(?P<thread>[^`]+)`\s*\n(?P<text>.*)$", re.S)


class SlackContextError(RuntimeError):
    """Raised when Slack context cannot be retrieved."""


def parse_slack_text_to_caresignal_message(
    raw_text: str,
    *,
    fallback_user: str = "participant",
    fallback_thread: str = "message",
) -> dict[str, str] | None:
    """Convert one Slack text payload into a compact CareSignal message.

    The synthetic demo scenario posts messages in the form:
    `*Ana* · `t1`\n...`. This parser extracts the synthetic participant name
    and thread label so the brief reads like the human scenario rather than
    showing the bot's Slack user ID for every message.
    """
    text = str(raw_text or "").strip()
    if not text:
        return None

    # Skip CareSignal UI/control messages; keep participant scenario messages.
    if text.startswith("♡ CareSignal demo scenario") or text.startswith("♡ Demo scenario posted"):
        return None
    if text.startswith("♡ CareSignal Care Brief") or text.startswith("♡ CareSignal commands"):
        return None

    parsed = DEMO_LINE_RE.match(text)
    if parsed:
        return {
            "user": parsed.group("user").strip(),
            "thread_id": parsed.group("thread").strip(),
            "text": parsed.group("text").strip(),
        }

    return {"user": fallback_user, "thread_id": fallback_thread, "text": text}


def fetch_recent_channel_messages(client: Any, channel_id: str, *, limit: int = 40) -> list[dict[str, Any]]:
    """Fetch recent messages from a Slack channel using `conversations.history`.

    Required bot scopes for public channels:
    - channels:history
    - channels:read

    The returned order is chronological, which helps the core detector reason
    about whether a question received an answer later in the context.
    """
    try:
        response = client.conversations_history(channel=channel_id, limit=limit, inclusive=True)
    except SlackApiError as exc:
        error = exc.response.get("error", "unknown_error") if exc.response else "unknown_error"
        raise SlackContextError(f"Slack context retrieval failed: {error}") from exc

    if not response.get("ok", False):
        raise SlackContextError(f"Slack context retrieval failed: {response.get('error', 'unknown_error')}")

    messages = response.get("messages", []) or []
    return list(reversed(messages))


def slack_messages_to_caresignal_messages(messages: list[dict[str, Any]]) -> list[dict[str, str]]:
    """Convert Slack Web API messages into the compact CareSignal message shape."""
    converted: list[dict[str, str]] = []
    for index, message in enumerate(messages):
        fallback_user = str(message.get("user") or message.get("username") or "participant")
        fallback_thread = str(message.get("thread_ts") or message.get("ts") or f"message-{index}")
        parsed = parse_slack_text_to_caresignal_message(
            str(message.get("text") or ""),
            fallback_user=fallback_user,
            fallback_thread=fallback_thread,
        )
        if parsed:
            converted.append(parsed)
    return converted
