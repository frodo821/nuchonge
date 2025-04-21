"""活用形編集ダイアログ"""
from typing import Optional, Dict, Any, TYPE_CHECKING

from PySide6.QtWidgets import (
  QDialog,
  QVBoxLayout,
  QFormLayout,
  QLineEdit,
  QComboBox,
  QDialogButtonBox
)

from mcp_dic.utils.normalize_str import normalize_str
from mcp_dic.editor.models import Inflection

if TYPE_CHECKING:
  from mcp_dic.editor.database import DictionaryDatabase


class InflectionDialog(QDialog):
  """活用形編集ダイアログ"""

  def __init__(
    self,
    db: Optional['DictionaryDatabase'],
    stem_id: int,
    inflection: Optional[Dict[str,
                              Any]] = None,
    parent=None
  ):
    """
        活用形編集ダイアログを初期化
        
        Args:
            db: データベース接続
            stem_id: 語幹ID
            inflection: 編集する活用形（Noneの場合は新規作成）
            parent: 親ウィジェット
        """
    super().__init__(parent)
    self.db = db
    self.stem_id = stem_id
    self.inflection = inflection

    # ウィンドウ設定
    self.setWindowTitle("活用形編集" if inflection else "活用形追加")
    self.resize(400, 200)

    # UIを初期化
    self.init_ui()

    # 活用型をロード
    self.load_inflection_types()

    # データをロード
    if inflection:
      self.load_inflection(inflection)

  def init_ui(self):
    """UIを初期化"""
    # メインレイアウト
    layout = QVBoxLayout(self)

    # フォームレイアウト
    form_layout = QFormLayout()

    # 活用型選択コンボボックス
    self.type_combo = QComboBox()
    form_layout.addRow("活用型:", self.type_combo)

    # 活用形フィールド
    self.form_edit = QLineEdit()
    form_layout.addRow("活用形:", self.form_edit)

    layout.addLayout(form_layout)

    # ボタン
    button_box = QDialogButtonBox(
      QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
    )
    button_box.accepted.connect(self.accept)
    button_box.rejected.connect(self.reject)

    layout.addWidget(button_box)

  def load_inflection_types(self):
    """活用型をロード"""
    if not self.db:
      return

    try:
      types = self.db.get_inflection_types()
      for t in types:
        display_text = f"{t.category} - {t.name}"
        self.type_combo.addItem(display_text, t.id)
    except Exception as e:
      from PySide6.QtWidgets import QMessageBox
      QMessageBox.critical(self, "エラー", f"活用型の取得中にエラーが発生しました: {str(e)}")

  def load_inflection(self, inflection: Dict[str, Any]):
    """
        活用形データをロード
        
        Args:
            inflection: 活用形データ
        """
    # 活用型を選択
    type_id = inflection.get('inflection_type_id')
    if type_id is not None:
      index = self.type_combo.findData(type_id)
      if index >= 0:
        self.type_combo.setCurrentIndex(index)

    # 活用形をセット
    self.form_edit.setText(inflection.get('form', ''))

  def get_inflection(self) -> Inflection:
    """
        編集された活用形データを取得（正規化済み）
        
        Returns:
            活用形データ
        """
    # 活用形を取得し、正規化
    form = normalize_str(self.form_edit.text())

    if self.inflection and self.inflection.get('id') is not None:
      # 既存の活用形を更新
      return Inflection(
        id=self.inflection.get('id'),
        stem_id=self.stem_id,
        inflection_type_id=self.type_combo.currentData(),
        form=form
      )
    else:
      # 新規活用形
      return Inflection(
        stem_id=self.stem_id,
        inflection_type_id=self.type_combo.currentData(),
        form=form
      )
