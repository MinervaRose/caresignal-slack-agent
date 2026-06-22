# Changelog

## v1.0-rc2

- Compact Slack Care Brief formatting for demo readability.
- Shortened each signal to Evidence, Action, and Retrieval.
- Preserved human-review buttons and RTS/live/demo functionality.


## v1.0-rc1

Submission-level release candidate.

- Consolidates Slack commands: `/caresignal help`, `/caresignal demo`, `/caresignal brief`, `/caresignal live`, `/caresignal rts`, and `@CareSignal rts brief`.
- Adds polished Block Kit Care Brief formatting with human-review buttons.
- Keeps three context modes: synthetic demo context, recent channel history, and RTS app-mention path.
- Adds transparent fallback when RTS succeeds technically but returns no hits in the sandbox.
- Adds submission docs, architecture diagram, judge testing guide, and Devpost draft text.
- Expands tests to cover detection, Slack blocks, context normalization, and RTS query behavior.

## v0.6

- Added app-mention RTS path using `assistant.search.context`.
- Added RTS setup diagnostic command.

## v0.5

- Added `/caresignal live` with recent channel-history retrieval.

## v0.4

- Added `/caresignal demo` and Slack-native synthetic demo scenario.

## v0.3

- Added Slack Bolt slash command and Block Kit care brief.
