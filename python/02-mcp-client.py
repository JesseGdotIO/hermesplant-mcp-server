"""
02-mcp-client.py

Connect to Hermes Plant's Streamable HTTP MCP endpoint, list tools, and call
a free one. Paid tools still require an x402 wallet; see 01-call-endpoint.py
for the payment flow.
"""
import asyncio
import json
import os

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

MCP_URL = os.environ.get("HERMES_MCP_URL", "https://hermesplant.com/mcp")


async def main() -> None:
    async with streamablehttp_client(MCP_URL) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            print("Connected.")

            tools = await session.list_tools()
            print(f"\nTools ({len(tools.tools)}):")
            for tool in tools.tools:
                description = tool.description or ""
                print(f"  - {tool.name}: {description}")

            free_tool = next(
                (
                    t for t in tools.tools
                    if any(token in t.name.lower() for token in ("discover", "health", "catalog", "llms"))
                ),
                None,
            )
            if free_tool:
                print(f"\nCalling {free_tool.name} (free) ...")
                result = await session.call_tool(free_tool.name, {})
                print(json.dumps(result.model_dump(), indent=2)[:800])


if __name__ == "__main__":
    asyncio.run(main())
