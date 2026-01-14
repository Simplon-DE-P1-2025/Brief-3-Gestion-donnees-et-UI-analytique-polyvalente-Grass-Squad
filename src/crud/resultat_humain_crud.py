from src.database.load_database import get_connection

def insert_resultat_humain(data: dict):
    query = """
    INSERT INTO resultats_humain (
        operation_id, categorie_personne,
        resultat_humain, nombre, dont_nombre_blesse
    )
    VALUES (
        %(operation_id)s, %(categorie_personne)s,
        %(resultat_humain)s, %(nombre)s,
        %(dont_nombre_blesse)s
    );
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, data)
    conn.commit()
    cur.close()
    conn.close()
