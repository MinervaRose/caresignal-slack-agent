from src.slack_app.handlers import build_demo_care_brief_blocks, demo_messages_for_channel
from src.slack_app.blocks import help_blocks


def test_care_brief_blocks_include_actions():
    blocks = build_demo_care_brief_blocks(channel_name="ai-challenge-support")
    action_ids = []
    for block in blocks:
        if block.get("type") == "actions":
            action_ids.extend(element.get("action_id") for element in block.get("elements", []))

    assert "resolved" in action_ids
    assert "assign_followup" in action_ids
    assert "needs_context" in action_ids


def test_care_brief_blocks_have_ethics_footer():
    blocks = build_demo_care_brief_blocks()
    text_dump = str(blocks)
    assert "not identities or diagnoses" in text_dump
    assert "Human review" in text_dump


def test_care_brief_blocks_do_not_overclaim_live_context():
    blocks = build_demo_care_brief_blocks(channel_name="general")
    text_dump = str(blocks)
    assert "demo Slack context" in text_dump
    assert "live Slack context" not in text_dump


def test_demo_messages_for_channel_are_readable():
    lines = demo_messages_for_channel()
    assert len(lines) >= 5
    assert any("overwhelmed" in line for line in lines)
    assert any("API auth" in line for line in lines)


def test_help_blocks_list_supported_commands():
    text_dump = str(help_blocks())
    assert "/caresignal demo" in text_dump
    assert "/caresignal brief" in text_dump
    assert "/caresignal help" in text_dump


def test_help_blocks_include_live_and_rts_paths():
    text_dump = str(help_blocks())
    assert "/caresignal live" in text_dump
    assert "/caresignal rts" in text_dump
    assert "@CareSignal rts brief" in text_dump
