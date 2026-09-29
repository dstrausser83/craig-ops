# Craig Ops — Deploy Runbook (parent-side, credential-mediated steps)

Craig's backend is a Cloudflare Worker: Telegram webhook → Workers AI
(`@cf/meta/llama-3.1-8b-instruct`) → KV memory. $0 on the free tier.
Code: `worker/src/index.js` (syntax-verified). This doc is the exact
sequence to take him live. Two credentials are needed; both stay out of
chat/logs — set them via `wrangler secret put` (values pass through only
the terminal that runs the command).

## Prerequisites (one-time, parent via approved flows)

1. **Telegram bot token** for `@craig_deadbrands_bot`
   - Browser task: open the BotFather chat (Telegram Web, David's session),
     the token is in the chat history from the 2026-09-28 creation.
     If the token was rotated or is unrecoverable, send `/token` to
     @BotFather for @craig_deadbrands_bot and use the new one.
   - Alternative Rock-controlled path: `credential_fill` via Secure Vault
     if a card was saved at creation.
2. **Cloudflare API token** (vault card `custom.cloudflare` or equivalent)
   with Workers + KV permissions on David's Cloudflare account.

## Deploy (terminal with `wrangler` installed, `CLOUDFLARE_API_TOKEN` exported)

```bash
cd ~/workspace/craig-ops/worker

# 1. KV namespace (Craig's own memory — separate from everything else)
wrangler kv namespace create CRAIG_KV
# -> paste the returned `id` into wrangler.toml under [[kv_namespaces]]

# 2. Secrets (type/paste values when prompted — never echo them)
wrangler secret put TELEGRAM_BOT_TOKEN
wrangler secret put DAVID_TELEGRAM_ID        # 8883483072
wrangler secret put WEBHOOK_SECRET           # any long random string, e.g. openssl rand -hex 32

# 3. Deploy
wrangler deploy
# -> note the workers.dev URL, e.g. https://craig-ops.<acct>.workers.dev

# 4. Point Telegram at the Worker (run in the SAME terminal, token transient)
curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/setWebhook" \
  --data-urlencode "url=https://craig-ops.<acct>.workers.dev/webhook/${WEBHOOK_SECRET}" \
  | head -c 300
# expect: {"ok":true,...}
# 5. Verify bot identity
curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getMe"
```

## Go-live verification (in order)

1. `curl https://craig-ops.<acct>.workers.dev/health` → `{"ok":true,...}`
2. David opens @craig_deadbrands_bot, sends `/start` → Craig answers with
   the online message and registers David's ID in KV.
3. David sends a normal message → Craig replies conversationally.
4. In the "David + Craig HQ" group: mention `@craig_deadbrands_bot` →
   Craig replies in-thread.
5. `/status` → shows stack, Rock mode, open tasks.
6. Wait 15 min → `/health` shows a fresh `last_heartbeat`.

## Post-deploy (Craig's own credential custody — David's order)

Once live, Craig mints/stores his own credential record in the Drive
folder "Craig — Credentials" (david@deadbrands.co Drive, shared with
dstrausser83@gmail.com): Worker URL (public), KV namespace id (not secret),
bot username (public). The bot token and webhook secret stay ONLY in
wrangler secrets — never in Drive, chat, or logs.

## Fallback command test (do once)

1. In KV (or via a `/rock down` command added later), set `rock_mode=down`.
2. David messages Craig → Craig acknowledges fallback command and reports
   directly.
3. Set back to `online` → normal chain resumes (David > Rock > Craig).

## Costs

$0. Workers free: 100k req/day. Workers AI free: 10k neurons/day
(chat uses a few hundred/day). KV free: 1 GB, 100k reads/day.
Cron triggers included on free.

## Optional: craig.deadbrands.co

After deploy, add a Custom Domain in the Cloudflare dashboard
(Workers → craig-ops → Settings → Domains): `craig.deadbrands.co`
(requires deadbrands.co on Cloudflare DNS). Then Telegram's webhook URL
and `CRAIG_WORKER_URL` become `https://craig.deadbrands.co/webhook/...`.
Cosmetic only — the workers.dev URL works fine.
