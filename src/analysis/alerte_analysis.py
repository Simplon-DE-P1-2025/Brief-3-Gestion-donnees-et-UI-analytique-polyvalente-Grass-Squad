"""
Module d'analyse pour le dashboard Alerte & Typologie des événements
Contient les requêtes SQL optimisées avec cache pour les alertes, événements et typologies
"""

import streamlit as st
import pandas as pd


@st.cache_data(ttl=600)
def get_global_kpi(_engine):
    """
    Calcule les KPI globaux pour le dashboard alerte
    
    Args:
        _engine: SQLAlchemy engine (exclu du cache)
    
    Returns:
        dict: total_operations, total_impliques, total_deces
    """
    query = """
    SELECT
        COUNT(DISTINCT o.operation_id) AS total_operations,
        SUM(COALESCE(os.nombre_personnes_impliquees, 0)) AS total_impliques,
        SUM(COALESCE(os.nombre_personnes_decedees, 0)) AS total_deces
    FROM operations o
    LEFT JOIN operations_stats os USING(operation_id)
    """
    
    result = pd.read_sql(query, _engine).iloc[0]
    return result.to_dict()


@st.cache_data(ttl=300)
def get_top_events(_engine, limit=15):
    """
    Récupère les événements les plus fréquents avec leur charge humaine
    
    Args:
        _engine: SQLAlchemy engine (exclu du cache)
        limit: nombre max d'événements à retourner
    
    Returns:
        DataFrame: evenement, operations, personnes_impliquees
    """
    query = f"""
    SELECT
        NULLIF(TRIM(o.evenement), '') AS evenement,
        COUNT(DISTINCT o.operation_id) AS operations,
        SUM(COALESCE(os.nombre_personnes_impliquees, 0)) AS personnes_impliquees
    FROM operations o
    LEFT JOIN operations_stats os USING(operation_id)
    WHERE NULLIF(TRIM(o.evenement), '') IS NOT NULL
    GROUP BY 1
    ORDER BY operations DESC
    LIMIT {limit}
    """
    
    return pd.read_sql(query, _engine)


@st.cache_data(ttl=300)
def get_event_categories(_engine):
    """
    Récupère les catégories d'événements avec statistiques
    
    Args:
        _engine: SQLAlchemy engine (exclu du cache)
    
    Returns:
        DataFrame: categorie, operations, personnes_impliquees
    """
    query = """
    SELECT
        NULLIF(TRIM(o.categorie_evenement), '') AS categorie,
        COUNT(DISTINCT o.operation_id) AS operations,
        SUM(COALESCE(os.nombre_personnes_impliquees, 0)) AS personnes_impliquees
    FROM operations o
    LEFT JOIN operations_stats os USING(operation_id)
    WHERE NULLIF(TRIM(o.categorie_evenement), '') IS NOT NULL
    GROUP BY 1
    ORDER BY operations DESC
    """
    
    return pd.read_sql(query, _engine)


@st.cache_data(ttl=300)
def get_alert_methods(_engine):
    """
    Récupère les moyens d'alerte et leur fréquence d'utilisation
    
    Args:
        _engine: SQLAlchemy engine (exclu du cache)
    
    Returns:
        DataFrame: moyen_alerte, operations
    """
    query = """
    SELECT
        NULLIF(TRIM(o.moyen_alerte), '') AS moyen_alerte,
        COUNT(DISTINCT o.operation_id) AS operations
    FROM operations o
    WHERE NULLIF(TRIM(o.moyen_alerte), '') IS NOT NULL
    GROUP BY 1
    ORDER BY operations DESC
    """
    
    return pd.read_sql(query, _engine)
