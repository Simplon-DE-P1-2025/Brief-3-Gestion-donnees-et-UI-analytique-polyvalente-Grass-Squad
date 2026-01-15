"""
Fonctions d'analyse pour le dashboard Météo.
Optimisé avec cache Streamlit pour améliorer les performances.
"""
import pandas as pd
import streamlit as st


@st.cache_data(ttl=300)
def get_wind_force_analysis(_engine, where_sql: str, params: dict) -> pd.DataFrame:
    """
    Retourne le volume d'opérations par force de vent.
    Optimisé avec cache Streamlit.
    
    Returns:
        DataFrame avec colonnes:
        - vent_force: force du vent (entier)
        - operations: nombre d'opérations
    """
    q = f"""
    SELECT
        FLOOR(o.vent_force)::int AS vent_force,
        COUNT(DISTINCT o.operation_id) AS operations
    FROM operations o
    WHERE {where_sql}
        AND o.vent_force IS NOT NULL
        AND FLOOR(o.vent_force) BETWEEN 1 AND 12
    GROUP BY 1
    ORDER BY 1;
    """
    return pd.read_sql(q, _engine, params=params)


@st.cache_data(ttl=300)
def get_sea_force_analysis(_engine, where_sql: str, params: dict) -> pd.DataFrame:
    """
    Retourne le volume d'opérations par force de mer.
    Optimisé avec cache Streamlit.
    
    Returns:
        DataFrame avec colonnes:
        - mer_force: force de la mer (entier)
        - operations: nombre d'opérations
    """
    q = f"""
    SELECT
        FLOOR(o.mer_force)::int AS mer_force,
        COUNT(DISTINCT o.operation_id) AS operations
    FROM operations o
    WHERE {where_sql}
        AND o.mer_force IS NOT NULL
        AND FLOOR(o.mer_force) BETWEEN 1 AND 12
    GROUP BY 1
    ORDER BY 1;
    """
    return pd.read_sql(q, _engine, params=params)


@st.cache_data(ttl=300)
def get_gravity_by_sea_force(_engine) -> pd.DataFrame:
    """
    Retourne la charge humaine (personnes impliquées) par force de mer.
    Optimisé avec cache Streamlit.
    
    Returns:
        DataFrame avec colonnes:
        - mer_force: force de la mer
        - personnes_impliquees: total de personnes impliquées
    """
    q = """
    SELECT
        FLOOR(o.mer_force)::int AS mer_force,
        COALESCE(SUM(os.nombre_personnes_impliquees),0) AS personnes_impliquees
    FROM operations o
    JOIN operations_stats os USING(operation_id)
    WHERE o.mer_force IS NOT NULL
        AND FLOOR(o.mer_force) BETWEEN 1 AND 12
    GROUP BY 1
    ORDER BY 1;
    """
    return pd.read_sql(q, _engine)


@st.cache_data(ttl=300)
def get_sea_categories_distribution(_engine, where_sql: str, params: dict) -> pd.DataFrame:
    """
    Retourne la répartition des opérations par catégories de mer (calme/modéré/difficile).
    Optimisé avec cache Streamlit.
    
    Returns:
        DataFrame avec colonnes:
        - categorie_mer: catégorie (Calme/Modéré/Difficile)
        - operations: nombre d'opérations
    """
    q = f"""
    SELECT
        CASE
            WHEN FLOOR(o.mer_force) BETWEEN 1 AND 2 THEN 'Calme (1-2)'
            WHEN FLOOR(o.mer_force) BETWEEN 3 AND 4 THEN 'Modéré (3-4)'
            WHEN FLOOR(o.mer_force) >= 5 THEN 'Difficile (>=5)'
            ELSE NULL
        END AS categorie_mer,
        COUNT(DISTINCT o.operation_id) AS operations
    FROM operations o
    WHERE {where_sql}
        AND o.mer_force IS NOT NULL
        AND FLOOR(o.mer_force) >= 1
    GROUP BY 1
    HAVING CASE
            WHEN FLOOR(o.mer_force) BETWEEN 1 AND 2 THEN 'Calme (1-2)'
            WHEN FLOOR(o.mer_force) BETWEEN 3 AND 4 THEN 'Modéré (3-4)'
            WHEN FLOOR(o.mer_force) >= 5 THEN 'Difficile (>=5)'
            ELSE NULL
        END IS NOT NULL;
    """
    return pd.read_sql(q, _engine, params=params)


@st.cache_data(ttl=300)
def get_tide_analysis(_engine) -> pd.DataFrame:
    """
    Retourne l'analyse des marées : volume d'opérations et charge humaine par catégorie de marée.
    Optimisé avec cache Streamlit.
    
    Returns:
        DataFrame avec colonnes:
        - maree_categorie: catégorie de marée
        - operations: nombre d'opérations
        - personnes_impliquees: total de personnes impliquées
    """
    q = """
    SELECT
        maree_categorie,
        COUNT(*) AS operations,
        COALESCE(SUM(nombre_personnes_impliquees), 0) AS personnes_impliquees
    FROM operations_stats
    WHERE maree_categorie IS NOT NULL
        AND maree_categorie <> 'moyenne'
    GROUP BY 1
    ORDER BY operations DESC;
    """
    return pd.read_sql(q, _engine)
