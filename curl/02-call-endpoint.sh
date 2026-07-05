#!/usr/bin/env bash
# Walk a full x402 handshake against a Hermes Plant paid endpoint. Shows the
# 402 challenge, prints the headers about to be signed, signs via a tiny Node
# helper, and replays the request with the PAYMENT-SIGNATURE header attached.
set -euo pipefail

BASE="${HERMES_BASE_URL:-https://hermesplant.com}"
ENDPOINT="${HERMES_ENDPOINT:-/agent-services/dealanalyzer}"

if [[ -z "${WALLET_PRIVATE_KEY:-}" ]]; then
  echo "Set WALLET_PRIVATE_KEY to a 0x-prefixed EOA private key on Base mainnet."
  exit 2
fi

PAYLOAD='{
  "cashflows": [-1000000, 250000, 250000, 300000, 400000],
  "discountRate": 0.10
}'

echo "## Step 1 - unpaid POST returns 402"
RESP=$(curl -sS -D /tmp/hermes-headers.txt -o /tmp/hermes-body.txt -w "%{http_code}" \
  -X POST "$BASE$ENDPOINT" \
  -H 'Content-Type: application/json' \
  -d "$PAYLOAD")
echo "HTTP $RESP"
echo "Response headers:"
grep -iE '^(payment-required|x-payment|content-type):' /tmp/hermes-headers.txt
echo "Body:"
cat /tmp/hermes-body.txt
echo

if [[ "$RESP" != "402" ]]; then
  echo "Expected 402 but got $RESP - endpoint may have changed or already paid."
  exit 3
fi

# Pull the base64-encoded PAYMENT-REQUIRED challenge from the headers.
CHALLENGE_B64=$(grep -i '^payment-required:' /tmp/hermes-headers.txt | head -1 | awk -F': ' '{print $2}' | tr -d '\r')
if [[ -z "$CHALLENGE_B64" ]]; then
  echo "No PAYMENT-REQUIRED header - endpoint may not be x402-protected."
  exit 4
fi

echo "## Step 2 - decoded challenge"
CHALLENGE=$(echo "$CHALLENGE_B64" | base64 -d)
echo "$CHALLENGE" | jq '.'
echo

echo "## Step 3 - sign EIP-712 USDC authorization (Node helper)"
SIGNATURE=$(node ./sign.mjs "$CHALLENGE")
echo "Signature: ${SIGNATURE:0:30}..."
echo

echo "## Step 4 - replay request with PAYMENT-SIGNATURE"
curl -sS -X POST "$BASE$ENDPOINT" \
  -H 'Content-Type: application/json' \
  -H "PAYMENT-SIGNATURE: $SIGNATURE" \
  -d "$PAYLOAD" | jq '.'
