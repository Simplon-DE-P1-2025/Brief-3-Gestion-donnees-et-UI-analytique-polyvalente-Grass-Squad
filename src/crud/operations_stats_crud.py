from src.database.load_database import get_connection

def insert_operations_stats(data: dict):
    cols = ", ".join(data.keys())
    placeholders = ", ".join([f"%({k})s" for k in data.keys()])

    query = f"""
    INSERT INTO cross_sec.operations_stats ({cols})
    VALUES ({placeholders})
    ON CONFLICT (operation_id) DO NOTHING;
    """

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, data)
    conn.commit()
    cur.close()
    conn.close()
