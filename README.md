# Hermes Plant MCP Server

Runnable MCP server and integration examples for [Hermes Plant](https://hermesplant.com): deterministic finance and quant APIs that AI agents call and pay for per call over [x402](https://x402.org). No API keys, no shared secrets, no hallucinated math.

**What's here**: a runnable stdio MCP bridge for registry crawlers and local clients, plus drop-in examples in `curl`, TypeScript, Python, [CrewAI](https://www.crewai.com/), [LangChain](https://www.langchain.com/), and MCP client configs for Claude Desktop / Cline / Cursor.

## What is Hermes Plant?

A hosted catalog of deterministic finance + quant endpoints AI agents call and pay for per call:

| Endpoint | Use it for | Hosted path |
|---|---|---|
| **DealAnalyzer** | DCF, IRR, XIRR, NPV | [/agent-services/dealanalyzer](https://hermesplant.com/agent-services/dealanalyzer) |
| **Waterfall** | LP/GP private-equity distribution waterfalls | [/agent-services/waterfall](https://hermesplant.com/agent-services/waterfall) |
| **Options** | Black-Scholes pricing + Greeks | [/agent-services/options](https://hermesplant.com/agent-services/options) |
| **Bond** | Yield, duration, convexity | [/agent-services/bond](https://hermesplant.com/agent-services/bond) |
| **CashflowLens** | Cash-flow projection + sensitivity | [/agent-services/cashflowlens](https://hermesplant.com/agent-services/cashflowlens) |
| **PortfolioGuard** | Portfolio risk scoring | [/agent-services/portfolioguard](https://hermesplant.com/agent-services/portfolioguard) |
| **WalletGuard** | Wallet AML + sanctions screening | [/agent-services/walletguard](https://hermesplant.com/agent-services/walletguard) |
| **EmailGuard** | Email reputation + risk | [/agent-services/emailguard](https://hermesplant.com/agent-services/emailguard) |
| **DestructGuard** | Block destructive AI-agent commands | [/agent-services/destructguard](https://hermesplant.com/agent-services/destructguard) |
| **MCP risk** | Score MCP server risk before connecting | [/agent-services/mcp-risk](https://hermesplant.com/agent-services/mcp-risk) |
| **Evidence** | Evidence-bundle for paid calls | [/agent-services/evidence](https://hermesplant.com/agent-services/evidence) |
| **Payment policy** | Inspect/score an x402 payment policy | [/agent-services/payment-policy](https://hermesplant.com/agent-services/payment-policy) |
| **ReviewQueue** | Human-in-the-loop approval routing | [/agent-services/reviewqueue](https://hermesplant.com/agent-services/reviewqueue) |

Agents discover endpoints through OpenAPI, llms.txt, the x402 manifest, the API catalog, MCP metadata, or agent skills. Pricing is metered per call in USDC on Base mainnet.

## How an x402 call works

```
┌────────┐                          ┌───────────────┐                ┌──────────────┐
│ Client │ ── POST /endpoint ─────▶ │ Hermes Plant  │                │  Facilitator │
│        │                          │               │                │ (Coinbase)   │
│        │ ◀── 402 + challenge ─── │               │                │              │
│        │                          │               │                │              │
│        │ ── POST + signature ──▶ │               │ ─ verify ────▶ │              │
│        │                          │               │ ◀─ ok ─────── │              │
│        │ ◀── 200 + result ────── │               │ ─ settle ───▶  │              │
└────────┘                          └───────────────┘                └──────────────┘
```

1. Client makes an HTTP request.
2. Server replies with `402 Payment Required` + a `PAYMENT-REQUIRED` header carrying the price, network, asset, recipient, and a server-issued nonce.
3. Client parses the challenge, signs a USDC transfer authorization locally, replays the request with a `PAYMENT-SIGNATURE` header.
4. Server verifies the signature via the facilitator, runs the work, settles the payment on-chain, returns `200 OK` with the result and a `PAYMENT-RESPONSE` header.

The full spec lives at [github.com/x402-foundation/x402](https://github.com/x402-foundation/x402).

## Discovery surfaces

These let any agent (or human) self-onboard without help:

- [hermesplant.com/llms.txt](https://hermesplant.com/llms.txt) — agent-readable catalog
- [hermesplant.com/openapi.json](https://hermesplant.com/openapi.json) — full OpenAPI 3.1
- [hermesplant.com/.well-known/x402](https://hermesplant.com/.well-known/x402) — x402 manifest (facilitator, network, payTo)
- [hermesplant.com/.well-known/api-catalog](https://hermesplant.com/.well-known/api-catalog) — RFC 9727 API catalog
- [hermesplant.com/.well-known/mcp/server-card.json](https://hermesplant.com/.well-known/mcp/server-card.json) — MCP server descriptor
- [hermesplant.com/mcp](https://hermesplant.com/mcp) — Streamable-HTTP MCP endpoint

## Quickstart

Pick the runtime that matches your stack:

| Runtime | Folder | Notes |
|---|---|---|
| `curl` / Bash | [curl/](./curl/) | Pure shell; useful for inspecting the 402 handshake |
| TypeScript | [typescript/](./typescript/) | Uses `x402-fetch` + `@modelcontextprotocol/sdk` |
| Python | [python/](./python/) | Uses the `x402` package |
| CrewAI | [crewai/](./crewai/) | Finance-agent crew calling Hermes endpoints |
| LangChain | [langchain/](./langchain/) | LangChain `Tool` wrapping Hermes |
| MCP config | [mcp-config/](./mcp-config/) | One-paste config for Claude Desktop / Cline / Cursor |
| MCP server | [mcp-server/](./mcp-server/) | Runnable stdio MCP bridge for discovery, server-card inspection, and hosted-tool listing |

### MCP server registry build

This repo includes a root `glama.json` and root `Dockerfile` for MCP registry crawlers:

```bash
docker build -t hermesplant-mcp-server .
docker run --rm -i hermesplant-mcp-server
```

The container starts the stdio MCP bridge in [mcp-server/](./mcp-server/), which exposes Hermes Plant discovery tools and hosted MCP metadata without requiring API keys.

## Wallet setup

Every example assumes:
- A funded wallet on **Base mainnet** (chain id `8453`).
- A small **USDC** balance for paying per-call fees (typical call: $0.01–$0.50).
- An EOA private key (any standard EVM wallet — MetaMask, Coinbase Smart Wallet, Privy, Dynamic, etc.) — examples read it from `WALLET_PRIVATE_KEY`.

For testing without real funds, point your client at Base **Sepolia** (`84532`) and use the testnet x402 facilitator at `https://x402.org/facilitator`. Hermes Plant supports both — its `/.well-known/x402` manifest declares the active network.

## Status

These examples target the production deployment at `hermesplant.com`. Endpoint signatures may evolve — always cross-reference [openapi.json](https://hermesplant.com/openapi.json) and the `/.well-known/x402` manifest before going to production.

## Contributing

Issues and PRs welcome. New runtime? New framework? Open a PR with one working example and a tight README.

## License

MIT — see [LICENSE](./LICENSE).
