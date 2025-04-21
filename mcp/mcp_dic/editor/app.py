"""アプリケーションモジュール"""
import sys
from typing import Optional

from PySide6.QtWidgets import QApplication, QFileDialog, QMessageBox
from PySide6.QtCore import QTranslator, QLocale

from mcp_dic.editor.database import DictionaryDatabase
from mcp_dic.editor.views.main_window import MainWindow


class DictionaryEditorApp:
  """辞書エディタアプリケーション"""

  def __init__(self, db_path: Optional[str] = None):
    """
        アプリケーションを初期化
        
        Args:
            db_path: データベースファイルのパス（Noneの場合は初期状態ではデータベースを開きません）
        """
    self.app = QApplication(sys.argv)
    self.db_path = db_path
    self.database = None
    self.main_window = None

    # アプリケーション名を設定
    self.app.setApplicationName("辞書エディタ")

    # 日本語翻訳ファイルをロード（存在する場合）
    translator = QTranslator()
    if translator.load(QLocale.system(), "dictionary_editor", "_", "translations"):
      self.app.installTranslator(translator)

  def setup_database(self, db_path: Optional[str] = None):
    """
        データベース接続を設定
        
        Args:
            db_path: データベースファイルのパス（Noneの場合は前回のパスを使用）
        """
    if db_path:
      self.db_path = db_path

    if self.db_path:
      try:
        # 既存のデータベース接続を閉じる
        if self.database:
          self.database.close()

        # 新しいデータベース接続を作成
        self.database = DictionaryDatabase(self.db_path)

        # メインウィンドウが存在する場合、データベース接続を更新
        if self.main_window:
          self.main_window.set_database(self.database)

        return True
      except Exception as e:
        # エラーメッセージを表示
        parent = self.main_window if hasattr(self, 'main_window') and self.main_window else None

        # 親ウィンドウがなければQMessageBoxを直接使用
        if parent:
          QMessageBox.critical(parent, "エラー", f"データベースを開けませんでした: {str(e)}")
        else:
          msg_box = QMessageBox()
          msg_box.setIcon(QMessageBox.Icon.Critical)
          msg_box.setWindowTitle("エラー")
          msg_box.setText(f"データベースを開けませんでした: {str(e)}")
          msg_box.exec()
        return False
    return False

  def open_database_dialog(self):
    """
        データベースファイル選択ダイアログを表示し、選択されたファイルを開く
        
        Returns:
            成功した場合はTrue
        """
    file_dialog = QFileDialog()
    file_dialog.setWindowTitle("データベースファイルを開く")
    file_dialog.setNameFilter("SQLiteデータベース (*.sqlite3 *.db);;すべてのファイル (*)")
    file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)

    if file_dialog.exec():
      selected_files = file_dialog.selectedFiles()
      if selected_files:
        db_path = selected_files[0]
        return self.setup_database(db_path)
    return False

  def close_database(self):
    """
        現在開いているデータベースを閉じる
        """
    if self.database:
      self.database.close()
      self.database = None
      self.db_path = None

      # メインウィンドウにも反映
      if self.main_window:
        self.main_window.set_database(None)

  def setup_ui(self):
    """UIを設定"""
    # メインウィンドウを作成（初期状態ではデータベースはNullかもしれない）
    self.main_window = MainWindow(self.database)

    # ファイル選択機能をメインウィンドウに接続
    self.main_window.open_database_requested.connect(self.open_database_dialog)
    self.main_window.close_database_requested.connect(self.close_database)

    self.main_window.show()

  def run(self) -> int:
    """
        アプリケーションを実行
        
        Returns:
            終了コード
        """
    # UIを設定
    self.setup_ui()

    # データベースが指定されている場合は開く
    if self.db_path:
      self.setup_database()

    # イベントループを開始
    return self.app.exec()
