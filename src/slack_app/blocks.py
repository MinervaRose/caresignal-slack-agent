from __future__ import annotations

from src.caresignal_core.models import CareSignal


MAX_SIGNALS_IN_SLACK = 5


def care_brief_blocks(
    signals: list[CareSignal],
    *,
    context_label: str = "demo Slack context",
    channel_name: str | None = None,
    messages_reviewed: int | None = None,
    retrieval_note: str | None = None,
) -> list[dict]:
    """Build Slack Block Kit blocks for a compact, judge-demo-ready Care Brief."""
    location = f" in #{channel_name}" if channel_name else ""
    high = sum(1 for signal in signals if signal.priority.lower() == "high")
    medium = sum(1 for signal in signals if signal.priority.lower() == "medium")

    summary_line = f"*{len(signals)} support gaps* surfaced from *{context_label}*{location}."
    if messages_reviewed is not None:
        summary_line += f"\nMessages reviewed: *{messages_reviewed}*."
    if signals:
        summary_line += f"\nPriority mix: *{high} high* · *{medium} medium*."

    blocks: list[dict] = [
        {"type": "header", "text": {"type": "plain_text", "text": "♡ CareSignal Care Brief", "emoji": True}},
        {"type": "section", "text": {"type": "mrkdwn", "text": summary_line}},
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": retrieval_note
                    or "CareSignal turns Slack context into a human-reviewable care queue. Humans decide the next action.",
                }
            ],
        },
        {"type": "divider"},
    ]

    if not signals:
        blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": "No urgent care signals detected."}})
        blocks.append(_ethics_context_block())
        return blocks

    blocks.append(
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Human review queue*\nReview each signal, then choose `Resolved`, `Assign follow-up`, or `Needs context`.",
            },
        }
    )

    for index, signal in enumerate(signals[:MAX_SIGNALS_IN_SLACK]):
        priority = signal.priority.lower()
        priority_icon = "🔴" if priority == "high" else "🟡" if priority == "medium" else "⚪"
        evidence = _compact_text(signal.evidence, max_chars=120)
        action = _compact_text(signal.next_kind_action, max_chars=96)
        retrieval = _compact_text(signal.rts_query or "not set", max_chars=72)
        blocks.append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        f"*{index + 1}. {priority_icon} {signal.kind}* · `{signal.priority}` · @{signal.user}\n"
                        f"*Evidence:* “{evidence}”\n"
                        f"*Action:* {action}\n"
                        f"*Retrieval:* `{retrieval}`"
                    ),
                },
            }
        )
        blocks.append(
            {
                "type": "actions",
                "block_id": f"care_signal_actions_{index}",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Resolved"},
                        "action_id": "resolved",
                        "value": f"{index}:{signal.kind}:{signal.user}",
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Assign follow-up"},
                        "style": "primary",
                        "action_id": "assign_followup",
                        "value": f"{index}:{signal.kind}:{signal.user}",
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Needs context"},
                        "action_id": "needs_context",
                        "value": f"{index}:{signal.kind}:{signal.user}",
                    },
                ],
            }
        )
        blocks.append({"type": "divider"})

    blocks.append(_ethics_context_block())
    return blocks


def _compact_text(text: str | None, *, max_chars: int = 120) -> str:
    """Return short Slack-safe text that stays readable in demo videos."""
    if not text:
        return ""
    normalized = " ".join(str(text).split())
    if len(normalized) <= max_chars:
        return normalized
    return normalized[: max_chars - 1].rstrip() + "…"


def _ethics_context_block() -> dict:
    return {
        "type": "context",
        "elements": [
            {
                "type": "mrkdwn",
                "text": "CareSignal detects patterns, not identities or diagnoses. Human review remains required.",
            }
        ],
    }


def help_blocks() -> list[dict]:
    """Slack help text for the CareSignal command."""
    return [
        {"type": "header", "text": {"type": "plain_text", "text": "♡ CareSignal commands", "emoji": True}},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    "CareSignal is a support-differentiation agent for busy Slack communities.\n\n"
                    "• `/caresignal demo` posts a synthetic noisy support-channel scenario.\n"
                    "• `/caresignal brief` generates a reliable Care Brief from demo context.\n"
                    "• `/caresignal live` analyzes recent messages from the current channel.\n"
                    "• `/caresignal rts` explains the Real-Time Search path.\n"
                    "• `@CareSignal rts brief` attempts Slack Real-Time Search via `assistant.search.context`.\n"
                    "• `/caresignal help` shows this guide."
                ),
            },
        },
    ]


def demo_intro_blocks() -> list[dict]:
    """Blocks posted before the synthetic demo messages."""
    return [
        {"type": "header", "text": {"type": "plain_text", "text": "♡ CareSignal demo scenario", "emoji": True}},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    "This channel will receive a short synthetic learning-community scenario. "
                    "It shows the workflow CareSignal is built to support: buried questions, blockers, overload, "
                    "follow-up gaps, and quiet voices."
                ),
            },
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "Synthetic demo data only. No real participant data is used. Next: run `/caresignal live` or mention `@CareSignal rts brief`.",
                }
            ],
        },
    ]


def rts_setup_blocks() -> list[dict]:
    """Explain how to trigger the RTS path."""
    return [
        {"type": "header", "text": {"type": "plain_text", "text": "♡ CareSignal RTS workflow", "emoji": True}},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    "Real-Time Search uses `assistant.search.context` with an `action_token` from an in-Slack interaction. "
                    "Slash commands do not provide that token, so the RTS path uses an app mention.\n\n"
                    "Try this in a channel where CareSignal has been added:\n"
                    "`@CareSignal rts brief`\n\n"
                    "Required setup: `search:read.public`, `app_mentions:read`, `channels:read`, `channels:history`, "
                    "the `app_mention` event subscription, and reinstalling the app after scope changes."
                ),
            },
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "If RTS returns no hits in a sandbox, CareSignal reports that honestly and can use `/caresignal live` as the working channel-history fallback.",
                }
            ],
        },
    ]
