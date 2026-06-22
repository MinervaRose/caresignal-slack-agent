# ♡ CareSignal

**AI that helps humans care better in busy Slack communities.**

CareSignal is a Slack Agent for Good project built for the Slack Agent Builder Challenge. It helps moderators, mentors, and community leads surface buried questions, unresolved blockers, overload signals, follow-up gaps, and quiet voices in fast-moving Slack channels.

Busy Slack communities often reward the loudest and fastest participants. CareSignal helps make support more legible for quieter, newer, neurodivergent, anxious, or simply overwhelmed participants — without labeling them.

## What it does

CareSignal turns Slack context into a short, human-reviewable care brief:

- **Buried questions** — questions that may have been missed.
- **Unresolved blockers** — people who may be unable to continue.
- **Overload signals** — signs that the channel is too noisy to navigate.
- **Follow-up gaps** — promised resources or answers that need closure.
- **Quiet voices** — useful contributions that may have been ignored.

Each signal includes evidence, why it matters, a suggested next kind action, and human-review buttons:

- `Resolved`
- `Assign follow-up`
- `Needs context`

CareSignal does **not** diagnose, classify, or label participants. It detects support patterns and asks humans to decide what to do next.

## Slack commands

| Command | Purpose |
|---|---|
| `/caresignal help` | Show available commands. |
| `/caresignal demo` | Post a synthetic noisy support-channel scenario. |
| `/caresignal brief` | Generate a reliable Care Brief from packaged demo context. |
| `/caresignal live` | Analyze recent messages from the current Slack channel. |
| `/caresignal rts` | Explain the Real-Time Search workflow. |
| `@CareSignal rts brief` | Attempt Slack Real-Time Search via `assistant.search.context`. |

## Retrieval modes

CareSignal supports three context paths:

1. **Demo context** — stable synthetic data for judges and video demonstration.
2. **Live channel history** — retrieves recent messages from the current channel with Slack Web API channel history.
3. **Real-Time Search path** — calls Slack `assistant.search.context` from an app mention using an `action_token`; if sandbox RTS returns no hits, the app reports this honestly and falls back to recent channel history for a usable care queue.

## Tech stack

- Python
- Slack Bolt for Python
- Slack Socket Mode
- Slack Block Kit
- Slack Web API channel history
- Slack Real-Time Search API path: `assistant.search.context`
- Pytest

## Local setup

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Fill `.env` with your Slack credentials:

```env
SLACK_BOT_TOKEN=xoxb-...
SLACK_SIGNING_SECRET=...
SLACK_APP_TOKEN=xapp-...
```

Run tests:

```powershell
.venv\Scripts\python.exe -m pytest
```

Run the Slack app locally:

```powershell
.venv\Scripts\python.exe -m src.slack_app.server
```

## Required Slack setup

Bot scopes:

```text
commands
chat:write
channels:read
channels:history
app_mentions:read
search:read.public
```

Socket Mode app-level token scope:

```text
connections:write
```

Event subscription:

```text
app_mention
```

After adding scopes or events, reinstall the app to the sandbox workspace.

## Demo flow

In a channel where CareSignal has been added:

```text
/caresignal demo
/caresignal live
```

Then click `Assign follow-up` and `Needs context` on two signals.

For the RTS path:

```text
@CareSignal rts brief
```

## Ethics and safety stance

CareSignal is not “AI that cares.” It is **AI that helps humans care better**.

It detects patterns, not identities. It does not infer disability, anxiety, vulnerability, motivation, or personal traits. It surfaces possible care gaps for human review and keeps the human accountable for all decisions.

## Submission materials

See:

- `docs/architecture.md`
- `docs/architecture_diagram.svg`
- `docs/demo_script.md`
- `docs/devpost_submission.md`
- `docs/judge_testing.md`
- `docs/ethics_and_safety.md`
- `docs/submission_checklist.md`

## License

MIT
