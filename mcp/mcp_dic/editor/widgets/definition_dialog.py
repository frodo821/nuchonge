"""定義編集ダイアログ"""
from typing import Optional, Dict, Any

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QTextEdit, QDialogButtonBox)

from mcp_dic.utils.normalize_str import normalize_str
from mcp_dic.editor.models import Definition


class DefinitionDialog(QDialog):
  """定義編集ダイアログ"""

  def __init__(self, definition: Optional[Dict[str, Any]] = None, parent=None):
    """
        定義編集ダイアログを初期化
        
        Args:
            definition: 編集する定義（Noneの場合は新規作成）
            parent: 親ウィジェット
        """
    super().__init__(parent)
    self.definition = definition

    # ウィンドウ設定
    self.setWindowTitle("定義編集" if definition else "定義追加")
    self.resize(500, 300)

    # UIを初期化
    self.init_ui()

    # データをロード
    if definition:
      self.load_definition(definition)

  def init_ui(self):
    """UIを初期化"""
    # メインレイアウト
    layout = QVBoxLayout(self)

    # フォームレイアウト
    form_layout = QFormLayout()

    # 定義フィールド
    self.definition_edit = QTextEdit()
    form_layout.addRow("定義:", self.definition_edit)

    # 用例フィールド
    self.example_edit = QTextEdit()
    form_layout.addRow("用例:", self.example_edit)

    layout.addLayout(form_layout)

    # ボタン
    button_box = QDialogButtonBox(
      QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
    )
    button_box.accepted.connect(self.accept)
    button_box.rejected.connect(self.reject)

    layout.addWidget(button_box)

  def load_definition(self, definition: Dict[str, Any]):
    """
        定義データをロード
        
        Args:
            definition: 定義データ
        """
    self.definition_edit.setText(definition.get('definition', ''))
    self.example_edit.setText(definition.get('example', ''))

  def get_definition(self) -> Definition:
    """
        編集された定義データを取得（正規化済み）
        
        Returns:
            定義データ
        """
    # 定義と用例を取得し、正規化
    definition_text = normalize_str(self.definition_edit.toPlainText())
    example_text = self.example_edit.toPlainText()
    if example_text:
      example_text = normalize_str(example_text)

    if self.definition:
      # 既存の定義を更新
      return Definition(
        id=self.definition.get('id'),
        stem_id=self.definition.get('stem_id'),
        definition_number=self.definition.get('definition_number'),
        definition=definition_text,
        example=example_text
      )
    else:
      # 新規定義
      return Definition(definition=definition_text, example=example_text)
