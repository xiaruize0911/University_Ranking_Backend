from db.database import get_db_connection

def get_translated_name(univ_id, language):
    """Get the translated name for a university by its translation table id."""
    conn = get_db_connection()
    cur = conn.execute("SELECT english_name, chinese_name FROM University_names_en_to_zh WHERE id = ?", (univ_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return row['chinese_name'] if language == 'zh' else row['english_name']


def get_translated_name_by_normalized(normalized_name, language):
    """Get the translated name by normalized_name.

    The database uses `normalized_name` as the canonical key across ranking tables. Query
    `University_names_en_to_zh` directly by that column instead of joining to a missing
    `Universities` table.
    """
    conn = get_db_connection()
    cur = conn.execute("SELECT english_name, chinese_name FROM University_names_en_to_zh WHERE normalized_name = ?", (normalized_name,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return row['chinese_name'] if language == 'zh' else row['english_name']


def get_all_translations(language=None):
    """Return all translations. When `language` is provided, return only that language value.

    Because `University_names_en_to_zh` already contains `normalized_name`, select directly
    from that table instead of attempting to join to a `Universities` table that doesn't
    exist in this DB snapshot.
    """
    conn = get_db_connection()
    if language == 'zh':
        cur = conn.execute("SELECT normalized_name, chinese_name FROM University_names_en_to_zh")
        results = [{'normalized_name': row['normalized_name'], 'name': row['chinese_name']} for row in cur.fetchall()]
    elif language == 'en':
        cur = conn.execute("SELECT normalized_name, english_name FROM University_names_en_to_zh")
        results = [{'normalized_name': row['normalized_name'], 'name': row['english_name']} for row in cur.fetchall()]
    else:
        cur = conn.execute("SELECT normalized_name, english_name, chinese_name FROM University_names_en_to_zh")
        results = [{'normalized_name': row['normalized_name'], 'english_name': row['english_name'], 'chinese_name': row['chinese_name']} for row in cur.fetchall()]
    conn.close()
    return results