# -*- coding: utf-8 -*-
"""
Fonctions d'analyse pour le dashboard principal
Optimisé avec cache Streamlit pour améliorer les performances
"""

import pandas as pd
import streamlit as st
from sqlalchemy import Engine


@st.cache_data(ttl=300)  # Cache pendant 5 minutes
def get_global_kpis(_engine: Engine) -> pd.Series:
    """
    Récupère les KPIs globaux (opérations, personnes sauvées, décès, etc.)
    Optimisé avec cache pour éviter les requêtes répétées.
    
    Args:
        _engine: Connexion à la base (préfixé _ pour ignorer dans le cache)
    
    Returns:
        pd.Series: KPIs avec colonnes total_secourus, total_deces, total_impliques, total_operations
    """
    query = """
    SELECT 
        COALESCE(SUM(nombre_personnes_secourues), 0) as total_secourus,
        COALESCE(SUM(nombre_personnes_tous_deces), 0) as total_deces,
        COALESCE(SUM(nombre_personnes_impliquees), 0) as total_impliques,
        COUNT(DISTINCT operation_id) as total_operations
    FROM operations_stats
    """
    df = pd.read_sql(query, _engine)
    return df.iloc[0] if not df.empty else pd.Series()


@st.cache_data(ttl=300)
def get_operations_map_data(_engine: Engine, limit: int = 1000) -> pd.DataFrame:
    """
    Récupère les données GPS des opérations pour affichage sur carte.
    Optimisé avec cache et limite pour performances.
    
    Args:
        _engine: Connexion à la base de données
        limit: Nombre maximum d'opérations à récupérer
    
    Returns:
        pd.DataFrame: Colonnes operation_id, latitude, longitude, evenement
    """
    query = f"""
    SELECT operation_id, latitude, longitude, evenement 
    FROM operations 
    WHERE latitude IS NOT NULL 
        AND longitude IS NOT NULL
        AND latitude BETWEEN -90 AND 90
        AND longitude BETWEEN -180 AND 180
    LIMIT {limit}
    """
    return pd.read_sql(query, _engine)


@st.cache_data(ttl=600)  # Cache 10 minutes (change rarement)
def get_database_info(_engine: Engine) -> pd.DataFrame:
    """
    Récupère les informations de connexion à la base de données.
    Optimisé avec cache long car ces infos changent rarement.
    
    Args:
        _engine: Connexion à la base de données
    
    Returns:
        pd.DataFrame: Informations sur la base actuelle
    """
    query = "SELECT current_database(), inet_server_addr(), inet_server_port();"
    return pd.read_sql(query, _engine)
