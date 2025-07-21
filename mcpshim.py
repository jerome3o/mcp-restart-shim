import sys
import os

import anyio
from mcp.server.stdio import stdio_server
from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp.shared.message import SessionMessage


def is_tool_list(message: SessionMessage) -> bool:
    """
    Check if the message is a tool list request.
    """
    try:
        return message.message.root.method == "tools/list"
    except Exception:
        print(f"Invalid message format: {message}", file=sys.stderr)




async def main():
    sys_args = sys.argv[1:]
    command = sys_args[0]
    args = sys_args[1:] if len(sys_args) > 1 else []

    print(f"{command=}", file=sys.stderr)
    print(f"{args=}", file=sys.stderr)

    params = StdioServerParameters(
        command=command,
        args=args,
        env=os.environ.copy(),
        cwd=os.getcwd(),
        encoding='utf-8',
        encoding_error_handler='replace'
    )

    async with stdio_server() as (from_outer_client, to_outer_client):
        init_message: SessionMessage | None = None

        async with anyio.create_task_group() as tg:
            print("Starting inner server...", file=sys.stderr)
            async with stdio_client(params, errlog=sys.stderr) as (from_inner_server, to_inner_server):
                print("Inner server started.", file=sys.stderr)
                tools_list_id_set = {}

                async def relay_to_server():
                    print("Relaying messages from outer client to inner server...", file=sys.stderr)

                    async for message in from_outer_client:
                        # if is_tool_list(message):
                            # tools_list_id_set[message.id] = message
                            # print(f"Received tool list request: {message.message.root.id}", file=sys.stderr)

                        print(f"Relaying message to inner server: {message.message.root.model_dump().get("id", "NA")}", file=sys.stderr)
                        await to_inner_server.send(message)
                    print("Outer client has closed the connection.", file=sys.stderr)

                async def relay_to_client():
                    print("Relaying messages from inner server to outer client...", file=sys.stderr)
                    async for message in from_inner_server:
                        print(f"Relaying message to outer client", file=sys.stderr)
                        await to_outer_client.send(message)
                    print("Inner server has closed the connection.", file=sys.stderr)

                tg.start_soon(relay_to_server)
                tg.start_soon(relay_to_client)
                print("Relay tasks started.", file=sys.stderr)
                # sleep forever
                while True:
                    await anyio.sleep(3600)


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    anyio.run(main)
