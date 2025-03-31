#!/usr/bin/env python3
"""
1000年後の日本語辞書例文追加ツール
例文をデータベースに追加し、単語との関連付けを行います。
"""

import argparse
import json
import sqlite3
import sys
import os
import re
from pathlib import Path

# 自作モジュールをインポート
try:
    from db_utils import (
        connect_db, get_stem_id, get_sentence_schema, get_batch_sentences_schema
    )
except ImportError:
    print("db_utils.pyが見つかりません。同じディレクトリに配置してください。", file=sys.stderr)
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='1000年後の日本語辞書例文追加ツール')
    
    # 基本情報
    parser.add_argument('--original', help='原文')
    parser.add_argument('--translation', help='翻訳')
    parser.add_argument('--notes', help='注釈')
    
    # 単語との関連付け
    parser.add_argument('--stems', help='関連付ける単語（カンマ区切り）')
    parser.add_argument('--auto-detect', action='store_true', 
                        help='単語の自動検出')
    
    # JSONファイルからのインポート
    parser.add_argument('--import-file', help='JSONファイルからインポート')
    
    # Markdownファイルからのインポート
    parser.add_argument('--import-markdown', help='例文Markdownファイルからインポート')
    
    # バッチ処理
    parser.add_argument('--batch-file', help='複数例文のバッチ処理（JSONファイル）')
    
    # スキーマ表示
    parser.add_argument('--schema', action='store_true', 
                        help='単一例文入力JSONスキーマを表示して終了')
    parser.add_argument('--batch-schema', action='store_true', 
                        help='バッチ処理用JSONスキーマを表示して終了')
    
    args = parser.parse_args()
    
    # スキーマオプションの処理
    if args.schema:
        schema = get_sentence_schema()
        print(json.dumps(schema, ensure_ascii=False, indent=2))
        return
    elif args.batch_schema:
        schema = get_batch_sentences_schema()
        print(json.dumps(schema, ensure_ascii=False, indent=2))
        return
    
    # 入力チェック
    if not any([args.original and args.translation, args.import_file, 
                args.import_markdown, args.batch_file]):
        parser.error('例文情報、インポートファイル、またはバッチファイルを指定してください')
    
    # データベース接続
    conn = connect_db()
    
    # インポート処理
    if args.import_markdown:
        sentences = import_from_markdown(args.import_markdown)
        for sentence in sentences:
            add_sentence_to_db(conn, sentence, args.auto_detect)
        print(f"{len(sentences)}件の例文を追加しました")
    elif args.import_file:
        sentence = import_from_json(args.import_file)
        add_sentence_to_db(conn, sentence, args.auto_detect)
        print("例文を追加しました")
    elif args.batch_file:
        sentences = import_batch(args.batch_file)
        for sentence in sentences:
            add_sentence_to_db(conn, sentence, args.auto_detect)
        print(f"{len(sentences)}件の例文を追加しました")
    else:
        # 単一例文の追加
        sentence = {
            'original_text': args.original,
            'translation': args.translation,
            'notes': args.notes,
        }
        
        # 単語の関連付け
        if args.stems:
            stem_list = args.stems.split(',')
            sentence['stems'] = []
            for stem_info in stem_list:
                parts = stem_info.split(':')
                if len(parts) == 2:
                    stem, form_used = parts
                else:
                    stem = parts[0]
                    form_used = stem  # デフォルトでは語幹と同じ形を使用
                
                sentence['stems'].append({
                    'stem': stem.strip(),
                    'form_used': form_used.strip()
                })
        
        add_sentence_to_db(conn, sentence, args.auto_detect)
        print(f"例文 '{sentence['original_text']}' を追加しました")
    
    conn.close()

def import_from_markdown(markdown_file):
    """Markdownファイルから例文をインポート"""
    try:
        with open(markdown_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 例文部分を正規表現で抽出
        sentences = []
        
        # 原文と翻訳文のパターン
        original_pattern = re.compile(r'^## 原文\s*\n(.*?)(?=\n##|\Z)', re.MULTILINE | re.DOTALL)
        translation_pattern = re.compile(r'^## 現代日本語訳\s*\n(.*?)(?=\n##|\Z)', re.MULTILINE | re.DOTALL)
        notes_pattern = re.compile(r'^## 文法注釈\s*\n(.*?)(?=\n##|\Z)', re.MULTILINE | re.DOTALL)
        
        # 形態素解析部分
        morphological_pattern = re.compile(r'^## 形態素解析\s*\n(.*?)(?=\n##|\Z)', re.MULTILINE | re.DOTALL)
        
        # 使用単語リスト部分
        words_pattern = re.compile(r'^## 使用単語リスト\s*\n(.*?)(?=\n##|\Z)', re.MULTILINE | re.DOTALL)
        word_line_pattern = re.compile(r'- ([^:]+):(.*)', re.MULTILINE)
        
        # 抽出
        original_match = original_pattern.search(content)
        translation_match = translation_pattern.search(content)
        notes_match = notes_pattern.search(content)
        morphological_match = morphological_pattern.search(content)
        words_match = words_pattern.search(content)
        
        if original_match and translation_match:
            sentence = {
                'original_text': original_match.group(1).strip(),
                'translation': translation_match.group(1).strip(),
                'notes': notes_match.group(1).strip() if notes_match else None,
                'stems': []
            }
            
            # 使用単語リストから単語と活用形を抽出
            if words_match:
                words_content = words_match.group(1)
                for match in word_line_pattern.finditer(words_content):
                    stem = match.group(1).strip()
                    info = match.group(2).strip()
                    
                    # 活用形を推定（情報からの抽出）
                    form_used = stem  # デフォルト値
                    
                    # 形態素解析から活用形を検索
                    if morphological_match:
                        morpho_content = morphological_match.group(1)
                        stem_pattern = re.compile(rf'{stem}\s*=\s*([^(,]+)')
                        stem_match = stem_pattern.search(morpho_content)
                        if stem_match:
                            form_used = stem_match.group(1).strip()
                    
                    sentence['stems'].append({
                        'stem': stem,
                        'form_used': form_used
                    })
            
            sentences.append(sentence)
        else:
            print(f"警告: {markdown_file} からの例文抽出に失敗しました", file=sys.stderr)
        
        return sentences
        
    except FileNotFoundError:
        print(f"エラー: ファイル {markdown_file} が見つかりません", file=sys.stderr)
        sys.exit(1)

def import_from_json(json_file):
    """JSONファイルから例文をインポート"""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 必須項目の確認
        required_fields = ['original_text', 'translation']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            print(f"エラー: JSONファイルに必須フィールドが欠けています: {', '.join(missing_fields)}", 
                  file=sys.stderr)
            sys.exit(1)
        
        # stems フィールドがない場合は空のリストを追加
        if 'stems' not in data:
            data['stems'] = []
        
        return data
        
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"JSONファイルのインポートエラー: {e}", file=sys.stderr)
        sys.exit(1)

def import_batch(batch_file):
    """バッチファイルから複数例文をインポート"""
    try:
        with open(batch_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # データが配列形式であることを確認
        if not isinstance(data, list):
            print("エラー: バッチファイルは例文オブジェクトの配列である必要があります", file=sys.stderr)
            sys.exit(1)
        
        # 各例文の必須項目を確認
        sentences = []
        for i, sentence in enumerate(data):
            if not isinstance(sentence, dict):
                print(f"警告: インデックス {i} の例文がオブジェクト形式ではありません。スキップします。", 
                      file=sys.stderr)
                continue
            
            required_fields = ['original_text', 'translation']
            missing_fields = [field for field in required_fields if field not in sentence]
            if missing_fields:
                print(f"警告: インデックス {i} の例文に必須フィールドが欠けています: {', '.join(missing_fields)}。スキップします。", 
                      file=sys.stderr)
                continue
            
            # stems フィールドがない場合は空のリストを追加
            if 'stems' not in sentence:
                sentence['stems'] = []
            
            sentences.append(sentence)
        
        return sentences
        
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"バッチファイルのインポートエラー: {e}", file=sys.stderr)
        sys.exit(1)

def detect_stems(conn, text):
    """テキストから単語を自動検出"""
    # データベースから全ての語幹を取得
    cursor = conn.cursor()
    cursor.execute("SELECT id, stem FROM stems")
    stems = cursor.fetchall()
    
    # 単語を検出（単純マッチ）
    detected = {}
    for stem in stems:
        if stem['stem'] in text:
            detected[stem['id']] = {
                'stem': stem['stem'],
                'form_used': stem['stem']  # デフォルトでは見つかった形そのものを使用
            }
    
    # 活用形からも検出
    cursor.execute("""
        SELECT s.id, s.stem, i.form
        FROM stems s
        JOIN inflections i ON s.id = i.stem_id
    """)
    
    for row in cursor.fetchall():
        if row['form'] in text and row['form'] != row['stem']:  # 語幹と異なる活用形のみ
            detected[row['id']] = {
                'stem': row['stem'],
                'form_used': row['form']
            }
    
    return list(detected.values())

def add_sentence_to_db(conn, sentence, auto_detect=False):
    """例文をデータベースに追加"""
    cursor = conn.cursor()
    
    # 例文の追加
    cursor.execute(
        """
        INSERT INTO sentences 
        (original_text, translation, notes)
        VALUES (?, ?, ?)
        """,
        (sentence['original_text'], 
         sentence['translation'],
         sentence.get('notes'))
    )
    
    sentence_id = cursor.lastrowid
    
    # 自動検出
    if auto_detect:
        detected_stems = detect_stems(conn, sentence['original_text'])
        
        # 既存のステムリストと自動検出されたステムをマージ
        existing_stems = {s['stem']: s for s in sentence.get('stems', [])}
        for detected in detected_stems:
            if detected['stem'] not in existing_stems:
                sentence.setdefault('stems', []).append(detected)
    
    # 関連単語の追加
    for stem_info in sentence.get('stems', []):
        stem_name = stem_info['stem']
        form_used = stem_info.get('form_used', stem_name)
        
        # 語幹の存在確認
        stem_id = get_stem_id(conn, stem_name)
        if stem_id is None:
            print(f"警告: 関連付けようとした単語 '{stem_name}' が見つかりません。スキップします。", 
                  file=sys.stderr)
            continue
        
        # 関連付け
        cursor.execute(
            """
            INSERT INTO stem_sentence_rel 
            (stem_id, sentence_id, form_used)
            VALUES (?, ?, ?)
            """,
            (stem_id, sentence_id, form_used)
        )
    
    conn.commit()
    return sentence_id

if __name__ == "__main__":
    main()
