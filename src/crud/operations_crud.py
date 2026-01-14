from src.database.load_database import get_db_connection

def insert_operation(data: dict):
    """Insère une nouvelle opération et retourne l'ID généré"""
    # Seuls cross et date_heure_reception_alerte sont obligatoires
    # On ajoute les valeurs par défaut pour les champs manquants selon la vraie structure de la table
    defaults = {
        "operation_id": None,  # Sera auto-généré si None
        "type_operation": None,
        "pourquoi_alerte": None,
        "moyen_alerte": None,
        "qui_alerte": None,
        "categorie_qui_alerte": None,
        "departement": None,
        "est_metropolitain": None,
        "evenement": None,
        "categorie_evenement": None,
        "autorite": None,
        "seconde_autorite": None,
        "zone_responsabilite": None,
        "latitude": None,
        "longitude": None,
        "vent_direction": None,
        "vent_direction_categorie": None,
        "vent_force": None,
        "mer_force": None,
        "date_heure_fin_operation": None,
        "numero_sitrep": None,
        "cross_sitrep": None,
        "fuseau_horaire": None,
        "systeme_source": None
    }
    
    # Fusionner les données avec les valeurs par défaut
    full_data = {**defaults, **data}
    
    # Si operation_id n'est pas fourni, on génère le prochain ID
    if full_data["operation_id"] is None:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT COALESCE(MAX(operation_id), 0) + 1 FROM operations")
        full_data["operation_id"] = cur.fetchone()[0]
        cur.close()
        conn.close()
    
    query = """
    INSERT INTO operations (
        operation_id, "cross", date_heure_reception_alerte, type_operation,
        pourquoi_alerte, moyen_alerte, qui_alerte, categorie_qui_alerte,
        departement, est_metropolitain, evenement, categorie_evenement,
        autorite, seconde_autorite, zone_responsabilite, latitude, longitude,
        vent_direction, vent_direction_categorie, vent_force, mer_force,
        date_heure_fin_operation, numero_sitrep, cross_sitrep, fuseau_horaire, systeme_source
    )
    VALUES (
        %(operation_id)s, %(cross)s, %(date_heure_reception_alerte)s, %(type_operation)s,
        %(pourquoi_alerte)s, %(moyen_alerte)s, %(qui_alerte)s, %(categorie_qui_alerte)s,
        %(departement)s, %(est_metropolitain)s, %(evenement)s, %(categorie_evenement)s,
        %(autorite)s, %(seconde_autorite)s, %(zone_responsabilite)s, %(latitude)s, %(longitude)s,
        %(vent_direction)s, %(vent_direction_categorie)s, %(vent_force)s, %(mer_force)s,
        %(date_heure_fin_operation)s, %(numero_sitrep)s, %(cross_sitrep)s, %(fuseau_horaire)s, %(systeme_source)s
    )
    RETURNING operation_id;
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(query, full_data)
    operation_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return operation_id

def select_operation(operation_id: int):
    """Récupère une opération par son ID"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM operations WHERE operation_id = %s",
        (operation_id,)
    )
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result

def update_operation(operation_id: int, data: dict):
    """Met à jour une opération existante"""
    fields = []
    values = []
    for key, value in data.items():
        if key != 'operation_id':
            if key == 'cross':
                fields.append(f'"{key}" = %s')
            else:
                fields.append(f'{key} = %s')
            values.append(value)
    
    values.append(operation_id)
    
    query = f"UPDATE operations SET {', '.join(fields)} WHERE operation_id = %s"
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(query, tuple(values))
    conn.commit()
    cur.close()
    conn.close()

def delete_operation(operation_id: int):
    """Supprime une opération et toutes ses données associées (cascade)"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Suppression en cascade (l'ordre est important à cause des FK)
    cur.execute("DELETE FROM operations_stats WHERE operation_id = %s", (operation_id,))
    cur.execute("DELETE FROM resultats_humain WHERE operation_id = %s", (operation_id,))
    cur.execute("DELETE FROM flotteurs WHERE operation_id = %s", (operation_id,))
    cur.execute("DELETE FROM operations WHERE operation_id = %s", (operation_id,))
    
    conn.commit()
    cur.close()
    conn.close()
    return True
