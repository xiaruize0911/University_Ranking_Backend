from db.database import get_db_connection

def get_translated_name(univ_id, language):
    """
    Get the translated name for a university by id and language.
    language: 'en' for English, 'zh' for Chinese
    """
    conn = get_db_connection()
    cur = conn.execute("SELECT english_name, chinese_name FROM University_names_en_to_zh WHERE id = ?", (univ_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        if language == 'zh':
            return row['chinese_name']
        else:
            return row['english_name']
    return None

def get_translated_name_by_normalized(normalized_name, language):
    """
    Get the translated name for a university by normalized_name and language.
    First get the id from Universities table, then get translation.
    """
    conn = get_db_connection()
    # Get id from Universities
    cur = conn.execute("SELECT id FROM Universities WHERE normalized_name = ?", (normalized_name,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return None
    univ_id = row['id']
    # Get translation
    cur = conn.execute("SELECT english_name, chinese_name FROM University_names_en_to_zh WHERE id = ?", (univ_id,))
    trans_row = cur.fetchone()
    conn.close()
    if trans_row:
        if language == 'zh':
            return trans_row['chinese_name']
        else:
            return trans_row['english_name']
    return None

def get_all_translations(language=None):
    """
    Get all translations. If language is specified ('en' or 'zh'), filter by that language.
    """
    conn = get_db_connection()
    if language == 'zh':
        cur = conn.execute("SELECT Universities.normalized_name, University_names_en_to_zh.chinese_name FROM Universities LEFT JOIN University_names_en_to_zh ON Universities.id = University_names_en_to_zh.id")
        results = [{'normalized_name': row['normalized_name'], 'name': row['chinese_name']} for row in cur.fetchall()]
    elif language == 'en':
        cur = conn.execute("SELECT Universities.normalized_name, University_names_en_to_zh.english_name FROM Universities LEFT JOIN University_names_en_to_zh ON Universities.id = University_names_en_to_zh.id")
        results = [{'normalized_name': row['normalized_name'], 'name': row['english_name']} for row in cur.fetchall()]
    else:
        cur = conn.execute("SELECT Universities.normalized_name, University_names_en_to_zh.english_name, University_names_en_to_zh.chinese_name FROM Universities LEFT JOIN University_names_en_to_zh ON Universities.id = University_names_en_to_zh.id")
        results = [{'normalized_name': row['normalized_name'], 'english_name': row['english_name'], 'chinese_name': row['chinese_name']} for row in cur.fetchall()]
    conn.close()
    return results