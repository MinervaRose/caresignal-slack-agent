from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.caresignal_core.signals import detect_signals
from src.slack_app.blocks import care_brief_blocks
from src.slack_app.context import SlackContextError, fetch_recent_channel_messages, slack_messages_to_caresignal_messages
from src.slack_app.rts import default_care_rts_queries, search_relevant_context


def load_synthetic_messages() -> list[dict]:
    sample_path = Path(__file__).resolve().parents[2] / "sample_data" / "synthetic_slack_messages.json"
    return json.loads(sample_path.read_text(encoding="utf-8"))


def build_demo_care_brief_blocks(*, channel_name: str | None = None) -> list[dict]:
    messages = load_synthetic_messages()
    signals = detect_signals(messages)
    return care_brief_blocks(
        signals,
        context_label="demo Slack context",
        channel_name=channel_name,
        messages_reviewed=len(messages),
        retrieval_note="Synthetic demo data only. Use `/caresignal live` for recent channel history or `@CareSignal rts brief` for RTS.",
    )


def build_live_care_brief_blocks(client: Any, *, channel_id: str, channel_name: str | None = None) -> list[dict]:
    """Build a Care Brief from recent Slack messages in the current channel."""
    try:
        care_messages = get_recent_care_messages(client, channel_id=channel_id, limit=50)
    except SlackContextError as exc:
        return care_brief_blocks(
            [],
            context_label="Slack channel history",
            channel_name=channel_name,
            retrieval_note=(
                f"Could not retrieve channel history: `{exc}`. "
                "Check that the app is in the channel and has `channels:history` + `channels:read` scopes, then reinstall the app."
            ),
        )

    signals = detect_signals(care_messages)
    return care_brief_blocks(
        signals,
        context_label="recent Slack channel history",
        channel_name=channel_name,
        messages_reviewed=len(care_messages),
        retrieval_note=(
            "Working retrieval path: Slack Web API channel history. "
            "For the RTS path, mention `@CareSignal rts brief`."
        ),
    )


def get_recent_care_messages(client: Any, *, channel_id: str, limit: int = 50) -> list[dict[str, str]]:
    slack_messages = fetch_recent_channel_messages(client, channel_id, limit=limit)
    return slack_messages_to_caresignal_messages(slack_messages)


def build_rts_care_brief_blocks(
    client: Any,
    *,
    channel_id: str,
    channel_name: str | None = None,
    action_token: str | None = None,
) -> list[dict]:
    """Build a Care Brief from Slack RTS results, with an honest fallback.

    RTS is attempted first. If the sandbox returns no hits, the response falls
    back to recent channel history so the demo remains usable while making the
    RTS result transparent.
    """
    if not action_token:
        return care_brief_blocks(
            [],
            context_label="Real-Time Search",
            channel_name=channel_name,
            retrieval_note=(
                "No `action_token` was present. Trigger RTS with `@CareSignal rts brief` in a channel, "
                "and make sure the app is subscribed to `app_mention` events."
            ),
        )

    queries = default_care_rts_queries(channel_name=channel_name)
    all_messages: list[dict[str, str]] = []
    errors: list[str] = []
    raw_hits = 0

    for query in queries:
        result = search_relevant_context(
            client,
            query=query,
            action_token=action_token,
            channel_id=channel_id,
            limit=10,
        )
        raw_hits += result.raw_count
        if result.ok:
            all_messages.extend(result.messages)
        else:
            errors.append(f"`{query}` → `{result.error}`")

    deduped = dedupe_care_messages(all_messages)

    if deduped:
        signals = detect_signals(deduped)
        note = (
            "RTS retrieval path: `assistant.search.context` using an app-mention `action_token`. "
            f"Queries attempted: {len(queries)}. Raw RTS hits: {raw_hits}."
        )
        if errors:
            note += " Some RTS queries returned errors: " + "; ".join(errors[:3])
        return care_brief_blocks(
            signals,
            context_label="Slack Real-Time Search results",
            channel_name=channel_name,
            messages_reviewed=len(deduped),
            retrieval_note=note,
        )

    if errors:
        return care_brief_blocks(
            [],
            context_label="Real-Time Search",
            channel_name=channel_name,
            retrieval_note=(
                "RTS call attempted, but Slack returned an error. "
                + "; ".join(errors[:3])
                + ". Use `/caresignal live` as the working channel-history fallback while checking RTS scopes/features."
            ),
        )

    # Sandbox-safe fallback: RTS succeeded but returned no hits. Keep the demo
    # useful while making the retrieval situation explicit.
    try:
        fallback_messages = get_recent_care_messages(client, channel_id=channel_id, limit=50)
    except SlackContextError as exc:
        return care_brief_blocks(
            [],
            context_label="Real-Time Search",
            channel_name=channel_name,
            retrieval_note=(
                f"RTS succeeded but returned 0 hits, and channel-history fallback failed: `{exc}`. "
                "Try `/caresignal demo` first, then `/caresignal live`."
            ),
        )

    signals = detect_signals(fallback_messages)
    return care_brief_blocks(
        signals,
        context_label="RTS attempt + channel-history fallback",
        channel_name=channel_name,
        messages_reviewed=len(fallback_messages),
        retrieval_note=(
            "RTS path succeeded technically through `assistant.search.context`, but returned 0 hits in this sandbox. "
            f"Queries attempted: {len(queries)}. Raw RTS hits: 0. "
            "CareSignal used recent channel history as a transparent fallback for the human-review queue."
        ),
    )


def dedupe_care_messages(messages: list[dict[str, str]]) -> list[dict[str, str]]:
    deduped: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    for message in messages:
        key = (message.get("user", ""), message.get("thread_id", ""), message.get("text", ""))
        if key not in seen:
            seen.add(key)
            deduped.append(message)
    return deduped


def demo_messages_for_channel() -> list[str]:
    """Human-readable synthetic messages to post into a Slack demo channel."""
    messages = load_synthetic_messages()
    lines: list[str] = []
    for message in messages:
        user = message.get("user", "participant")
        text = message.get("text", "")
        thread = message.get("thread_id", "thread")
        lines.append(f"*{user}* · `{thread}`\n{text}")
    return lines
