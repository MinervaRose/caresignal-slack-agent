from pathlib import Path
import json

from src.caresignal_core.signals import detect_signals
from src.caresignal_core.brief import build_care_brief_markdown


def main() -> None:
    sample_path = Path(__file__).resolve().parents[1] / "sample_data" / "synthetic_slack_messages.json"
    messages = json.loads(sample_path.read_text(encoding="utf-8"))
    signals = detect_signals(messages)
    print(build_care_brief_markdown(signals, messages_reviewed=len(messages)))


if __name__ == "__main__":
    main()
