from src.database.load_database import get_db_connection
from src.crud.audit_crud import log_action

def insert_operation(data: dict):
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
    
    # Formatage de la requête SQL avec les vraies valeurs pour l'audit
    sql_for_audit = cur.mogrify(query, full_data).decode('utf-8')
    
    cur.execute(query, full_data)
    operation_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    
    # Enregistrer l'action dans l'audit avec la requête SQL
    log_action(
        table='operations',
        action='INSERT',
        record_id=operation_id,
        new_values=full_data,
        details=f"Nouvelle opération créée - CROSS: {full_data.get('cross')}",
        sql_query=sql_for_audit
    )
    
    return operation_id

def select_operation(operation_id: int):
    """Récupère une opération par son ID"""
    conn = get_db_connection()
    cur = conn.cursor()
    query = "SELECT * FROM operations WHERE operation_id = %s"
    cur.execute(query, (operation_id,))
    result = cur.fetchone()
    
    if result:
        columns = [desc[0] for desc in cur.description]
        operation = dict(zip(columns, result))
        
        # Enregistrer l'action dans l'audit
        log_action(
            table='operations',
            action='VIEW',
            record_id=operation_id,
            details=f"Consultation de l'opération {operation_id}",
            sql_query=f"SELECT * FROM operations WHERE operation_id = {operation_id}"
        )
    else:
        operation = None
    
    cur.close()
    conn.close()
    return operation

def update_operation(operation_id: int, data: dict):
    """Met à jour une opération existante"""
    # Récupérer les anciennes valeurs pour l'audit
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM operations WHERE operation_id = %s", (operation_id,))
    old_record = cur.fetchone()
    old_columns = [desc[0] for desc in cur.description]
    old_values_full = dict(zip(old_columns, old_record)) if old_record else {}
    
    # Identifier seulement les valeurs qui changent
    changed_old_values = {}
    changed_new_values = {}
    
    for key, new_value in data.items():
        if key in old_values_full:
            old_value = old_values_full[key]
            # Comparer les valeurs (gérer None et NaN)
            if old_value != new_value:
                # Vérifier si ce n'est pas juste None vs None ou NaN
                if not (old_value is None and new_value is None):
                    changed_old_values[key] = old_value
                    changed_new_values[key] = new_value
    
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
    
    # Formater la requête SQL pour l'audit
    sql_for_audit = cur.mogrify(query, tuple(values)).decode('utf-8')
    
    cur.execute(query, tuple(values))
    conn.commit()
    cur.close()
    conn.close()
    
    # Enregistrer l'action dans l'audit seulement si des changements existent
    if changed_old_values:
        log_action(
            table='operations',
            action='UPDATE',
            record_id=operation_id,
            old_values=changed_old_values,
            new_values=changed_new_values,
            details=f"Modification de l'opération {operation_id} - {len(changed_old_values)} champ(s) modifié(s)",
            sql_query=sql_for_audit
        )
    
    return True

def delete_operation(operation_id: int):
    """Supprime une opération et toutes ses données associées (cascade)"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Récupérer les données avant suppression pour l'audit
    cur.execute("SELECT * FROM operations WHERE operation_id = %s", (operation_id,))
    old_record = cur.fetchone()
    old_columns = [desc[0] for desc in cur.description]
    old_values = dict(zip(old_columns, old_record)) if old_record else {}
    
    # Suppression en cascade (l'ordre est important à cause des FK)
    cur.execute("DELETE FROM operations_stats WHERE operation_id = %s", (operation_id,))
    cur.execute("DELETE FROM resultats_humain WHERE operation_id = %s", (operation_id,))
    cur.execute("DELETE FROM flotteurs WHERE operation_id = %s", (operation_id,))
    delete_query = "DELETE FROM operations WHERE operation_id = %s"
    cur.execute(delete_query, (operation_id,))
    
    conn.commit()
    cur.close()
    conn.close()
    
    # Enregistrer l'action dans l'audit
    log_action(
        table='operations',
        action='DELETE',
        record_id=operation_id,
        old_values=old_values,
        details=f"Suppression de l'opération {operation_id} et toutes ses données associées",
        sql_query=f"DELETE FROM operations WHERE operation_id = {operation_id}"
    )
    
    return True
