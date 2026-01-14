from src.database.load_database import get_db_connection

def insert_flotteur(data: dict):
    query = """
    INSERT INTO flotteurs (
        operation_id, numero_ordre, pavillon,
        resultat_flotteur, type_flotteur,
        categorie_flotteur, numero_immatriculation
    )
    VALUES (
        %(operation_id)s, %(numero_ordre)s, %(pavillon)s,
        %(resultat_flotteur)s, %(type_flotteur)s,
        %(categorie_flotteur)s, %(numero_immatriculation)s
    );
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(query, data)
    conn.commit()
    cur.close()
    conn.close()

def select_flotteurs_by_operation(operation_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM flotteurs WHERE operation_id = %s",
        (operation_id,)
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def delete_flotteur(operation_id: int, numero_ordre: int):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        DELETE FROM flotteurs
        WHERE operation_id = %s AND numero_ordre = %s
        """,
        (operation_id, numero_ordre)
    )
    conn.commit()
    cur.close()
    conn.close()
