#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sqlite3
import os
import sys
from pathlib import Path

# プロジェクトのルートディレクトリの取得
ROOT_DIR = Path(__file__).parent.parent


def load_json(filename):
    """JSONファイルを読み込む関数"""
    file_path = ROOT_DIR / filename
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"エラー: {filename}が見つかりません。")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"エラー: {filename}の形式が正しくありません。")
        sys.exit(1)


def connect_db():
    """データベースに接続する関数"""
    db_path = ROOT_DIR / "dictionary.sqlite3"
    try:
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"データベース接続エラー: {e}")
        sys.exit(1)


def get_stem_id(cursor, stem_text, part_of_speech_id):
    """stemテーブルから語幹IDを取得する関数"""
    cursor.execute(
        "SELECT id FROM stems WHERE stem = ? AND part_of_speech_id = ?",
        (stem_text, part_of_speech_id))
    result = cursor.fetchone()
    if result:
        return result['id']
    return None


def get_inflection_type_id(cursor, category, name):
    """inflection_typesテーブルから変化形タイプIDを取得する関数"""
    cursor.execute(
        "SELECT id FROM inflection_types WHERE category = ? AND name = ?",
        (category, name))
    result = cursor.fetchone()
    if result:
        return result['id']

    raise ValueError(f"変化形タイプ「{category} {name}」が見つかりません。")


def generate_noun_inflections(stem, pattern_id, animacy, patterns):
    """名詞の変化形を生成する関数"""
    inflections = []
    noun_patterns = patterns["名詞曲用"][animacy][str(pattern_id)]

    for definite in ["定", "不定"]:
        for case, suffix in noun_patterns[definite].items():
            num, case = case.split('数')

            # 完全な変化形を作成
            inflection = {
                "type_category": "名詞曲用",
                "type_name": f"{num}数{definite}{case}",
                "form": stem + suffix
            }
            inflections.append(inflection)

    return inflections


def generate_verb_inflections(stem, pattern_id, patterns):
    """動詞の変化形を生成する関数"""
    inflections = []
    verb_patterns = patterns["動詞活用"][str(pattern_id)]

    for form, suffix in verb_patterns.items():
        # 完全な変化形を作成
        inflection = {
            "type_category": "動詞活用",
            "type_name": form,
            "form": stem + suffix
        }
        inflections.append(inflection)

    return inflections


def generate_adjective_inflections(stem, pattern_id, patterns):
    """形容詞の変化形を生成する関数"""
    inflections = []
    adj_patterns = patterns["形容詞曲用"][str(pattern_id)]

    for form, suffix in adj_patterns.items():
        # 完全な変化形を作成
        inflection = {
            "type_category": "形容詞曲用",
            "type_name": form,
            "form": stem + suffix
        }
        inflections.append(inflection)

    return inflections


def insert_inflections(cursor, stem_id, inflections):
    """変化形をデータベースに挿入する関数"""
    inserted_count = 0
    for inflection in inflections:
        type_id = get_inflection_type_id(cursor, inflection["type_category"],
                                         inflection["type_name"])

        # 既存のエントリを確認
        cursor.execute(
            "SELECT id FROM inflections WHERE stem_id = ? AND inflection_type_id = ?",
            (stem_id, type_id))
        existing = cursor.fetchone()

        if existing:
            # 既存のエントリを更新
            cursor.execute("UPDATE inflections SET form = ? WHERE id = ?",
                           (inflection["form"], existing['id']))
        else:
            # 新しいエントリを挿入
            cursor.execute(
                "INSERT INTO inflections (stem_id, inflection_type_id, form) VALUES (?, ?, ?)",
                (stem_id, type_id, inflection["form"]))

        inserted_count += 1

    return inserted_count


def main():
    # データの読み込み
    regular_stems = load_json("regular_stems.json")
    inflection_patterns = load_json("inflection_patterns.json")["patterns"]

    # データベース接続
    conn = connect_db()
    cursor = conn.cursor()

    try:
        # トランザクション開始
        conn.execute("BEGIN TRANSACTION")

        total_processed = 0
        total_inserted = 0

        # 1. 名詞語幹の処理
        for noun_stem in regular_stems["1"]:
            stem_id = get_stem_id(cursor, noun_stem["stem"], 1)  # 1は名詞の品詞ID
            if not stem_id:
                print(f"警告: 名詞語幹「{noun_stem['stem']}」はデータベースに存在しません。")
                continue

            inflections = generate_noun_inflections(
                noun_stem["stem"], noun_stem["phonological_pattern_id"],
                noun_stem["animacy"], inflection_patterns)

            inserted = insert_inflections(cursor, stem_id, inflections)

            total_processed += 1
            total_inserted += inserted

        # 2. 動詞語幹の処理
        for verb_stem in regular_stems["2"]:
            stem_id = get_stem_id(cursor, verb_stem["stem"], 2)  # 2は動詞の品詞ID
            if not stem_id:
                print(f"警告: 動詞語幹「{verb_stem['stem']}」はデータベースに存在しません。")
                continue

            inflections = generate_verb_inflections(
                verb_stem["stem"], verb_stem["phonological_pattern_id"],
                inflection_patterns)

            inserted = insert_inflections(cursor, stem_id, inflections)

            total_processed += 1
            total_inserted += inserted

        # 3. 形容詞語幹の処理
        for adj_stem in regular_stems["3"]:
            stem_id = get_stem_id(cursor, adj_stem["stem"], 3)  # 3は形容詞の品詞ID
            if not stem_id:
                print(f"警告: 形容詞語幹「{adj_stem['stem']}」はデータベースに存在しません。")
                continue

            inflections = generate_adjective_inflections(
                adj_stem["stem"], adj_stem["phonological_pattern_id"],
                inflection_patterns)

            inserted = insert_inflections(cursor, stem_id, inflections)

            total_processed += 1
            total_inserted += inserted

        # トランザクション終了（コミット）
        conn.execute("COMMIT")

        print(
            f"処理完了: {total_processed}語幹を処理し、{total_inserted}個の変化形をデータベースに挿入しました。"
        )

    except Exception as e:
        # エラーが発生した場合はロールバック
        conn.execute("ROLLBACK")
        print(f"エラー: {e}")
        sys.exit(1)
    finally:
        # データベース接続を閉じる
        conn.close()


if __name__ == "__main__":
    main()
