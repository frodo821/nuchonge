#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
import_stems.py - マークダウンファイルから語幹情報を抽出してSQLiteに登録するスクリプト
"""

import os
import re
import sqlite3
import glob
from pathlib import Path


def get_part_of_speech_id(cursor, pos_name):
    """
    品詞名からIDを取得する
    
    Args:
        cursor: SQLiteカーソル
        pos_name: 品詞名
    
    Returns:
        int or None: 品詞ID
    """
    # 完全一致で検索
    cursor.execute("SELECT id FROM parts_of_speech WHERE name = ?", (pos_name,))
    result = cursor.fetchone()
    
    if result:
        return result[0]
    
    # 部分一致で検索（名詞、形容詞などの部分が含まれるか）
    cursor.execute("SELECT id, name FROM parts_of_speech WHERE name IS NOT NULL")
    all_pos = cursor.fetchall()
    
    for pos_id, db_pos_name in all_pos:
        if db_pos_name in pos_name or pos_name in db_pos_name:
            return pos_id
    
    # ID 1が名詞（nullになっている可能性がある）
    if "名詞" in pos_name:
        return 1
    
    return None


def get_phonological_pattern_id(cursor, pattern_name):
    """
    音韻型名からIDを取得する
    
    Args:
        cursor: SQLiteカーソル
        pattern_name: 音韻型名
    
    Returns:
        int or None: 音韻型ID
    """
    # マークダウンの「前舌」は「前舌子音」か確認
    if pattern_name == "前舌":
        cursor.execute("SELECT id FROM phonological_patterns WHERE name = '前舌子音'")
        result = cursor.fetchone()
        if result:
            return result[0]
    
    # 完全一致で検索
    cursor.execute("SELECT id FROM phonological_patterns WHERE name = ?", (pattern_name,))
    result = cursor.fetchone()
    
    if result:
        return result[0]
    
    # 部分一致で検索
    cursor.execute("SELECT id, name FROM phonological_patterns WHERE name IS NOT NULL")
    all_patterns = cursor.fetchall()
    
    for pattern_id, db_pattern_name in all_patterns:
        if db_pattern_name in pattern_name or pattern_name in db_pattern_name:
            return pattern_id
    
    return None


def extract_stem_info(md_path):
    """
    マークダウンファイルから語幹情報を抽出する
    
    Returns:
        dict: 抽出された語幹情報
    """
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 見出し語を抽出
    stem_match = re.search(r'# 見出し語: (.+)', content)
    stem = stem_match.group(1).strip() if stem_match else os.path.basename(md_path).replace('.md', '')
    
    # ファイル名から追加情報を抽出（例：kjo-noun.md → "kjo"と"noun"）
    file_name = os.path.basename(md_path)
    file_stem, file_suffix = os.path.splitext(file_name)
    
    # 品詞を抽出
    pos_match = re.search(r'\*\*類別\*\*: (.+)', content)
    pos = pos_match.group(1).strip() if pos_match else None
    
    # ファイル名に品詞情報が含まれている場合（例：kjo-noun.md）
    if '-' in file_stem and not pos:
        parts = file_stem.split('-')
        if len(parts) >= 2:
            stem_part = parts[0]
            pos_part = parts[1]
            
            # ファイル名から抽出した品詞情報を使用
            if not pos and pos_part in ['noun', 'verb', 'adverb', 'adjective', 'prefix', 'suffix']:
                # 英語の品詞名を日本語に変換
                pos_map = {
                    'noun': '名詞',
                    'verb': '動詞',
                    'adverb': '副詞',
                    'adjective': '形容詞',
                    'prefix': '接頭辞',
                    'suffix': '接尾辞'
                }
                pos = pos_map.get(pos_part, pos_part)
    
    # 音韻型を抽出
    pattern_match = re.search(r'\*\*音韻型\*\*: (.+)', content)
    pattern = pattern_match.group(1).strip() if pattern_match else None
    
    # 語源情報を抽出
    etymology_section = re.search(r'## 語源情報\s+(.*?)(?=##|\Z)', content, re.DOTALL)
    etymology = etymology_section.group(1).strip() if etymology_section else None
    
    # 語源情報の前処理（Markdown形式の箇条書きを整形）
    if etymology:
        # 箇条書きの「*」を削除し、代わりに改行と「- 」で整形
        etymology = re.sub(r'\*\s+', '\n- ', etymology)
    
    # 備考を抽出（備考セクションがある場合）
    notes_section = re.search(r'## 備考\s+(.*?)(?=##|\Z)', content, re.DOTALL)
    notes = notes_section.group(1).strip() if notes_section else None
    
    # 定義を抽出
    definitions = []
    definition_section = re.search(r'## 定義\s+(.*?)(?=##|\Z)', content, re.DOTALL)
    if definition_section:
        def_content = definition_section.group(1)
        # 定義番号と定義内容のパターン
        def_pattern = re.compile(r'(\d+)\.\s+(.+?)(?=\d+\.|$)', re.DOTALL)
        for match in def_pattern.finditer(def_content):
            number = int(match.group(1))
            definition = match.group(2).strip()
            definitions.append((number, definition))
    
    return {
        'stem': stem,
        'part_of_speech': pos,
        'phonological_pattern': pattern,
        'etymology': etymology,
        'notes': notes,
        'definitions': definitions
    }


def insert_stem(conn, stem_info):
    """
    抽出した語幹情報をデータベースに挿入する
    
    Args:
        conn: SQLite接続オブジェクト
        stem_info: 抽出された語幹情報
    
    Returns:
        int: 挿入されたstemのID
    """
    cursor = conn.cursor()
    
    # 品詞IDを取得
    pos_id = None
    if stem_info['part_of_speech']:
        pos_id = get_part_of_speech_id(cursor, stem_info['part_of_speech'])
    
    # 音韻型IDを取得
    pattern_id = None
    if stem_info['phonological_pattern']:
        pattern_id = get_phonological_pattern_id(cursor, stem_info['phonological_pattern'])
    
    # stemテーブルに挿入
    cursor.execute(
        """
        INSERT INTO stems 
        (stem, part_of_speech_id, phonological_pattern_id, etymology, notes)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            stem_info['stem'],
            pos_id,
            pattern_id,
            stem_info['etymology'],
            stem_info['notes']
        )
    )
    
    # 挿入されたstemのIDを取得
    stem_id = cursor.lastrowid
    
    # 定義を挿入
    for def_num, def_text in stem_info['definitions']:
        cursor.execute(
            """
            INSERT INTO definitions
            (stem_id, definition_number, definition)
            VALUES (?, ?, ?)
            """,
            (stem_id, def_num, def_text)
        )
    
    conn.commit()
    return stem_id


def main():
    """メイン処理"""
    # データベース接続
    conn = sqlite3.connect('dictionary.sqlite3')
    
    # 語彙ファイルのリストを取得
    lexicon_dir = "lexicon"
    md_files = glob.glob(os.path.join(lexicon_dir, "*.md"))
    
    # 各ファイルを処理
    processed = 0
    skipped = 0
    errors = 0
    
    for md_file in md_files:
        try:
            stem_info = extract_stem_info(md_file)
            
            # 品詞IDを取得（同じ語幹でも品詞が異なれば別エントリとして扱う）
            cursor = conn.cursor()
            pos_id = None
            if stem_info['part_of_speech']:
                pos_id = get_part_of_speech_id(cursor, stem_info['part_of_speech'])
            
            # 語幹と品詞IDの両方で重複チェック
            if pos_id:
                cursor.execute(
                    "SELECT id FROM stems WHERE stem = ? AND part_of_speech_id = ?", 
                    (stem_info['stem'], pos_id)
                )
            else:
                cursor.execute("SELECT id FROM stems WHERE stem = ?", (stem_info['stem'],))
            
            existing_stem = cursor.fetchone()
            
            if existing_stem:
                print(f"スキップ: {stem_info['stem']} (品詞: {stem_info['part_of_speech']}) - 既に存在します")
                skipped += 1
                continue
            
            # 新しいstemを挿入
            stem_id = insert_stem(conn, stem_info)
            print(f"登録完了: {stem_info['stem']} (ID: {stem_id})")
            processed += 1
            
        except Exception as e:
            print(f"エラー: {md_file} の処理中に問題が発生しました - {str(e)}")
            errors += 1
    
    print(f"\n処理完了: {processed}個の語幹を登録, {skipped}個をスキップ, {errors}個で問題発生")
    
    # 接続を閉じる
    conn.close()


if __name__ == "__main__":
    main()
