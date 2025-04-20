from pathlib import Path

from mcp_dic.database.sqlite import SQLiteDatabase


SQL_PATH = Path(__file__).parent / "ddl.sql"


def initialize_database(db: SQLiteDatabase):
  script = SQL_PATH.read_text()
  db.rw_conn.executescript(script)

