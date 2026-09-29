# Craig standup — parent handoff checklist

Everything buildable without credentials is DONE and verified (see below).
These are the only remaining steps, all parent-side (browser + vault flows
a subagent cannot touch).

## A. Deploy the Worker (needs Cloudflare API token via vault)

Follow `DEPLOY.md` sections Deploy → Go-live verification. Exact commands
are in that file. Expected time: ~10 min.

## B. Bot token (needs browser → BotFather)

1. Browser task: Telegram Web (David's session) → @BotFather chat →
   copy the `@craig_deadbrands_bot` token from the 2026-09-28 creation
   history. If unrecoverable: `/token` → @craig_deadbrands_bot.
2. `wrangler secret put TELEGRAM_BOT_TOKEN` (paste once, never echo).
3. `setWebhook` per DEPLOY.md §4. David sends `/start` → Craig answers.

## C. Bot HQ wiring (browser task `browser-task:42009492-...` completed 16:49 EDT)

Verify in Telegram (David's session or bot API):
1. Private group "Bot HQ" exists and contains @craig_deadbrands_bot.
2. Privacy mode DISABLED on @craig_deadbrands_bot (BotFather → /setprivacy)
   — required for Craig to see group messages in Bot HQ.
3. Send a test mention `@craig_deadbrands_bot ping` in Bot HQ → Craig replies.
4. If the group was never created, create it now and add the bot.

## D. Portal chat box (needs PC file copy + portal restart)

1. Copy `portal/craig_chat.py` → `<portal>/app/craig_chat.py` on the PC.
2. Copy `portal/craig_panel.html` → `<portal>/app/templates/craig_panel.html`.
3. Register the blueprint in the portal's `main.py` (see docstring).
4. Set `CRAIG_WORKER_URL` + `CRAIG_PORTAL_SECRET` env on the portal host;
   `wrangler secret put PORTAL_SECRET` with the same value.
5. Restart portal, open /craig/panel as David → chat works.

## E. Continuity sync (hourly)

Cron on a credential-holding host (Hatch VM is fine — it only PUSHES):
`worker/push-context.sh` every 1h with CLOUDFLARE_API_TOKEN, CF_ACCOUNT_ID,
CRAIG_KV_ID. This replaces the Hatch-local craig-hourly-sync staging.

## F. Fallback command test (do once, David awake)

Set KV `rock_mode=down` → David messages Craig → Craig takes direct
command → set back `online`.

## Verified tonight (subagent, no credentials needed)

- `worker/src/index.js` — node syntax OK; 10/10 logic tests pass with
  stubbed AI/KV (auth, commands, tasks, group mention filter, webhook
  secret guard, portal HMAC endpoint, health, history persistence).
- `portal/craig_chat.py` — python AST OK.
- Repo: github.com/dstrausser83/craig-ops (public, 2 commits).
- @craig_deadbrands_bot EXISTS (t.me page live, "Craig Bennett").
- "David + Craig HQ" private group exists with bot as member (per 16:46 note).

## Known limits (honest)

- Craig's brain is Workers AI (Llama 3.1 8B) — strong for ops chat, not a
  70B reasoner. Upgrade path: Oracle Ampere VM + Ollama (needs David's
  hands for a 2nd account — original RUNBOOK.md Phase 1).
- No shell on Workers: `/run` is intentionally absent; Craig's tools are
  tasks, handoffs, heartbeat, and HTTP-callable actions (phase 2).
- End-to-end Telegram proof (David→Craig→David) is BLOCKED on A+B above.
