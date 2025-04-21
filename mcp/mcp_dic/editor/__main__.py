"""エディタアプリケーションのエントリーポイント"""
from pathlib import Path
import sys

from mcp_dic.editor.app import DictionaryEditorApp


def main():
  """
    メイン関数
    
    アプリケーションを起動します。
    初期状態ではデータベースは開かれていませんが、
    メニューからデータベースファイルを選択して開くことができます。
    """
  # データベースパスを指定せずにアプリケーションを起動

  arg1 = Path(sys.argv[1])

  path = str(arg1)

  if not arg1.exists():
    print("エラー: ファイルが存在しません")
    path = None

  if not arg1.is_file():
    print("エラー: ファイルではありません")
    path = None

  if arg1.suffix not in [".sqlite3", ".sqlite", ".db"]:
    print(arg1.suffix)
    print("エラー: SQLite3データベースファイルではありません")
    path = None

  app = DictionaryEditorApp(path)
  sys.exit(app.run())


if __name__ == "__main__":
  main()
