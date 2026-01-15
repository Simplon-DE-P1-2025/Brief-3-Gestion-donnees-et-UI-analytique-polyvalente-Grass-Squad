from src.database.load_database import get_db_connection
from src.crud.audit_crud import log_action

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
        table='resultats_humain',
        action='INSERT',
        record_id=str(data.get('operation_id')),
        new_values=data,
        details=f"Résultat humain ajouté - Opération: {data.get('operation_id')}, Catégorie: {data.get('categorie_personne')}",
        sql_query=sql_for_audit
    )

def select_resultats_by_operation(operation_id: int):
    """Récupère tous les résultats humains d'une opération"""
    conn = get_db_connection()
    cur = conn.cursor()
    query = "SELECT * FROM resultats_humain WHERE operation_id = %s"
    cur.execute(query, (operation_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    
    # Enregistrer l'action dans l'audit si des résultats sont trouvés
    if rows:
        log_action(
            table='resultats_humain',
            action='VIEW',
            record_id=str(operation_id),
            details=f"Consultation de {len(rows)} résultat(s) humain(s) pour l'opération {operation_id}",
            sql_query=f"SELECT * FROM resultats_humain WHERE operation_id = {operation_id}"
        )
    
    return rows

def update_resultat_humain(operation_id: int, categorie_personne: str, data: dict):
    """Met à jour un résultat humain"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Récupérer les anciennes valeurs pour l'audit
    cur.execute(
        "SELECT * FROM resultats_humain WHERE operation_id = %s AND categorie_personne = %s",
        (operation_id, categorie_personne)
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
        if key not in ['operation_id', 'categorie_personne']:
            fields.append(f'{key} = %s')
            values.append(value)
    
    values.extend([operation_id, categorie_personne])
    
    query = f"""
        UPDATE resultats_humain 
        SET {', '.join(fields)}
        WHERE operation_id = %s AND categorie_personne = %s
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
            table='resultats_humain',
            action='UPDATE',
            record_id=f"{operation_id}_{categorie_personne}",
            old_values=changed_old_values,
            new_values=changed_new_values,
            details=f"Modification du résultat humain - Opération: {operation_id}, Catégorie: {categorie_personne} - {len(changed_old_values)} champ(s) modifié(s)",
            sql_query=sql_for_audit
        )
    
    return True

def delete_resultat_humain(operation_id: int, categorie_personne: str):
    """Supprime un résultat humain"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Récupérer les données avant suppression pour l'audit
    cur.execute(
        "SELECT * FROM resultats_humain WHERE operation_id = %s AND categorie_personne = %s",
        (operation_id, categorie_personne)
    )
    old_record = cur.fetchone()
    old_columns = [desc[0] for desc in cur.description]
    old_values = dict(zip(old_columns, old_record)) if old_record else {}
    
    cur.execute(
        "DELETE FROM resultats_humain WHERE operation_id = %s AND categorie_personne = %s",
        (operation_id, categorie_personne)
    )
    conn.commit()
    cur.close()
    conn.close()
    
    # Enregistrer l'action dans l'audit
    if old_values:
        log_action(
            table='resultats_humain',
            action='DELETE',
            record_id=f"{operation_id}_{categorie_personne}",
            old_values=old_values,
            details=f"Résultat humain supprimé - Opération: {operation_id}, Catégorie: {categorie_personne}",
            sql_query=f"DELETE FROM resultats_humain WHERE operation_id = {operation_id} AND categorie_personne = '{categorie_personne}'"
        )
    
    return True
