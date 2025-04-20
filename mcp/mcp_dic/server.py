from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any, AsyncGenerator, Literal
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel

from mcp_dic.database.sqlite import SQLiteDatabase
from mcp_dic.tools import register_tools


@dataclass
class AppContext:
  db: SQLiteDatabase


class SQLiteMCPServerArgs(BaseModel):
  database_path: str = "dictionary.sqlite3"
  server_name: str = "Dictionary MCP"
  server_port: int = 8000
  server_host: str = "localhost"
  mode: Literal['sse', 'stdio'] = 'sse'


def create_server(args: SQLiteMCPServerArgs) -> FastMCP:

  @asynccontextmanager
  async def lifespan(server: FastMCP) -> 'AsyncGenerator[AppContext, Any]':
    """Get the application context."""
    db = SQLiteDatabase(args.database_path)
    try:
      yield AppContext(db)
    finally:
      db.close()

  mcp = FastMCP(
    name=args.server_name,
    lifespan=lifespan,
    host=args.server_host,
    port=args.server_port,
    instructions=""""""
  )

  register_tools(mcp)

  return mcp


def main():
  import argparse
  parser = argparse.ArgumentParser(description="SQLite MCP Server")
  parser.add_argument(
    "--database-path",
    type=str,
    default="sqlite.db",
    help="Path to the SQLite database file.",
  )
  parser.add_argument(
    "--server-name",
    type=str,
    default="SQLite MCP Server",
    help="Name of the server.",
  )
  parser.add_argument(
    "--server-port",
    type=int,
    default=8000,
    help="Port of the server.",
  )
  parser.add_argument(
    "--server-host",
    type=str,
    default="localhost",
    help="Host of the server.",
  )
  parser.add_argument(
    "--mode",
    type=str,
    choices=[
      'sse',
      'stdio',
    ],
    default='sse',
    help="Mode of the server.",
  )
  args = SQLiteMCPServerArgs(**vars(parser.parse_args()))
  mcp = create_server(args)
  mcp.run(transport=args.mode)
