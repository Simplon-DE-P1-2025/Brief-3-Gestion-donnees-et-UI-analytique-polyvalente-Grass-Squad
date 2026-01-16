# -*- coding: utf-8 -*-
"""
Fonctions d'analyse géographique
Optimisé avec cache Streamlit pour améliorer les performances
"""

import pandas as pd
import streamlit as st
from sqlalchemy import Engine


@st.cache_data(ttl=300)
def get_geographic_kpis(_engine: Engine, where_sql: str = "1=1", params: dict = None, france_metro_only: bool = False) -> pd.Series:
    """
    Récupère les KPIs géographiques (couverture GPS, taux de décès).
    Optimisé avec cache et COALESCE pour éviter NULL.
    
    Args:
        _engine: Connexion à la base de données
        where_sql: Clause WHERE SQL (default "1=1")
        params: Paramètres pour la requête SQL
        france_metro_only: Si True, filtre uniquement la France métropolitaine
    
    Returns:
        pd.Series: ops_total, ops_geo, gps_pct, impliquees_total, deces_total, taux_deces_global_pct
    """
    if params is None:
        params = {}
    
    # Filtre géographique optionnel
    geo_filter = ""
    if france_metro_only:
        geo_filter = """
        AND o.latitude BETWEEN 41.0 AND 51.5
        AND o.longitude BETWEEN -5.5 AND 10.0
        """
    
    query = f"""
    WITH base AS (
        SELECT
            o.operation_id,
            (o.latitude IS NOT NULL AND o.longitude IS NOT NULL) AS has_gps,
            COALESCE(os.nombre_personnes_impliquees,0) AS impliquees,
            COALESCE(os.nombre_personnes_decedees,0) AS deces
        FROM operations o
        LEFT JOIN operations_stats os USING(operation_id)
        WHERE {where_sql}
            {geo_filter}
    )
    SELECT
        COUNT(DISTINCT operation_id) AS ops_total,
        COUNT(*) FILTER (WHERE has_gps) AS ops_geo,
        ROUND(100.0 * COUNT(*) FILTER (WHERE has_gps)::numeric / NULLIF(COUNT(*),0), 1) AS gps_pct,
        COALESCE(SUM(impliquees), 0) AS impliquees_total,
        COALESCE(SUM(deces), 0) AS deces_total,
        ROUND(100.0 * COALESCE(SUM(deces), 0)::numeric / NULLIF(COALESCE(SUM(impliquees), 0),0), 2) AS taux_deces_global_pct
    FROM base;
    """
    df = pd.read_sql(query, _engine, params=params)
    return df.iloc[0] if not df.empty else pd.Series()


@st.cache_data(ttl=300)
def get_map_coordinates(_engine: Engine, where_sql: str = "1=1", params: dict = None, limit: int = 3000, france_metro_only: bool = False) -> pd.DataFrame:
    """
    Récupère les coordonnées GPS des opérations pour affichage sur carte.
    Optimisé avec cache et validation des coordonnées.
    
    Args:
        _engine: Connexion à la base de données
        where_sql: Clause WHERE SQL (default "1=1")
        params: Paramètres pour la requête SQL
        limit: Nombre maximum de points à retourner
        france_metro_only: Si True, filtre uniquement la France métropolitaine
    
    Returns:
        pd.DataFrame: Colonnes latitude, longitude
    """
    if params is None:
        params = {}
    
    # Filtres géographiques pour exclure les coordonnées invalides
    # Exclut: (0,0), pôles exacts (-90,90), et limites exactes (-180,180)
    geo_filter = """
        AND o.latitude IS NOT NULL 
        AND o.longitude IS NOT NULL
        AND NOT (o.latitude = 0 AND o.longitude = 0)
        AND o.latitude > -89.9 AND o.latitude < 89.9
        AND o.longitude > -179.9 AND o.longitude < 179.9
    """
    
    # Filtre optionnel pour France métropolitaine uniquement
    if france_metro_only:
        geo_filter += """
        AND o.latitude BETWEEN 41.0 AND 51.5
        AND o.longitude BETWEEN -5.5 AND 10.0
        """
    
    query = f"""
    SELECT 
        o.latitude, 
        o.longitude
    FROM operations o
    WHERE {where_sql}
        {geo_filter}
    LIMIT {limit};
    """
    return pd.read_sql(query, _engine, params=params)


@st.cache_data(ttl=300)
def get_top_zones_cross(_engine: Engine, where_sql: str = "1=1", params: dict = None, limit: int = 15, france_metro_only: bool = False) -> pd.DataFrame:
    """
    Analyse des zones CROSS par volume et charge humaine.
    Optimisé avec cache et agrégations efficaces.
    
    Args:
        _engine: Connexion à la base de données
        where_sql: Clause WHERE SQL (default "1=1")
        params: Paramètres pour la requête SQL
        limit: Nombre de zones à retourner
        france_metro_only: Si True, filtre uniquement la France métropolitaine
    
    Returns:
        pd.DataFrame: Colonnes cross, operations, impliquees, impliquees_par_operation, deces, taux_deces_pct
    """
    if params is None:
        params = {}
    
    # Filtre géographique optionnel
    geo_filter = ""
    if france_metro_only:
        geo_filter = """
        AND o.latitude BETWEEN 41.0 AND 51.5
        AND o.longitude BETWEEN -5.5 AND 10.0
        """
    
    query = f"""
    SELECT
        NULLIF(TRIM(o.cross),'') AS cross,
        COUNT(DISTINCT o.operation_id) AS operations,
        COALESCE(SUM(os.nombre_personnes_impliquees),0) AS impliquees,
        ROUND(
            COALESCE(SUM(os.nombre_personnes_impliquees),0)::numeric
            / NULLIF(COUNT(DISTINCT o.operation_id),0),
            2
        ) AS impliquees_par_operation,
        COALESCE(SUM(os.nombre_personnes_decedees),0) AS deces,
        ROUND(
            100.0 * COALESCE(SUM(os.nombre_personnes_decedees),0)::numeric
            / NULLIF(COALESCE(SUM(os.nombre_personnes_impliquees),0),0),
            2
        ) AS taux_deces_pct
    FROM operations o
    LEFT JOIN operations_stats os USING(operation_id)
    WHERE {where_sql}
        {geo_filter}
        AND NULLIF(TRIM(o.cross),'') IS NOT NULL
    GROUP BY 1
    ORDER BY operations DESC
    LIMIT {limit};
    """
    return pd.read_sql(query, _engine, params=params)
