"""
CRUD operations pour la table reference_lists
Gestion des listes de référence prédéfinies
"""
from src.database.load_database import get_db_connection

def get_reference_list_values(category: str, active_only: bool = True):
    """
    Récupère toutes les valeurs d'une catégorie de liste de référence
    
    Args:
        category: Le nom de la catégorie (ex: 'type_operation', 'pavillon')
        active_only: Si True, retourne uniquement les valeurs actives
    
    Returns:
        Liste de tuples (id, value, description)
    """
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
    """
    Récupère toutes les catégories distinctes
    
    Returns:
        Liste des catégories
    """
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
    """
    Récupère une entrée de référence par son ID
    
    Args:
        ref_id: ID de l'entrée
    
    Returns:
        Tuple (id, category, value, display_order, is_active, description)
    """
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
    """
    Insère une nouvelle valeur dans une liste de référence
    
    Args:
        category: La catégorie
        value: La valeur à insérer
        display_order: L'ordre d'affichage
        description: Description optionnelle
    
    Returns:
        ID de l'entrée créée ou None si erreur
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        query = """
            INSERT INTO reference_lists (category, value, display_order, description)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """
        cursor.execute(query, (category, value, display_order, description))
        new_id = cursor.fetchone()[0]
        conn.commit()
        return new_id
    except Exception as e:
        conn.rollback()
        print(f"Erreur lors de l'insertion: {e}")
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
        
        cursor.execute(query, params)
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        conn.rollback()
        print(f"Erreur lors de la mise à jour: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def delete_reference_list_value(ref_id: int):
    """
    Supprime une entrée de liste de référence
    
    Args:
        ref_id: ID de l'entrée à supprimer
    
    Returns:
        True si succès, False sinon
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        query = "DELETE FROM reference_lists WHERE id = %s"
        cursor.execute(query, (ref_id,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        conn.rollback()
        print(f"Erreur lors de la suppression: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def toggle_reference_list_status(ref_id: int):
    """
    Bascule le statut actif/inactif d'une entrée
    
    Args:
        ref_id: ID de l'entrée
    
    Returns:
        True si succès, False sinon
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        query = """
            UPDATE reference_lists 
            SET is_active = NOT is_active
            WHERE id = %s
        """
        cursor.execute(query, (ref_id,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        conn.rollback()
        print(f"Erreur lors du changement de statut: {e}")
        return False
    finally:
        cursor.close()
        conn.close()
