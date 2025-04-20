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

## inflection_typesテーブルの詳細

### テーブル構造
```sql
CREATE TABLE inflection_types (
    id INTEGER PRIMARY KEY,
    category TEXT NOT NULL,      -- カテゴリ（時制、人称、数、格など）
    name TEXT NOT NULL,          -- 名前（現在形、過去形、単数、複数など）
    description TEXT             -- 説明
)
```

### カテゴリ一覧と主要データ

#### 1. 人称 
- 一人称 (id: 31) - 話し手
- 二人称 (id: 32) - 聞き手
- 三人称 (id: 33) - 話し手と聞き手以外

#### 2. 動詞活用
動詞活用は以下の要素の組み合わせで構成されています:
- 法（直説法、条件法、命令法、義務法、可能法、推定法、希求法、様態推量法、伝聞法）
- 時制（未来時制、過去時制、現在時制）
- 相（非完了相、完遂相、結果状態相、準備相、起動相、終結相）
- 人称（一人称、二人称、三人称）
- 数（単数、複数）

例: 「直説法現在時制非完了相一人称単数」(id: 202) - 動詞の直説法現在時制非完了相一人称単数形

#### 3. 名詞曲用
名詞曲用は以下の要素の組み合わせで構成されています:
- 数（単数、複数）
- 定性（定、不定）
- 格（主格、対格、与格、所格、属格、出格、向格、共格）

例: 「単数定主格」(id: 98) - 名詞の単数定主格形

#### 4. 形容詞曲用
形容詞曲用は以下の要素の組み合わせで構成されています:
- 有生/無生
- 数（単数、複数）
- 定性（定、不定）
- 格（主格、対格、与格、所格、属格、出格、向格、共格）

例: 「有生単数定主格」(id: 34) - 形容詞の有生単数定主格形

#### 5. 基本文法カテゴリ
個別に使用される文法カテゴリも含まれています:

- **数**: 
  - 単数 (id: 1) - 単一の対象を指す
  - 複数 (id: 2) - 複数の対象を指す

- **定性**: 
  - 定 (id: 3) - 特定の対象を指す
  - 不定 (id: 4) - 不特定の対象を指す

- **格**: 
  - 主格 (id: 5) - 文の主語を示す
  - 対格 (id: 6) - 動詞の目的語を示す
  - 与格 (id: 7) - 間接目的語や受益者を示す
  - 所格 (id: 8) - 場所や位置を示す
  - 属格 (id: 9) - 所有や関連性を示す
  - 出格 (id: 10) - 起点や出所を示す
  - 向格 (id: 11) - 方向や目的地を示す
  - 共格 (id: 12) - 共同や手段を示す

- **法**: 
  - 直説法 (id: 13) - 事実や現実を述べる
  - 条件法 (id: 14) - 条件や仮定を表現する
  - 命令法 (id: 15) - 命令や要求を表現する
  - 義務法 (id: 16) - 義務や必要性を表現する
  - 可能法 (id: 17) - 可能性を表現する
  - 推定法 (id: 18) - 推測や不確かさを表現する
  - 希求法 (id: 19) - 願望や希望を表現する
  - 様態推量法 (id: 20) - 様態や推量を表現する
  - 伝聞法 (id: 21) - 伝聞情報を表現する

- **時制**: 
  - 未来時制 (id: 22) - 未来の事柄を表す
  - 過去時制 (id: 23) - 過去の事柄を表す
  - 現在時制 (id: 24) - 現在の事柄を表す

- **相**: 
  - 非完了相 (id: 25) - 完了していない動作を表す
  - 完遂相 (id: 26) - 完全に遂行された動作を表す
  - 結果状態相 (id: 27) - 動作の結果の状態を表す
  - 準備相 (id: 28) - 動作の準備段階を表す
  - 起動相 (id: 29) - 動作の開始を表す
  - 終結相 (id: 30) - 動作の終結を表す

### 活用・曲用形の使用方法

このデータベースでは、inflection_typesテーブルで定義された活用・曲用形のIDを使って、inflectionsテーブルで実際の活用形を管理しています。これにより、各語幹（単語）がどのように活用・曲用するかを効率的に管理できます。

#### 活用・曲用形の検索例
```sql
-- 特定の法・時制・相・人称・数の動詞活用形を検索
SELECT i.form
FROM inflections i
JOIN inflection_types it ON i.inflection_type_id = it.id
JOIN stems s ON i.stem_id = s.id
WHERE s.stem = '検索単語' 
  AND it.name = '直説法現在時制非完了相一人称単数';

-- 特定の数・定性・格の名詞曲用形を検索
SELECT i.form
FROM inflections i
JOIN inflection_types it ON i.inflection_type_id = it.id
JOIN stems s ON i.stem_id = s.id
WHERE s.stem = '検索単語' 
  AND it.name = '単数定主格';
```

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
