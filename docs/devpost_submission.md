# Devpost Submission Draft

## Project name

CareSignal

## Elevator pitch

CareSignal turns busy Slack conversations into care briefs, helping moderators spot unanswered questions, unresolved blockers, and overlooked members.

## Track

Slack Agent for Good

## Built with

Slack Agent Builder, Slack Bolt for Python, Slack Socket Mode, Slack Block Kit, Slack Web API, Slack Real-Time Search API, Python, Pytest.

## What it does

CareSignal helps moderators, mentors, and community leads surface support gaps in busy Slack channels. It identifies buried questions, unresolved blockers, overload signals, follow-up gaps, and quiet voices, then turns them into a short Care Brief with human-review actions.

## The problem

Busy Slack communities often reward the loudest and fastest participants. The people who need support may be quieter, newer, overwhelmed, or simply unable to keep up with message volume. Their questions can disappear in the noise.

## Impact

CareSignal can help learning cohorts, volunteer groups, support teams, and community spaces notice people who might otherwise fall through the cracks. It is accessibility-adjacent and education-oriented without labeling or diagnosing participants.

## How we built it

CareSignal is a Slack-native app built with Slack Bolt for Python and Socket Mode. It supports slash commands, app mentions, and Block Kit buttons. The detector is a small testable Python core that receives normalized Slack messages and produces care signals. The app can analyze packaged demo context, recent channel history, and an RTS pathway through `assistant.search.context`.

## What makes it different

This is not a generic Slack summarizer. CareSignal is designed around a specific workflow: making support gaps legible for human review. Its core output is not a summary; it is a care queue with evidence, rationale, and next kind actions.

## Safety note

CareSignal detects patterns, not identities or diagnoses. Human review remains required. The demo uses synthetic data.
