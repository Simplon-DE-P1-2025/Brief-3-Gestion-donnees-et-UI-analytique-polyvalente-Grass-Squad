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
def get_operations_map_data(_engine: Engine, limit: int = 1000, france_metro_only: bool = False) -> pd.DataFrame:
    """
    Récupère les données GPS des opérations pour affichage sur carte.
    Optimisé avec cache et limite pour performances.
    
    Args:
        _engine: Connexion à la base de données
        limit: Nombre maximum d'opérations à récupérer
        france_metro_only: Si True, filtre uniquement la France métropolitaine
    
    Returns:
        pd.DataFrame: Colonnes operation_id, latitude, longitude, evenement
    """
    # Filtres géographiques pour exclure les coordonnées invalides
    # Exclut: (0,0), pôles exacts (-90,90), et limites exactes (-180,180)
    geo_filter = """
        AND latitude IS NOT NULL 
        AND longitude IS NOT NULL
        AND NOT (latitude = 0 AND longitude = 0)
        AND latitude > -89.9 AND latitude < 89.9
        AND longitude > -179.9 AND longitude < 179.9
    """
    
    # Filtre optionnel pour France métropolitaine uniquement
    if france_metro_only:
        geo_filter += """
        AND latitude BETWEEN 41.0 AND 51.5
        AND longitude BETWEEN -5.5 AND 10.0
        """
    
    query = f"""
    SELECT operation_id, latitude, longitude, evenement 
    FROM operations 
    WHERE 1=1
        {geo_filter}
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
