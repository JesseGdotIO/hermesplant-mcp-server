#!/usr/bin/env bash
# Fetch every Hermes Plant discovery surface and summarize it.
# No payment is required. Use this before signing payments to verify that your
# client can read the advertised metadata.
set -euo pipefail

BASE="${HERMES_BASE_URL:-https://hermesplant.com}"

echo "## llms.txt (first 500 bytes)"
curl -s "$BASE/llms.txt" | head -c 500
echo
echo
echo "## openapi.json - info + first 5 paths"
curl -s "$BASE/openapi.json" | jq '{info: .info, paths: (.paths | to_entries | .[0:5] | from_entries)}'
echo
echo "## .well-known/x402 manifest"
curl -s "$BASE/.well-known/x402" | jq '{x402Version, configured, network, payTo, facilitator, openapi}'
echo
echo "## .well-known/api-catalog (RFC 9727)"
curl -s "$BASE/.well-known/api-catalog" | jq '.'
echo
echo "## MCP server card"
curl -s "$BASE/.well-known/mcp/server-card.json" | jq '.'
echo
echo "## Discovery Link header on the homepage"
curl -sI "$BASE/" | grep -i '^link:' || echo "(no Link header)"
