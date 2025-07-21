import sys
from mcp.server.fastmcp import FastMCP


app = FastMCP()

# with open("test.txt", "w") as f:
#     f.write("This is a test file created by FastMCP.\n")

# print("hello", file=sys.stderr)

@app.tool()
def hello_world(name: str = "World") -> str:
    """Returns a greeting message."""
    return f"Hello, {name}!"

@app.resource(
    uri="http://example.com/resource",
    name="example_resource",
    title="Example Resource",
    description="An example resource that returns a simple message.",
)
def example_resource() -> str:
    """Returns a simple message from the example resource."""
    return "This is an example resource message."

app.run("stdio")
