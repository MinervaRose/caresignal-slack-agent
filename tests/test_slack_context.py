from src.slack_app.context import slack_messages_to_caresignal_messages


def test_parses_demo_scenario_messages():
    slack_messages = [
        {"user": "U_BOT", "ts": "1", "text": "♡ CareSignal demo scenario"},
        {"user": "U_BOT", "ts": "2", "text": "*Ana* · `t1`\nHi, I'm stuck on the API auth step."},
    ]

    converted = slack_messages_to_caresignal_messages(slack_messages)

    assert converted == [
        {"user": "Ana", "thread_id": "t1", "text": "Hi, I'm stuck on the API auth step."}
    ]


def test_converts_regular_slack_messages():
    slack_messages = [{"user": "U123", "ts": "1700000000.0001", "text": "I am overwhelmed by this channel."}]

    converted = slack_messages_to_caresignal_messages(slack_messages)

    assert converted[0]["user"] == "U123"
    assert converted[0]["thread_id"] == "1700000000.0001"
    assert "overwhelmed" in converted[0]["text"]
