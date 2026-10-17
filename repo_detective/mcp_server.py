import sys # Used to access command-line arguments and exit the program.

from mcp.server.fastmcp import FastMCP # A class from the MCP Python SDK that makes creating an MCP server easier.

from repo_detective import tools

if len(sys.argv) < 2:
    print("Usage: python -m repo_detective.mcp_server <path-to-repo>", file=sys.stderr)
    sys.exit(1)

REPO_PATH = sys.argv[1]  # the server is locked to this one folder
mcp = FastMCP("repo-detective")


@mcp.tool()
def list_files(directory: str = ".") -> str:
    """List the files and folders inside a directory of the repository. Folders end with '/'."""
    return tools.list_files(REPO_PATH, directory)


@mcp.tool()
def read_file(path: str, start_line: int = 1, end_line: int = 200) -> str:
    """Read a source file with line numbers. Returns at most 200 lines per call."""
    return tools.read_file(REPO_PATH, path, start_line, end_line)


@mcp.tool()
def search_code(query: str) -> str:
    """Search all files for some text (case-insensitive). Returns path:line: text."""
    return tools.search_code(REPO_PATH, query)


@mcp.tool()
def find_function(name: str) -> str:
    """Find where a function or class is defined. Returns path:line: definition."""
    return tools.find_function(REPO_PATH, name)


@mcp.tool()
def git_history(path: str = "", max_count: int = 5) -> str:
    """Show recent commits for the whole repo, or for one file if a path is given."""
    return tools.git_history(REPO_PATH, path, max_count)


if __name__ == "__main__":
    mcp.run()  # talks over stdio by default