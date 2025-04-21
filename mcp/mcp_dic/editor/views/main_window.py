"""メインウィンドウ"""
from typing import TYPE_CHECKING, Optional, cast

from PySide6.QtWidgets import (
  QMainWindow,
  QTabWidget,
  QVBoxLayout,
  QWidget,
  QStatusBar,
  QToolBar,
  QMenuBar,
  QMenu,
  QMessageBox
)
from PySide6.QtCore import Qt, Slot, Signal
from PySide6.QtGui import QAction, QIcon

from mcp_dic.editor.widgets import SearchWidget, StemEditor

if TYPE_CHECKING:
  from mcp_dic.editor.database import DictionaryDatabase


class MainWindow(QMainWindow):
  """辞書エディタのメインウィンドウ"""

  # データベース操作のためのシグナル
  open_database_requested = Signal()
  close_database_requested = Signal()

  def __init__(
    self,
    db: Optional['DictionaryDatabase'] = None,
    parent: Optional[QWidget] = None
  ):
    """
        メインウィンドウを初期化
        
        Args:
            db: データベース接続
            parent: 親ウィジェット
        """
    super().__init__(parent)
    self.db = db

    # ウィンドウ設定
    self.setWindowTitle("辞書エディタ")
    self.resize(1200, 800)

    # メニューバーの作成
    self.create_menus()

    # ツールバーの作成
    self.create_toolbar()

    # ステータスバーの設定
    status_bar = QStatusBar()
    self.setStatusBar(status_bar)
    status_bar.showMessage("準備完了")

    # タブウィジェットの作成
    self.tab_widget = QTabWidget()
    self.setCentralWidget(self.tab_widget)

    # タブの作成
    self.create_tabs()

  def create_menus(self):
    """メニューバーを作成"""
    # メニューバー
    menubar = QMenuBar()
    self.setMenuBar(menubar)

    # ファイルメニュー
    file_menu = QMenu("ファイル", self)
    menubar.addMenu(file_menu)

    # データベースを開くアクション
    open_db_action = QAction("データベースを開く...", self)
    open_db_action.setShortcut("Ctrl+O")
    open_db_action.triggered.connect(self.on_open_database)
    file_menu.addAction(open_db_action)

    # データベースを閉じるアクション
    close_db_action = QAction("データベースを閉じる", self)
    close_db_action.triggered.connect(self.on_close_database)
    file_menu.addAction(close_db_action)

    # 区切り線
    file_menu.addSeparator()

    # 終了アクション
    exit_action = QAction("終了", self)
    exit_action.setShortcut("Ctrl+Q")
    exit_action.triggered.connect(self.close)
    file_menu.addAction(exit_action)

    # 編集メニュー
    edit_menu = QMenu("編集", self)
    menubar.addMenu(edit_menu)

    # 新規作成アクション（追加）
    new_action = QAction("新規作成", self)
    new_action.setShortcut("Ctrl+N")
    new_action.triggered.connect(self.on_create_new)
    edit_menu.addAction(new_action)

    # ヘルプメニュー
    help_menu = QMenu("ヘルプ", self)
    menubar.addMenu(help_menu)

    # バージョン情報アクション
    about_action = QAction("バージョン情報", self)
    about_action.triggered.connect(self.show_about)
    help_menu.addAction(about_action)

  def create_toolbar(self):
    """ツールバーを作成"""
    toolbar = QToolBar("メインツールバー")
    self.addToolBar(toolbar)

    # 検索アクション
    search_action = QAction("検索", self)
    search_action.setStatusTip("辞書を検索")
    search_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(0))
    toolbar.addAction(search_action)

    # 新規作成アクション
    new_action = QAction("新規作成", self)
    new_action.setStatusTip("新しい単語を作成")
    new_action.triggered.connect(self.on_create_new)
    toolbar.addAction(new_action)

  def create_tabs(self):
    """タブを作成"""
    # 検索タブ
    search_tab = QWidget()
    search_layout = QVBoxLayout(search_tab)
    self.search_widget = SearchWidget(self.db) if self.db else SearchWidget(None)
    search_layout.addWidget(self.search_widget)
    self.tab_widget.addTab(search_tab, "検索")

    # 検索結果から編集タブへの連携
    self.search_widget.stem_selected.connect(self.on_stem_selected)

    # 編集タブ
    edit_tab = QWidget()
    edit_layout = QVBoxLayout(edit_tab)
    self.stem_editor = StemEditor(self.db) if self.db else StemEditor(None)
    edit_layout.addWidget(self.stem_editor)
    self.tab_widget.addTab(edit_tab, "編集")

    # データベースが開かれていない場合は無効化
    self.update_ui_state()

  @Slot(int)
  def on_stem_selected(self, stem_id: int):
    """
    検索結果から語幹が選択されたときの処理
    
    Args:
        stem_id: 選択された語幹ID
    """
    # 編集タブに切り替え
    self.tab_widget.setCurrentIndex(1)

    # 選択された語幹を編集
    self.stem_editor.edit_stem(stem_id)

  @Slot()
  def on_create_new(self):
    """新しい語幹を作成"""
    # 編集タブに切り替え
    self.tab_widget.setCurrentIndex(1)

    # 新規作成モードに設定
    self.stem_editor.create_new_stem()

  def set_database(self, db: Optional['DictionaryDatabase']):
    """
    データベース接続を設定（または変更）
    
    Args:
        db: 新しいデータベース接続（Noneの場合は接続を閉じる）
    """
    self.db = db

    # 子ウィジェットにも反映
    if hasattr(self, 'search_widget'):
      self.search_widget.db = db

    if hasattr(self, 'stem_editor'):
      self.stem_editor.db = db

      # データベースが設定された場合、品詞と音韻型のリストを再読み込み
      if db:
        self.stem_editor.load_parts_of_speech()
        self.stem_editor.load_phonological_patterns()

    # UIの状態を更新
    self.update_ui_state()

    # データベースが設定された場合、初期データをロード
    if db:
      # 検索ウィジェットで初期検索を実行
      if hasattr(self, 'search_widget'):
        self.search_widget.search_stems()

  def update_ui_state(self):
    """
    データベースの状態に応じてUIの有効/無効を切り替え
    """
    is_db_open = self.db is not None

    # タブの有効/無効
    if hasattr(self, 'search_widget'):
      self.search_widget.setEnabled(is_db_open)

    if hasattr(self, 'stem_editor'):
      self.stem_editor.setEnabled(is_db_open)

    # ステータスバーのメッセージを更新
    if is_db_open and self.db and hasattr(self.db, 'db_path') and self.db.db_path:
      self.statusBar().showMessage(f"データベース: {self.db.db_path}")
    else:
      self.statusBar().showMessage("データベースが開かれていません")

  @Slot()
  def on_open_database(self):
    """データベースを開くボタンが押されたとき"""
    self.open_database_requested.emit()

  @Slot()
  def on_close_database(self):
    """データベースを閉じるボタンが押されたとき"""
    self.close_database_requested.emit()

  @Slot()
  def show_about(self):
    """バージョン情報ダイアログを表示"""
    QMessageBox.about(self,
                      "辞書エディタについて",
                      "辞書エディタ v0.1\n"
                      "辞書データの編集・検索ツール")
