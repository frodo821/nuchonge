from typer import run
from mcp_dic.cli import create_app

app = create_app()
app()
