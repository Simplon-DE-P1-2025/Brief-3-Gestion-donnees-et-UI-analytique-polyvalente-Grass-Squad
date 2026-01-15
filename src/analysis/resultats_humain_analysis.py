"""
Fonctions d'analyse pour le dashboard Résultats Humains.
Optimisé avec cache Streamlit pour améliorer les performances.
"""
import pandas as pd
import streamlit as st


@st.cache_data(ttl=300)
def get_human_pipeline_kpis(_engine, where_sql: str, params: dict) -> pd.Series:
    """
    Retourne les KPIs du pipeline humain (impliquées, secourues, blessées, décédées, fausse alerte).
    Optimisé avec cache Streamlit.
    
    Returns:
        Series avec colonnes:
        - impliquees: nombre total de personnes impliquées
        - secourues: nombre de personnes secourues
        - blessees: nombre de personnes blessées
        - deces: nombre de décès
        - fausse_alerte: nombre de personnes dans fausse alerte
    """
    q = f"""
    SELECT
        COALESCE(SUM(os.nombre_personnes_impliquees),0) AS impliquees,
        COALESCE(SUM(os.nombre_personnes_secourues),0) AS secourues,
        COALESCE(SUM(os.nombre_personnes_blessees),0) AS blessees,
        COALESCE(SUM(os.nombre_personnes_decedees),0) AS deces,
        COALESCE(SUM(os.nombre_personnes_impliquees_dans_fausse_alerte),0) AS fausse_alerte
    FROM operations_stats os
    WHERE {where_sql};
    """
    return pd.read_sql(q, _engine, params=params).iloc[0]


@st.cache_data(ttl=300)
def get_profiles_analysis(_engine, where_sql: str, params: dict) -> pd.DataFrame:
    """
    Retourne l'analyse des profils : volume et taux de blessure par catégorie de personne.
    Optimisé avec cache Streamlit.
    
    Returns:
        DataFrame avec colonnes:
        - categorie_personne
        - personnes: nombre total de personnes
        - blesses: nombre de blessés
        - taux_blessure_pct: taux de blessure en %
    """
    q = f"""
    SELECT
        NULLIF(TRIM(rh.categorie_personne),'') AS categorie_personne,
        COALESCE(SUM(rh.nombre),0) AS personnes,
        COALESCE(SUM(rh.dont_nombre_blesse),0) AS blesses,
        ROUND(
            100.0 * COALESCE(SUM(rh.dont_nombre_blesse),0)::numeric
            / NULLIF(COALESCE(SUM(rh.nombre),0),0),
            2
        ) AS taux_blessure_pct
    FROM resultats_humain rh
    JOIN operations_stats os
        ON os.operation_id = rh.operation_id
    WHERE {where_sql}
        AND NULLIF(TRIM(rh.categorie_personne),'') IS NOT NULL
    GROUP BY 1
    ORDER BY personnes DESC;
    """
    return pd.read_sql(q, _engine, params=params)


@st.cache_data(ttl=300)
def get_human_outcomes_global(_engine, where_sql: str, params: dict) -> pd.DataFrame:
    """
    Retourne la répartition globale des issues humaines (résultat_humain).
    Optimisé avec cache Streamlit.
    
    Returns:
        DataFrame avec colonnes:
        - resultat_humain
        - personnes: nombre de personnes
    """
    q = f"""
    SELECT
        NULLIF(TRIM(rh.resultat_humain),'') AS resultat_humain,
        COALESCE(SUM(rh.nombre),0) AS personnes
    FROM resultats_humain rh
    JOIN operations_stats os
        ON os.operation_id = rh.operation_id
    WHERE {where_sql}
        AND NULLIF(TRIM(rh.resultat_humain),'') IS NOT NULL
    GROUP BY 1
    ORDER BY personnes DESC;
    """
    return pd.read_sql(q, _engine, params=params)


@st.cache_data(ttl=300)
def get_human_outcomes_by_profile(_engine, where_sql: str, params: dict, top_profils: list) -> pd.DataFrame:
    """
    Retourne la répartition des issues humaines par profil (top profils).
    Optimisé avec cache Streamlit.
    
    Args:
        top_profils: Liste des catégories de personne à analyser
    
    Returns:
        DataFrame avec colonnes:
        - categorie_personne
        - resultat_humain
        - personnes: nombre de personnes
    """
    q = f"""
    SELECT
        NULLIF(TRIM(rh.categorie_personne),'') AS categorie_personne,
        NULLIF(TRIM(rh.resultat_humain),'') AS resultat_humain,
        COALESCE(SUM(rh.nombre),0) AS personnes
    FROM resultats_humain rh
    JOIN operations_stats os
        ON os.operation_id = rh.operation_id
    WHERE {where_sql}
        AND NULLIF(TRIM(rh.categorie_personne),'') = ANY(%(top_profils)s::text[])
        AND NULLIF(TRIM(rh.resultat_humain),'') IS NOT NULL
    GROUP BY 1,2;
    """
    params_with_profils = dict(params)
    params_with_profils["top_profils"] = top_profils
    return pd.read_sql(q, _engine, params=params_with_profils)
