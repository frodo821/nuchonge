"""検索ウィジェット"""
from typing import Optional, List, Dict, Any, TYPE_CHECKING

from PySide6.QtWidgets import (
  QWidget,
  QVBoxLayout,
  QHBoxLayout,
  QFormLayout,
  QLineEdit,
  QPushButton,
  QLabel,
  QTabWidget,
  QTableView,
  QHeaderView,
  QComboBox,
  QMessageBox
)
from PySide6.QtCore import Qt, Signal, Slot, QSortFilterProxyModel, QTimer
from PySide6.QtGui import QStandardItemModel, QStandardItem

from mcp_dic.editor.models import Stem, Inflection

if TYPE_CHECKING:
  from mcp_dic.editor.database import DictionaryDatabase


class SearchWidget(QWidget):
  """検索ウィジェット"""

  # 検索結果から語幹が選択されたときに発行される
  stem_selected = Signal(int)  # 語幹ID

  def __init__(self, db: Optional['DictionaryDatabase'] = None, parent=None):
    """
        検索ウィジェットを初期化
        
        Args:
            db: データベース接続（Noneの場合は後から設定）
            parent: 親ウィジェット
        """
    super().__init__(parent)
    self.db = db

    # デバウンス用タイマー（連続した入力をまとめる）
    self.stem_search_timer = QTimer(self)
    self.stem_search_timer.setSingleShot(True)
    self.stem_search_timer.setInterval(500)  # 500ms
    self.stem_search_timer.timeout.connect(self._do_search_stems)

    self.form_search_timer = QTimer(self)
    self.form_search_timer.setSingleShot(True)
    self.form_search_timer.setInterval(500)  # 500ms
    self.form_search_timer.timeout.connect(self._do_search_forms)

    # UI初期化
    self.init_ui()

  def init_ui(self):
    """UIを初期化"""
    # メインレイアウト
    main_layout = QVBoxLayout(self)

    # タブウィジェット
    self.tab_widget = QTabWidget()
    main_layout.addWidget(self.tab_widget)

    # 語幹検索タブ
    stem_tab = QWidget()
    stem_layout = QVBoxLayout(stem_tab)

    # 検索フォーム
    form_layout = QFormLayout()

    self.stem_search_edit = QLineEdit()
    self.stem_search_edit.setPlaceholderText("語幹を入力")
    self.stem_search_edit.textChanged.connect(self.search_stems)
    form_layout.addRow("語幹:", self.stem_search_edit)

    stem_layout.addLayout(form_layout)

    # 結果テーブル
    self.stem_table = QTableView()
    self.stem_table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
    self.stem_table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
    self.stem_table.doubleClicked.connect(self.on_stem_selected)

    # モデル設定
    self.stem_model = QStandardItemModel()
    self.stem_model.setHorizontalHeaderLabels(["ID", "語幹", "品詞", "音韻型"])

    self.stem_table.setModel(self.stem_model)

    # ID列は表示しない
    self.stem_table.hideColumn(0)

    # 列幅の設定
    header = self.stem_table.horizontalHeader()
    header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # 語幹
    header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # 品詞
    header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # 音韻型

    stem_layout.addWidget(self.stem_table)

    self.tab_widget.addTab(stem_tab, "語幹検索")

    # 活用形検索タブ
    form_tab = QWidget()
    form_layout = QVBoxLayout(form_tab)

    # 検索フォーム
    form_search_layout = QFormLayout()

    self.form_search_edit = QLineEdit()
    self.form_search_edit.setPlaceholderText("活用形を入力")
    self.form_search_edit.textChanged.connect(self.search_forms)
    form_search_layout.addRow("活用形:", self.form_search_edit)

    form_layout.addLayout(form_search_layout)

    # 結果テーブル
    self.form_table = QTableView()
    self.form_table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
    self.form_table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
    self.form_table.doubleClicked.connect(self.on_form_selected)

    # モデル設定
    self.form_model = QStandardItemModel()
    self.form_model.setHorizontalHeaderLabels(["語幹ID", "語幹", "カテゴリ", "活用型", "活用形"])

    self.form_table.setModel(self.form_model)

    # 語幹ID列は表示しない
    self.form_table.hideColumn(0)

    # 列幅の設定
    header = self.form_table.horizontalHeader()
    header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # 語幹
    header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # カテゴリ
    header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # 活用型
    header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)  # 活用形

    form_layout.addWidget(self.form_table)

    self.tab_widget.addTab(form_tab, "活用形検索")

  @Slot()
  def search_stems(self):
    """
        語幹検索のタイマーをリセットして再開
        テキスト入力時に呼び出され、連続した入力をデバウンスする
        """
    # タイマーをリセットして再開
    self.stem_search_timer.stop()
    self.stem_search_timer.start()

  @Slot()
  def _do_search_stems(self):
    """
        語幹の実際の検索を実行
        タイマーのタイムアウト後に呼び出される
        """
    # データベースが接続されていない場合
    if not self.db:
      QMessageBox.warning(self, "エラー", "データベースが接続されていません。")
      return

    search_term = self.stem_search_edit.text()

    # テーブルをクリア
    self.stem_model.removeRows(0, self.stem_model.rowCount())

    try:
      if not search_term:
        # 検索語が空の場合は全件検索
        stems = self.db.get_stems()
      else:
        # 検索語で絞り込み
        stems = self.db.get_stems(search_term)

      # テーブルに追加
      for stem in stems:
        # ID（非表示だが選択時に使用）
        id_item = QStandardItem(str(stem.id))
        # 語幹
        stem_item = QStandardItem(stem.stem)
        # 品詞
        pos_item = QStandardItem(stem.part_of_speech_name or "")
        # 音韻型
        pattern_item = QStandardItem(stem.phonological_pattern_name or "")

        # 行を追加
        self.stem_model.appendRow([id_item, stem_item, pos_item, pattern_item])
    except Exception as e:
      QMessageBox.critical(self, "エラー", f"検索中にエラーが発生しました: {str(e)}")

  @Slot()
  def search_forms(self):
    """
        活用形検索のタイマーをリセットして再開
        テキスト入力時に呼び出され、連続した入力をデバウンスする
        """
    # タイマーをリセットして再開
    self.form_search_timer.stop()
    self.form_search_timer.start()

  @Slot()
  def _do_search_forms(self):
    """
        活用形の実際の検索を実行
        タイマーのタイムアウト後に呼び出される
        """
    # データベースが接続されていない場合
    if not self.db:
      QMessageBox.warning(self, "エラー", "データベースが接続されていません。")
      return

    search_term = self.form_search_edit.text()

    # テーブルをクリア
    self.form_model.removeRows(0, self.form_model.rowCount())

    if not search_term:
      # 検索語が空の場合は何もしない
      return

    try:
      # 検索語で活用形を検索
      results = self.db.search_by_form(search_term)

      # テーブルに追加
      for result in results:
        inflection = result['inflection']
        # 語幹ID（非表示だが選択時に使用）
        stem_id_item = QStandardItem(str(inflection.stem_id))
        # 語幹
        stem_item = QStandardItem(result['stem'])
        # カテゴリ
        category_item = QStandardItem(inflection.category or "")
        # 活用型
        type_item = QStandardItem(inflection.inflection_type_name or "")
        # 活用形
        form_item = QStandardItem(inflection.form)

        # 行を追加
        self.form_model.appendRow([
          stem_id_item,
          stem_item,
          category_item,
          type_item,
          form_item
        ])
    except Exception as e:
      QMessageBox.critical(self, "エラー", f"検索中にエラーが発生しました: {str(e)}")

  @Slot()
  def on_stem_selected(self, index):
    """
        語幹が選択されたときの処理
        
        Args:
            index: 選択されたモデルインデックス
        """
    # 選択された行から語幹IDを取得
    row = index.row()
    stem_id = int(self.stem_model.index(row, 0).data())

    # シグナルを発行
    self.stem_selected.emit(stem_id)

  @Slot()
  def on_form_selected(self, index):
    """
        活用形が選択されたときの処理
        
        Args:
            index: 選択されたモデルインデックス
        """
    # 選択された行から語幹IDを取得
    row = index.row()
    stem_id = int(self.form_model.index(row, 0).data())

    # シグナルを発行
    self.stem_selected.emit(stem_id)
