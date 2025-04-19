#!/usr/bin/env python3
"""
1000年後の日本語辞書データベースユーティリティ
各スクリプトで共通して使用するデータベース操作関数
"""

import sqlite3
import json
import sys
from pathlib import Path

# 基本設定
DB_PATH = '../dictionary.sqlite3'

def connect_db(db_path=DB_PATH):
    """データベースに接続"""
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # 行をディクショナリとして取得
        return conn
    except sqlite3.Error as e:
        print(f"データベース接続エラー: {e}", file=sys.stderr)
        sys.exit(1)

def get_parts_of_speech(conn):
    """品詞一覧を取得"""
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM parts_of_speech")
    return {row['name']: row['id'] for row in cursor.fetchall()}

def get_phonological_patterns(conn):
    """音韻型一覧を取得"""
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM phonological_patterns")
    return {row['name']: row['id'] for row in cursor.fetchall()}

def get_inflection_types(conn):
    """活用タイプ一覧を取得"""
    cursor = conn.cursor()
    cursor.execute("SELECT id, category, name FROM inflection_types")
    return cursor.fetchall()

def get_stem_id(conn, stem):
    """語幹IDを取得"""
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM stems WHERE stem = ?", (stem,))
    result = cursor.fetchone()
    return result['id'] if result else None

def get_stem_details(conn, stem_id):
    """語幹の詳細情報を取得"""
    cursor = conn.cursor()
    
    # 基本情報を取得
    cursor.execute("""
        SELECT s.*, pos.name as part_of_speech, pp.name as phonological_pattern
        FROM stems s
        JOIN parts_of_speech pos ON s.part_of_speech_id = pos.id
        LEFT JOIN phonological_patterns pp ON s.phonological_pattern_id = pp.id
        WHERE s.id = ?
    """, (stem_id,))
    
    stem_data = dict(cursor.fetchone())
    
    # 定義を取得
    cursor.execute("""
        SELECT definition_number, definition, example
        FROM definitions
        WHERE stem_id = ?
        ORDER BY definition_number
    """, (stem_id,))
    
    stem_data['definitions'] = [dict(row) for row in cursor.fetchall()]
    
    # 活用形を取得
    cursor.execute("""
        SELECT i.form, it.category, it.name
        FROM inflections i
        JOIN inflection_types it ON i.inflection_type_id = it.id
        WHERE i.stem_id = ?
        ORDER BY it.category, it.name
    """, (stem_id,))
    
    stem_data['inflections'] = []
    for row in cursor.fetchall():
        stem_data['inflections'].append({
            'form': row['form'],
            'inflection_type': {
                'category': row['category'],
                'name': row['name']
            }
        })
    
    # 関連語を取得
    cursor.execute("""
        SELECT s2.stem as related_stem, rs.relation_type
        FROM related_stems rs
        JOIN stems s2 ON rs.related_stem_id = s2.id
        WHERE rs.stem_id = ?
    """, (stem_id,))
    
    stem_data['related'] = [dict(row) for row in cursor.fetchall()]
    
    # 例文を取得
    cursor.execute("""
        SELECT sen.original_text, sen.translation, sen.notes, ssr.form_used
        FROM sentences sen
        JOIN stem_sentence_rel ssr ON sen.id = ssr.sentence_id
        WHERE ssr.stem_id = ?
    """, (stem_id,))
    
    stem_data['sentences'] = [dict(row) for row in cursor.fetchall()]
    
    return stem_data

def format_markdown_template(word_data):
    """単語データをMarkdown形式でフォーマット"""
    md = f"# 見出し語: {word_data['stem']}\n\n"
    
    # 文法情報
    md += "## 文法情報\n"
    md += f"- **類別**: {word_data['part_of_speech']}\n"
    md += f"- **音韻型**: {word_data['phonological_pattern']}\n"
    
    # 品詞別の追加情報
    if word_data['part_of_speech'] == '名詞':
        md += f"- **名詞分類**: {'有生' if '有生' in word_data['phonological_pattern'] else '無生'}\n"
    elif word_data['part_of_speech'] == '動詞':
        md += f"- **動詞分類**: {'他動詞' if word_data.get('notes', '').find('他動詞') >= 0 else '自動詞'}\n"
    
    # 語源情報
    md += "\n## 語源情報\n"
    md += f"{word_data.get('etymology', '情報なし')}\n"
    
    # 定義
    md += "\n## 定義\n"
    if word_data.get('definitions'):
        for definition in word_data['definitions']:
            num = definition['definition_number']
            text = definition['definition']
            md += f"{num}. {text}\n"
            if definition.get('example'):
                md += f"   例: {definition['example']}\n"
    else:
        md += "定義情報なし\n"
    
    # 曲用/活用表
    md += "\n## 曲用/活用表\n"
    if word_data['part_of_speech'] == '動詞':
        md += "※ 活用情報はデータベースを参照してください。\n"
    elif word_data['part_of_speech'] in ['名詞', '形容詞']:
        md += "※ 曲用情報はデータベースを参照してください。\n"
    else:
        md += "該当なし\n"
    
    # 例文
    if word_data.get('sentences'):
        md += "\n## 例文\n"
        for i, sentence in enumerate(word_data['sentences'], 1):
            md += f"{i}. {sentence['original_text']} ({sentence['translation']})\n"
    
    # 関連語
    if word_data.get('related'):
        md += "\n## 関連語\n"
        for related in word_data['related']:
            md += f"- {related['related_stem']} ({related['relation_type']})\n"
    
    # 備考
    if word_data.get('notes'):
        md += "\n## 備考\n"
        md += f"{word_data['notes']}\n"
    
    return md

def get_word_schema():
    """単語データのJSONスキーマを取得"""
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "required": ["stem", "part_of_speech", "phonological_pattern"],
        "properties": {
            "stem": {
                "type": "string",
                "description": "単語の語幹"
            },
            "part_of_speech": {
                "type": "string",
                "description": "品詞",
                "enum": ["名詞", "動詞", "形容詞", "副詞", "代名詞", "接頭辞", "接尾辞", "接続詞", "小辞"]
            },
            "phonological_pattern": {
                "type": "string",
                "description": "音韻型",
                "enum": ["前舌", "後舌", "前舌有生", "前舌無生", "後舌有生", "後舌無生", "混合"]
            },
            "etymology": {
                "type": "string",
                "description": "語源情報"
            },
            "notes": {
                "type": "string",
                "description": "注釈や備考"
            },
            "definitions": {
                "type": "array",
                "description": "単語の定義一覧",
                "items": {
                    "type": "object",
                    "required": ["definition_number", "definition"],
                    "properties": {
                        "definition_number": {
                            "type": "integer",
                            "description": "定義番号（1から始まる連番）"
                        },
                        "definition": {
                            "type": "string",
                            "description": "定義内容"
                        },
                        "example": {
                            "type": "string",
                            "description": "用例（オプション）"
                        }
                    }
                }
            },
            "inflections": {
                "type": "array",
                "description": "活用形一覧",
                "items": {
                    "type": "object",
                    "required": ["inflection_type", "form"],
                    "properties": {
                        "inflection_type": {
                            "type": "object",
                            "required": ["category", "name"],
                            "properties": {
                                "category": {
                                    "type": "string",
                                    "description": "活用カテゴリ（時制、人称、数、格など）"
                                },
                                "name": {
                                    "type": "string",
                                    "description": "活用名（現在、過去、単数、複数など）"
                                }
                            }
                        },
                        "form": {
                            "type": "string",
                            "description": "活用形"
                        }
                    }
                }
            },
            "related": {
                "type": "array",
                "description": "関連語一覧",
                "items": {
                    "type": "object",
                    "required": ["related_stem", "relation_type"],
                    "properties": {
                        "related_stem": {
                            "type": "string",
                            "description": "関連語の語幹"
                        },
                        "relation_type": {
                            "type": "string",
                            "description": "関連タイプ（synonym, antonym, derived等）"
                        }
                    }
                }
            }
        }
    }
    return schema

def get_sentence_schema():
    """例文データのJSONスキーマを取得"""
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "required": ["original_text", "translation"],
        "properties": {
            "original_text": {
                "type": "string",
                "description": "1000年後の日本語による原文"
            },
            "translation": {
                "type": "string",
                "description": "現代日本語訳"
            },
            "notes": {
                "type": "string",
                "description": "文法注釈や解説"
            },
            "stems": {
                "type": "array",
                "description": "関連する単語のリスト",
                "items": {
                    "type": "object",
                    "required": ["stem", "form_used"],
                    "properties": {
                        "stem": {
                            "type": "string",
                            "description": "単語の語幹"
                        },
                        "form_used": {
                            "type": "string",
                            "description": "例文中で使われている活用形"
                        }
                    }
                }
            }
        }
    }
    return schema

def get_batch_sentences_schema():
    """複数例文のバッチ処理用JSONスキーマを取得"""
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "array",
        "description": "複数の例文データ",
        "items": get_sentence_schema()
    }
    return schema

if __name__ == "__main__":
    print("このファイルは直接実行せず、他のスクリプトからインポートして使用してください。")
    sys.exit(1)
