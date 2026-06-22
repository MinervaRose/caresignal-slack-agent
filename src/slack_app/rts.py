"""Real-Time Search retrieval adapter for CareSignal.

The submission build keeps Slack Real-Time Search genuinely integrated while
preserving a reliable channel-history fallback for demo stability. RTS is
invoked through `assistant.search.context` when an `action_token` is available
from an app mention.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from slack_sdk.errors import SlackApiError

from src.caresignal_core.models import CareSignal
from src.slack_app.context import parse_slack_text_to_caresignal_message


@dataclass(frozen=True)
class RtsSearchResult:
    """Normalized RTS search result for CareSignal's detector."""

    ok: bool
    query: str
    messages: list[dict[str, str]]
    error: str | None = None
    raw_count: int = 0


def rts_queries_for_signals(signals: list[CareSignal]) -> list[str]:
    """Return the RTS query targets needed to validate or enrich signals."""
    return [signal.rts_query for signal in signals if signal.rts_query]


def default_care_rts_queries(*, channel_name: str | None = None) -> list[str]:
    """Queries that make RTS load-bearing for CareSignal's care workflow.

    The first queries are literal enough to work in a small sandbox/demo channel.
    The final queries are broader semantic queries for real Slack communities.
    """
    location = f" #{channel_name}" if channel_name else ""
    return [
        f"overwhelmed 200 messages{location}",
        f"invalid token API auth stuck help{location}",
        f"starter notebook link can't find{location}",
        f"submission checklist demo URL GitHub repo{location}",
        f"setup errors checklist pin it{location}",
        f"Who is stuck, overwhelmed, or asking for help{location}?",
        f"What questions, promised follow-ups, or quiet contributions need attention{location}?",
    ]


def search_relevant_context(
    client: Any,
    *,
    query: str,
    action_token: str,
    channel_id: str | None = None,
    limit: int = 10,
) -> RtsSearchResult:
    """Call Slack Real-Time Search and normalize message results."""
    payload: dict[str, Any] = {
        "query": query,
        "action_token": action_token,
        "channel_types": ["public_channel"],
        "content_types": ["messages"],
        "include_context_messages": True,
        "include_bots": True,
        "limit": limit,
    }
    if channel_id:
        payload["context_channel_id"] = channel_id

    try:
        response = client.api_call("assistant.search.context", json=payload)
    except SlackApiError as exc:
        error = exc.response.get("error", "unknown_error") if exc.response else "unknown_error"
        return RtsSearchResult(ok=False, query=query, messages=[], error=error)

    if not response.get("ok", False):
        return RtsSearchResult(
            ok=False,
            query=query,
            messages=[],
            error=str(response.get("error", "unknown_error")),
        )

    messages = rts_response_to_caresignal_messages(response)
    raw_count = len(((response.get("results") or {}).get("messages") or []))
    return RtsSearchResult(ok=True, query=query, messages=messages, raw_count=raw_count)


def rts_response_to_caresignal_messages(response: dict[str, Any]) -> list[dict[str, str]]:
    """Convert Slack RTS response messages into CareSignal message objects."""
    output: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    results = (response.get("results") or {}).get("messages") or []

    for index, item in enumerate(results):
        fallback_user = str(item.get("author_name") or item.get("author_user_id") or "participant")
        fallback_thread = str(item.get("thread_ts") or item.get("message_ts") or f"rts-{index}")
        parsed = parse_slack_text_to_caresignal_message(
            str(item.get("content") or item.get("text") or ""),
            fallback_user=fallback_user,
            fallback_thread=fallback_thread,
        )
        _append_unique(output, seen, parsed)

        context_messages = item.get("context_messages") or {}
        for group_name in ("before", "after"):
            for ctx_index, ctx in enumerate(context_messages.get(group_name, []) or []):
                ctx_user = str(ctx.get("author_name") or ctx.get("author_user_id") or fallback_user)
                ctx_thread = str(ctx.get("thread_ts") or ctx.get("message_ts") or f"{fallback_thread}-{group_name}-{ctx_index}")
                ctx_parsed = parse_slack_text_to_caresignal_message(
                    str(ctx.get("content") or ctx.get("text") or ""),
                    fallback_user=ctx_user,
                    fallback_thread=ctx_thread,
                )
                _append_unique(output, seen, ctx_parsed)

    return output


def _append_unique(
    output: list[dict[str, str]],
    seen: set[tuple[str, str, str]],
    parsed: dict[str, str] | None,
) -> None:
    if not parsed:
        return
    key = (parsed["user"], parsed["thread_id"], parsed["text"])
    if key not in seen:
        seen.add(key)
        output.append(parsed)
