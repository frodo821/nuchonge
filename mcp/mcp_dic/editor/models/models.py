"""データモデル定義"""
from typing import Optional, List, Dict
from datetime import datetime
from pydantic import BaseModel, Field

from mcp_dic.utils.normalize_str import normalize_str


class Definition(BaseModel):
  """定義データモデル"""
  id: Optional[int] = None
  stem_id: Optional[int] = None
  definition_number: Optional[int] = None
  definition: str
  example: Optional[str] = None

  @classmethod
  def from_dict(cls, data: Dict) -> 'Definition':
    """辞書からモデルを作成"""
    return cls(
      id=data.get('id'),
      stem_id=data.get('stem_id'),
      definition_number=data.get('definition_number'),
      definition=data.get('definition',
                          ''),
      example=data.get('example')
    )

  def normalize(self) -> 'Definition':
    """文字列を正規化したモデルを返す"""
    return Definition(
      id=self.id,
      stem_id=self.stem_id,
      definition_number=self.definition_number,
      definition=normalize_str(self.definition),
      example=normalize_str(self.example) if self.example else None
    )


class Inflection(BaseModel):
  """活用形データモデル"""
  id: Optional[int] = None
  stem_id: Optional[int] = None
  inflection_type_id: Optional[int] = None
  form: str
  category: Optional[str] = None  # 表示用
  inflection_type_name: Optional[str] = None  # 表示用

  @classmethod
  def from_dict(cls, data: Dict) -> 'Inflection':
    """辞書からモデルを作成"""
    return cls(
      id=data.get('id'),
      stem_id=data.get('stem_id'),
      inflection_type_id=data.get('inflection_type_id'),
      form=data.get('form',
                    ''),
      category=data.get('category'),
      inflection_type_name=data.get('inflection_type_name')
    )

  def normalize(self) -> 'Inflection':
    """文字列を正規化したモデルを返す"""
    return Inflection(
      id=self.id,
      stem_id=self.stem_id,
      inflection_type_id=self.inflection_type_id,
      form=normalize_str(self.form),
      category=self.category,
      inflection_type_name=self.inflection_type_name
    )


class Stem(BaseModel):
  """語幹データモデル"""
  id: Optional[int] = None
  stem: str
  part_of_speech_id: Optional[int] = None
  phonological_pattern_id: Optional[int] = None
  etymology: Optional[str] = None
  notes: Optional[str] = None
  created_at: Optional[datetime] = None
  updated_at: Optional[datetime] = None

  # 表示用の追加フィールド
  part_of_speech_name: Optional[str] = None
  phonological_pattern_name: Optional[str] = None

  @classmethod
  def from_dict(cls, data: Dict) -> 'Stem':
    """辞書からモデルを作成"""
    return cls(
      id=data.get('id'),
      stem=data.get('stem',
                    ''),
      part_of_speech_id=data.get('part_of_speech_id'),
      phonological_pattern_id=data.get('phonological_pattern_id'),
      etymology=data.get('etymology'),
      notes=data.get('notes'),
      created_at=data.get('created_at'),
      updated_at=data.get('updated_at'),
      part_of_speech_name=data.get('part_of_speech_name'),
      phonological_pattern_name=data.get('phonological_pattern_name')
    )

  def normalize(self) -> 'Stem':
    """文字列を正規化したモデルを返す"""
    return Stem(
      id=self.id,
      stem=normalize_str(self.stem),
      part_of_speech_id=self.part_of_speech_id,
      phonological_pattern_id=self.phonological_pattern_id,
      etymology=normalize_str(self.etymology) if self.etymology else None,
      notes=normalize_str(self.notes) if self.notes else None,
      created_at=self.created_at,
      updated_at=self.updated_at,
      part_of_speech_name=self.part_of_speech_name,
      phonological_pattern_name=self.phonological_pattern_name
    )


class PartOfSpeech(BaseModel):
  """品詞データモデル"""
  id: Optional[int] = None
  name: str
  description: Optional[str] = None

  @classmethod
  def from_dict(cls, data: Dict) -> 'PartOfSpeech':
    """辞書からモデルを作成"""
    return cls(
      id=data.get('id'),
      name=data.get('name',
                    ''),
      description=data.get('description')
    )


class PhonologicalPattern(BaseModel):
  """音韻型データモデル"""
  id: Optional[int] = None
  name: str
  description: Optional[str] = None

  @classmethod
  def from_dict(cls, data: Dict) -> 'PhonologicalPattern':
    """辞書からモデルを作成"""
    return cls(
      id=data.get('id'),
      name=data.get('name',
                    ''),
      description=data.get('description')
    )


class InflectionType(BaseModel):
  """活用型データモデル"""
  id: Optional[int] = None
  category: str
  name: str
  description: Optional[str] = None

  @classmethod
  def from_dict(cls, data: Dict) -> 'InflectionType':
    """辞書からモデルを作成"""
    return cls(
      id=data.get('id'),
      category=data.get('category',
                        ''),
      name=data.get('name',
                    ''),
      description=data.get('description')
    )
