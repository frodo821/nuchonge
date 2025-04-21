"""データベースアクセスモジュール"""
from typing import List, Dict, Any, Optional, Union, cast
import sqlite3
from pathlib import Path

from mcp_dic.editor.models import (
  Stem,
  Definition,
  Inflection,
  PartOfSpeech,
  PhonologicalPattern,
  InflectionType
)


class DictionaryDatabase:
  """辞書データベースアクセスクラス"""

  def __init__(self, db_path: Optional[str] = None):
    """
        データベース接続を初期化
        
        Args:
            db_path: データベースファイルのパス（Noneの場合はメモリ内DB）
        """
    self.db_path = db_path
    self.conn: Optional[sqlite3.Connection] = None
    self.connect()

  def connect(self):
    """データベースに接続"""
    if self.db_path:
      self.conn = sqlite3.connect(self.db_path)
    else:
      self.conn = sqlite3.connect(':memory:')

    # 行を辞書として取得するように設定
    self.conn.row_factory = sqlite3.Row

    # 外部キー制約を有効化
    self.conn.execute('PRAGMA foreign_keys = ON')

  def close(self):
    """データベース接続を閉じる"""
    if self.conn:
      self.conn.close()
      self.conn = None

  def _check_connection(self):
    """接続が有効かチェックし、必要ならば再接続"""
    if self.conn is None:
      self.connect()

  def get_stems(self, search_term: Optional[str] = None, limit: int = 100) -> List[Stem]:
    """
        語幹を検索
        
        Args:
            search_term: 検索語（Noneの場合は全件取得）
            limit: 取得件数の上限
            
        Returns:
            語幹のリスト
        """
    self._check_connection()
    conn = cast(sqlite3.Connection, self.conn)
    cursor = conn.cursor()

    query = """
            SELECT 
                s.*, 
                p.name as part_of_speech_name,
                pp.name as phonological_pattern_name
            FROM stems s
            LEFT JOIN parts_of_speech p ON s.part_of_speech_id = p.id
            LEFT JOIN phonological_patterns pp ON s.phonological_pattern_id = pp.id
        """

    params = []

    if search_term:
      query += " WHERE s.stem LIKE ? "
      params.append(f"%{search_term}%")

    query += " ORDER BY s.stem LIMIT ?"
    params.append(limit)

    cursor.execute(query, params)
    rows = cursor.fetchall()

    return [Stem.from_dict(dict(row)) for row in rows]

  def get_stem_by_id(self, stem_id: int) -> Optional[Stem]:
    """
        IDで語幹を取得
        
        Args:
            stem_id: 語幹ID
            
        Returns:
            語幹（存在しない場合はNone）
        """
    self._check_connection()
    conn = cast(sqlite3.Connection, self.conn)
    cursor = conn.cursor()

    query = """
            SELECT 
                s.*, 
                p.name as part_of_speech_name,
                pp.name as phonological_pattern_name
            FROM stems s
            LEFT JOIN parts_of_speech p ON s.part_of_speech_id = p.id
            LEFT JOIN phonological_patterns pp ON s.phonological_pattern_id = pp.id
            WHERE s.id = ?
        """

    cursor.execute(query,
                   (stem_id,
                   ))
    row = cursor.fetchone()

    if row:
      return Stem.from_dict(dict(row))
    return None

  def add_stem(
    self,
    stem: str,
    part_of_speech_id: Optional[int] = None,
    phonological_pattern_id: Optional[int] = None,
    etymology: Optional[str] = None,
    notes: Optional[str] = None
  ) -> Optional[int]:
    """
        語幹を追加
        
        Args:
            stem: 語幹
            part_of_speech_id: 品詞ID
            phonological_pattern_id: 音韻型ID
            etymology: 語源情報
            notes: 注釈
            
        Returns:
            追加された語幹のID（失敗時はNone）
        """
    self._check_connection()
    conn = cast(sqlite3.Connection, self.conn)
    cursor = conn.cursor()

    query = """
            INSERT INTO stems (
                stem, part_of_speech_id, phonological_pattern_id, etymology, notes
            ) VALUES (?, ?, ?, ?, ?)
        """

    cursor.execute(query, (stem, part_of_speech_id, phonological_pattern_id, etymology, notes))
    conn.commit()

    return cursor.lastrowid

  def update_stem(
    self,
    stem_id: int,
    stem: str,
    part_of_speech_id: Optional[int] = None,
    phonological_pattern_id: Optional[int] = None,
    etymology: Optional[str] = None,
    notes: Optional[str] = None
  ) -> bool:
    """
        語幹を更新
        
        Args:
            stem_id: 語幹ID
            stem: 語幹
            part_of_speech_id: 品詞ID
            phonological_pattern_id: 音韻型ID
            etymology: 語源情報
            notes: 注釈
            
        Returns:
            更新に成功した場合はTrue
        """
    self._check_connection()
    conn = cast(sqlite3.Connection, self.conn)
    cursor = conn.cursor()

    query = """
            UPDATE stems
            SET stem = ?, part_of_speech_id = ?, phonological_pattern_id = ?, etymology = ?, notes = ?
            WHERE id = ?
        """

    cursor.execute(
      query,
      (stem,
       part_of_speech_id,
       phonological_pattern_id,
       etymology,
       notes,
       stem_id)
    )
    conn.commit()

    return cursor.rowcount > 0

  def delete_stem(self, stem_id: int) -> bool:
    """
        語幹を削除
        
        Args:
            stem_id: 語幹ID
            
        Returns:
            削除に成功した場合はTrue
        """
    self._check_connection()
    conn = cast(sqlite3.Connection, self.conn)
    cursor = conn.cursor()

    query = "DELETE FROM stems WHERE id = ?"

    cursor.execute(query,
                   (stem_id,
                   ))
    conn.commit()

    return cursor.rowcount > 0

  def get_definitions_by_stem_id(self, stem_id: int) -> List[Definition]:
    """
        語幹IDから定義を取得
        
        Args:
            stem_id: 語幹ID
            
        Returns:
            定義のリスト
        """
    self._check_connection()
    conn = cast(sqlite3.Connection, self.conn)
    cursor = conn.cursor()

    query = """
            SELECT * FROM definitions
            WHERE stem_id = ?
            ORDER BY definition_number
        """

    cursor.execute(query,
                   (stem_id,
                   ))
    rows = cursor.fetchall()

    return [Definition.from_dict(dict(row)) for row in rows]

  def add_definition(self,
                     stem_id: int,
                     definition: str,
                     example: Optional[str] = None) -> Optional[int]:
    """
        定義を追加
        
        Args:
            stem_id: 語幹ID
            definition: 定義
            example: 用例
            
        Returns:
            追加された定義のID（失敗時はNone）
        """
    self._check_connection()
    conn = cast(sqlite3.Connection, self.conn)
    cursor = conn.cursor()

    # 次の番号を取得
    query_max = """
            SELECT MAX(definition_number) as max_num
            FROM definitions
            WHERE stem_id = ?
        """

    cursor.execute(query_max,
                   (stem_id,
                   ))
    row = cursor.fetchone()
    next_number = 1

    if row and row['max_num'] is not None:
      next_number = row['max_num'] + 1

    # 定義を追加
    query = """
            INSERT INTO definitions (
                stem_id, definition_number, definition, example
            ) VALUES (?, ?, ?, ?)
        """

    cursor.execute(query, (stem_id, next_number, definition, example))
    conn.commit()

    return cursor.lastrowid

  def update_definition(
    self,
    definition_id: int,
    definition: str,
    example: Optional[str] = None
  ) -> bool:
    """
        定義を更新
        
        Args:
            definition_id: 定義ID
            definition: 定義
            example: 用例
            
        Returns:
            更新に成功した場合はTrue
        """
    self._check_connection()
    conn = cast(sqlite3.Connection, self.conn)
    cursor = conn.cursor()

    query = """
            UPDATE definitions
            SET definition = ?, example = ?
            WHERE id = ?
        """

    cursor.execute(query, (definition, example, definition_id))
    conn.commit()

    return cursor.rowcount > 0

  def delete_definition(self, definition_id: int) -> bool:
    """
        定義を削除
        
        Args:
            definition_id: 定義ID
            
        Returns:
            削除に成功した場合はTrue
        """
    self._check_connection()
    conn = cast(sqlite3.Connection, self.conn)
    cursor = conn.cursor()

    query = "DELETE FROM definitions WHERE id = ?"

    cursor.execute(query,
                   (definition_id,
                   ))
    conn.commit()

    return cursor.rowcount > 0

  def get_inflections_by_stem_id(self, stem_id: int) -> List[Inflection]:
    """
        語幹IDから活用形を取得
        
        Args:
            stem_id: 語幹ID
            
        Returns:
            活用形のリスト
        """

    self._check_connection()
    conn = cast(sqlite3.Connection, self.conn)

    cur = conn.execute(
      f"SELECT inflections.* FROM inflections WHERE inflections.stem_id = {stem_id}",
    )
    rows = cur.fetchall()
    cur.close()

    print(rows)

    query = """
            SELECT inflections.*, t.category, t.name as inflection_type_name
            FROM inflections
            JOIN inflection_types t ON inflections.inflection_type_id = t.id
            WHERE inflections.stem_id = ?
            ORDER BY t.category, t.name
        """.strip()

    cursor = conn.execute(query,
                          (stem_id,
                          ))
    rows = cursor.fetchall()

    print(f"Fetched {len(rows)} inflections for stem_id: {stem_id}")

    cursor.close()

    return [Inflection.from_dict(dict(row)) for row in rows]

  def add_inflection(self, stem_id: int, inflection_type_id: int, form: str) -> Optional[int]:
    """
        活用形を追加
        
        Args:
            stem_id: 語幹ID
            inflection_type_id: 活用型ID
            form: 活用形
            
        Returns:
            追加された活用形のID（失敗時はNone）
        """
    self._check_connection()
    conn = cast(sqlite3.Connection, self.conn)
    cursor = conn.cursor()

    query = """
            INSERT INTO inflections (
                stem_id, inflection_type_id, form
            ) VALUES (?, ?, ?)
        """

    cursor.execute(query, (stem_id, inflection_type_id, form))
    conn.commit()

    return cursor.lastrowid

  def update_inflection(self, inflection_id: int, form: str) -> bool:
    """
        活用形を更新
        
        Args:
            inflection_id: 活用形ID
            form: 活用形
            
        Returns:
            更新に成功した場合はTrue
        """
    self._check_connection()
    conn = cast(sqlite3.Connection, self.conn)
    cursor = conn.cursor()

    query = """
            UPDATE inflections
            SET form = ?
            WHERE id = ?
        """

    cursor.execute(query, (form, inflection_id))
    conn.commit()

    return cursor.rowcount > 0

  def delete_inflection(self, inflection_id: int) -> bool:
    """
        活用形を削除
        
        Args:
            inflection_id: 活用形ID
            
        Returns:
            削除に成功した場合はTrue
        """
    self._check_connection()
    conn = cast(sqlite3.Connection, self.conn)
    cursor = conn.cursor()

    query = "DELETE FROM inflections WHERE id = ?"

    cursor.execute(query,
                   (inflection_id,
                   ))
    conn.commit()

    return cursor.rowcount > 0

  def get_parts_of_speech(self) -> List[PartOfSpeech]:
    """
        品詞一覧を取得
        
        Returns:
            品詞のリスト
        """
    self._check_connection()
    conn = cast(sqlite3.Connection, self.conn)
    cursor = conn.cursor()

    query = """
            SELECT * FROM parts_of_speech
            ORDER BY name
        """

    cursor.execute(query)
    rows = cursor.fetchall()

    return [PartOfSpeech.from_dict(dict(row)) for row in rows]

  def get_phonological_patterns(self) -> List[PhonologicalPattern]:
    """
        音韻型一覧を取得
        
        Returns:
            音韻型のリスト
        """
    self._check_connection()
    conn = cast(sqlite3.Connection, self.conn)
    cursor = conn.cursor()

    query = """
            SELECT * FROM phonological_patterns
            ORDER BY name
        """

    cursor.execute(query)
    rows = cursor.fetchall()

    return [PhonologicalPattern.from_dict(dict(row)) for row in rows]

  def get_inflection_types(self) -> List[InflectionType]:
    """
        活用型一覧を取得
        
        Returns:
            活用型のリスト
        """
    self._check_connection()
    conn = cast(sqlite3.Connection, self.conn)
    cursor = conn.cursor()

    query = """
            SELECT * FROM inflection_types
            ORDER BY category, name
        """

    cursor.execute(query)
    rows = cursor.fetchall()

    return [InflectionType.from_dict(dict(row)) for row in rows]

  def search_by_form(self, form: str, limit: int = 100) -> List[Dict[str, Any]]:
    """
        活用形で検索
        
        Args:
            form: 活用形
            limit: 取得件数の上限
            
        Returns:
            検索結果のリスト（語幹情報付き）
        """
    self._check_connection()
    conn = cast(sqlite3.Connection, self.conn)
    cursor = conn.cursor()

    query = """
            SELECT 
                i.*, s.stem, t.category, t.name as inflection_type_name
            FROM inflections i
            JOIN stems s ON i.stem_id = s.id
            JOIN inflection_types t ON i.inflection_type_id = t.id
            WHERE i.form LIKE ?
            ORDER BY s.stem, t.category, t.name
            LIMIT ?
        """

    cursor.execute(query, (f"%{form}%", limit))
    rows = cursor.fetchall()

    result = []
    for row in rows:
      row_dict = dict(row)
      inflection = Inflection.from_dict(row_dict)
      result.append({'inflection': inflection, 'stem': row_dict['stem']})

    return result
