from src.slack_app.rts import rts_response_to_caresignal_messages, default_care_rts_queries
from src.slack_app.blocks import rts_setup_blocks


def test_rts_response_parses_demo_style_results():
    response = {
        "ok": True,
        "results": {
            "messages": [
                {
                    "author_name": "CareSignal",
                    "message_ts": "123.456",
                    "content": "*Ana* · `t1`\nHi, I'm stuck on the API auth step. Can someone help?",
                }
            ]
        },
    }

    converted = rts_response_to_caresignal_messages(response)

    assert converted == [
        {"user": "Ana", "thread_id": "t1", "text": "Hi, I'm stuck on the API auth step. Can someone help?"}
    ]


def test_rts_response_includes_context_messages():
    response = {
        "ok": True,
        "results": {
            "messages": [
                {
                    "author_name": "Sam",
                    "message_ts": "1",
                    "content": "I am overwhelmed by this channel.",
                    "context_messages": {
                        "after": [
                            {
                                "author_name": "Maya",
                                "message_ts": "2",
                                "content": "You do not need to read every thread.",
                            }
                        ]
                    },
                }
            ]
        },
    }

    converted = rts_response_to_caresignal_messages(response)

    assert any(message["user"] == "Sam" for message in converted)
    assert any(message["user"] == "Maya" for message in converted)


def test_default_rts_queries_are_care_specific():
    queries = default_care_rts_queries(channel_name="general")
    joined = " ".join(queries).lower()

    assert "overwhelmed" in joined
    assert "asking for help" in joined
    assert "follow" in joined


def test_rts_setup_blocks_explain_app_mention():
    text_dump = str(rts_setup_blocks())
    assert "@CareSignal rts brief" in text_dump
    assert "action_token" in text_dump
    assert "search:read.public" in text_dump


def test_default_rts_queries_include_demo_literals():
    queries = default_care_rts_queries(channel_name="general")
    joined = " ".join(queries).lower()
    assert "invalid token" in joined
    assert "starter notebook" in joined
    assert "overwhelmed 200 messages" in joined
    assert "submission checklist" in joined
