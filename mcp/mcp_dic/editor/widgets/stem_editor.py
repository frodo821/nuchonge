"""語幹編集ウィジェット"""
from typing import Optional, Dict, Any, List, TYPE_CHECKING, cast

from PySide6.QtWidgets import (
  QWidget,
  QVBoxLayout,
  QHBoxLayout,
  QFormLayout,
  QTabWidget,
  QLineEdit,
  QComboBox,
  QPushButton,
  QTextEdit,
  QTableView,
  QLabel,
  QHeaderView,
  QMessageBox,
  QDialog
)
from PySide6.QtCore import Qt, Signal, Slot, QModelIndex
from PySide6.QtGui import QStandardItemModel, QStandardItem

from mcp_dic.utils.normalize_str import normalize_str
from mcp_dic.editor.models import Stem, Definition, Inflection
from mcp_dic.editor.widgets.definition_dialog import DefinitionDialog
from mcp_dic.editor.widgets.inflection_dialog import InflectionDialog

if TYPE_CHECKING:
  from mcp_dic.editor.database import DictionaryDatabase


class StemEditor(QWidget):
  """語幹編集ウィジェット"""

  def __init__(
    self,
    db: Optional['DictionaryDatabase'] = None,
    parent: Optional[QWidget] = None
  ):
    """
        語幹編集ウィジェットを初期化
        
        Args:
            db: データベース接続（Noneの場合は後から設定）
            parent: 親ウィジェット
        """
    super().__init__(parent)
    self.db = db
    self.current_stem: Optional[Stem] = None

    # UI初期化
    self.init_ui()

    # データロード
    self.load_parts_of_speech()
    self.load_phonological_patterns()

    # エディタを無効化（編集対象がない状態）
    self.set_editor_enabled(False)

  def init_ui(self):
    """UIを初期化"""
    # メインレイアウト
    main_layout = QVBoxLayout(self)

    # 保存・キャンセルボタン
    button_layout = QHBoxLayout()

    self.save_button = QPushButton("保存")
    self.save_button.clicked.connect(self.on_save)

    self.cancel_button = QPushButton("キャンセル")
    self.cancel_button.clicked.connect(self.on_cancel)

    button_layout.addWidget(self.save_button)
    button_layout.addWidget(self.cancel_button)
    button_layout.addStretch()

    main_layout.addLayout(button_layout)

    # タブウィジェット
    self.tab_widget = QTabWidget()
    main_layout.addWidget(self.tab_widget)

    # 基本情報タブ
    basic_tab = QWidget()
    basic_layout = QFormLayout(basic_tab)

    # 語幹フィールド
    self.stem_edit = QLineEdit()
    basic_layout.addRow("語幹:", self.stem_edit)

    # 品詞選択コンボボックス
    self.part_of_speech_combo = QComboBox()
    basic_layout.addRow("品詞:", self.part_of_speech_combo)

    # 音韻型選択コンボボックス
    self.phonological_pattern_combo = QComboBox()
    basic_layout.addRow("音韻型:", self.phonological_pattern_combo)

    # 語源情報フィールド
    self.etymology_edit = QTextEdit()
    basic_layout.addRow("語源情報:", self.etymology_edit)

    # 注釈フィールド
    self.notes_edit = QTextEdit()
    basic_layout.addRow("注釈:", self.notes_edit)

    self.tab_widget.addTab(basic_tab, "基本情報")

    # 定義タブ
    definitions_tab = QWidget()
    definitions_layout = QVBoxLayout(definitions_tab)

    # ツールバー
    definitions_toolbar = QHBoxLayout()

    self.add_definition_button = QPushButton("追加")
    self.add_definition_button.clicked.connect(self.on_add_definition)

    self.edit_definition_button = QPushButton("編集")
    self.edit_definition_button.clicked.connect(self.on_edit_definition)

    self.delete_definition_button = QPushButton("削除")
    self.delete_definition_button.clicked.connect(self.on_delete_definition)

    definitions_toolbar.addWidget(self.add_definition_button)
    definitions_toolbar.addWidget(self.edit_definition_button)
    definitions_toolbar.addWidget(self.delete_definition_button)
    definitions_toolbar.addStretch()

    definitions_layout.addLayout(definitions_toolbar)

    # 定義テーブル
    self.definitions_table = QTableView()
    self.definitions_table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
    self.definitions_table.setSelectionMode(QTableView.SelectionMode.SingleSelection)

    # モデル設定
    self.definitions_model = QStandardItemModel()
    self.definitions_model.setHorizontalHeaderLabels(["ID", "番号", "定義", "用例"])

    self.definitions_table.setModel(self.definitions_model)

    # ID列は表示しない
    self.definitions_table.hideColumn(0)

    # 列幅の設定
    header = self.definitions_table.horizontalHeader()
    header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # 番号
    header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # 定義
    header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # 用例

    definitions_layout.addWidget(self.definitions_table)

    self.tab_widget.addTab(definitions_tab, "定義")

    # 活用形タブ
    inflections_tab = QWidget()
    inflections_layout = QVBoxLayout(inflections_tab)

    # ツールバー
    inflections_toolbar = QHBoxLayout()

    self.add_inflection_button = QPushButton("追加")
    self.add_inflection_button.clicked.connect(self.on_add_inflection)

    self.edit_inflection_button = QPushButton("編集")
    self.edit_inflection_button.clicked.connect(self.on_edit_inflection)

    self.delete_inflection_button = QPushButton("削除")
    self.delete_inflection_button.clicked.connect(self.on_delete_inflection)

    inflections_toolbar.addWidget(self.add_inflection_button)
    inflections_toolbar.addWidget(self.edit_inflection_button)
    inflections_toolbar.addWidget(self.delete_inflection_button)
    inflections_toolbar.addStretch()

    inflections_layout.addLayout(inflections_toolbar)

    # 活用形テーブル
    self.inflections_table = QTableView()
    self.inflections_table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
    self.inflections_table.setSelectionMode(QTableView.SelectionMode.SingleSelection)

    # モデル設定
    self.inflections_model = QStandardItemModel()
    self.inflections_model.setHorizontalHeaderLabels(["ID", "カテゴリ", "活用型", "活用形"])

    self.inflections_table.setModel(self.inflections_model)

    # ID列は表示しない
    self.inflections_table.hideColumn(0)

    # 列幅の設定
    header = self.inflections_table.horizontalHeader()
    header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # カテゴリ
    header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # 活用型
    header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # 活用形

    inflections_layout.addWidget(self.inflections_table)

    self.tab_widget.addTab(inflections_tab, "活用形")

  def load_parts_of_speech(self):
    """品詞一覧をロード"""
    self.part_of_speech_combo.clear()
    self.part_of_speech_combo.addItem("", None)

    if not self.db:
      return

    try:
      parts = self.db.get_parts_of_speech()
      for part in parts:
        self.part_of_speech_combo.addItem(part.name, part.id)
    except Exception as e:
      QMessageBox.critical(self, "エラー", f"品詞一覧の取得中にエラーが発生しました: {str(e)}")

  def load_phonological_patterns(self):
    """音韻型一覧をロード"""
    self.phonological_pattern_combo.clear()
    self.phonological_pattern_combo.addItem("", None)

    if not self.db:
      return

    try:
      patterns = self.db.get_phonological_patterns()
      for pattern in patterns:
        self.phonological_pattern_combo.addItem(pattern.name, pattern.id)
    except Exception as e:
      QMessageBox.critical(self, "エラー", f"音韻型一覧の取得中にエラーが発生しました: {str(e)}")

  def set_editor_enabled(self, enabled: bool):
    """
        エディタの有効/無効を切り替え
        
        Args:
            enabled: 有効にする場合はTrue
        """
    # 基本情報フィールド
    self.stem_edit.setEnabled(enabled)
    self.part_of_speech_combo.setEnabled(enabled)
    self.phonological_pattern_combo.setEnabled(enabled)
    self.etymology_edit.setEnabled(enabled)
    self.notes_edit.setEnabled(enabled)

    # 定義関連ボタン
    self.add_definition_button.setEnabled(enabled)
    self.edit_definition_button.setEnabled(enabled)
    self.delete_definition_button.setEnabled(enabled)

    # 活用形関連ボタン
    self.add_inflection_button.setEnabled(enabled)
    self.edit_inflection_button.setEnabled(enabled)
    self.delete_inflection_button.setEnabled(enabled)

    # 保存・キャンセルボタン
    self.save_button.setEnabled(enabled)
    self.cancel_button.setEnabled(enabled)

  def edit_stem(self, stem_id: int):
    """
        指定したIDの語幹を編集
        
        Args:
            stem_id: 語幹ID
        """
    # データベース接続がない場合
    if not self.db:
      QMessageBox.warning(self, "エラー", "データベースが接続されていません。")
      return

    try:
      # 語幹データを取得
      stem = self.db.get_stem_by_id(stem_id)
      if not stem:
        QMessageBox.warning(self, "エラー", f"ID {stem_id} の語幹が見つかりません。")
        return

      # データをセット
      self.current_stem = stem
      self.load_stem_data()

      # 定義をロード
      self.load_definitions()

      # 活用形をロード
      self.load_inflections()

      # エディタを有効化
      self.set_editor_enabled(True)

      # 基本情報タブを選択
      self.tab_widget.setCurrentIndex(0)
    except Exception as e:
      QMessageBox.critical(self, "エラー", f"語幹の取得中にエラーが発生しました: {str(e)}")
      return

  def create_new_stem(self):
    """新しい語幹を作成"""
    # データベースが接続されている場合は品詞と音韻型のリストを再ロード
    if self.db:
      self.load_parts_of_speech()
      self.load_phonological_patterns()

    # 現在の語幹をクリア
    self.current_stem = None

    # フィールドをクリア
    self.stem_edit.clear()
    self.part_of_speech_combo.setCurrentIndex(0)
    self.phonological_pattern_combo.setCurrentIndex(0)
    self.etymology_edit.clear()
    self.notes_edit.clear()

    # 定義テーブルをクリア
    self.definitions_model.removeRows(0, self.definitions_model.rowCount())

    # 活用形テーブルをクリア
    self.inflections_model.removeRows(0, self.inflections_model.rowCount())

    # エディタを有効化
    self.set_editor_enabled(True)

    # 基本情報タブを選択
    self.tab_widget.setCurrentIndex(0)

  def load_stem_data(self):
    """現在選択されている語幹のデータをフォームにロード"""
    if not self.current_stem:
      return

    # 基本情報を設定
    self.stem_edit.setText(self.current_stem.stem)

    # 品詞
    if self.current_stem.part_of_speech_id is not None:
      index = self.part_of_speech_combo.findData(self.current_stem.part_of_speech_id)
      if index >= 0:
        self.part_of_speech_combo.setCurrentIndex(index)
    else:
      self.part_of_speech_combo.setCurrentIndex(0)

    # 音韻型
    if self.current_stem.phonological_pattern_id is not None:
      index = self.phonological_pattern_combo.findData(
        self.current_stem.phonological_pattern_id
      )
      if index >= 0:
        self.phonological_pattern_combo.setCurrentIndex(index)
    else:
      self.phonological_pattern_combo.setCurrentIndex(0)

    # 語源情報
    if self.current_stem.etymology:
      self.etymology_edit.setText(self.current_stem.etymology)
    else:
      self.etymology_edit.clear()

    # 注釈
    if self.current_stem.notes:
      self.notes_edit.setText(self.current_stem.notes)
    else:
      self.notes_edit.clear()

  def load_definitions(self):
    """現在選択されている語幹の定義をテーブルにロード"""
    if not self.current_stem or not self.current_stem.id or not self.db:
      return

    # テーブルをクリア
    self.definitions_model.removeRows(0, self.definitions_model.rowCount())

    try:
      # 定義を取得
      definitions = self.db.get_definitions_by_stem_id(self.current_stem.id)

      # テーブルに追加
      for definition in definitions:
        # ID（非表示だが選択時に使用）
        id_item = QStandardItem(str(definition.id))
        # 番号
        number_item = QStandardItem(str(definition.definition_number or ''))
        # 定義
        def_item = QStandardItem(definition.definition)
        # 用例
        example_item = QStandardItem(definition.example or '')

        # 行を追加
        self.definitions_model.appendRow([id_item, number_item, def_item, example_item])
    except Exception as e:
      QMessageBox.critical(self, "エラー", f"定義の取得中にエラーが発生しました: {str(e)}")

  def load_inflections(self):
    """現在選択されている語幹の活用形をテーブルにロード"""
    if not self.current_stem or not self.current_stem.id or not self.db:
      return

    # テーブルをクリア
    self.inflections_model.removeRows(0, self.inflections_model.rowCount())

    try:
      # 活用形を取得
      inflections = self.db.get_inflections_by_stem_id(self.current_stem.id)

      # テーブルに追加
      for inflection in inflections:
        # ID（非表示だが選択時に使用）
        id_item = QStandardItem(str(inflection.id))
        # カテゴリ
        category_item = QStandardItem(inflection.category or '')
        # 活用型
        type_item = QStandardItem(inflection.inflection_type_name or '')
        # 活用形
        form_item = QStandardItem(inflection.form)

        # 行を追加
        self.inflections_model.appendRow([id_item, category_item, type_item, form_item])
    except Exception as e:
      QMessageBox.critical(self, "エラー", f"活用形の取得中にエラーが発生しました: {str(e)}")

  @Slot()
  def on_save(self):
    """保存ボタンをクリックしたときの処理"""
    # 入力チェック
    if not self.stem_edit.text():
      QMessageBox.warning(self, "エラー", "語幹を入力してください。")
      return

    # データベース接続がない場合
    if not self.db:
      QMessageBox.warning(self, "エラー", "データベースが接続されていません。")
      return

    # 基本情報を取得（語幹は正規化）
    stem_text = normalize_str(self.stem_edit.text())
    part_of_speech_id = self.part_of_speech_combo.currentData()
    phonological_pattern_id = self.phonological_pattern_combo.currentData()

    # 語源と注釈も正規化
    etymology = self.etymology_edit.toPlainText()
    if etymology:
      etymology = normalize_str(etymology)

    notes = self.notes_edit.toPlainText()
    if notes:
      notes = normalize_str(notes)

    try:
      if self.current_stem and self.current_stem.id:
        # 既存の語幹を更新
        stem_id = cast(int, self.current_stem.id)
        success = self.db.update_stem(
          stem_id,
          stem_text,
          part_of_speech_id,
          phonological_pattern_id,
          etymology,
          notes
        )
        if success:
          QMessageBox.information(self, "成功", "語幹を更新しました。")
        else:
          QMessageBox.warning(self, "エラー", "語幹の更新に失敗しました。")
      else:
        # 新しい語幹を追加
        stem_id = self.db.add_stem(
          stem_text,
          part_of_speech_id,
          phonological_pattern_id,
          etymology,
          notes
        )
        if stem_id:
          QMessageBox.information(self, "成功", "語幹を追加しました。")

          # IDが割り当てられたので改めて語幹情報をロード
          self.current_stem = self.db.get_stem_by_id(stem_id)
        else:
          QMessageBox.warning(self, "エラー", "語幹の追加に失敗しました。")

    except Exception as e:
      QMessageBox.critical(self, "エラー", f"保存中にエラーが発生しました: {str(e)}")

  @Slot()
  def on_cancel(self):
    """キャンセルボタンをクリックしたときの処理"""
    if self.current_stem and self.current_stem.id:
      # 既存の語幹の編集をキャンセル
      self.load_stem_data()
      self.load_definitions()
      self.load_inflections()
    else:
      # 新規作成をキャンセル
      self.set_editor_enabled(False)
      self.current_stem = None

      # フィールドをクリア
      self.stem_edit.clear()
      self.part_of_speech_combo.setCurrentIndex(0)
      self.phonological_pattern_combo.setCurrentIndex(0)
      self.etymology_edit.clear()
      self.notes_edit.clear()

      # テーブルをクリア
      self.definitions_model.removeRows(0, self.definitions_model.rowCount())
      self.inflections_model.removeRows(0, self.inflections_model.rowCount())

  @Slot()
  def on_add_definition(self):
    """定義追加ボタンをクリックしたときの処理"""
    if not self.current_stem:
      return

    # データベース接続がない場合
    if not self.db:
      QMessageBox.warning(self, "エラー", "データベースが接続されていません。")
      return

    # 語幹が保存されていない場合
    if not self.current_stem.id:
      QMessageBox.warning(self, "エラー", "先に語幹を保存してください。")
      return

    # 定義編集ダイアログを表示
    dialog = DefinitionDialog(parent=self)
    if dialog.exec() == QDialog.DialogCode.Accepted:
      definition = dialog.get_definition()

      try:
        # 定義を追加
        definition_id = self.db.add_definition(
          cast(int,
               self.current_stem.id),
          definition.definition,
          definition.example
        )

        if definition_id:
          # 定義一覧を再ロード
          self.load_definitions()
        else:
          QMessageBox.warning(self, "エラー", "定義の追加に失敗しました。")

      except Exception as e:
        QMessageBox.critical(self, "エラー", f"定義の追加中にエラーが発生しました: {str(e)}")

  @Slot()
  def on_edit_definition(self):
    """定義編集ボタンをクリックしたときの処理"""
    if not self.current_stem or not self.current_stem.id:
      return

    # データベース接続がない場合
    if not self.db:
      QMessageBox.warning(self, "エラー", "データベースが接続されていません。")
      return

    # 選択された定義を取得
    selected_indexes = self.definitions_table.selectedIndexes()
    if not selected_indexes:
      QMessageBox.warning(self, "エラー", "編集する定義を選択してください。")
      return

    # 選択された行から定義IDを取得
    row = selected_indexes[0].row()
    definition_id = int(self.definitions_model.index(row, 0).data())

    try:
      # 定義データを取得
      definitions = self.db.get_definitions_by_stem_id(cast(int, self.current_stem.id))
      definition = next((d for d in definitions if d.id == definition_id), None)

      if not definition:
        QMessageBox.warning(self, "エラー", "選択された定義が見つかりません。")
        return

      # 定義編集ダイアログを表示（Pydanticモデルを辞書に変換）
      dialog = DefinitionDialog(definition.dict(), parent=self)
      if dialog.exec() == QDialog.DialogCode.Accepted:
        updated_definition = dialog.get_definition()

        try:
          # 定義を更新
          success = self.db.update_definition(
            definition_id,
            updated_definition.definition,
            updated_definition.example
          )

          if success:
            # 定義一覧を再ロード
            self.load_definitions()
          else:
            QMessageBox.warning(self, "エラー", "定義の更新に失敗しました。")

        except Exception as e:
          QMessageBox.critical(self, "エラー", f"定義の更新中にエラーが発生しました: {str(e)}")
    except Exception as e:
      QMessageBox.critical(self, "エラー", f"定義の取得中にエラーが発生しました: {str(e)}")

  @Slot()
  def on_delete_definition(self):
    """定義削除ボタンをクリックしたときの処理"""
    if not self.current_stem:
      return

    # データベース接続がない場合
    if not self.db:
      QMessageBox.warning(self, "エラー", "データベースが接続されていません。")
      return

    # 選択された定義を取得
    selected_indexes = self.definitions_table.selectedIndexes()
    if not selected_indexes:
      QMessageBox.warning(self, "エラー", "削除する定義を選択してください。")
      return

    # 選択された行から定義IDを取得
    row = selected_indexes[0].row()
    definition_id = int(self.definitions_model.index(row, 0).data())

    # 確認ダイアログを表示
    reply = QMessageBox.question(
      self,
      "確認",
      "選択された定義を削除しますか？",
      QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
      QMessageBox.StandardButton.No
    )

    if reply == QMessageBox.StandardButton.Yes:
      try:
        # 定義を削除
        success = self.db.delete_definition(definition_id)

        if success:
          # 定義一覧を再ロード
          self.load_definitions()
        else:
          QMessageBox.warning(self, "エラー", "定義の削除に失敗しました。")

      except Exception as e:
        QMessageBox.critical(self, "エラー", f"定義の削除中にエラーが発生しました: {str(e)}")

  @Slot()
  def on_add_inflection(self):
    """活用形追加ボタンをクリックしたときの処理"""
    if not self.current_stem:
      return

    # データベース接続がない場合
    if not self.db:
      QMessageBox.warning(self, "エラー", "データベースが接続されていません。")
      return

    # 語幹が保存されていない場合
    if not self.current_stem.id:
      QMessageBox.warning(self, "エラー", "先に語幹を保存してください。")
      return

    # 活用形編集ダイアログを表示
    dialog = InflectionDialog(self.db, cast(int, self.current_stem.id), None, self)
    if dialog.exec() == QDialog.DialogCode.Accepted:
      inflection = dialog.get_inflection()

      try:
        # 活用形を追加
        inflection_id = self.db.add_inflection(
          cast(int,
               inflection.stem_id),
          cast(int,
               inflection.inflection_type_id),
          inflection.form
        )

        if inflection_id:
          # 活用形一覧を再ロード
          self.load_inflections()
        else:
          QMessageBox.warning(self, "エラー", "活用形の追加に失敗しました。")

      except Exception as e:
        QMessageBox.critical(self, "エラー", f"活用形の追加中にエラーが発生しました: {str(e)}")

  @Slot()
  def on_edit_inflection(self):
    """活用形編集ボタンをクリックしたときの処理"""
    if not self.current_stem or not self.current_stem.id:
      return

    # データベース接続がない場合
    if not self.db:
      QMessageBox.warning(self, "エラー", "データベースが接続されていません。")
      return

    # 選択された活用形を取得
    selected_indexes = self.inflections_table.selectedIndexes()
    if not selected_indexes:
      QMessageBox.warning(self, "エラー", "編集する活用形を選択してください。")
      return

    # 選択された行から活用形IDを取得
    row = selected_indexes[0].row()
    inflection_id = int(self.inflections_model.index(row, 0).data())

    try:
      # 活用形データを取得
      inflections = self.db.get_inflections_by_stem_id(cast(int, self.current_stem.id))
      inflection = next((i for i in inflections if i.id == inflection_id), None)

      if not inflection:
        QMessageBox.warning(self, "エラー", "選択された活用形が見つかりません。")
        return

      # 活用形編集ダイアログを表示（Pydanticモデルを辞書に変換）
      dialog = InflectionDialog(
        self.db,
        cast(int,
             self.current_stem.id),
        inflection.dict(),
        parent=self
      )
      if dialog.exec() == QDialog.DialogCode.Accepted:
        updated_inflection = dialog.get_inflection()

        try:
          # 活用形を更新
          success = self.db.update_inflection(inflection_id, updated_inflection.form)

          if success:
            # 活用形一覧を再ロード
            self.load_inflections()
          else:
            QMessageBox.warning(self, "エラー", "活用形の更新に失敗しました。")

        except Exception as e:
          QMessageBox.critical(self, "エラー", f"活用形の更新中にエラーが発生しました: {str(e)}")
    except Exception as e:
      QMessageBox.critical(self, "エラー", f"活用形の取得中にエラーが発生しました: {str(e)}")

  @Slot()
  def on_delete_inflection(self):
    """活用形削除ボタンをクリックしたときの処理"""
    if not self.current_stem:
      return

    # データベース接続がない場合
    if not self.db:
      QMessageBox.warning(self, "エラー", "データベースが接続されていません。")
      return

    # 選択された活用形を取得
    selected_indexes = self.inflections_table.selectedIndexes()
    if not selected_indexes:
      QMessageBox.warning(self, "エラー", "削除する活用形を選択してください。")
      return

    # 選択された行から活用形IDを取得
    row = selected_indexes[0].row()
    inflection_id = int(self.inflections_model.index(row, 0).data())

    # 確認ダイアログを表示
    reply = QMessageBox.question(
      self,
      "確認",
      "選択された活用形を削除しますか？",
      QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
      QMessageBox.StandardButton.No
    )

    if reply == QMessageBox.StandardButton.Yes:
      try:
        # 活用形を削除
        success = self.db.delete_inflection(inflection_id)

        if success:
          # 活用形一覧を再ロード
          self.load_inflections()
        else:
          QMessageBox.warning(self, "エラー", "活用形の削除に失敗しました。")

      except Exception as e:
        QMessageBox.critical(self, "エラー", f"活用形の削除中にエラーが発生しました: {str(e)}")
