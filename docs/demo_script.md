# CareSignal Demo Video Notes

This file documents the final CareSignal demo video submitted with the project.

## Video goal

The demo video is designed to show CareSignal functioning inside a Slack developer sandbox in under three minutes.

It demonstrates:

* the problem CareSignal addresses;
* the Slack commands and app interaction;
* Care Brief generation;
* human-review actions;
* live Slack channel history retrieval;
* Real-Time Search context retrieval through `assistant.search.context`.

## Final video structure

### 0:00–0:15 — Problem

The video introduces the problem: busy Slack communities can move too quickly for moderators, mentors, and community leads to notice every support need.

CareSignal is framed as a tool that helps humans notice buried questions, unresolved blockers, overload signals, follow-up gaps, and overlooked contributions.

### 0:15–0:45 — Demo scenario

The video shows CareSignal running in a Slack developer sandbox.

Command shown:

```text
/caresignal demo
```

This posts a synthetic support-channel scenario. The demo uses synthetic data only, so no real participant data is exposed.

### 0:45–1:25 — Care Brief

The video shows CareSignal generating a Care Brief.

Command shown:

```text
/caresignal brief
```

The Care Brief surfaces support signals such as:

* overload signal;
* unresolved blocker;
* follow-up gap;
* quiet or overlooked contribution.

The brief is shown inside Slack using Block Kit.

### 1:25–1:50 — Human review actions

The video shows the human-review buttons in action.

Actions shown include:

```text
Assign follow-up
Needs context
```

This demonstrates the core design principle:

```text
AI surfaces signals. Humans decide.
```

### 1:50–2:15 — Live Slack context

The video shows CareSignal analyzing recent channel history.

Command shown:

```text
/caresignal live
```

This demonstrates that CareSignal is not limited to static demo data. It can retrieve recent Slack channel context and produce a Care Brief from it.

### 2:15–2:40 — Real-Time Search path

The video shows the Real-Time Search workflow through an app mention.

Command shown:

```text
@CareSignal rts brief
```

The output demonstrates the Real-Time Search path through:

```text
assistant.search.context
```

The demo shows retrieved RTS context being transformed into the same Care Brief workflow.

### 2:40–2:55 — Closing

The video closes with CareSignal’s main message:

```text
CareSignal: AI that helps humans care better.
```

## Notes

The architecture diagram is submitted separately as part of the Devpost submission materials.

The video focuses on the app functioning inside Slack rather than presenting the architecture diagram in detail.

## Public video link

```text
https://youtu.be/Q9j0i6mnlc0
```

