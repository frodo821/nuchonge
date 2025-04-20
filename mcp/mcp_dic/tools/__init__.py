from mcp.server.fastmcp import FastMCP

from mcp_dic.tools.tools import known_tools
import mcp_dic.tools.reading


def register_tools(mcp: FastMCP):
  for tool in known_tools:
    mcp.tool()(tool)
