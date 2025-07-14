from db.database import get_db_connection
def run_db_cmd(cmd: str):
    conn = get_db_connection()
    ret = conn.execute(cmd)
    return ret