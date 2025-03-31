PRAGMA foreign_keys = OFF;

BEGIN TRANSACTION;

CREATE TABLE parts_of_speech (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  -- 品詞名（動詞、名詞など）
  description TEXT -- 説明
);

CREATE TABLE phonological_patterns (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  -- 音韻型名（前舌、後舌など）
  description TEXT -- 説明
);

CREATE TABLE stems (
  id INTEGER PRIMARY KEY,
  stem TEXT NOT NULL,
  -- 見出し語
  part_of_speech_id INTEGER,
  -- 品詞ID
  phonological_pattern_id INTEGER,
  -- 音韻型ID
  etymology TEXT,
  -- 語源情報（単一テキストフィールド）
  notes TEXT,
  -- 注釈
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (part_of_speech_id) REFERENCES parts_of_speech(id),
  FOREIGN KEY (phonological_pattern_id) REFERENCES phonological_patterns(id)
);

CREATE TABLE definitions (
  id INTEGER PRIMARY KEY,
  stem_id INTEGER NOT NULL,
  -- 語幹ID
  definition_number INTEGER,
  -- 定義番号（1, 2, 3...）
  definition TEXT NOT NULL,
  -- 定義内容
  example TEXT,
  -- 用例
  FOREIGN KEY (stem_id) REFERENCES stems(id)
);

CREATE TABLE inflection_types (
  id INTEGER PRIMARY KEY,
  category TEXT NOT NULL,
  -- カテゴリ（時制、人称、数、格など）
  name TEXT NOT NULL,
  -- 名前（現在形、過去形、単数、複数など）
  description TEXT -- 説明
);

CREATE TABLE inflections (
  id INTEGER PRIMARY KEY,
  stem_id INTEGER NOT NULL,
  -- 語幹ID
  inflection_type_id INTEGER NOT NULL,
  -- 活用タイプID
  form TEXT NOT NULL,
  -- 活用形
  FOREIGN KEY (stem_id) REFERENCES stems(id),
  FOREIGN KEY (inflection_type_id) REFERENCES inflection_types(id)
);

CREATE TABLE sentences (
  id INTEGER PRIMARY KEY,
  original_text TEXT NOT NULL,
  -- 原文
  translation TEXT,
  -- 翻訳
  notes TEXT -- 注釈
);

CREATE TABLE stem_sentence_rel (
  stem_id INTEGER NOT NULL,
  -- 語幹ID
  sentence_id INTEGER NOT NULL,
  -- 例文ID
  form_used TEXT,
  -- 使用されている活用形
  PRIMARY KEY (stem_id, sentence_id),
  FOREIGN KEY (stem_id) REFERENCES stems(id),
  FOREIGN KEY (sentence_id) REFERENCES sentences(id)
);

CREATE TABLE related_stems (
  stem_id INTEGER NOT NULL,
  -- 語幹ID
  related_stem_id INTEGER NOT NULL,
  -- 関連語ID
  relation_type TEXT NOT NULL,
  -- 関連タイプ（類義語、対義語など）
  PRIMARY KEY (stem_id, related_stem_id, relation_type),
  FOREIGN KEY (stem_id) REFERENCES stems(id),
  FOREIGN KEY (related_stem_id) REFERENCES stems(id)
);

CREATE INDEX idx_stems_stem ON stems(stem);

CREATE INDEX idx_inflections_form ON inflections(form);

CREATE INDEX idx_definitions_stem_id ON definitions(stem_id);

COMMIT;
