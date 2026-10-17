import asyncio
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from repo_detective.repo_manager import clone_repo


async def main(url):
    try:
        repo_path = clone_repo(url)
    except ValueError as error:
        print("Error:", error)
        return
    print("Cloned to:", repo_path)

    server = StdioServerParameters(
        command=sys.executable,
        args=["-m", "repo_detective.mcp_server", repo_path],
    )
    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("Tools:", [tool.name for tool in tools.tools])

            result = await session.call_tool("list_files", {"directory": "."})
            print("\nlist_files:\n" + result.content[0].text)

            result = await session.call_tool("git_history", {"max_count": 3})
            print("\ngit_history:\n" + result.content[0].text)


asyncio.run(main(sys.argv[1]))