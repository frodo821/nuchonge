#!/usr/bin/env python3
"""
1000年後の日本語辞書検索ツール
単語の検索と表示を行います。
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
        connect_db, get_stem_id, get_stem_details, format_markdown_template
    )
except ImportError:
    print("db_utils.pyが見つかりません。同じディレクトリに配置してください。", file=sys.stderr)
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='1000年後の日本語辞書検索ツール')
    
    # 検索条件オプション
    parser.add_argument('--stem', help='語幹で検索')
    parser.add_argument('--form', help='活用形で検索')
    parser.add_argument('--part-of-speech', help='品詞で検索')
    parser.add_argument('--phonological-pattern', help='音韻型で検索')
    parser.add_argument('--definition', help='定義内容で検索（部分一致）')
    
    # 出力形式オプション
    parser.add_argument('--format', choices=['text', 'json', 'markdown'], 
                        default='text', help='出力形式（デフォルトはtext）')
    parser.add_argument('--output', help='出力ファイル（指定がなければ標準出力）')
    
    # 表示オプション
    parser.add_argument('--show-all', action='store_true', 
                        help='すべての情報を表示')
    parser.add_argument('--show-definitions', action='store_true', 
                        help='定義を表示')
    parser.add_argument('--show-inflections', action='store_true', 
                        help='活用形を表示')
    parser.add_argument('--show-sentences', action='store_true', 
                        help='例文を表示')
    parser.add_argument('--show-related', action='store_true', 
                        help='関連語を表示')
    
    args = parser.parse_args()
    
    # 検索条件チェック（少なくとも1つの検索条件が必要）
    if not any([args.stem, args.form, args.part_of_speech, 
                args.phonological_pattern, args.definition]):
        parser.error('少なくとも1つの検索条件を指定してください')
    
    # データベース接続
    conn = connect_db()
    
    # 検索実行
    results = search_words(conn, args)
    
    # 結果出力
    if not results:
        print("検索条件に一致する単語が見つかりませんでした。", file=sys.stderr)
        return
    
    if args.format == 'json':
        output = format_json(results)
    elif args.format == 'markdown':
        output = format_markdown(results)
    else:  # text
        output = format_text(results, args)
    
    # 出力先
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"検索結果を {args.output} に保存しました。")
    else:
        print(output)
    
    conn.close()

def search_words(conn, args):
    """検索条件に基づいて単語を検索"""
    query_parts = []
    query_params = []
    joins = []
    
    # 語幹検索
    if args.stem:
        query_parts.append("s.stem = ?")
        query_params.append(args.stem)
    
    # 活用形検索
    if args.form:
        joins.append("JOIN inflections i ON s.id = i.stem_id")
        query_parts.append("i.form = ?")
        query_params.append(args.form)
    
    # 品詞検索
    if args.part_of_speech:
        joins.append("JOIN parts_of_speech pos ON s.part_of_speech_id = pos.id")
        query_parts.append("pos.name = ?")
        query_params.append(args.part_of_speech)
    
    # 音韻型検索
    if args.phonological_pattern:
        joins.append("JOIN phonological_patterns pp ON s.phonological_pattern_id = pp.id")
        query_parts.append("pp.name = ?")
        query_params.append(args.phonological_pattern)
    
    # 定義検索
    if args.definition:
        joins.append("JOIN definitions d ON s.id = d.stem_id")
        query_parts.append("d.definition LIKE ?")
        query_params.append(f"%{args.definition}%")
    
    # JOINs de-duplication
    unique_joins = list(dict.fromkeys(joins))
    
    # クエリ構築
    query = "SELECT DISTINCT s.id, s.stem FROM stems s "
    if unique_joins:
        query += " ".join(unique_joins) + " "
    if query_parts:
        query += "WHERE " + " AND ".join(query_parts)
    
    cursor = conn.cursor()
    cursor.execute(query, query_params)
    
    # 検索結果から詳細情報を取得
    results = []
    for row in cursor.fetchall():
        stem_details = get_stem_details(conn, row['id'])
        results.append(stem_details)
    
    return results

def format_text(results, args):
    """テキスト形式で結果を整形"""
    output = []
    
    for word in results:
        word_info = [f"単語: {word['stem']}"]
        word_info.append(f"品詞: {word['part_of_speech']}")
        word_info.append(f"音韻型: {word['phonological_pattern']}")
        
        if args.show_all or args.show_definitions:
            word_info.append("\n定義:")
            for definition in word['definitions']:
                deftext = f"  {definition['definition_number']}. {definition['definition']}"
                if definition.get('example'):
                    deftext += f" (例: {definition['example']})"
                word_info.append(deftext)
        
        if args.show_all or args.show_inflections:
            word_info.append("\n活用形:")
            current_category = None
            for inflection in word['inflections']:
                category = inflection['inflection_type']['category']
                name = inflection['inflection_type']['name']
                form = inflection['form']
                
                if current_category != category:
                    word_info.append(f"  {category}:")
                    current_category = category
                
                word_info.append(f"    {name}: {form}")
        
        if args.show_all or args.show_sentences:
            if word.get('sentences'):
                word_info.append("\n例文:")
                for i, sentence in enumerate(word['sentences'], 1):
                    word_info.append(f"  {i}. {sentence['original_text']}")
                    word_info.append(f"     訳: {sentence['translation']}")
        
        if args.show_all or args.show_related:
            if word.get('related'):
                word_info.append("\n関連語:")
                for related in word['related']:
                    word_info.append(f"  {related['related_stem']} ({related['relation_type']})")
        
        output.append("\n".join(word_info))
    
    if len(results) > 1:
        return "\n\n" + "\n\n---\n\n".join(output)
    else:
        return "\n".join(output)

def format_json(results):
    """JSON形式で結果を整形"""
    # 特殊なオブジェクトを変換するカスタムJSON encoderは不要
    # sqlite3.Rowオブジェクトはすでにdictに変換されている
    return json.dumps(results, ensure_ascii=False, indent=2)

def format_markdown(results):
    """Markdown形式で結果を整形"""
    output = []
    
    for word in results:
        md = format_markdown_template(word)
        output.append(md)
    
    return "\n\n---\n\n".join(output)

if __name__ == "__main__":
    main()
