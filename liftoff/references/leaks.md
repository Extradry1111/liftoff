# Leak Scan: what ships with the share link

Templates copy the bot's **description, skills, routines, relevant memories and many first-party plugins**. Anything written in those ships with the link. Grok Bot doesn't strip secrets for you.

These **don't** travel: conversation history, the author's computer, logins, custom code and private MCP servers.

## Blocking leaks (scan exits 1)

| Kind | Looks like |
|---|---|
| API key | `sk-…`, `xai-…`, `sk-ant-…`, `sk-proj-…` |
| GitHub / AWS / Slack tokens | `ghp_…`, `AKIA…`, `xoxb-…` |
| Bearer token | `Bearer eyJ…` |
| Secret value | `api_key = …`, `token: …`, `password=…` |
| Webhook URL | Slack or Discord webhook links |
| Email | any address except `example.com` / GitHub noreply |
| Phone number | `+1 415-555-0198`, `(415) 555-0198` |
| Private address | `192.168.x.x`, `10.x.x.x`, `172.16-31.x.x` |
| Private doc link | Google Docs/Drive, Notion |

## Warnings (won't travel)

These references make the bot break for everyone who copies it: logins, custom scripts, private MCP servers, localhost and "my computer".

## Fixes

- **Secret:** delete it. If the bot needs the service, switch to built-in web/X search, or tell the user to connect their own.
- **Personal data:** replace it with a placeholder (`[YOUR_EMAIL]`) or turn it into a first-message question.
- **Won't travel:** rewrite the step to use built-in tools.
- **Memories:** check that nothing personal (finances, health, family) sits in memories that would be copied.

When you report a leak, never repeat the full value. Show the first 4 characters and `…`.
