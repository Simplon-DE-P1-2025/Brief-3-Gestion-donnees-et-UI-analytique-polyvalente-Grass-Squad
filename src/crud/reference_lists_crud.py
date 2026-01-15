"""
CRUD operations pour la table reference_lists
Gestion des listes de référence prédéfinies
"""
from src.database.load_database import get_db_connection
import logging

logger = logging.getLogger(__name__)
from src.crud.audit_crud import log_action

def get_reference_list_values(category: str, active_only: bool = True):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if active_only:
            query = """
                SELECT id, value, description 
                FROM reference_lists 
                WHERE category = %s AND is_active = TRUE
                ORDER BY display_order, value
            """
        else:
            query = """
                SELECT id, value, description, is_active 
                FROM reference_lists 
                WHERE category = %s
                ORDER BY display_order, value
            """
        
        cursor.execute(query, (category,))
        results = cursor.fetchall()
        
        return results
    finally:
        cursor.close()
        conn.close()

def get_all_categories():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        query = """
            SELECT DISTINCT category 
            FROM reference_lists 
            ORDER BY category
        """
        cursor.execute(query)
        results = [row[0] for row in cursor.fetchall()]
        
        return results
    finally:
        cursor.close()
        conn.close()

def get_reference_list_by_id(ref_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        query = """
            SELECT id, category, value, display_order, is_active, description 
            FROM reference_lists 
            WHERE id = %s
        """
        cursor.execute(query, (ref_id,))
        result = cursor.fetchone()
        
        return result
    finally:
        cursor.close()
        conn.close()

def insert_reference_list_value(category: str, value: str, display_order: int = 0, description: str = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        query = """
            INSERT INTO reference_lists (category, value, display_order, description)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """
        sql_query = cursor.mogrify(query, (category, value, display_order, description)).decode('utf-8')
        cursor.execute(query, (category, value, display_order, description))
        new_id = cursor.fetchone()[0]
        conn.commit()
        
        # Enregistrer l'action dans l'audit
        log_action(
            table='reference_lists',
            action='INSERT',
            record_id=str(new_id),
            new_values={'category': category, 'value': value, 'display_order': display_order, 'description': description},
            details=f"Nouvelle valeur de référence - Catégorie: {category}, Valeur: {value}",
            sql_query=sql_query
        )
        
        return new_id
    except Exception as e:
        conn.rollback()
        logger.error(f"Insert reference list error: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def update_reference_list_value(ref_id: int, value: str = None, display_order: int = None, 
                                is_active: bool = None, description: str = None):
    """
    Met à jour une entrée de liste de référence
    
    Args:
        ref_id: ID de l'entrée à modifier
        value: Nouvelle valeur (optionnel)
        display_order: Nouvel ordre d'affichage (optionnel)
        is_active: Nouveau statut actif (optionnel)
        description: Nouvelle description (optionnel)
    
    Returns:
        True si succès, False sinon
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Récupérer les anciennes valeurs pour l'audit
        cursor.execute("SELECT * FROM reference_lists WHERE id = %s", (ref_id,))
        old_record = cursor.fetchone()
        old_columns = [desc[0] for desc in cursor.description]
        old_values = dict(zip(old_columns, old_record)) if old_record else {}
        
        updates = []
        params = []
        
        if value is not None:
            updates.append("value = %s")
            params.append(value)
        if display_order is not None:
            updates.append("display_order = %s")
            params.append(display_order)
        if is_active is not None:
            updates.append("is_active = %s")
            params.append(is_active)
        if description is not None:
            updates.append("description = %s")
            params.append(description)
        
        if not updates:
            return False
        
        params.append(ref_id)
        query = f"""
            UPDATE reference_lists 
            SET {', '.join(updates)}
            WHERE id = %s
        """
        
        sql_query = cursor.mogrify(query, params).decode('utf-8')
        cursor.execute(query, params)
        conn.commit()
        success = cursor.rowcount > 0
        
        # Enregistrer l'action dans l'audit
        if success and old_values:
            new_values = {}
            if value is not None: new_values['value'] = value
            if display_order is not None: new_values['display_order'] = display_order
            if is_active is not None: new_values['is_active'] = is_active
            if description is not None: new_values['description'] = description
            
            log_action(
                table='reference_lists',
                action='UPDATE',
                record_id=str(ref_id),
                old_values=old_values,
                new_values=new_values,
                details=f"Valeur de référence mise à jour - ID: {ref_id}",
                sql_query=sql_query
            )
        
        return success
    except Exception as e:
        conn.rollback()
        logger.error(f"Update reference list error: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def delete_reference_list_value(ref_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Récupérer les données avant suppression pour l'audit
        cursor.execute("SELECT * FROM reference_lists WHERE id = %s", (ref_id,))
        old_record = cursor.fetchone()
        old_columns = [desc[0] for desc in cursor.description]
        old_values = dict(zip(old_columns, old_record)) if old_record else {}
        
        query = "DELETE FROM reference_lists WHERE id = %s"
        sql_query = cursor.mogrify(query, (ref_id,)).decode('utf-8')
        cursor.execute(query, (ref_id,))
        conn.commit()
        success = cursor.rowcount > 0
        
        # Enregistrer l'action dans l'audit
        if success and old_values:
            log_action(
                table='reference_lists',
                action='DELETE',
                record_id=str(ref_id),
                old_values=old_values,
                details=f"Valeur de référence supprimée - ID: {ref_id}, Catégorie: {old_values.get('category')}",
                sql_query=sql_query
            )
        
        return success
    except Exception as e:
        conn.rollback()
        logger.error(f"Delete reference list error: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def toggle_reference_list_status(ref_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Récupérer les anciennes valeurs pour l'audit
        cursor.execute("SELECT * FROM reference_lists WHERE id = %s", (ref_id,))
        old_record = cursor.fetchone()
        old_columns = [desc[0] for desc in cursor.description]
        old_values = dict(zip(old_columns, old_record)) if old_record else {}
        
        query = """
            UPDATE reference_lists 
            SET is_active = NOT is_active
            WHERE id = %s
        """
        sql_query = cursor.mogrify(query, (ref_id,)).decode('utf-8')
        cursor.execute(query, (ref_id,))
        conn.commit()
        success = cursor.rowcount > 0
        
        # Enregistrer l'action dans l'audit
        if success and old_values:
            new_status = not old_values.get('is_active', False)
            log_action(
                table='reference_lists',
                action='UPDATE',
                record_id=str(ref_id),
                old_values=old_values,
                new_values={'is_active': new_status},
                details=f"Statut modifié - ID: {ref_id}, Nouveau statut: {'Actif' if new_status else 'Inactif'}",
                sql_query=sql_query
            )
        
        return success
    except Exception as e:
        conn.rollback()
        logger.error(f"Toggle reference list status error: {e}")
        return False
    finally:
        cursor.close()
        conn.close()
