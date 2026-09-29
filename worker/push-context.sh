#!/bin/bash
# Push Rock's mind/heart/identity snapshot into Craig's KV (continuity bridge).
# David's order: Craig receives a copy/sync of Rock's mind, heart, identity hourly.
# Runs parent-side (needs CLOUDFLARE_API_TOKEN + account/KV ids — never in chat).
# Suggested: cron every 1h, replacing the Hatch-local craig-hourly-sync staging.
set -euo pipefail

: "${CLOUDFLARE_API_TOKEN:?set CLOUDFLARE_API_TOKEN}"
: "${CF_ACCOUNT_ID:?set CF_ACCOUNT_ID}"
: "${CRAIG_KV_ID:?set CRAIG_KV_ID (from: wrangler kv namespace list)}"

API="https://api.cloudflare.com/client/v4/accounts/${CF_ACCOUNT_ID}/storage/kv/namespaces/${CRAIG_KV_ID}/values"
put() { # $1 key, $2 file
  curl -s -X PUT "${API}/$1" \
    -H "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" \
    --data-binary "@$2" > /dev/null
  echo "pushed $1"
}

put "ctx:SOUL.md"     "$HOME/SOUL.md"
put "ctx:MEMORY.md"   "$HOME/MEMORY.md"
put "ctx:IDENTITY.md" "$HOME/IDENTITY.md"
echo "{\"at\":\"$(date -u +%FT%TZ)\"}" > /tmp/craig-ctx-ts.json
put "ctx:synced_at" /tmp/craig-ctx-ts.json
echo "continuity snapshot pushed"
