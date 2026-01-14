from src.database.load_database import get_connection

def log_action(table: str, action: str, record_id: str):
    query = """
    INSERT INTO cross_sec.audit_log (table_name, action, record_id)
    VALUES (%s, %s, %s);
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, (table, action, record_id))
    conn.commit()
    cur.close()
    conn.close()
