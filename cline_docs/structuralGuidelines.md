# 構造的ガイドライン

## エントリー構造とフォーマット

### 基本エントリー構造
辞書エントリーは以下の構造で統一します：

```markdown
# 見出し語: [単語]

## 文法情報
- **類別**: [名詞/動詞/形容詞/副詞/その他]
- **音韻型**: [前舌/後舌]
- **名詞分類**: [有生/無生]（名詞の場合）
- **動詞分類**: [前舌/後舌]（動詞の場合）

## 語源情報
[現代日本語からの変化過程]

## 定義
1. [第一義]
2. [第二義]（複数の意味がある場合）

## 曲用/活用表
[名詞の場合は格変化、動詞の場合は時制・人称変化]

## 例文
1. [例文1]
2. [例文2]

## 関連語
- [同義語/反義語/関連語]

## 備考
[特記事項]
```

### 見出し語の形式
- 見出し語は基本形で表示（名詞は主格不定単数形の語幹、動詞は不定詞形）
- 必要に応じて発音記号を追加
- 同形異義語の場合は数字を付加して区別（例：「kar¹」「kar²」）

### 文法情報の記述
- 品詞分類を最初に明記
- 語の文法的特性に関する情報を箇条書きで列挙
- 品詞特有の情報を追加（名詞の場合は有生/無生、動詞の場合は自動詞/他動詞など）

## 用法ラベルシステム

### ラベルの表記形式
ラベルは括弧内に斜体で表記：
- *(公式)*
- *(口語)*
- *(専門)*
- *(古語)*
- *(新語)*

### ラベルの配置
- 定義の直前に配置
- 複数のラベルがある場合はセミコロンで区切る：*(公式; 専門)*
- 特定の意味にのみ適用される場合は、その意味の番号の直前に配置

## 発音表記システム

### 音素表記
- 国際音声記号（IPA）を使用
- 特殊な音素：/n̩/, /r̩/, /l̩/, /m̩/（音節主音）
- 強勢記号は語幹の最初の音節に「ˈ」を付加して表示

### 発音変異の表記
- 環境による変異は斜線で区切る：/ç/ → [ç]／[ʃ]
- 任意の音素は括弧で囲む：/(ə)/
- 音節境界は「.」で表記：/çit.n̩/

## 格変化表示

### 名詞の格変化表
名詞の曲用表は以下の形式で表示：

| 格   | 単数不定形  | 単数定形  | 複数不定形  | 複数定形  |
| ---- | --------- | -------- | --------- | -------- |
| 主格  | 形式      | 形式      | 形式      | 形式      |
| 対格  | 形式      | 形式      | 形式      | 形式      |
| ...  | ...       | ...      | ...       | ...      |

### 形容詞の格変化表
形容詞の曲用表は以下の形式で表示：

```markdown
### 有生名詞修飾

| 格   | 単数不定形  | 単数定形  | 複数不定形  | 複数定形  |
| ---- | --------- | -------- | --------- | -------- |
| 主格  | 形式      | 形式      | 形式      | 形式      |
| 対格  | 形式      | 形式      | 形式      | 形式      |
| ...  | ...       | ...      | ...       | ...      |

### 無生名詞修飾

| 格   | 単数不定形  | 単数定形  | 複数不定形  | 複数定形  |
| ---- | --------- | -------- | --------- | -------- |
| 主格  | 形式      | 形式      | 形式      | 形式      |
| 対格  | 形式      | 形式      | 形式      | 形式      |
| ...  | ...       | ...      | ...       | ...      |
```

### 動詞の活用表 (TAMマトリクス)

動詞の活用表は、時制(Tense)・相(Aspect)・法(Mood)を統合したTAMマトリクス形式で表示します。Markdownに埋め込めるHTMLテーブルを使用して、以下の情報を体系的に表示します：

```markdown
### 動詞（意味）の活用表

<table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse;">
  <thead>
    <tr style="background-color: #e6e6ff;">
      <th colspan="2" rowspan="2"></th>
      <th colspan="3" style="text-align: center;">単数</th>
      <th colspan="3" style="text-align: center;">複数</th>
    </tr>
    <tr style="background-color: #e6e6ff;">
      <th>1人称</th>
      <th>2人称</th>
      <th>3人称</th>
      <th>1人称</th>
      <th>2人称</th>
      <th>3人称</th>
    </tr>
  </thead>
  <tbody>
    <!-- 直説法 -->
    <tr style="background-color: #f0f0ff;">
      <th rowspan="3" style="background-color: #d9d9ff;">直説法</th>
      <th>現在</th>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
    </tr>
    <tr style="background-color: #f0f0ff;">
      <th>過去</th>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
    </tr>
    <tr style="background-color: #f0f0ff;">
      <th>未来</th>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
    </tr>
    <!-- 条件法 -->
    <tr style="background-color: #fff0f0;">
      <th rowspan="3" style="background-color: #ffd9d9;">条件法</th>
      <th>現在</th>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
    </tr>
    <tr style="background-color: #fff0f0;">
      <th>過去</th>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
    </tr>
    <tr style="background-color: #fff0f0;">
      <th>未来</th>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
    </tr>
    <!-- 命令法 -->
    <tr style="background-color: #f0fff0;">
      <th rowspan="1" style="background-color: #d9ffd9;">命令法</th>
      <th>現在</th>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
    </tr>
    <!-- 義務法 -->
    <tr style="background-color: #fff0ff;">
      <th rowspan="3" style="background-color: #ffd9ff;">義務法</th>
      <th>現在</th>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
    </tr>
    <tr style="background-color: #fff0ff;">
      <th>過去</th>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
    </tr>
    <tr style="background-color: #fff0ff;">
      <th>未来</th>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
    </tr>
    <!-- 可能法 -->
    <tr style="background-color: #f0f0f0;">
      <th rowspan="3" style="background-color: #d9d9d9;">可能法</th>
      <th>現在</th>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
    </tr>
    <tr style="background-color: #f0f0f0;">
      <th>過去</th>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
    </tr>
    <tr style="background-color: #f0f0f0;">
      <th>未来</th>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
    </tr>
    <!-- 推定法 -->
    <tr style="background-color: #fffff0;">
      <th rowspan="3" style="background-color: #ffffd9;">推定法</th>
      <th>現在</th>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
    </tr>
    <tr style="background-color: #fffff0;">
      <th>過去</th>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
    </tr>
    <tr style="background-color: #fffff0;">
      <th>未来</th>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
    </tr>
    <!-- 希求法 -->
    <tr style="background-color: #f0ffff;">
      <th rowspan="3" style="background-color: #d9ffff;">希求法</th>
      <th>現在</th>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
    </tr>
    <tr style="background-color: #f0ffff;">
      <th>過去</th>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
    </tr>
    <tr style="background-color: #f0ffff;">
      <th>未来</th>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
    </tr>
    <!-- 様態推量法 -->
    <tr style="background-color: #f0ffe0;">
      <th rowspan="3" style="background-color: #d9ffc0;">様態推量法</th>
      <th>現在</th>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
    </tr>
    <tr style="background-color: #f0ffe0;">
      <th>過去</th>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
    </tr>
    <tr style="background-color: #f0ffe0;">
      <th>未来</th>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
    </tr>
    <!-- 伝聞法 -->
    <tr style="background-color: #ffe0f0;">
      <th rowspan="3" style="background-color: #ffc0d9;">伝聞法</th>
      <th>現在</th>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
    </tr>
    <tr style="background-color: #ffe0f0;">
      <th>過去</th>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
    </tr>
    <tr style="background-color: #ffe0f0;">
      <th>未来</th>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
      <td>形式</td>
    </tr>
  </tbody>
</table>

### 相（アスペクト）形式（3人称単数現在形）

<table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse;">
  <tr style="background-color: #fffff0;">
    <th style="background-color: #f2f2d9;">完遂相（-sm-）</th>
    <td>形式</td>
    <th style="background-color: #f2f2d9;">結果状態相（-tr-）</th>
    <td>形式</td>
  </tr>
  <tr style="background-color: #fffff0;">
    <th style="background-color: #f2f2d9;">先行準備相（-tk-）</th>
    <td>形式</td>
    <th style="background-color: #f2f2d9;">起動相（-ds-）</th>
    <td>形式</td>
  </tr>
  <tr style="background-color: #fffff0;">
    <th style="background-color: #f2f2d9;">終結相（-və-/-v-）</th>
    <td>形式</td>
    <th style="background-color: #f2f2d9;"></th>
    <td></td>
  </tr>
</table>

### 代表的複合形式

<table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse;">
  <tr style="background-color: #f5f5f5;">
    <th style="background-color: #e6e6e6; width: 200px;">過去完遂相</th>
    <td>形式</td>
    <td style="font-style: italic;">意味説明</td>
  </tr>
  <tr style="background-color: #f5f5f5;">
    <th style="background-color: #e6e6e6;">未来結果状態相</th>
    <td>形式</td>
    <td style="font-style: italic;">意味説明</td>
  </tr>
  <!-- 追加の複合形式 -->
</table>
```

主な活用表の特徴：
1. **直説法セクション**: 現在形・過去形・未来形の基本活用
2. **条件法・命令法など**: 状況に応じて必要な法を追加
3. **アスペクト形式表**: 代表的な5つのアスペクト接辞の活用例
4. **代表的複合形式表**: 時制・相・法の代表的な組み合わせ例とその意味

形態素境界（ハイフン）は表記せず、活用形全体を一つの単語として表示します。

## 相互参照規則

### 参照タイプ
- **同義語参照**：「⇒ [語]」形式
- **関連語参照**：「→ [語]」形式
- **反義語参照**：「⇔ [語]」形式
- **派生語参照**：「⊂ [語]」形式
- **語源参照**：「← [語]」形式

### 参照位置
- 定義内の特定の単語への参照は、その単語の直後に配置
- 見出し語全体に関する参照は「関連語」セクションに配置
- 特定の定義に関する参照は、その定義の末尾に配置

## 例文提示形式

### 基本形式
例文は以下の形式で提示：
1. 1000年後の日本語による例文
2. 括弧内に現代日本語訳

### 文法的特徴の強調
- 見出し語の使用例では、その語を **太字** で強調
- 特定の文法的特徴を示す場合は、関連部分に下線を引く

### 例文の配列
- 基本的な用法から複雑な用法へと順に配列
- 異なる文法的環境での使用例を含める
- 異なる意味での使用例を意味の番号順に配列

## 語彙間関係の表示

### 派生関係
- 接頭辞派生：「接頭辞-」の形式で表示
- 接尾辞派生：「-接尾辞」の形式で表示
- 複合語派生：構成要素をプラス記号（+）で結合

### 語彙の階層関係
- 上位語：「⊃」記号で表示
- 下位語：「⊂」記号で表示
- 同位語：「≈」記号で表示

## 注釈と備考

### 注釈の種類
- **使用上の注意**：特定の使用上の制約や注意点
- **文化的背景**：語の使用に関連する文化的情報
- **文法的特徴**：特殊な文法的振る舞い
- **語用論的情報**：実際の使用文脈に関する情報

### 注釈の形式
注釈は「備考」セクションに箇条書きで記載します。特に重要な注釈は先頭に配置します。
