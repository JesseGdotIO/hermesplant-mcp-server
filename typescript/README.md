# TypeScript examples

End-to-end TypeScript clients that call Hermes Plant endpoints.

| File | What it shows |
|---|---|
| [`src/01-call-endpoint.ts`](./src/01-call-endpoint.ts) | Direct x402 call using `@x402/fetch` and `@x402/evm` to handle the 402 challenge automatically. |
| [`src/02-mcp-client.ts`](./src/02-mcp-client.ts) | Streamable HTTP MCP client that connects to `hermesplant.com/mcp`, lists tools, and invokes one. |

## Setup

```sh
cd typescript
npm install
```

Set wallet env:

```sh
export WALLET_PRIVATE_KEY="0x..."   # EOA private key, Base mainnet
```

## Run

```sh
npm run example:call         # direct x402 call
npm run example:mcp          # MCP client
```

## Production note

The current TypeScript example uses the x402 v2 client pattern: create an `x402Client`, register an `ExactEvmScheme` for `eip155:8453`, then pass it to `wrapFetchWithPayment(fetch, client)`. Pin package versions in production apps and re-run `npm run typecheck` after SDK upgrades.
