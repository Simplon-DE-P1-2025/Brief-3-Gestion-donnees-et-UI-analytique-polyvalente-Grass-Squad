from src.database.load_database import get_db_connection
from src.crud.audit_crud import log_action

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
    
    # Formater la requête SQL pour l'audit
    sql_for_audit = cur.mogrify(query, data).decode('utf-8')
    
    cur.execute(query, data)
    conn.commit()
    cur.close()
    conn.close()
    
    # Enregistrer l'action dans l'audit
    log_action(
        table='flotteurs',
        action='INSERT',
        record_id=f"{data.get('operation_id')}_{data.get('numero_ordre')}",
        new_values=data,
        details=f"Nouveau flotteur ajouté - Opération: {data.get('operation_id')}, Ordre: {data.get('numero_ordre')}",
        sql_query=sql_for_audit
    )

def select_flotteurs_by_operation(operation_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    query = "SELECT * FROM flotteurs WHERE operation_id = %s"
    cur.execute(query, (operation_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    
    # Enregistrer l'action dans l'audit si des flotteurs sont trouvés
    if rows:
        log_action(
            table='flotteurs',
            action='VIEW',
            record_id=str(operation_id),
            details=f"Consultation de {len(rows)} flotteur(s) pour l'opération {operation_id}",
            sql_query=f"SELECT * FROM flotteurs WHERE operation_id = {operation_id}"
        )
    
    return rows

def update_flotteur(operation_id: int, numero_ordre: int, data: dict):
    """Met à jour un flotteur"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Récupérer les anciennes valeurs pour l'audit
    cur.execute(
        "SELECT * FROM flotteurs WHERE operation_id = %s AND numero_ordre = %s",
        (operation_id, numero_ordre)
    )
    old_record = cur.fetchone()
    old_columns = [desc[0] for desc in cur.description]
    old_values_full = dict(zip(old_columns, old_record)) if old_record else {}
    
    # Identifier seulement les valeurs qui changent
    changed_old_values = {}
    changed_new_values = {}
    
    for key, new_value in data.items():
        if key in old_values_full:
            old_value = old_values_full[key]
            if old_value != new_value:
                if not (old_value is None and new_value is None):
                    changed_old_values[key] = old_value
                    changed_new_values[key] = new_value
    
    fields = []
    values = []
    for key, value in data.items():
        if key not in ['operation_id', 'numero_ordre']:
            fields.append(f'{key} = %s')
            values.append(value)
    
    values.extend([operation_id, numero_ordre])
    
    query = f"""
        UPDATE flotteurs 
        SET {', '.join(fields)}
        WHERE operation_id = %s AND numero_ordre = %s
    """
    
    # Formater la requête SQL pour l'audit
    sql_for_audit = cur.mogrify(query, tuple(values)).decode('utf-8')
    
    cur.execute(query, tuple(values))
    conn.commit()
    cur.close()
    conn.close()
    
    # Enregistrer l'action dans l'audit seulement si des changements existent
    if changed_old_values:
        log_action(
            table='flotteurs',
            action='UPDATE',
            record_id=f"{operation_id}_{numero_ordre}",
            old_values=changed_old_values,
            new_values=changed_new_values,
            details=f"Modification du flotteur - Opération: {operation_id}, Ordre: {numero_ordre} - {len(changed_old_values)} champ(s) modifié(s)",
            sql_query=sql_for_audit
        )
    
    return True

def delete_flotteur(operation_id: int, numero_ordre: int):
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Récupérer les données avant suppression pour l'audit
    cur.execute(
        "SELECT * FROM flotteurs WHERE operation_id = %s AND numero_ordre = %s",
        (operation_id, numero_ordre)
    )
    old_record = cur.fetchone()
    old_columns = [desc[0] for desc in cur.description]
    old_values = dict(zip(old_columns, old_record)) if old_record else {}
    
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
    
    # Enregistrer l'action dans l'audit
    if old_values:
        log_action(
            table='flotteurs',
            action='DELETE',
            record_id=f"{operation_id}_{numero_ordre}",
            old_values=old_values,
            details=f"Flotteur supprimé - Opération: {operation_id}, Ordre: {numero_ordre}",
            sql_query=f"DELETE FROM flotteurs WHERE operation_id = {operation_id} AND numero_ordre = {numero_ordre}"
        )
