from src.database.load_database import get_db_connection
from src.crud.audit_crud import log_action

def insert_operations_stats(data: dict):
    cols = ", ".join(data.keys())
    placeholders = ", ".join([f"%({k})s" for k in data.keys()])

    query = f"""
    INSERT INTO operations_stats ({cols})
    VALUES ({placeholders})
    ON CONFLICT (operation_id) DO NOTHING;
    """

    conn = get_db_connection()
    cur = conn.cursor()
    
    # Formater la requête SQL pour l'audit
    sql_for_audit = cur.mogrify(query, data).decode('utf-8')
    
    cur.execute(query, data)
    affected_rows = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()
    
    # Enregistrer l'action dans l'audit (seulement si une ligne a été insérée)
    if affected_rows > 0:
        log_action(
            table='operations_stats',
            action='INSERT',
            record_id=str(data.get('operation_id')),
            new_values=data,
            details=f"Statistiques d'opération ajoutées - Opération: {data.get('operation_id')}",
            sql_query=sql_for_audit
        )

def select_operations_stats(operation_id: int):
    """Récupère les statistiques d'une opération"""
    conn = get_db_connection()
    cur = conn.cursor()
    query = "SELECT * FROM operations_stats WHERE operation_id = %s"
    cur.execute(query, (operation_id,))
    result = cur.fetchone()
    
    if result:
        columns = [desc[0] for desc in cur.description]
        stats = dict(zip(columns, result))
        
        # Enregistrer l'action dans l'audit
        log_action(
            table='operations_stats',
            action='VIEW',
            record_id=str(operation_id),
            details=f"Consultation des statistiques de l'opération {operation_id}",
            sql_query=f"SELECT * FROM operations_stats WHERE operation_id = {operation_id}"
        )
    else:
        stats = None
    
    cur.close()
    conn.close()
    return stats

def update_operations_stats(operation_id: int, data: dict):
    """Met à jour les statistiques d'une opération"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Récupérer les anciennes valeurs pour l'audit
    cur.execute(
        "SELECT * FROM operations_stats WHERE operation_id = %s",
        (operation_id,)
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
        if key != 'operation_id':
            fields.append(f'{key} = %s')
            values.append(value)
    
    values.append(operation_id)
    
    query = f"""
        UPDATE operations_stats 
        SET {', '.join(fields)}
        WHERE operation_id = %s
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
            table='operations_stats',
            action='UPDATE',
            record_id=str(operation_id),
            old_values=changed_old_values,
            new_values=changed_new_values,
            details=f"Modification des statistiques de l'opération {operation_id} - {len(changed_old_values)} champ(s) modifié(s)",
            sql_query=sql_for_audit
        )
    
    return True

def delete_operations_stats(operation_id: int):
    """Supprime les statistiques d'une opération"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Récupérer les données avant suppression pour l'audit
    cur.execute(
        "SELECT * FROM operations_stats WHERE operation_id = %s",
        (operation_id,)
    )
    old_record = cur.fetchone()
    old_columns = [desc[0] for desc in cur.description]
    old_values = dict(zip(old_columns, old_record)) if old_record else {}
    
    cur.execute(
        "DELETE FROM operations_stats WHERE operation_id = %s",
        (operation_id,)
    )
    conn.commit()
    cur.close()
    conn.close()
    
    # Enregistrer l'action dans l'audit
    if old_values:
        log_action(
            table='operations_stats',
            action='DELETE',
            record_id=str(operation_id),
            old_values=old_values,
            details=f"Statistiques de l'opération {operation_id} supprimées",
            sql_query=f"DELETE FROM operations_stats WHERE operation_id = {operation_id}"
        )
    
    return True
