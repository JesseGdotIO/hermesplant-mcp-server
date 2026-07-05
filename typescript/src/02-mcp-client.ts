/**
 * 02-mcp-client.ts
 *
 * Connect to Hermes Plant's Streamable HTTP MCP endpoint, list available
 * tools, and call one. MCP handles the protocol envelope; the underlying
 * tool calls still go through x402 for paid endpoints, so your wallet
 * authorizes each paid call.
 *
 *   WALLET_PRIVATE_KEY=0x... npm run example:mcp
 */
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js";

const MCP_URL = process.env.HERMES_MCP_URL ?? "https://hermesplant.com/mcp";

async function main() {
  const transport = new StreamableHTTPClientTransport(new URL(MCP_URL));
  const client = new Client(
    { name: "hermesplant-examples-mcp", version: "0.1.0" },
    { capabilities: {} },
  );

  await client.connect(transport);
  console.log("Connected:", client.getServerVersion());

  const tools = await client.listTools();
  console.log(`Tools (${tools.tools.length}):`);
  for (const tool of tools.tools) {
    console.log(`  - ${tool.name}: ${tool.description ?? ""}`);
  }

  // Try a free tool first, such as discovery, health, catalog, or llms.
  // Escalate to a paid tool only after wallet auth is wired into the runtime.
  const freeTool = tools.tools.find((t) =>
    /discover|health|catalog|llms/i.test(t.name),
  );
  if (freeTool) {
    console.log(`\nCalling ${freeTool.name} (free) ...`);
    const result = await client.callTool({ name: freeTool.name, arguments: {} });
    console.log("Result:", JSON.stringify(result, null, 2).slice(0, 800));
  }

  await client.close();
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
