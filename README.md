# Craig Ops — independent backend for Craig Bennett

Craig Bennett, Director of Operations, Dead Brands, LLC. Genuine co-commander:
own compute (Cloudflare Workers), own credentials, own model stack (Workers AI),
own memory (KV), real authority under David > Rock > Craig > workers.

## Layout

- `worker/` — Cloudflare Worker: Telegram webhook + Workers AI brain + KV memory
  + 15-min heartbeat cron + HMAC-secured portal chat endpoint. **This is Craig.**
- `portal/` — drop-in Flask blueprint + chat widget for the CRM portal
  (portal is only a UI client; the brain stays on the Worker).
- `bot/` — long-polling Python bot for the future Oracle VM phase.
- `DEPLOY.md` — exact parent-side deploy steps (2 credential-mediated steps).

## Status

Built and syntax-verified 2026-09-29. Awaiting deploy (Cloudflare API token +
@craig_deadbrands_bot token, both parent-side via approved flows). See DEPLOY.md.

$0/month. Workers free + Workers AI free + KV free.
