# MCP config - Claude Desktop, Cline, Cursor

Drop-in MCP server configurations for the runtimes that consume MCP servers natively. Each config points to `https://hermesplant.com/mcp` (Streamable HTTP, no install needed).

| Runtime | File | Where to drop it |
|---|---|---|
| Claude Desktop | [`claude-desktop.json`](./claude-desktop.json) | macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`; Windows: `%APPDATA%/Claude/claude_desktop_config.json` |
| Cline (VS Code) | [`cline.json`](./cline.json) | VS Code -> Cline -> Settings -> MCP Servers -> paste the JSON |
| Cursor | (use `claude-desktop.json` as a starting point) | Cursor -> Settings -> MCP -> Add new MCP server |

## What happens

1. Your editor / agent runtime connects to `hermesplant.com/mcp`.
2. Hermes Plant exposes its agent-services catalog as MCP tools.
3. When the model picks a paid tool, the runtime is expected to handle x402 payment via its configured wallet or surface the 402 challenge to the user for approval, depending on runtime.

## Free vs paid tools

Some tools (discovery, health, catalog reads) are free. Paid tools (DealAnalyzer, Options, etc.) settle one USDC payment per call. Your wallet authorization model depends on the runtime. Claude Desktop / Cline can pop a confirmation; programmatic runtimes typically use a `WALLET_PRIVATE_KEY` env var.

## Production wallet routing

For autonomous agents that should pay without prompting, run a thin proxy MCP server locally that:

1. Talks to `hermesplant.com/mcp` over Streamable HTTP.
2. Handles the 402 challenge with its own EOA signer.
3. Surfaces the verified result back to the model.

Several open-source x402 proxies exist. Search [github.com/x402-foundation/x402](https://github.com/x402-foundation/x402) and the x402 ecosystem page.
