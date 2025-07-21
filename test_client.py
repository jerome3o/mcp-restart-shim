import sys
import os
import anyio
from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp.client.session import ClientSession
from mcp.types import Implementation

args = sys.argv[1:]

stdio_params = StdioServerParameters(
    command=args[0],
    args=args[1:],
    env={**os.environ, "PYTHONPATH": ":".join(sys.path)},
    cwd=os.getcwd(),
    encoding="utf-8",
    encoding_error_handler="replace"
)

async def main():
    async with stdio_client(stdio_params, errlog=sys.stderr) as (read_stream, write_steam):
        async with ClientSession(
            read_stream=read_stream,
            write_stream=write_steam,
            client_info=Implementation(
                name="Test Client",
                title="Test Client for MCP",
                version="1.0.0",
            ),
        ) as client:
            await anyio.sleep(1)
            print("Initializing client...")
            await client.initialize()
            print("Initializing client... complete")
            resources = await client.list_resources()
            print("Available Resources:")
            print([r.name for r in resources.resources])

            tools = await client.list_tools()
            print("Available Tools:")
            print([t.name for t in tools.tools])

anyio.run(main)
