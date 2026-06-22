# Judge Testing Guide

## Sandbox

CareSignal was developed in a Slack Developer Sandbox.

Sandbox URL used during development:

```text
https://caresignal-sandbox.enterprise.slack.com
```

Before final submission, invite or grant access to:

```text
slackhack@salesforce.com
testing@devpost.com
```

## Recommended test flow

1. Open a channel where CareSignal has been added, such as `#general`.
2. Run:

```text
/caresignal help
```

3. Run:

```text
/caresignal demo
```

4. Run:

```text
/caresignal live
```

5. Click `Assign follow-up` on one signal.
6. Click `Needs context` on another signal.
7. Try the Real-Time Search path:

```text
@CareSignal rts brief
```

## Notes

- `/caresignal demo` posts synthetic messages into the channel.
- `/caresignal live` analyzes recent channel history.
- `@CareSignal rts brief` attempts Slack Real-Time Search. If RTS returns no hits in the sandbox, the app reports that honestly and uses channel history as fallback.
