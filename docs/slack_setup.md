# Slack Setup for CareSignal

## 1. Create / open the Slack app

Create a Slack app named `CareSignal` in the developer sandbox.

Development sandbox used in this project:

```text
https://caresignal-sandbox.enterprise.slack.com
```

If the workspace dropdown is empty during app creation, first open/sign into the sandbox URL, then return to `https://api.slack.com/apps`.

## 2. Enable Socket Mode

Create an app-level token with:

```text
connections:write
```

Save it locally in `.env` as:

```env
SLACK_APP_TOKEN=xapp-...
```

## 3. Bot token scopes

In **OAuth & Permissions**, add:

```text
commands
chat:write
channels:read
channels:history
app_mentions:read
search:read.public
```

Reinstall the app after changing scopes.

Save the bot token locally as:

```env
SLACK_BOT_TOKEN=xoxb-...
```

## 4. Signing secret

From **Basic Information → App Credentials**, copy the signing secret into `.env`:

```env
SLACK_SIGNING_SECRET=...
```

Do not use the old verification token.

## 5. Slash command

Create one slash command:

```text
Command: /caresignal
Request URL: https://example.com/slack/commands
Short description: Generate a human-reviewable Care Brief
Usage hint: demo | live | brief | rts | help
```

The placeholder URL is acceptable for Socket Mode local development; events arrive through the app-level token connection.

## 6. Event subscriptions

Enable Event Subscriptions and subscribe to bot event:

```text
app_mention
```

If Slack requires a Request URL, use a placeholder for now while developing with Socket Mode.

Reinstall the app after adding the event.

## 7. Add CareSignal to the demo channel

In the Slack channel, add the app through the channel integration UI. If `/caresignal demo` returns `not_in_channel`, the app has not been added to that channel yet.

## 8. Run locally

```powershell
.venv\Scripts\python.exe -m src.slack_app.server
```

## 9. Test

```text
/caresignal help
/caresignal demo
/caresignal live
@CareSignal rts brief
```
