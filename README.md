# Hermes Plant MCP Server

[![Glama score](https://glama.ai/mcp/servers/JesseGdotIO/hermesplant-mcp-server/badges/score.svg)](https://glama.ai/mcp/servers/JesseGdotIO/hermesplant-mcp-server)
[![CI](https://github.com/JesseGdotIO/hermesplant-mcp-server/actions/workflows/lint.yml/badge.svg)](https://github.com/JesseGdotIO/hermesplant-mcp-server/actions/workflows/lint.yml)

Runnable MCP server and integration examples for [Hermes Plant](https://hermesplant.com), the Agent Commerce Assurance layer that lets AI agents preflight, approve, and prove consequential actions. Start with a one-cent action-safety check, route only high-risk actions into signed review evidence, and pay per call over [x402](https://x402.org).

**What's here**: a runnable stdio MCP bridge for registry crawlers and local clients, plus drop-in examples in `curl`, TypeScript, Python, [CrewAI](https://www.crewai.com/), [LangChain](https://www.langchain.com/), and MCP client configs for Claude Desktop / Cline / Cursor.

## Glama registry

[![Hermes Plant MCP Server Glama card](https://glama.ai/mcp/servers/JesseGdotIO/hermesplant-mcp-server/badges/card.svg)](https://glama.ai/mcp/servers/JesseGdotIO/hermesplant-mcp-server)

This repo is arranged for Glama to build and inspect the MCP server without secrets or funded wallets:

- `glama.json` declares the GitHub maintainer.
- The root `Dockerfile` starts the stdio MCP server in `mcp-server/`.
- `npm run smoke:mcp` lists all local MCP tools and fetches the live x402 manifest.
- GitHub Actions validates the MCP server, Docker image, TypeScript examples, shell examples, and Python syntax.

A Glama release is still an account-side action, not a GitHub release. After claiming the server in Glama, use the Dockerfile admin page to deploy the build, wait for the build test to pass, then publish a Glama release version. That release unlocks Glama's Server Coherence and Tool Definition Quality scoring.

## Start with an assurance workflow

| Workflow | Use it for | Tracked entrypoint |
|---|---|---|
| **Action Safety** | Preflight shell, Git, SQL, deploy, x402, and MCP actions; escalate high-risk work into review plus a signed receipt. | [Open workflow](https://hermesplant.com/agent-services/action-safety-workflow?utm_source=glama&utm_medium=registry&utm_campaign=biweekly-registry-wave&utm_content=action-safety-workflow) |
| **Spend Assurance** | Check payment policy, wallet context, and evidence before an agent spends. | [Open workflow](https://hermesplant.com/agent-services/spend-assurance?utm_source=glama&utm_medium=registry&utm_campaign=biweekly-registry-wave&utm_content=spend-assurance-workflow) |
| **Investment Evidence** | Run deterministic underwriting and return verifiable evidence in one paid call. | [Open workflow](https://hermesplant.com/agent-services/investment-evidence?utm_source=glama&utm_medium=registry&utm_campaign=biweekly-registry-wave&utm_content=investment-evidence-workflow) |

Use the free API key for up to 250 calls/month, the **$29/month Agent API Pass** for regular volume, or per-call USDC on Base. Public proof and machine-readable contracts are available at [hermesplant.com/proof](https://hermesplant.com/proof) and [hermesplant.com/openapi.json](https://hermesplant.com/openapi.json).

## Component catalog

Nineteen hosted x402 endpoints remain available as composable utilities:

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
| **Evidence** | Evidence bundle for paid calls | [/agent-services/evidence](https://hermesplant.com/agent-services/evidence) |
| **Payment policy** | Inspect/score an x402 payment policy | [/agent-services/payment-policy](https://hermesplant.com/agent-services/payment-policy) |
| **ReviewQueue** | Human-in-the-loop approval routing | [/agent-services/reviewqueue](https://hermesplant.com/agent-services/reviewqueue) |

Agents discover endpoints through OpenAPI, llms.txt, the x402 manifest, the API catalog, MCP metadata, or agent skills. The workflow links above carry source-specific attribution so registry traffic can be evaluated against paid calls instead of impressions.

## How an x402 call works

```text
Client                    Hermes Plant                 Facilitator
  |                            |                            |
  | POST /endpoint             |                            |
  |--------------------------->|                            |
  | 402 Payment Required       |                            |
  | + PAYMENT-REQUIRED         |                            |
  |<---------------------------|                            |
  | sign payment locally       |                            |
  | POST /endpoint             |                            |
  | + PAYMENT-SIGNATURE        |                            |
  |--------------------------->| verify signature           |
  |                            |--------------------------->|
  |                            | ok                         |
  |                            |<---------------------------|
  | 200 OK + result            | settle payment             |
  |<---------------------------|--------------------------->|
```

1. Client makes an HTTP request.
2. Server replies with `402 Payment Required` plus a `PAYMENT-REQUIRED` header carrying the price, network, asset, recipient, and a server-issued nonce.
3. Client parses the challenge, signs a USDC transfer authorization locally, and replays the request with a `PAYMENT-SIGNATURE` header.
4. Server verifies the signature via the facilitator, runs the work, settles the payment on-chain, and returns `200 OK` with the result plus a `PAYMENT-RESPONSE` header.

The full spec lives at [github.com/x402-foundation/x402](https://github.com/x402-foundation/x402).

## Discovery surfaces

These let any agent or human self-onboard without help:

- [hermesplant.com/llms.txt](https://hermesplant.com/llms.txt) - agent-readable catalog
- [hermesplant.com/openapi.json](https://hermesplant.com/openapi.json) - full OpenAPI 3.1
- [hermesplant.com/.well-known/x402](https://hermesplant.com/.well-known/x402) - x402 manifest with facilitator, network, asset, prices, and payTo metadata
- [hermesplant.com/.well-known/api-catalog](https://hermesplant.com/.well-known/api-catalog) - RFC 9727-style API catalog
- [hermesplant.com/.well-known/mcp/server-card.json](https://hermesplant.com/.well-known/mcp/server-card.json) - MCP server descriptor
- [hermesplant.com/mcp](https://hermesplant.com/mcp) - Streamable HTTP MCP endpoint

## MCP tools in this repo

The runnable stdio server exposes five read-only discovery tools:

| Tool | Purpose |
|---|---|
| `hermesplant_x402_manifest` | Fetch the live x402 manifest before paid calls. |
| `hermesplant_llms_catalog` | Fetch the agent-readable `llms.txt` catalog. |
| `hermesplant_api_catalog` | Fetch the machine-readable API catalog. |
| `hermesplant_mcp_server_card` | Fetch the hosted MCP server descriptor. |
| `hermesplant_list_hosted_tools` | Introspect the hosted Streamable HTTP MCP endpoint and list its advertised tools. |

These local tools do not sign wallet messages, approve transactions, call paid endpoints, or spend USDC. They expose the discovery layer that clients need before invoking paid hosted tools.

## Quickstart

Pick the runtime that matches your stack:

| Runtime | Folder | Notes |
|---|---|---|
| `curl` / Bash | [curl/](./curl/) | Pure shell; useful for inspecting the 402 handshake |
| TypeScript | [typescript/](./typescript/) | Uses `@x402/fetch` + `@modelcontextprotocol/sdk` |
| Python | [python/](./python/) | Uses the `x402` package |
| CrewAI | [crewai/](./crewai/) | Finance-agent crew calling Hermes endpoints |
| LangChain | [langchain/](./langchain/) | LangChain `Tool` wrapping Hermes |
| MCP config | [mcp-config/](./mcp-config/) | One-paste config for Claude Desktop / Cline / Cursor |
| MCP server | [mcp-server/](./mcp-server/) | Runnable stdio MCP bridge for discovery, server-card inspection, and hosted-tool listing |

### Run the MCP server locally

```bash
npm install
npm run smoke:mcp
npm start
```

### MCP server registry build

This repo includes a root `glama.json` and root `Dockerfile` for MCP registry crawlers:

```bash
docker build -t hermesplant-mcp-server .
docker run --rm -i hermesplant-mcp-server
```

The container starts the stdio MCP bridge in [mcp-server/](./mcp-server/), which exposes Hermes Plant discovery tools and hosted MCP metadata without requiring API keys.

## Wallet setup

Every paid-call example assumes:

- A funded wallet on **Base mainnet** with chain id `8453`.
- A small **USDC** balance for paying per-call fees. Typical calls are about `$0.01` to `$0.50`.
- An EOA private key from a standard EVM wallet such as MetaMask, Coinbase Smart Wallet, Privy, or Dynamic. Examples read it from `WALLET_PRIVATE_KEY`.

For testing without real funds, point your client at Base **Sepolia** (`84532`) and use the testnet x402 facilitator at `https://x402.org/facilitator`. Hermes Plant supports both; its `/.well-known/x402` manifest declares the active network.

## Status

These examples target the production deployment at `hermesplant.com`. Endpoint signatures may evolve, so cross-reference [openapi.json](https://hermesplant.com/openapi.json) and the `/.well-known/x402` manifest before going to production.

## Contributing

Issues and PRs welcome. New runtime? New framework? Open a PR with one working example and a tight README.

## License

MIT - see [LICENSE](./LICENSE).
