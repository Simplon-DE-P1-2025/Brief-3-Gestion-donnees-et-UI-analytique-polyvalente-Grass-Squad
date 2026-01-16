from src.database.load_database import get_db_connection
import json
import logging

logger = logging.getLogger(__name__)

def log_action(table: str, action: str, record_id: str, user_name: str = 'system', 
               old_values: dict = None, new_values: dict = None, details: str = None, sql_query: str = None):
    """
    Enregistre une action dans le log d'audit avec historique complet
    
    Args:
        table: Nom de la table concernée
        action: Type d'action (INSERT, UPDATE, DELETE, VIEW)
        record_id: ID de l'enregistrement concerné
        user_name: Nom de l'utilisateur (par défaut 'system')
        old_values: Anciennes valeurs (pour UPDATE et DELETE)
        new_values: Nouvelles valeurs (pour INSERT et UPDATE)
        details: Détails supplémentaires sur l'action
        sql_query: Requête SQL exécutée (optionnelle)
    """
    conn = None
    cur = None
    
    try:
        query = """
        INSERT INTO audit_log (table_name, action, record_id, user_name, old_values, new_values, details, sql_query)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """
        
        # Convertir les dictionnaires en JSON
        old_values_json = json.dumps(old_values, default=str) if old_values else None
        new_values_json = json.dumps(new_values, default=str) if new_values else None
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute(query, (table, action, str(record_id), user_name, old_values_json, new_values_json, details, sql_query))
        conn.commit()
        
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Audit log error - Table: {table}, Action: {action}, Record: {record_id}, Error: {str(e)}")
        
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def get_audit_logs(limit: int = 200, table_name: str = None, action: str = None, record_id: str = None):
    query = "SELECT * FROM audit_log WHERE 1=1"
    params = []
    
    if table_name:
        query += " AND table_name = %s"
        params.append(table_name)
    
    if action:
        query += " AND action = %s"
        params.append(action)
    
    if record_id:
        query += " AND record_id = %s"
        params.append(str(record_id))
    
    query += " ORDER BY created_at DESC LIMIT %s"
    params.append(limit)
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(query, tuple(params))
    columns = [desc[0] for desc in cur.description]
    results = [dict(zip(columns, row)) for row in cur.fetchall()]
    cur.close()
    conn.close()
    
    return results

def get_record_history(table_name: str, record_id: str):
    query = """
    SELECT * FROM audit_log 
    WHERE table_name = %s AND record_id = %s 
    ORDER BY created_at ASC
    """
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(query, (table_name, str(record_id)))
    columns = [desc[0] for desc in cur.description]
    results = [dict(zip(columns, row)) for row in cur.fetchall()]
    cur.close()
    conn.close()
    
    return results

def get_audit_statistics():
    query = """
    SELECT 
        COUNT(*) as total_logs,
        COUNT(DISTINCT table_name) as tables_count,
        COUNT(DISTINCT record_id) as records_count,
        SUM(CASE WHEN action = 'INSERT' THEN 1 ELSE 0 END) as inserts,
        SUM(CASE WHEN action = 'UPDATE' THEN 1 ELSE 0 END) as updates,
        SUM(CASE WHEN action = 'DELETE' THEN 1 ELSE 0 END) as deletes,
        SUM(CASE WHEN action = 'VIEW' THEN 1 ELSE 0 END) as views,
        MIN(created_at) as first_log,
        MAX(created_at) as last_log
    FROM audit_log
    """
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(query)
    columns = [desc[0] for desc in cur.description]
    result = dict(zip(columns, cur.fetchone()))
    cur.close()
    conn.close()
    
    return result
