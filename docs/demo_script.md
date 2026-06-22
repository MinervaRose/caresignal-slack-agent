# CareSignal Demo Video Script — under 3 minutes

## 0:00–0:20 — Problem

Busy Slack learning communities often reward the loudest and fastest participants. The people who need help can be the least visible: someone stuck, someone overwhelmed, someone whose useful suggestion gets buried.

CareSignal helps moderators turn noisy Slack conversations into a short, human-reviewable care brief.

## 0:20–1:00 — Demo scenario

In the Slack sandbox, open `#general` or a demo channel where CareSignal has been added.

Run:

```text
/caresignal demo
```

Explain that the app posts synthetic demo messages only, so no real participant data is used.

## 1:00–1:45 — Working live analysis

Run:

```text
/caresignal live
```

Show the Care Brief:

- overload signal;
- unresolved blockers;
- follow-up gap;
- quiet voice;
- evidence and next kind action;
- human-review buttons.

Click:

- `Assign follow-up` on the overload or blocker signal;
- `Needs context` on the quiet voice or follow-up gap.

Say: CareSignal does not decide for the team. It makes support gaps legible and asks humans to choose the next action.

## 1:45–2:20 — Real-Time Search path

Mention CareSignal in the channel:

```text
@CareSignal rts brief
```

Explain that this path calls Slack `assistant.search.context` through an app-mention action token. If the sandbox returns no RTS hits, CareSignal reports that honestly and uses channel history as a transparent fallback.

## 2:20–2:45 — Architecture

Show `docs/architecture_diagram.svg`.

Slack command or mention → context retrieval → CareSignal detector → Block Kit Care Brief → human review actions.

## 2:45–3:00 — Impact

CareSignal is for learning cohorts, volunteer groups, support teams, and online communities where people can disappear in message noise. It helps humans care better without labeling participants.
