#!/usr/bin/env python3
"""
データベース内の活用データをスキャンして実際の構造を確認するためのスクリプト
"""

import sys
import json
import db_utils

def scan_inflection_types(conn):
    """
    inflection_typesテーブルをスキャンして存在するすべてのカテゴリとその名前を収集
    """
    cursor = conn.cursor()
    cursor.execute("SELECT id, category, name FROM inflection_types")
    
    categories = {}
    for row in cursor.fetchall():
        cat = row['category']
        name = row['name']
        if cat not in categories:
            categories[cat] = set()
        categories[cat].add(name)
    
    # set型はJSON変換不可のため、リストに変換
    for cat in categories:
        categories[cat] = sorted(list(categories[cat]))
    
    return categories

def scan_stem_inflections(conn, stem_id):
    """
    特定の語幹IDについて、実際の活用形を収集して構造化
    """
    cursor = conn.cursor()
    cursor.execute("""
        SELECT i.id, i.form, it.category, it.name 
        FROM inflections i
        JOIN inflection_types it ON i.inflection_type_id = it.id
        WHERE i.stem_id = ?
    """, (stem_id,))
    
    inflections = {}
    for row in cursor.fetchall():
        form = row['form']
        category = row['category']
        name = row['name']
        
        if category not in inflections:
            inflections[category] = {}
        
        inflections[category][name] = form
    
    return inflections

def main():
    """メイン関数"""
    if len(sys.argv) < 2:
        print("使用法: python process_inflections.py <stem_id>")
        return 1
    
    try:
        stem_id = int(sys.argv[1])
    except ValueError:
        print(f"エラー: {sys.argv[1]} は有効な整数IDではありません")
        return 1
    
    # データベース接続
    conn = db_utils.connect_db()
    
    try:
        # 指定された語幹の基本情報を取得
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.*, pos.name as part_of_speech, pp.name as phonological_pattern
            FROM stems s
            JOIN parts_of_speech pos ON s.part_of_speech_id = pos.id
            JOIN phonological_patterns pp ON s.phonological_pattern_id = pp.id
            WHERE s.id = ?
        """, (stem_id,))
        
        stem_info = cursor.fetchone()
        if not stem_info:
            print(f"ID {stem_id} の語幹情報が見つかりません")
            return 1
        
        # inflection_typesのすべてのカテゴリ・名前のセットを取得
        categories = scan_inflection_types(conn)
        
        # 指定された語幹の活用形を取得して構造化
        inflections = scan_stem_inflections(conn, stem_id)
        
        # 結果をJSON出力
        result = {
            "stem_id": stem_id,
            "stem": stem_info['stem'],
            "part_of_speech": stem_info['part_of_speech'],
            "phonological_pattern": stem_info['phonological_pattern'],
            "all_categories": categories,
            "stem_inflections": inflections
        }
        
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        return 0
    
    finally:
        conn.close()

if __name__ == "__main__":
    sys.exit(main())
