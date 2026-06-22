# CareSignal Architecture

CareSignal is a Slack-native support-differentiation agent. It uses Slack as the product surface and keeps detection logic in a small, testable Python core.

## Core data flow

```text
Slack channel / app mention / slash command
        ↓
Slack Bolt app over Socket Mode
        ↓
Context retrieval layer
        ├── Demo context: packaged synthetic messages
        ├── Live context: Slack Web API conversations.history
        └── RTS context: assistant.search.context via app mention action_token
        ↓
CareSignal core detector
        ├── buried questions
        ├── unresolved blockers
        ├── overload signals
        ├── follow-up gaps
        └── quiet voices
        ↓
Slack Block Kit Care Brief
        ↓
Human review buttons
        ├── Resolved
        ├── Assign follow-up
        └── Needs context
```

## Components

| Component | File(s) | Role |
|---|---|---|
| Slack entry point | `src/slack_app/server.py` | Receives slash commands, app mentions, and button actions. |
| Block Kit UI | `src/slack_app/blocks.py` | Formats concise Slack Care Briefs and action buttons. |
| Channel context | `src/slack_app/context.py` | Retrieves recent Slack channel history and normalizes messages. |
| RTS adapter | `src/slack_app/rts.py` | Calls `assistant.search.context` and normalizes search results. |
| Signal detector | `src/caresignal_core/signals.py` | Detects care signals from normalized messages. |
| Brief renderer | `src/caresignal_core/brief.py` | Renders terminal/Markdown brief for local verification. |
| Tests | `tests/` | Unit tests for detection, Slack blocks, context, and RTS parsing. |

## Required Slack technologies

CareSignal uses Slack Agent Builder-style interactions through a Slack app, slash commands, app mentions, and Block Kit. It also includes a Real-Time Search integration path through `assistant.search.context`.

RTS requires an `action_token`, so the RTS path uses an app mention:

```text
@CareSignal rts brief
```

If RTS returns no hits in a sandbox, CareSignal reports this transparently and falls back to recent channel history for the human-review queue. This keeps the demo reliable without misrepresenting retrieval provenance.

## Diagram

A submission-ready SVG diagram is included at:

```text
docs/architecture_diagram.svg
```
