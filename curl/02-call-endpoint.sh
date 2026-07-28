#!/usr/bin/env bash
# Inspect the live CashflowLens x402 challenge without signing or spending.
set -euo pipefail

for command_name in curl jq base64; do
  if ! command -v "$command_name" >/dev/null 2>&1; then
    echo "Missing required command: $command_name" >&2
    exit 2
  fi
done

BASE="${HERMES_BASE_URL:-https://hermesplant.com}"
ENDPOINT="/api/agent-services/cashflowlens/analyze"
EXPECTED_NETWORK="eip155:8453"
MAX_ATOMIC_USDC=200000

PAYLOAD='{
  "cashflows": [-1000000, 250000, 250000, 300000, 400000],
  "discountRate": 0.10,
  "periodsPerYear": 1
}'

TMP_DIR="$(mktemp -d)"
trap 'rm -rf -- "$TMP_DIR"' EXIT
HEADERS="$TMP_DIR/headers.txt"
BODY="$TMP_DIR/body.txt"

echo "## Unpaid POST returns the x402 challenge"
STATUS=$(curl -sS -D "$HEADERS" -o "$BODY" -w "%{http_code}" \
  -X POST "$BASE$ENDPOINT" \
  -H 'Content-Type: application/json' \
  -d "$PAYLOAD")

echo "HTTP $STATUS"
if [[ "$STATUS" != "402" ]]; then
  echo "Expected HTTP 402; refusing to continue."
  cat "$BODY"
  exit 3
fi

CHALLENGE_B64=$(grep -i '^payment-required:' "$HEADERS" | head -1 | awk -F': ' '{print $2}' | tr -d '\r')
if [[ -z "$CHALLENGE_B64" ]]; then
  echo "Missing PAYMENT-REQUIRED header."
  exit 4
fi

CHALLENGE=$(printf '%s' "$CHALLENGE_B64" | base64 -d)
printf '%s\n' "$CHALLENGE" | jq '.'

printf '%s\n' "$CHALLENGE" | jq -e \
  --arg network "$EXPECTED_NETWORK" \
  --argjson max "$MAX_ATOMIC_USDC" \
  '.accepts | any(.network == $network and ((.amount | tonumber) <= $max))' \
  >/dev/null

echo
echo "Verified: at least one Base mainnet option is at or below 200000 atomic USDC."
echo "No signature was created and no payment was made."
echo "Use the guarded Python or TypeScript client for a paid call."
