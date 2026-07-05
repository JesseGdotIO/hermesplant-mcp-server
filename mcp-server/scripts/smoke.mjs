import path from "node:path";
import { fileURLToPath } from "node:url";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const serverPath = path.resolve(__dirname, "../src/server.js");
const dockerImage = process.env.MCP_SMOKE_DOCKER_IMAGE;

const expectedTools = [
  "hermesplant_x402_manifest",
  "hermesplant_llms_catalog",
  "hermesplant_api_catalog",
  "hermesplant_mcp_server_card",
  "hermesplant_list_hosted_tools",
];

const serverCommand = dockerImage ? "docker" : process.execPath;
const serverArgs = dockerImage ? ["run", "--rm", "-i", dockerImage] : [serverPath];

const transport = new StdioClientTransport({
  command: serverCommand,
  args: serverArgs,
  env: {
    ...process.env,
    HERMES_BASE_URL: process.env.HERMES_BASE_URL ?? "https://hermesplant.com",
    HERMES_MCP_URL: process.env.HERMES_MCP_URL ?? "https://hermesplant.com/mcp",
  },
  stderr: "pipe",
});

const stderr = [];
transport.stderr?.on("data", (chunk) => stderr.push(String(chunk)));

const client = new Client(
  { name: "hermesplant-mcp-smoke", version: "0.1.0" },
  { capabilities: {} },
);

try {
  await client.connect(transport);

  const { tools } = await client.listTools();
  const actualNames = new Set(tools.map((tool) => tool.name));
  const missing = expectedTools.filter((name) => !actualNames.has(name));

  if (missing.length > 0) {
    throw new Error(`Missing expected tools: ${missing.join(", ")}`);
  }

  for (const tool of tools) {
    if (!tool.description || tool.description.length < 80) {
      throw new Error(`Tool ${tool.name} needs a fuller description for registry quality scoring.`);
    }

    if (tool.inputSchema?.additionalProperties !== false) {
      throw new Error(`Tool ${tool.name} must reject undeclared input properties.`);
    }
  }

  const manifest = await client.callTool({
    name: "hermesplant_x402_manifest",
    arguments: {},
  });
  const manifestText = manifest.content?.find((part) => part.type === "text")?.text;

  if (!manifestText) {
    throw new Error("x402 manifest tool returned no text content.");
  }

  const parsedManifest = JSON.parse(manifestText);
  const serializedManifest = JSON.stringify(parsedManifest);

  if (!/x402|base|facilitator|payTo/i.test(serializedManifest)) {
    throw new Error("x402 manifest response did not contain expected payment discovery fields.");
  }

  const target = dockerImage ? `Docker image ${dockerImage}` : "local Node server";
  console.log(`Smoke OK: ${target}; ${tools.length} tools listed and x402 manifest fetched.`);
} catch (error) {
  if (stderr.length > 0) {
    console.error(stderr.join(""));
  }
  throw error;
} finally {
  await client.close().catch(() => {});
}
