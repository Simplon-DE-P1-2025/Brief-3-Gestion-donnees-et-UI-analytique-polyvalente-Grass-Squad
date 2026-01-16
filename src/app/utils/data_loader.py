"""Module centralisé pour le chargement des données avec cache optimisé"""
import streamlit as st
import pandas as pd
from src.database.load_database import engine
from src.crud.reference_lists_crud import get_reference_list_values

@st.cache_data(ttl=120)
def get_operations_count(cross=None, evenement=None):
    """Compte les opérations avec filtres optionnels"""
    query = "SELECT COUNT(*) as total FROM operations WHERE 1=1"
    params = []
    
    if cross:
        query += " AND cross = %s"
        params.append(cross)
    if evenement:
        query += " AND evenement = %s"
        params.append(evenement)
    
    if params:
        return pd.read_sql(query, engine, params=tuple(params))['total'].iloc[0]
    return pd.read_sql(query, engine)['total'].iloc[0]

@st.cache_data(ttl=120)
def get_stats_totals():
    """Récupère les statistiques globales"""
    query = """
    SELECT 
        SUM(nombre_personnes_secourues) as total_secourus,
        SUM(nombre_personnes_tous_deces) as total_deces,
        SUM(nombre_personnes_impliquees) as total_impliques,
        SUM(nombre_personnes_disparues) as total_disparus,
        COUNT(DISTINCT operation_id) as total_operations
    FROM operations_stats
    """
    return pd.read_sql(query, engine)

@st.cache_data(ttl=60)
def get_operation_by_id(operation_id: int):
    """Charge une opération par ID"""
    query = "SELECT * FROM operations WHERE operation_id = %s"
    return pd.read_sql(query, engine, params=(operation_id,))

@st.cache_data(ttl=60)
def get_flotteurs_by_operation(operation_id: int):
    """Charge les flotteurs d'une opération"""
    query = "SELECT * FROM flotteurs WHERE operation_id = %s"
    return pd.read_sql(query, engine, params=(operation_id,))

@st.cache_data(ttl=60)
def get_resultats_humain_by_operation(operation_id: int):
    """Charge les résultats humains d'une opération"""
    query = "SELECT * FROM resultats_humain WHERE operation_id = %s"
    return pd.read_sql(query, engine, params=(operation_id,))

@st.cache_data(ttl=60)
def get_stats_by_operation(operation_id: int):
    """Charge les statistiques d'une opération"""
    query = "SELECT * FROM operations_stats WHERE operation_id = %s"
    return pd.read_sql(query, engine, params=(operation_id,))

@st.cache_data(ttl=300)
def get_map_data(limit=1000):
    """Charge les données pour la carte"""
    query = """
    SELECT operation_id, latitude, longitude, evenement 
    FROM operations 
    WHERE latitude IS NOT NULL AND longitude IS NOT NULL
    LIMIT %s
    """
    return pd.read_sql(query, engine, params=(limit,))

@st.cache_data(ttl=300)
def get_reference_list_cached(category):
    """Charge une liste de référence avec cache"""
    try:
        values = get_reference_list_values(category, active_only=True)
        return [None] + [val[1] for val in values]
    except:
        return [None]

@st.cache_data(ttl=300)
def get_db_info():
    """Récupère les infos de connexion DB"""
    return pd.read_sql("SELECT current_database(), inet_server_addr(), inet_server_port();", engine)

def clear_operation_cache(operation_id: int):
    """Nettoie le cache pour une opération spécifique"""
    get_operation_by_id.clear()
    get_flotteurs_by_operation.clear()
    get_resultats_humain_by_operation.clear()
    get_stats_by_operation.clear()
    get_operations_count.clear()
    get_stats_totals.clear()
