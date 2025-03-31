# SQLite辞書データベース利用ガイド

## データベース概要
`dictionary.sqlite3`は1000年後の日本語辞書のデータを体系的に管理するSQLiteデータベースです。語幹に対して活用形と例文、および関連語が保存でき、活用形で語幹を検索でき、語幹と活用の種類から活用形が検索できるリレーショナルデータベースです。

## データベース構造
データベースは以下のテーブルから構成されています：

### 基本テーブル
- **stems**: 単語の基本情報（語幹、品詞、音韻型など）
- **definitions**: 単語の定義情報
- **inflections**: 活用形・曲用形
- **sentences**: 例文
- **related_stems**: 単語間の関連（類義語、対義語など）

### 参照テーブル
- **parts_of_speech**: 品詞情報（名詞、動詞、形容詞など）
- **phonological_patterns**: 音韻型情報（前舌、後舌、前舌有生など）
- **inflection_types**: 活用・曲用の種類カテゴリ（時制、人称、数、格など）

### 関連テーブル
- **stem_sentence_rel**: 単語と例文の関連付け

## 主要検索クエリ例

### 1. 基本的な語幹検索
```sql
-- 単語の基本情報検索
SELECT s.stem, pos.name AS part_of_speech, pp.name AS phonological_pattern, s.etymology, s.notes
FROM stems s
JOIN parts_of_speech pos ON s.part_of_speech_id = pos.id
JOIN phonological_patterns pp ON s.phonological_pattern_id = pp.id
WHERE s.stem = '検索単語';

-- 単語の定義検索
SELECT d.definition_number, d.definition, d.example
FROM definitions d
JOIN stems s ON d.stem_id = s.id
WHERE s.stem = '検索単語'
ORDER BY d.definition_number;
```

### 2. 活用形検索
```sql
-- 単語の活用形検索
SELECT i.form, it.category, it.name  
FROM inflections i
JOIN inflection_types it ON i.inflection_type_id = it.id
JOIN stems s ON i.stem_id = s.id
WHERE s.stem = '検索単語'
ORDER BY it.category, it.name;

-- 特定の活用タイプの活用形検索
SELECT i.form 
FROM inflections i
JOIN inflection_types it ON i.inflection_type_id = it.id
JOIN stems s ON i.stem_id = s.id
WHERE s.stem = '検索単語' AND it.category = '時制' AND it.name = '未来';
```

### 3. 活用形から語幹を検索
```sql
SELECT s.stem, pos.name AS part_of_speech
FROM stems s
JOIN inflections i ON s.id = i.stem_id
JOIN parts_of_speech pos ON s.part_of_speech_id = pos.id
WHERE i.form = '検索したい活用形';
```

### 4. 例文検索
```sql
-- 単語が使用されている例文検索
SELECT sen.original_text, sen.translation, ssr.form_used
FROM sentences sen
JOIN stem_sentence_rel ssr ON sen.id = ssr.sentence_id
JOIN stems s ON ssr.stem_id = s.id
WHERE s.stem = '検索単語';
```

### 5. 関連語検索
```sql
SELECT s2.stem AS related_stem, rs.relation_type, pos.name AS part_of_speech
FROM stems s1
JOIN related_stems rs ON s1.id = rs.stem_id
JOIN stems s2 ON rs.related_stem_id = s2.id
JOIN parts_of_speech pos ON s2.part_of_speech_id = pos.id
WHERE s1.stem = '検索単語';
```

## 新規エントリー追加手順

### 1. マスターデータの確認
```sql
-- 品詞一覧の確認
SELECT * FROM parts_of_speech;

-- 音韻型一覧の確認
SELECT * FROM phonological_patterns;

-- 活用タイプ一覧の確認
SELECT * FROM inflection_types;
```

### 2. 語幹情報の追加
```sql
INSERT INTO stems (stem, part_of_speech_id, phonological_pattern_id, etymology, notes)
VALUES ('新単語', 
        (SELECT id FROM parts_of_speech WHERE name = '対象品詞'), 
        (SELECT id FROM phonological_patterns WHERE name = '対象音韻型'),
        '語源情報（現代日本語からの変化過程など）', 
        '注釈（活用パターンなど）');
```

### 3. 定義の追加
```sql
INSERT INTO definitions (stem_id, definition_number, definition, example)
VALUES 
  ((SELECT id FROM stems WHERE stem = '新単語'), 1, '第一義', '用例1'),
  ((SELECT id FROM stems WHERE stem = '新単語'), 2, '第二義', '用例2');
```

### 4. 活用形の追加
```sql
-- 基本活用形の追加
INSERT INTO inflections (stem_id, inflection_type_id, form)
VALUES
  ((SELECT id FROM stems WHERE stem = '新単語'), 
   (SELECT id FROM inflection_types WHERE category = '時制' AND name = '現在'), 
   '現在形'),
  ((SELECT id FROM stems WHERE stem = '新単語'), 
   (SELECT id FROM inflection_types WHERE category = '時制' AND name = '過去'), 
   '過去形');
```

### 5. 例文の追加
```sql
-- 例文の追加
INSERT INTO sentences (original_text, translation, notes)
VALUES ('例文原文', '例文訳', '注釈');

-- 単語と例文の関連付け
INSERT INTO stem_sentence_rel (stem_id, sentence_id, form_used)
VALUES (
  (SELECT id FROM stems WHERE stem = '新単語'),
  (SELECT id FROM sentences WHERE original_text = '例文原文'),
  '使用された活用形'
);
```

### 6. 関連語の追加
```sql
-- 関連語の追加
INSERT INTO related_stems (stem_id, related_stem_id, relation_type)
VALUES (
  (SELECT id FROM stems WHERE stem = '新単語'),
  (SELECT id FROM stems WHERE stem = '関連単語'),
  '関連タイプ（synonym, antonym, derivedなど）'
);
```

## レコード更新と削除

### 更新
```sql
-- 単語情報の更新
UPDATE stems
SET notes = '更新された注釈'
WHERE stem = '対象単語';

-- 定義の更新
UPDATE definitions
SET definition = '更新された定義'
WHERE stem_id = (SELECT id FROM stems WHERE stem = '対象単語')
AND definition_number = 1;
```

### 削除
```sql
-- 注意: 参照整合性のため、関連テーブルから先に削除する必要がある
-- 活用形の削除
DELETE FROM inflections
WHERE stem_id = (SELECT id FROM stems WHERE stem = '対象単語');

-- 定義の削除
DELETE FROM definitions
WHERE stem_id = (SELECT id FROM stems WHERE stem = '対象単語');

-- 単語の削除（関連するすべてのデータを先に削除した後）
DELETE FROM stems
WHERE stem = '対象単語';
```

## データベース管理コマンド

### 基本操作
```bash
# データベースへの接続
sqlite3 dictionary.sqlite3

# テーブル一覧の表示
.tables

# テーブルのスキーマ表示
.schema stems

# 結果表示形式の設定
.mode column
.headers on

# データベースのバックアップ
.backup dictionary_backup.sqlite3

# SQLiteシェルの終了
.exit
```

### 高度な操作
```bash
# データベースの整合性チェック
PRAGMA integrity_check;

# インデックスの再構築
REINDEX idx_stems_stem;
REINDEX idx_inflections_form;
```

## 注意点
- 外部キー制約により、関連するテーブル間の整合性が保たれます
- データを削除する際は、依存関係のあるデータから順に削除する必要があります
- アクセス競合を避けるため、複数プロセスから同時に書き込みを行わないよう注意してください
