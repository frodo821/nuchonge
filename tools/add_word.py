#!/usr/bin/env python3
"""
1000年後の日本語辞書単語追加ツール
新しい単語エントリーをデータベースに追加します。
"""

import argparse
import json
import sqlite3
import sys
import os
from pathlib import Path

# 自作モジュールをインポート
try:
    from db_utils import (
        connect_db, get_parts_of_speech, get_phonological_patterns,
        get_inflection_types, get_stem_id, get_stem_details,
        format_markdown_template, get_word_schema
    )
except ImportError:
    print("db_utils.pyが見つかりません。同じディレクトリに配置してください。", file=sys.stderr)
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='1000年後の日本語辞書単語追加ツール')
    
    # 基本情報
    parser.add_argument('--stem', help='語幹')
    parser.add_argument('--part-of-speech', 
                        help='品詞（名詞,動詞,形容詞,副詞,代名詞,接頭辞,接尾辞,接続詞,小辞）')
    parser.add_argument('--phonological-pattern', 
                        help='音韻型（前舌,後舌,前舌有生,前舌無生,後舌有生,後舌無生,混合）')
    parser.add_argument('--etymology', help='語源情報')
    parser.add_argument('--notes', help='注釈')
    
    # 定義情報（JSON形式）
    parser.add_argument('--definitions', help='定義情報（JSON形式）')
    
    # 活用形情報（JSON形式）
    parser.add_argument('--inflections', help='活用形情報（JSON形式）')
    
    # 関連語情報（JSON形式）
    parser.add_argument('--related', help='関連語情報（JSON形式）')
    
    # 既存単語の更新
    parser.add_argument('--update', action='store_true', 
                        help='既存単語の更新モード')
    
    # JSONファイルからのインポート
    parser.add_argument('--import-file', help='JSONファイルからインポート')
    
    # マークダウンファイルの生成
    parser.add_argument('--generate-markdown', action='store_true', 
                        help='対応するMarkdownファイルも生成')
    parser.add_argument('--markdown-dir', default='../lexicon', 
                        help='Markdownファイルの出力先（デフォルト: ../lexicon）')
    
    # スキーマ表示
    parser.add_argument('--schema', action='store_true', 
                        help='入力JSONスキーマを表示して終了')
    
    args = parser.parse_args()
    
    # スキーマオプションの処理
    if args.schema:
        schema = get_word_schema()
        print(json.dumps(schema, ensure_ascii=False, indent=2))
        return
    
    # JSONファイルからのインポート
    if args.import_file:
        try:
            with open(args.import_file, 'r', encoding='utf-8') as f:
                word_data = json.load(f)
            
            # 必須項目の確認
            required_fields = ['stem', 'part_of_speech', 'phonological_pattern']
            missing_fields = [field for field in required_fields if field not in word_data]
            if missing_fields:
                print(f"エラー: JSONファイルに必須フィールドが欠けています: {', '.join(missing_fields)}", 
                      file=sys.stderr)
                sys.exit(1)
                
            # 引数にJSONデータを設定
            args.stem = word_data['stem']
            args.part_of_speech = word_data['part_of_speech']
            args.phonological_pattern = word_data['phonological_pattern']
            args.etymology = word_data.get('etymology')
            args.notes = word_data.get('notes')
            
            # JSONオブジェクトとして保持
            if 'definitions' in word_data:
                args.definitions = json.dumps(word_data['definitions'], ensure_ascii=False)
            if 'inflections' in word_data:
                args.inflections = json.dumps(word_data['inflections'], ensure_ascii=False)
            if 'related' in word_data:
                args.related = json.dumps(word_data['related'], ensure_ascii=False)
                
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"JSONファイルのインポートエラー: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # インポートしない場合は基本情報が必須
        if not args.update and not all([args.stem, args.part_of_speech, args.phonological_pattern]):
            parser.error('新規単語追加には --stem, --part-of-speech, --phonological-pattern が必須です')
        
        # 更新モードの場合はstemのみ必須
        if args.update and not args.stem:
            parser.error('更新モードには --stem が必須です')
    
    # データベース接続
    conn = connect_db()
    
    # 更新モードチェック
    if args.update:
        # 既存単語の存在チェック
        stem_id = get_stem_id(conn, args.stem)
        if stem_id is None:
            print(f"エラー: 更新対象の単語 '{args.stem}' が見つかりません", file=sys.stderr)
            conn.close()
            sys.exit(1)
        
        # 単語の更新処理
        update_word(conn, args, stem_id)
        print(f"単語 '{args.stem}' を更新しました")
        
        # 更新後の最新情報を取得
        stem_id = get_stem_id(conn, args.stem)
    else:
        # 新規単語の存在チェック（重複防止）
        if get_stem_id(conn, args.stem) is not None:
            print(f"エラー: 単語 '{args.stem}' は既に存在します。更新には --update オプションを使用してください", 
                  file=sys.stderr)
            conn.close()
            sys.exit(1)
        
        # 単語の追加処理
        stem_id = add_word(conn, args)
        print(f"単語 '{args.stem}' を追加しました")
    
    # Markdownファイル生成
    if args.generate_markdown and stem_id:
        generate_markdown(conn, stem_id, args.stem, args.markdown_dir)
        print(f"Markdownファイルを生成しました: {args.markdown_dir}/{args.stem}.md")
    
    conn.close()

def add_word(conn, args):
    """新規単語の追加"""
    cursor = conn.cursor()
    
    # 品詞と音韻型のIDを取得
    parts_of_speech = get_parts_of_speech(conn)
    phonological_patterns = get_phonological_patterns(conn)
    
    # 品詞や音韻型が存在するか確認
    if args.part_of_speech not in parts_of_speech:
        print(f"エラー: 品詞 '{args.part_of_speech}' が見つかりません", file=sys.stderr)
        print(f"有効な品詞: {', '.join(parts_of_speech.keys())}", file=sys.stderr)
        sys.exit(1)
    
    if args.phonological_pattern not in phonological_patterns:
        print(f"エラー: 音韻型 '{args.phonological_pattern}' が見つかりません", file=sys.stderr)
        print(f"有効な音韻型: {', '.join(phonological_patterns.keys())}", file=sys.stderr)
        sys.exit(1)
    
    # stems テーブルに基本情報を追加
    cursor.execute(
        """
        INSERT INTO stems 
        (stem, part_of_speech_id, phonological_pattern_id, etymology, notes)
        VALUES (?, ?, ?, ?, ?)
        """,
        (args.stem, 
         parts_of_speech[args.part_of_speech], 
         phonological_patterns[args.phonological_pattern],
         args.etymology,
         args.notes)
    )
    
    stem_id = cursor.lastrowid
    
    # 定義情報の追加
    if args.definitions:
        try:
            definitions = json.loads(args.definitions)
            for definition in definitions:
                cursor.execute(
                    """
                    INSERT INTO definitions 
                    (stem_id, definition_number, definition, example)
                    VALUES (?, ?, ?, ?)
                    """,
                    (stem_id, 
                     definition['definition_number'],
                     definition['definition'],
                     definition.get('example'))
                )
        except (json.JSONDecodeError, KeyError) as e:
            print(f"定義情報のパースエラー: {e}", file=sys.stderr)
    
    # 活用形情報の追加
    if args.inflections:
        inflection_types = {}
        for it in get_inflection_types(conn):
            key = f"{it['category']}:{it['name']}"
            inflection_types[key] = it['id']
            
        try:
            inflections = json.loads(args.inflections)
            for inflection in inflections:
                category = inflection['inflection_type']['category']
                name = inflection['inflection_type']['name']
                form = inflection['form']
                
                type_key = f"{category}:{name}"
                if type_key not in inflection_types:
                    print(f"警告: 活用タイプ '{type_key}' が見つかりません。スキップします。", file=sys.stderr)
                    continue
                
                cursor.execute(
                    """
                    INSERT INTO inflections 
                    (stem_id, inflection_type_id, form)
                    VALUES (?, ?, ?)
                    """,
                    (stem_id, inflection_types[type_key], form)
                )
        except (json.JSONDecodeError, KeyError) as e:
            print(f"活用形情報のパースエラー: {e}", file=sys.stderr)
    
    # 関連語情報の追加
    if args.related:
        try:
            related_words = json.loads(args.related)
            for related in related_words:
                related_stem = related['related_stem']
                relation_type = related['relation_type']
                
                # 関連語の存在確認
                related_stem_id = get_stem_id(conn, related_stem)
                if related_stem_id is None:
                    print(f"警告: 関連語 '{related_stem}' が見つかりません。スキップします。", file=sys.stderr)
                    continue
                
                cursor.execute(
                    """
                    INSERT INTO related_stems 
                    (stem_id, related_stem_id, relation_type)
                    VALUES (?, ?, ?)
                    """,
                    (stem_id, related_stem_id, relation_type)
                )
        except (json.JSONDecodeError, KeyError) as e:
            print(f"関連語情報のパースエラー: {e}", file=sys.stderr)
    
    conn.commit()
    return stem_id

def update_word(conn, args, stem_id):
    """既存単語の更新"""
    cursor = conn.cursor()
    
    # 基本情報の更新
    update_fields = []
    update_params = []
    
    if args.part_of_speech:
        parts_of_speech = get_parts_of_speech(conn)
        if args.part_of_speech not in parts_of_speech:
            print(f"エラー: 品詞 '{args.part_of_speech}' が見つかりません", file=sys.stderr)
            print(f"有効な品詞: {', '.join(parts_of_speech.keys())}", file=sys.stderr)
            sys.exit(1)
        update_fields.append("part_of_speech_id = ?")
        update_params.append(parts_of_speech[args.part_of_speech])
    
    if args.phonological_pattern:
        phonological_patterns = get_phonological_patterns(conn)
        if args.phonological_pattern not in phonological_patterns:
            print(f"エラー: 音韻型 '{args.phonological_pattern}' が見つかりません", file=sys.stderr)
            print(f"有効な音韻型: {', '.join(phonological_patterns.keys())}", file=sys.stderr)
            sys.exit(1)
        update_fields.append("phonological_pattern_id = ?")
        update_params.append(phonological_patterns[args.phonological_pattern])
    
    if args.etymology is not None:
        update_fields.append("etymology = ?")
        update_params.append(args.etymology)
    
    if args.notes is not None:
        update_fields.append("notes = ?")
        update_params.append(args.notes)
    
    # 更新すべき基本情報があれば実行
    if update_fields:
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        
        query = f"""
        UPDATE stems 
        SET {', '.join(update_fields)}
        WHERE id = ?
        """
        update_params.append(stem_id)
        
        cursor.execute(query, update_params)
    
    # 定義情報の更新
    if args.definitions:
        try:
            # 既存の定義を削除
            cursor.execute("DELETE FROM definitions WHERE stem_id = ?", (stem_id,))
            
            # 新しい定義を追加
            definitions = json.loads(args.definitions)
            for definition in definitions:
                cursor.execute(
                    """
                    INSERT INTO definitions 
                    (stem_id, definition_number, definition, example)
                    VALUES (?, ?, ?, ?)
                    """,
                    (stem_id, 
                     definition['definition_number'],
                     definition['definition'],
                     definition.get('example'))
                )
        except (json.JSONDecodeError, KeyError) as e:
            print(f"定義情報のパースエラー: {e}", file=sys.stderr)
    
    # 活用形情報の更新
    if args.inflections:
        inflection_types = {}
        for it in get_inflection_types(conn):
            key = f"{it['category']}:{it['name']}"
            inflection_types[key] = it['id']
            
        try:
            # 既存の活用形を削除
            cursor.execute("DELETE FROM inflections WHERE stem_id = ?", (stem_id,))
            
            # 新しい活用形を追加
            inflections = json.loads(args.inflections)
            for inflection in inflections:
                category = inflection['inflection_type']['category']
                name = inflection['inflection_type']['name']
                form = inflection['form']
                
                type_key = f"{category}:{name}"
                if type_key not in inflection_types:
                    print(f"警告: 活用タイプ '{type_key}' が見つかりません。スキップします。", file=sys.stderr)
                    continue
                
                cursor.execute(
                    """
                    INSERT INTO inflections 
                    (stem_id, inflection_type_id, form)
                    VALUES (?, ?, ?)
                    """,
                    (stem_id, inflection_types[type_key], form)
                )
        except (json.JSONDecodeError, KeyError) as e:
            print(f"活用形情報のパースエラー: {e}", file=sys.stderr)
    
    # 関連語情報の更新
    if args.related:
        try:
            # 既存の関連語を削除
            cursor.execute("DELETE FROM related_stems WHERE stem_id = ?", (stem_id,))
            
            # 新しい関連語を追加
            related_words = json.loads(args.related)
            for related in related_words:
                related_stem = related['related_stem']
                relation_type = related['relation_type']
                
                # 関連語の存在確認
                related_stem_id = get_stem_id(conn, related_stem)
                if related_stem_id is None:
                    print(f"警告: 関連語 '{related_stem}' が見つかりません。スキップします。", file=sys.stderr)
                    continue
                
                cursor.execute(
                    """
                    INSERT INTO related_stems 
                    (stem_id, related_stem_id, relation_type)
                    VALUES (?, ?, ?)
                    """,
                    (stem_id, related_stem_id, relation_type)
                )
        except (json.JSONDecodeError, KeyError) as e:
            print(f"関連語情報のパースエラー: {e}", file=sys.stderr)
    
    conn.commit()

def generate_markdown(conn, stem_id, stem, markdown_dir):
    """単語のMarkdownファイル生成"""
    stem_data = get_stem_details(conn, stem_id)
    markdown_content = format_markdown_template(stem_data)
    
    # 出力ディレクトリ確認
    os.makedirs(markdown_dir, exist_ok=True)
    
    # ファイル書き込み
    output_path = os.path.join(markdown_dir, f"{stem}.md")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)

if __name__ == "__main__":
    main()
