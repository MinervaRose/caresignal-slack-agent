# Submission Checklist

## App functionality

- [ ] `/caresignal help` works.
- [ ] `/caresignal demo` works.
- [ ] `/caresignal live` works.
- [ ] Human-review buttons work.
- [ ] `@CareSignal rts brief` works or reports RTS status transparently.
- [ ] App is installed in the Slack developer sandbox.
- [ ] CareSignal is added to the demo channel.

## Slack configuration

- [ ] Bot scopes: `commands`, `chat:write`, `channels:read`, `channels:history`, `app_mentions:read`, `search:read.public`.
- [ ] App-level token scope: `connections:write`.
- [ ] Socket Mode enabled.
- [ ] Event subscription: `app_mention`.
- [ ] App reinstalled after scope/event changes.

## Devpost

- [ ] Track: Slack Agent for Good.
- [ ] Demo video under 3 minutes.
- [ ] Architecture diagram uploaded.
- [ ] Sandbox URL provided.
- [ ] Judge access granted to `slackhack@salesforce.com` and `testing@devpost.com`.
- [ ] GitHub repo public or accessible as required.
- [ ] Description and impact text completed.

## Safety

- [ ] Demo uses synthetic data only.
- [ ] No confidential/personal data in video.
- [ ] No claim that CareSignal diagnoses or labels participants.
