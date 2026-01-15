"""
Requêtes SQL optimisées pour les opérations
Centralise toutes les requêtes pour faciliter la maintenance et l'optimisation
"""
import pandas as pd
from typing import Dict, Any, Optional, Tuple
from src.crud.audit_crud import log_action


class OperationsQueries:
    """Gestionnaire de requêtes SQL pour les opérations"""
    
    @staticmethod
    def count_operations(engine, search_pattern: Optional[str] = None, search_column: str = "operation_id") -> int:
        """
        Compte le nombre total d'opérations avec filtre optionnel
        
        Args:
            engine: Connexion SQLAlchemy
            search_pattern: Pattern de recherche optionnel
            search_column: Colonne sur laquelle effectuer la recherche
            
        Returns:
            Nombre total d'opérations
        """
        if search_pattern:
            # Gérer le cas spécial du cross qui nécessite des guillemets
            column_name = f'"{search_column}"' if search_column == 'cross' else search_column
            query = f"""
            SELECT COUNT(*) as total
            FROM operations 
            WHERE CAST({column_name} AS TEXT) ILIKE %(search_pattern)s
            """
            params = {'search_pattern': f'%{search_pattern}%'}
            return pd.read_sql(query, engine, params=params)['total'].iloc[0]
        else:
            query = "SELECT COUNT(*) as total FROM operations"
            return pd.read_sql(query, engine)['total'].iloc[0]
    
    @staticmethod
    def get_operations_paginated(
        engine, 
        limit: int, 
        offset: int, 
        search_pattern: Optional[str] = None,
        search_column: str = "operation_id"
    ) -> pd.DataFrame:
        """
        Récupère les opérations avec pagination et filtre optionnel
        
        Args:
            engine: Connexion SQLAlchemy
            limit: Nombre d'éléments par page
            offset: Décalage pour la pagination
            search_pattern: Pattern de recherche optionnel
            search_column: Colonne sur laquelle effectuer la recherche
            
        Returns:
            DataFrame des opérations
        """
        base_query = """
        SELECT 
            operation_id,
            "cross",
            evenement,
            date_heure_reception_alerte,
            departement,
            pourquoi_alerte,
            latitude,
            longitude
        FROM operations 
        """
        
        if search_pattern:
            # Gérer le cas spécial du cross qui nécessite des guillemets
            column_name = f'"{search_column}"' if search_column == 'cross' else search_column
            query = base_query + f"""
            WHERE CAST({column_name} AS TEXT) ILIKE %(search_pattern)s
            ORDER BY date_heure_reception_alerte DESC
            LIMIT %(limit)s OFFSET %(offset)s
            """
            params = {
                'search_pattern': f'%{search_pattern}%',
                'limit': limit,
                'offset': offset
            }
        else:
            query = base_query + """
            ORDER BY date_heure_reception_alerte DESC
            LIMIT %(limit)s OFFSET %(offset)s
            """
            params = {'limit': limit, 'offset': offset}
        
        return pd.read_sql(query, engine, params=params)
    
    @staticmethod
    def get_operation_full(engine, operation_id: int) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Récupère toutes les données d'une opération (opération, flotteurs, résultats humains, stats)
        
        Args:
            engine: Connexion SQLAlchemy
            operation_id: ID de l'opération
            
        Returns:
            Tuple de (df_operation, df_flotteurs, df_humain, df_stats)
        """
        # Utiliser des requêtes paramétrées pour éviter l'injection SQL
        query_op = "SELECT * FROM operations WHERE operation_id = %(op_id)s"
        df_op = pd.read_sql(query_op, engine, params={'op_id': operation_id})
        
        query_flotteurs = "SELECT * FROM flotteurs WHERE operation_id = %(op_id)s"
        df_flotteurs = pd.read_sql(query_flotteurs, engine, params={'op_id': operation_id})
        
        query_humain = "SELECT * FROM resultats_humain WHERE operation_id = %(op_id)s"
        df_humain = pd.read_sql(query_humain, engine, params={'op_id': operation_id})
        
        query_stats = "SELECT * FROM operations_stats WHERE operation_id = %(op_id)s"
        df_stats = pd.read_sql(query_stats, engine, params={'op_id': operation_id})
        
        # Enregistrer l'action dans l'audit
        if not df_op.empty:
            log_action(
                table='operations',
                action='VIEW',
                record_id=operation_id,
                details=f"Consultation complète de l'opération {operation_id} (incluant {len(df_flotteurs)} flotteur(s), {len(df_humain)} résultat(s) humain(s), stats)",
                sql_query=f"SELECT * FROM operations WHERE operation_id = {operation_id}"
            )
        
        return df_op, df_flotteurs, df_humain, df_stats
    
    @staticmethod
    def get_next_operation_id(engine) -> int:
        """
        Récupère le prochain ID d'opération disponible
        
        Args:
            engine: Connexion SQLAlchemy
            
        Returns:
            Prochain ID disponible
        """
        query = "SELECT COALESCE(MAX(operation_id), 0) + 1 as next_id FROM operations"
        result = pd.read_sql(query, engine)
        return int(result['next_id'].iloc[0])
    
    @staticmethod
    def get_operation_counts(engine, operation_id: int) -> Dict[str, int]:
        """
        Compte les données liées à une opération
        
        Args:
            engine: Connexion SQLAlchemy
            operation_id: ID de l'opération
            
        Returns:
            Dictionnaire avec les compteurs
        """
        counts = {}
        
        query_flot = "SELECT COUNT(*) as nb FROM flotteurs WHERE operation_id = %(op_id)s"
        counts['flotteurs'] = pd.read_sql(query_flot, engine, params={'op_id': operation_id})['nb'].iloc[0]
        
        query_hum = "SELECT COUNT(*) as nb FROM resultats_humain WHERE operation_id = %(op_id)s"
        counts['humains'] = pd.read_sql(query_hum, engine, params={'op_id': operation_id})['nb'].iloc[0]
        
        query_stats = "SELECT COUNT(*) as nb FROM operations_stats WHERE operation_id = %(op_id)s"
        counts['stats'] = pd.read_sql(query_stats, engine, params={'op_id': operation_id})['nb'].iloc[0]
        
        return counts
