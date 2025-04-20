#!/usr/bin/env python3
"""
SQLite3データベースからマークダウン形式の辞書エントリを自動生成するスクリプト
"""

import os
import sys
import argparse
import sqlite3
from pathlib import Path
import db_utils

# 基本設定
LEXICON_DIR = '../lexicon'

def get_detailed_stem_data(conn, stem_id):
    """
    語幹の詳細情報を取得（活用形や曲用形を構造化）
    """
    # 基本情報を取得
    basic_data = db_utils.get_stem_details(conn, stem_id)

    # 基本データがNoneの場合はNoneを返す
    if basic_data is None:
        print(f"警告: ID {stem_id} の基本データが取得できませんでした。")
        return None

    # 活用/曲用データの構造化
    structured_data = structure_inflections(basic_data)

    return structured_data

def structure_inflections(stem_data):
    """
    活用形や曲用形を構造化したデータに変換
    """
    # 辞書のキーを安全に取得
    if 'part_of_speech' not in stem_data and 'part_of_speech_id' in stem_data:
        # データベースから品詞名を取得
        cursor = db_utils.connect_db().cursor()
        cursor.execute("SELECT name FROM parts_of_speech WHERE id = ?", (stem_data['part_of_speech_id'],))
        result = cursor.fetchone()
        part_of_speech = result['name'] if result else '不明'
        stem_data['part_of_speech'] = part_of_speech
    else:
        part_of_speech = stem_data.get('part_of_speech', '不明')

    if 'phonological_pattern' not in stem_data and 'phonological_pattern_id' in stem_data:
        # データベースから音韻型名を取得
        cursor = db_utils.connect_db().cursor()
        cursor.execute("SELECT name FROM phonological_patterns WHERE id = ?", (stem_data['phonological_pattern_id'],))
        result = cursor.fetchone()
        phonological_pattern = result['name'] if result else '不明'
        stem_data['phonological_pattern'] = phonological_pattern
    else:
        phonological_pattern = stem_data.get('phonological_pattern', '不明')

    inflections = stem_data.get('inflections', [])

    # 結果を格納する辞書
    result = stem_data.copy()
    structured_inflections = {}

    # 各品詞の活用/曲用情報を取得
    if inflections:
        # 品詞によってカテゴリ名を選択
        if part_of_speech == '形容詞':
            # 形容詞曲用
            adjective_declension = {}
            for infl in inflections:
                category = infl['inflection_type']['category']
                name = infl['inflection_type']['name']
                form = infl['form']

                # 形容詞曲用カテゴリだけを処理
                if category == '形容詞曲用':
                    adjective_declension[name] = form
                else:
                    if category not in structured_inflections:
                        structured_inflections[category] = {}
                    structured_inflections[category][name] = form

            structured_inflections['形容詞曲用'] = adjective_declension
            structured_inflections['declension'] = {}  # 互換性のため空の辞書を設定

        elif part_of_speech == '名詞':
            # 名詞曲用
            noun_declension = {}
            for infl in inflections:
                category = infl['inflection_type']['category']
                name = infl['inflection_type']['name']
                form = infl['form']

                # 名詞曲用カテゴリだけを処理
                if category == '名詞曲用':
                    noun_declension[name] = form
                else:
                    if category not in structured_inflections:
                        structured_inflections[category] = {}
                    structured_inflections[category][name] = form

            structured_inflections['名詞曲用'] = noun_declension
            structured_inflections['declension'] = {}  # 互換性のため空の辞書を設定

        elif part_of_speech == '動詞':
            # 動詞活用
            verb_conjugation = {}
            for infl in inflections:
                category = infl['inflection_type']['category']
                name = infl['inflection_type']['name']
                form = infl['form']

                # 動詞活用カテゴリだけを処理
                if category == '動詞活用':
                    verb_conjugation[name] = form
                else:
                    if category not in structured_inflections:
                        structured_inflections[category] = {}
                    structured_inflections[category][name] = form

            structured_inflections['動詞活用'] = verb_conjugation
            structured_inflections['conjugation'] = verb_conjugation  # 互換性のため

        else:
            # その他の品詞
            for infl in inflections:
                category = infl['inflection_type']['category']
                name = infl['inflection_type']['name']
                form = infl['form']

                if category not in structured_inflections:
                    structured_inflections[category] = {}
                structured_inflections[category][name] = form

    result['structured_inflections'] = structured_inflections
    return result

def generate_declension_table(stem_data):
    """
    曲用表をマークダウンの表形式で生成（名詞・形容詞用）
    """
    part_of_speech = stem_data['part_of_speech']
    phonological_pattern = stem_data['phonological_pattern']

    # 形容詞と名詞で異なるカテゴリ名を使用
    if part_of_speech == '形容詞':
        inflection_category = '形容詞曲用'
    else:
        inflection_category = '名詞曲用'

    declension_data = stem_data.get('structured_inflections', {}).get(inflection_category, {})

    if not declension_data:
        return "曲用表のデータがありません。\n"

    # 曲用表のヘッダー部分を設定
    md = ""

    # 有生/無生の区別を検出
    has_animate_forms = any('有生' in key for key in declension_data.keys())
    has_inanimate_forms = any('無生' in key for key in declension_data.keys())

    # 格のリスト定義
    cases = ['主格', '対格', '与格', '所格', '属格', '出格', '向格', '共格']

    # 有生と無生の両方のデータがある場合は分けて表示
    if has_animate_forms and has_inanimate_forms:
        # 有生名詞修飾形
        md += "### 有生名詞修飾\n\n"
        md += "| 格   | 単数不定形  | 単数定形  | 複数不定形  | 複数定形  |\n"
        md += "| ---- | --------- | -------- | --------- | -------- |\n"

        # 各格の行を生成
        for case in cases:
            # 対応するキーがあるか確認
            if not any(case in key for key in declension_data.keys()):
                continue

            forms = []
            # 各形式のデータを取得
            form_types = [
                ('有生単数不定' + case, '単数不定形'),
                ('有生単数定' + case, '単数定形'),
                ('有生複数不定' + case, '複数不定形'),
                ('有生複数定' + case, '複数定形')
            ]

            form_values = []
            for db_key, display_type in form_types:
                form = declension_data.get(db_key, "-")
                form_values.append(form)

            # 行を追加（少なくとも1つの値が「-」以外なら表示）
            if any(form != "-" for form in form_values):
                md += f"| {case}  | {form_values[0]}      | {form_values[1]}     | {form_values[2]}    | {form_values[3]}   |\n"

        # 無生名詞修飾形
        md += "\n### 無生名詞修飾\n\n"
        md += "| 格   | 単数不定形  | 単数定形  | 複数不定形  | 複数定形  |\n"
        md += "| ---- | --------- | -------- | --------- | -------- |\n"

        # 各格の行を生成
        for case in cases:
            # 対応するキーがあるか確認
            if not any(case in key for key in declension_data.keys()):
                continue

            forms = []
            # 各形式のデータを取得
            form_types = [
                ('無生単数不定' + case, '単数不定形'),
                ('無生単数定' + case, '単数定形'),
                ('無生複数不定' + case, '複数不定形'),
                ('無生複数定' + case, '複数定形')
            ]

            form_values = []
            for db_key, display_type in form_types:
                form = declension_data.get(db_key, "-")
                form_values.append(form)

            # 行を追加（少なくとも1つの値が「-」以外なら表示）
            if any(form != "-" for form in form_values):
                md += f"| {case}  | {form_values[0]}      | {form_values[1]}     | {form_values[2]}    | {form_values[3]}   |\n"

    # 有生または無生のみの場合
    else:
        # 表のヘッダー
        md += "| 格   | 単数不定形  | 単数定形  | 複数不定形  | 複数定形  |\n"
        md += "| ---- | --------- | -------- | --------- | -------- |\n"

        # アニメーション接頭辞を決定
        animate_prefix = '有生' if has_animate_forms else ('無生' if has_inanimate_forms else '')

        # 各格の行を生成
        for case in cases:
            # 対応するキーがあるか確認
            if not any(case in key for key in declension_data.keys()):
                continue

            # 各形式のデータを取得
            form_types = [
                (animate_prefix + '単数不定' + case, '単数不定形'),
                (animate_prefix + '単数定' + case, '単数定形'),
                (animate_prefix + '複数不定' + case, '複数不定形'),
                (animate_prefix + '複数定' + case, '複数定形')
            ]

            form_values = []
            for db_key, display_type in form_types:
                form = declension_data.get(db_key, "-")
                form_values.append(form)

            # 行を追加（少なくとも1つの値が「-」以外なら表示）
            if any(form != "-" for form in form_values):
                md += f"| {case}  | {form_values[0]}      | {form_values[1]}     | {form_values[2]}    | {form_values[3]}   |\n"

    return md

def generate_conjugation_table(stem_data):
    """
    TAMマトリクス形式の活用表をHTML表形式で生成（動詞用）
    """
    # 'conjugation'または'動詞活用'カテゴリのデータを取得
    conjugation_data = stem_data.get('structured_inflections', {}).get('conjugation', {})

    # もし'conjugation'が空なら'動詞活用'カテゴリを使用
    if not conjugation_data:
        conjugation_data = stem_data.get('structured_inflections', {}).get('動詞活用', {})

    # それでも空なら、データがないと返す
    if not conjugation_data:
        return "活用表のデータがありません。\n"

    stem = stem_data['stem']
    part_of_speech = stem_data['part_of_speech']

    # タイトル（法の情報を追加）
    md = f"\n<h3>{stem}（{part_of_speech}）の直説法活用表</h3>\n\n"

    # 活用形から時制・相・人称・数の情報を抽出して構造化データを作成
    tam_matrix = {}

    # 各活用形を解析してマトリクスに配置（直説法のみを抽出）
    # データ構造に応じて処理する
    for form_type, form in conjugation_data.items():
        # 活用形名から時制・相・人称・数を抽出（直説法のみ）
        if isinstance(form, dict):
            # 古い構造（ネストがある場合）- 現状では使わない
            for sub_form_type, sub_form in form.items():
                if '時制' in sub_form_type and '直説法' in sub_form_type:
                    # ここに元のコードのロジックを適用
                    pass
        else:
            # 新しい構造（フラットな場合）
            if '時制' in form_type and '直説法' in form_type:
                tense = None
                aspect = None
                person = None
                number = None

                # 時制の抽出
                parts = form_type.split('時制')
                if len(parts) > 0:
                    mood_tense = parts[0]  # 例: 直説法現在
                    # 直説法かどうか確認
                    if not '直説法' in mood_tense:
                        continue
                    tense = mood_tense.split('法')[-1] + '時制' if '法' in mood_tense else mood_tense + '時制'  # 現在時制

                    # 相・人称・数の抽出
                    if len(parts) > 1:
                        aspect_person = parts[1]  # 例: 非完了相一人称単数

                        # 相の抽出
                        if '相' in aspect_person:
                            aspect_parts = aspect_person.split('相')
                            aspect = aspect_parts[0] + '相'  # 非完了相

                            # 人称と数の抽出
                            if len(aspect_parts) > 1:
                                person_number = aspect_parts[1]  # 例: 一人称単数

                                if '人称' in person_number:
                                    person_parts = person_number.split('人称')
                                    person = person_parts[0] + '人称'  # 一人称

                                    # 数の抽出
                                    if '単数' in person_number:
                                        number = '単数'
                                    elif '複数' in person_number:
                                        number = '複数'

                # 抽出できた情報を使ってマトリクスに配置
                if tense and aspect and person and number:
                    if tense not in tam_matrix:
                        tam_matrix[tense] = {}
                    if aspect not in tam_matrix[tense]:
                        tam_matrix[tense][aspect] = {}
                    if person not in tam_matrix[tense][aspect]:
                        tam_matrix[tense][aspect][person] = {}

                    tam_matrix[tense][aspect][person][number] = form

    # 時制と相の順序を定義
    tense_order = ['現在時制', '過去時制', '未来時制']
    aspect_order = ['非完了相', '完遂相', '結果状態相', '準備相', '起動相', '終結相']

    # 出現する時制と相を抽出
    tenses = list(tam_matrix.keys())

    # 時制を既定の順序でソート
    sorted_tenses = sorted(tenses, key=lambda t: tense_order.index(t) if t in tense_order else 999)

    # テーブル開始
    md += "<table border=\"1\">\n"

    # ヘッダー行（人称と数）
    md += "<tr style=\"background-color: #e6ef\"><th colspan=\"2\" rowspan=\"2\"></th>"
    md += "<th colspan=\"3\" style=\"text-align: center\">単数</th>"
    md += "<th colspan=\"3\" style=\"text-align: center\">複数</th></tr>\n"

    md += "<tr style=\"background-color: #e6ef\">"
    md += "<th>1人称</th><th>2人称</th><th>3人称</th>"
    md += "<th>1人称</th><th>2人称</th><th>3人称</th></tr>\n"

    # 時制ごとに行グループを生成
    for tense in sorted_tenses:
        # この時制の相を抽出して既定の順序でソート
        aspects_in_tense = list(tam_matrix[tense].keys())
        sorted_aspects = sorted(aspects_in_tense, key=lambda a: aspect_order.index(a) if a in aspect_order else 999)

        if not sorted_aspects:
            continue

        # 時制の行（最初の行）- 時制ごとのrowspan
        md += f"<tr style=\"background-color: #d9df\"><th rowspan=\"{len(sorted_aspects)}\">{tense}</th>"

        # 各相の行を生成
        first_aspect = True
        for aspect in sorted_aspects:
            # 最初の相以外は新しい行を開始
            if not first_aspect:
                md += f"<tr style=\"background-color: #f0ff\">"

            # 相の列
            md += f"<th>{aspect}</th>"

            # ヘッダーと一致させるための人称と数の配置順
            # ヘッダー: 1人称単数, 2人称単数, 3人称単数, 1人称複数, 2人称複数, 3人称複数
            person_numbers = [
                ('一人称', '単数'), ('二人称', '単数'), ('三人称', '単数'),
                ('一人称', '複数'), ('二人称', '複数'), ('三人称', '複数')
            ]

            # 人称と数ごとの活用形
            for person_label, number in person_numbers:
                form = "-"

                # 該当する活用形があればセット
                if (person_label in tam_matrix[tense][aspect] and
                    number in tam_matrix[tense][aspect][person_label]):
                    form = tam_matrix[tense][aspect][person_label][number]

                md += f"<td>{form}</td>"

            md += "</tr>\n"
            first_aspect = False

    # テーブル終了
    md += "</table>\n\n"

    # 直説法以外の活用形（命令法、条件法など）
    non_indicative_forms = {}

    # すべての活用形から直説法以外のものを抽出
    # 動詞活用データはネストがなく、フラットな構造になっている
    for form_type, form in conjugation_data.items():
        if isinstance(form, dict):
            # 古い構造（ネストがある場合）
            for sub_form_type, sub_form in form.items():
                if '直説法' not in sub_form_type:
                    category = '動詞活用'
                    if category not in non_indicative_forms:
                        non_indicative_forms[category] = {}
                    non_indicative_forms[category][sub_form_type] = sub_form
        else:
            # 新しい構造（フラットな場合）
            if '直説法' not in form_type:
                category = '動詞活用'
                if category not in non_indicative_forms:
                    non_indicative_forms[category] = {}
                non_indicative_forms[category][form_type] = form

    if non_indicative_forms:
        md += "### その他の活用形\n\n"
        md += "<table class='special-forms'>\n"
        md += "  <thead>\n"
        md += "    <tr>\n"
        md += "      <th>分類</th>\n"
        md += "      <th>形式</th>\n"
        md += "      <th>活用形</th>\n"
        md += "    </tr>\n"
        md += "  </thead>\n"
        md += "  <tbody>\n"

        for mode, forms in non_indicative_forms.items():
            for form_type, form in sorted(forms.items()):
                md += "    <tr>\n"
                md += f"      <td>{mode}</td>\n"
                md += f"      <td>{form_type}</td>\n"
                md += f"      <td>{form}</td>\n"
                md += "    </tr>\n"

        md += "  </tbody>\n"
        md += "</table>\n"

    return md

def format_detailed_markdown(stem_data):
    """
    詳細なマークダウンテンプレートを生成
    """
    # 基本情報
    stem = stem_data['stem']
    part_of_speech = stem_data['part_of_speech']
    phonological_pattern = stem_data['phonological_pattern']

    # マークダウン文書の開始
    md = f"# 見出し語: {stem}\n\n"

    # 文法情報セクション
    md += "## 文法情報\n"
    md += f"- **類別**: {part_of_speech}\n"
    md += f"- **音韻型**: {phonological_pattern}\n"

    # 品詞別の追加情報
    if part_of_speech == '名詞' or part_of_speech == '代名詞':
        md += f"- **名詞分類**: {'有生' if '有生' in phonological_pattern else '無生'}\n"
    elif part_of_speech == '動詞':
        notes = stem_data.get('notes') or ''
        transitivity = "他動詞" if notes.find('他動詞') >= 0 else "自動詞"
        md += f"- **動詞分類**: {transitivity}\n"

        # 不規則変化の有無
        is_irregular = notes.find('不規則') >= 0
        if is_irregular:
            md += "- **活用**: 不規則変化\n"
        else:
            md += "- **活用**: 規則変化\n"
    elif part_of_speech == '形容詞':
        # 不規則変化の有無
        notes = stem_data.get('notes') or ''
        is_irregular = notes.find('不規則') >= 0
        if is_irregular:
            md += "- **活用**: 不規則変化\n"
        else:
            md += "- **活用**: 規則変化\n"

    # 語源情報セクション
    md += "\n## 語源情報\n"
    etymology = stem_data.get('etymology', '情報なし')
    md += f"{etymology}\n"

    # 定義セクション
    md += "\n## 定義\n"
    definitions = stem_data.get('definitions', [])
    if definitions:
        for definition in definitions:
            num = definition['definition_number']
            text = definition['definition']
            md += f"{num}. {text}\n"
            if definition.get('example'):
                md += f"   例: {definition['example']}\n"
    else:
        md += "定義情報なし\n"

    # 曲用/活用表セクション
    if part_of_speech in ['名詞', '形容詞', '代名詞']:
        md += "\n## 曲用表\n\n"
        md += generate_declension_table(stem_data)
    elif part_of_speech == '動詞':
        md += "\n## 活用表\n\n"
        md += generate_conjugation_table(stem_data)

    # 音韻変化の規則（備考から抽出）
    if stem_data.get('notes') and '音韻変化' in stem_data.get('notes'):
        md += "\n## 音韻変化の規則\n"
        md += stem_data.get('notes') + "\n"

    # 例文セクション
    sentences = stem_data.get('sentences', [])
    if sentences:
        md += "\n## 例文\n"
        for i, sentence in enumerate(sentences, 1):
            form_used = sentence.get('form_used', '')
            if form_used:
                form_used = f"**{form_used}**"
            else:
                form_used = f"**{stem}**"

            md += f"{i}. {form_used} {sentence['original_text']} ({sentence['translation']})\n"

    # 関連語セクション
    related = stem_data.get('related', [])
    if related:
        md += "\n## 関連語\n"
        for relation in related:
            related_stem = relation['related_stem']
            relation_type = relation['relation_type']
            md += f"- {related_stem}: {relation_type}\n"

    return md

def generate_entry_file(conn, stem_id, output_dir, verbose=False):
    """
    指定された語幹IDに対応するマークダウンエントリファイルを生成
    """
    try:
        # 詳細データの取得
        print(f"ステップ1: ID {stem_id} の詳細データを取得中...")
        stem_data = get_detailed_stem_data(conn, stem_id)

        if not stem_data:
            print(f"エラー: ID {stem_id} の語幹情報が見つかりません", file=sys.stderr)
            return False

        print(f"ID {stem_id} のデータ取得成功。見出し語: {stem_data.get('stem', '不明')}")

        # マークダウン形式に変換
        print("ステップ2: マークダウン形式に変換中...")
        markdown_content = format_detailed_markdown(stem_data)

        # ファイル名の決定（同音異義語の場合は接尾辞を追加）
        stem = stem_data['stem']
        part_of_speech = stem_data['part_of_speech']
        filename = stem

        print(f"見出し語: {stem}, 品詞: {part_of_speech}")

        # 同音異義語チェック（同じstemの別エントリがあるか）
        print("ステップ3: 同音異義語のチェック中...")
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT id, part_of_speech_id 
                FROM stems 
                WHERE stem = ? AND id != ?
            """, (stem, stem_id))
            homonyms = cursor.fetchall()

            if homonyms:
                print(f"同音異義語が見つかりました: {homonyms}")

                # 同じ見出し語で別の品詞を持つエントリの場合、品詞を接尾辞として追加
                pos_map = {
                    1: 'noun',    # 名詞
                    2: 'verb',    # 動詞
                    3: 'adj',     # 形容詞
                    4: 'adv',     # 副詞
                    5: 'pron',    # 代名詞
                    6: 'prefix',  # 接頭辞
                    7: 'suffix',  # 接尾辞
                    8: 'conj',    # 接続詞
                    9: 'part'     # 小辞
                }

                # part_of_speech_idの場合
                part_of_speech_id = stem_data.get('part_of_speech_id')
                if part_of_speech_id:
                    pos_suffix = pos_map.get(part_of_speech_id, str(part_of_speech_id))
                # part_of_speechの文字列の場合
                else:
                    pos_suffix_map = {
                        '名詞': 'noun',
                        '動詞': 'verb',
                        '形容詞': 'adj',
                        '副詞': 'adv',
                        '代名詞': 'pron',
                        '接頭辞': 'prefix',
                        '接尾辞': 'suffix',
                        '接続詞': 'conj',
                        '小辞': 'part'
                    }
                    pos_suffix = pos_suffix_map.get(part_of_speech, part_of_speech)

                filename = f"{stem}-{pos_suffix}"
        except sqlite3.Error as e:
            print(f"SQLiteエラー（同音異義語チェック中）: {e}", file=sys.stderr)
            # エラーが発生しても処理を続行

        # ファイルパスの決定
        file_path = os.path.join(output_dir, f"{filename}.md")
        print(f"ステップ4: ファイル生成 - パス: {file_path}")

        # ファイルへの書き込み
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)

            print(f"成功: ファイル {file_path} を生成しました")
            return True
        except Exception as file_error:
            print(f"ファイル書き込みエラー: {file_error}", file=sys.stderr)
            # 書き込み先ディレクトリのパーミッションチェック
            print(f"ディレクトリ情報: {output_dir}")
            try:
                print(f"ディレクトリ存在確認: {os.path.exists(output_dir)}")
                print(f"ディレクトリ書き込み権限: {os.access(output_dir, os.W_OK)}")
            except Exception as dir_error:
                print(f"ディレクトリ情報取得エラー: {dir_error}", file=sys.stderr)
            return False

    except Exception as e:
        print(f"エラー: エントリファイル生成中の例外: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return False

def generate_all_entries(conn, output_dir, verbose=False):
    """
    すべての語幹に対応するマークダウンエントリファイルを生成
    """
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM stems")
    stem_ids = [row['id'] for row in cursor.fetchall()]

    success_count = 0
    error_count = 0

    for stem_id in stem_ids:
        success = generate_entry_file(conn, stem_id, output_dir, verbose)
        if success:
            success_count += 1
        else:
            error_count += 1

    print(f"\n生成完了: 成功 {success_count}, 失敗 {error_count}")
    return success_count, error_count

def main():
    # コマンドライン引数の処理
    parser = argparse.ArgumentParser(description='SQLite3データベースからマークダウン形式の辞書エントリを生成')
    parser.add_argument('-s', '--stem', help='特定の語幹（見出し語）を指定')
    parser.add_argument('-i', '--id', type=int, help='特定の語幹IDを指定')
    parser.add_argument('-a', '--all', action='store_true', help='すべての語幹のエントリを生成')
    parser.add_argument('-o', '--output-dir', default=LEXICON_DIR, help=f'出力ディレクトリ（デフォルト: {LEXICON_DIR}）')
    parser.add_argument('-d', '--database', default=db_utils.DB_PATH, help=f'SQLiteデータベースのパス（デフォルト: {db_utils.DB_PATH}）')
    parser.add_argument('-v', '--verbose', action='store_true', help='詳細な出力')

    args = parser.parse_args()

    # 詳細出力モード
    verbose = args.verbose

    # データベースパスの表示
    db_path = args.database
    print(f"データベースパス: {os.path.abspath(db_path)}")

    # 出力ディレクトリの確認
    output_dir = args.output_dir
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # データベース接続
    conn = db_utils.connect_db(args.database)

    try:
        # 単一エントリの生成
        if args.stem:
            stem_id = db_utils.get_stem_id(conn, args.stem)
            if stem_id:
                generate_entry_file(conn, stem_id, output_dir, verbose)
            else:
                print(f"エラー: 語幹「{args.stem}」が見つかりません", file=sys.stderr)
                return 1

        # IDによる単一エントリの生成
        elif args.id:
            generate_entry_file(conn, args.id, output_dir, verbose)

        # すべてのエントリの生成
        elif args.all:
            generate_all_entries(conn, output_dir, verbose)

        # 引数がない場合はヘルプ表示
        else:
            parser.print_help()
            return 0

    finally:
        conn.close()

    return 0

if __name__ == "__main__":
    sys.exit(main())
