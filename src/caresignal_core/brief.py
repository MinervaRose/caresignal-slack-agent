from .models import CareSignal


def build_care_brief_markdown(signals: list[CareSignal], messages_reviewed: int) -> str:
    high = sum(1 for s in signals if s.priority == "high")
    medium = sum(1 for s in signals if s.priority == "medium")
    low = sum(1 for s in signals if s.priority == "low")

    lines = [
        "# ♡ CareSignal Care Brief",
        "",
        "**Workflow:** Turn live Slack context into a short, human-reviewable support brief.",
        "",
        f"Messages reviewed: **{messages_reviewed}**",
        f"Care gaps surfaced: **{len(signals)}** — High: {high}, Medium: {medium}, Low: {low}",
        "",
        "## Suggested human review queue",
    ]

    if not signals:
        lines.extend(["", "No urgent care signals detected in this sample."])
        return "\n".join(lines)

    for index, signal in enumerate(signals, start=1):
        lines.extend([
            "",
            f"### {index}. {signal.kind} · {signal.priority.title()} · @{signal.user}",
            f"- **Thread:** {signal.thread_id}",
            f"- **Evidence:** {signal.evidence}",
            f"- **Why it matters:** {signal.why_it_matters}",
            f"- **Next kind action:** {signal.next_kind_action}",
            f"- **Suggested action:** {signal.suggested_action}",
        ])
        if signal.rts_query:
            lines.append(f"- **RTS context target:** {signal.rts_query}")

    lines.extend([
        "",
        "---",
        "CareSignal detects patterns, not identities or diagnoses. Human review remains required.",
    ])
    return "\n".join(lines)
