# TypeScript examples

End-to-end TypeScript clients for Hermes Plant.

| File | What it shows |
|---|---|
| [`src/01-call-endpoint.ts`](./src/01-call-endpoint.ts) | A fail-closed x402 2.17 call to the $0.20 CashflowLens endpoint. |
| [`src/02-mcp-client.ts`](./src/02-mcp-client.ts) | A Streamable HTTP MCP client that lists tools and invokes a free tool. |

## Setup

```sh
cd typescript
npm ci
```

## Paid-call safety

The paid quickstart registers only Base mainnet and filters out payment
requirements above 200,000 atomic USDC. It will not spend until explicitly
enabled:

```sh
export EVM_PRIVATE_KEY="0x..."
export HERMES_ALLOW_PAYMENT="1"
```

Fund the wallet with enough USDC on Base and a small amount of ETH for gas. Never
commit the private key. Leave `HERMES_ALLOW_PAYMENT` unset for tests.

## Run and verify

```sh
npm run typecheck
npm run test:clients
npm run example:call
npm run example:mcp
```
