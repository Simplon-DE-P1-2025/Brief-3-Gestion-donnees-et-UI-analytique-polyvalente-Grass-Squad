from src.database.load_database import get_connection

def insert_operation(data: dict):
    query = """
    INSERT INTO operations (
        operation_id, type_operation, pourquoi_alerte, moyen_alerte,
        qui_alerte, categorie_qui_alerte, cross, departement,
        est_metropolitain, evenement, categorie_evenement,
        autorite, seconde_autorite, zone_responsabilite,
        latitude, longitude, vent_direction, vent_direction_categorie,
        vent_force, mer_force, date_heure_reception_alerte,
        date_heure_fin_operation, numero_sitrep, cross_sitrep,
        fuseau_horaire, systeme_source
    )
    VALUES (%(operation_id)s, %(type_operation)s, %(pourquoi_alerte)s,
            %(moyen_alerte)s, %(qui_alerte)s, %(categorie_qui_alerte)s,
            %(cross)s, %(departement)s, %(est_metropolitain)s,
            %(evenement)s, %(categorie_evenement)s, %(autorite)s,
            %(seconde_autorite)s, %(zone_responsabilite)s,
            %(latitude)s, %(longitude)s, %(vent_direction)s,
            %(vent_direction_categorie)s, %(vent_force)s,
            %(mer_force)s, %(date_heure_reception_alerte)s,
            %(date_heure_fin_operation)s, %(numero_sitrep)s,
            %(cross_sitrep)s, %(fuseau_horaire)s, %(systeme_source)s
    )
    ON CONFLICT (operation_id) DO NOTHING;
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, data)
    conn.commit()
    cur.close()
    conn.close()

def select_operation(operation_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM operations WHERE operation_id = %s",
        (operation_id,)
    )
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result
