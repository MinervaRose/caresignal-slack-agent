"""Slack Bolt entry point for CareSignal v1.0 release candidate."""

from __future__ import annotations

import os
import re
from typing import Any

from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk.errors import SlackApiError

from src.slack_app.blocks import demo_intro_blocks, help_blocks, rts_setup_blocks
from src.slack_app.handlers import (
    build_demo_care_brief_blocks,
    build_live_care_brief_blocks,
    build_rts_care_brief_blocks,
    demo_messages_for_channel,
)

load_dotenv()

MENTION_RE = re.compile(r"<@[^>]+>")


def create_app() -> App:
    """Create the Slack Bolt app for Socket Mode local development."""
    app = App(
        token=os.environ.get("SLACK_BOT_TOKEN"),
        signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
    )

    @app.command("/caresignal")
    def handle_caresignal_command(ack: Any, respond: Any, command: dict, client: Any) -> None:
        ack()
        text = (command.get("text") or "").strip().lower()
        channel_id = command.get("channel_id")
        channel_name = command.get("channel_name")

        if text in {"", "help"}:
            respond(response_type="ephemeral", text="♡ CareSignal help", blocks=help_blocks())
            return

        if text == "demo":
            if not channel_id:
                respond(response_type="ephemeral", text="CareSignal could not identify the current channel.")
                return
            try:
                _post_demo_scenario(client, channel_id)
            except SlackApiError as exc:
                error = exc.response.get("error", "unknown_error") if exc.response else "unknown_error"
                respond(
                    response_type="ephemeral",
                    text=(
                        f"CareSignal could not post the demo scenario: `{error}`. "
                        "Make sure the app has been added to this channel, then try `/caresignal demo` again."
                    ),
                )
                return
            respond(response_type="ephemeral", text="♡ Demo scenario posted. Run `/caresignal live` next.")
            return

        if text == "brief":
            respond(
                response_type="ephemeral",
                text="♡ CareSignal Care Brief",
                blocks=build_demo_care_brief_blocks(channel_name=channel_name),
            )
            return

        if text in {"live", "channel", "context"}:
            if not channel_id:
                respond(response_type="ephemeral", text="CareSignal could not identify the current channel.")
                return
            respond(
                response_type="ephemeral",
                text="♡ CareSignal Live Care Brief",
                blocks=build_live_care_brief_blocks(client, channel_id=channel_id, channel_name=channel_name),
            )
            return

        if text in {"rts", "rts brief", "search"}:
            respond(response_type="ephemeral", text="♡ CareSignal RTS workflow", blocks=rts_setup_blocks())
            return

        respond(response_type="ephemeral", text="Try `/caresignal demo`, `/caresignal live`, `/caresignal rts`, `/caresignal brief`, or `/caresignal help`.")

    @app.event("app_mention")
    def handle_app_mention(event: dict, client: Any, say: Any) -> None:
        channel_id = event.get("channel")
        text = MENTION_RE.sub("", event.get("text") or "").strip().lower()
        thread_ts = event.get("thread_ts") or event.get("ts")
        action_token = event.get("action_token")
        channel_name = _safe_channel_name(client, channel_id)

        if "rts" in text or "brief" in text or text == "":
            client.chat_postMessage(
                channel=channel_id,
                thread_ts=thread_ts,
                text="♡ CareSignal RTS Care Brief",
                blocks=build_rts_care_brief_blocks(
                    client,
                    channel_id=channel_id,
                    channel_name=channel_name,
                    action_token=action_token,
                ),
            )
            return

        say(text="Try `@CareSignal rts brief` to attempt Real-Time Search, or `/caresignal help` for commands.", thread_ts=thread_ts)

    @app.action("resolved")
    def handle_resolved(ack: Any, body: dict, respond: Any) -> None:
        ack()
        _respond_to_human_action(respond, body, "Resolved", "This signal has been marked as handled by a human reviewer.")

    @app.action("assign_followup")
    def handle_assign_followup(ack: Any, body: dict, respond: Any) -> None:
        ack()
        _respond_to_human_action(respond, body, "Assign follow-up", "A human follow-up should be assigned for this care signal.")

    @app.action("needs_context")
    def handle_needs_context(ack: Any, body: dict, respond: Any) -> None:
        ack()
        _respond_to_human_action(respond, body, "Needs context", "This care signal needs more Slack context before a decision.")

    return app


def _post_demo_scenario(client: Any, channel_id: str) -> None:
    client.chat_postMessage(channel=channel_id, text="♡ CareSignal demo scenario", blocks=demo_intro_blocks())
    for line in demo_messages_for_channel():
        client.chat_postMessage(channel=channel_id, text=line)


def _safe_channel_name(client: Any, channel_id: str | None) -> str | None:
    if not channel_id:
        return None
    try:
        response = client.conversations_info(channel=channel_id)
    except SlackApiError:
        return None
    if not response.get("ok"):
        return None
    channel = response.get("channel") or {}
    return channel.get("name")


def _respond_to_human_action(respond: Any, body: dict, label: str, detail: str) -> None:
    user_id = body.get("user", {}).get("id", "human reviewer")
    try:
        value = body.get("actions", [{}])[0].get("value", "")
    except (KeyError, IndexError, TypeError):
        value = ""
    signal_context = f"\nSignal: `{value}`" if value else ""
    respond(
        response_type="ephemeral",
        replace_original=False,
        text=f"♡ {label}: {detail}",
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"♡ *{label}*\n{detail}\nMarked by <@{user_id}>.{signal_context}",
                },
            }
        ],
    )


def main() -> None:
    app = create_app()
    app_token = os.environ.get("SLACK_APP_TOKEN")
    if not app_token:
        raise RuntimeError("Missing SLACK_APP_TOKEN. Add it to your .env file for Socket Mode local development.")
    SocketModeHandler(app, app_token).start()


if __name__ == "__main__":
    main()
