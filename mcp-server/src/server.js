#!/usr/bin/env node
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js";
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";

const DEFAULT_BASE_URL = "https://hermesplant.com";
const DEFAULT_MCP_URL = "https://hermesplant.com/mcp";

const baseUrl = (process.env.HERMES_BASE_URL ?? DEFAULT_BASE_URL).replace(/\/$/, "");
const hostedMcpUrl = process.env.HERMES_MCP_URL ?? DEFAULT_MCP_URL;

const tools = [
  discoveryTool({
    name: "hermesplant_x402_manifest",
    title: "Get x402 payment manifest",
    description: [
      "Fetches Hermes Plant's live x402 manifest from /.well-known/x402.",
      "Use this before paid API or MCP calls to discover the active network, USDC asset, facilitator URL, payTo address, endpoint prices, and payment-policy metadata.",
      "This read-only tool returns raw JSON text and never signs payments, approves wallet transactions, calls paid endpoints, or spends funds.",
    ].join(" "),
  }),
  discoveryTool({
    name: "hermesplant_llms_catalog",
    title: "Get llms.txt catalog",
    description: [
      "Fetches Hermes Plant's /llms.txt catalog for agent-readable onboarding context.",
      "Use this to understand the available deterministic finance, quant, safety, and payment-policy services before selecting an endpoint.",
      "This read-only tool returns plain text documentation and does not execute paid work.",
    ].join(" "),
  }),
  discoveryTool({
    name: "hermesplant_api_catalog",
    title: "Get API catalog",
    description: [
      "Fetches Hermes Plant's RFC 9727-style API catalog from /.well-known/api-catalog.",
      "Use this when a client needs machine-readable service discovery, OpenAPI links, MCP metadata links, pricing metadata, and provider contact details.",
      "This read-only tool returns raw JSON text and performs no paid API calls.",
    ].join(" "),
  }),
  discoveryTool({
    name: "hermesplant_mcp_server_card",
    title: "Get hosted MCP server card",
    description: [
      "Fetches Hermes Plant's MCP server descriptor from /.well-known/mcp/server-card.json.",
      "Use this to discover the hosted Streamable HTTP MCP endpoint, advertised capabilities, pricing policy, and integration metadata.",
      "This read-only tool returns raw JSON text and does not connect to a wallet or spend funds.",
    ].join(" "),
  }),
  discoveryTool({
    name: "hermesplant_list_hosted_tools",
    title: "List hosted Hermes Plant tools",
    description: [
      "Connects to Hermes Plant's hosted Streamable HTTP MCP endpoint and lists the tools it advertises.",
      "Use this to inspect tool names, descriptions, and input schemas before wiring an x402-capable runtime.",
      "This read-only introspection call does not invoke paid tools, sign wallet messages, approve payments, or spend USDC.",
    ].join(" "),
  }),
];

const server = new Server(
  {
    name: "hermesplant-mcp-server",
    version: "0.1.0",
  },
  {
    capabilities: {
      tools: {},
    },
  },
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({ tools }));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  try {
    switch (request.params.name) {
      case "hermesplant_x402_manifest":
        return textResult(await fetchText(`${baseUrl}/.well-known/x402`, "application/json"));
      case "hermesplant_llms_catalog":
        return textResult(await fetchText(`${baseUrl}/llms.txt`, "text/plain"));
      case "hermesplant_api_catalog":
        return textResult(await fetchText(`${baseUrl}/.well-known/api-catalog`, "application/json"));
      case "hermesplant_mcp_server_card":
        return textResult(
          await fetchText(`${baseUrl}/.well-known/mcp/server-card.json`, "application/json"),
        );
      case "hermesplant_list_hosted_tools":
        return textResult(await listHostedTools());
      default:
        return {
          isError: true,
          content: [{ type: "text", text: `Unknown tool: ${request.params.name}` }],
        };
    }
  } catch (error) {
    return {
      isError: true,
      content: [
        {
          type: "text",
          text: error instanceof Error ? error.message : String(error),
        },
      ],
    };
  }
});

const transport = new StdioServerTransport();
await server.connect(transport);

function emptyInputSchema() {
  return {
    type: "object",
    properties: {},
    additionalProperties: false,
  };
}

function discoveryTool({ name, title, description }) {
  return {
    name,
    description,
    inputSchema: emptyInputSchema(),
    annotations: {
      title,
      readOnlyHint: true,
      destructiveHint: false,
      idempotentHint: true,
      openWorldHint: true,
    },
  };
}

function textResult(text) {
  return {
    content: [{ type: "text", text }],
  };
}

async function fetchText(url, accept) {
  const response = await fetch(url, {
    headers: {
      Accept: accept,
      "User-Agent": "hermesplant-mcp-server/0.1",
    },
  });

  if (!response.ok) {
    throw new Error(`Hermes Plant request failed: ${response.status} ${response.statusText} (${url})`);
  }

  return response.text();
}

async function listHostedTools() {
  const transport = new StreamableHTTPClientTransport(new URL(hostedMcpUrl));
  const client = new Client(
    { name: "hermesplant-mcp-server-bridge", version: "0.1.0" },
    { capabilities: {} },
  );

  try {
    await client.connect(transport);
    const { tools: hostedTools } = await client.listTools();

    return JSON.stringify(
      {
        hostedMcpUrl,
        toolCount: hostedTools.length,
        tools: hostedTools.map((tool) => ({
          name: tool.name,
          description: tool.description ?? "",
          inputSchema: tool.inputSchema ?? null,
        })),
      },
      null,
      2,
    );
  } finally {
    await client.close().catch(() => {});
  }
}
