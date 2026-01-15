"""
Fonctions d'analyse pour le dashboard Flotteurs.
Optimisé avec cache Streamlit pour améliorer les performances.
"""
import pandas as pd
import streamlit as st


@st.cache_data(ttl=300)
def get_operations_coverage(_engine) -> pd.Series:
    """
    Retourne la couverture globale des opérations avec/sans flotteurs.
    Optimisé avec cache Streamlit.
    
    Returns:
        Series avec colonnes:
        - ops_total: nombre total d'opérations
        - ops_sans_flotteur: nombre d'opérations sans flotteur
    """
    q = """
    SELECT
        COUNT(*) AS ops_total,
        COUNT(*) FILTER (WHERE sans_flotteur_implique = TRUE) AS ops_sans_flotteur
    FROM operations_stats;
    """
    return pd.read_sql(q, _engine).iloc[0]


@st.cache_data(ttl=300)
def get_flotteurs_coverage(_engine, where_sql: str, params: dict) -> pd.Series:
    """
    Retourne les statistiques globales de couverture flotteurs.
    Optimisé avec cache Streamlit.
    
    Returns:
        Series avec colonnes:
        - flotteurs_total: nombre total de flotteurs
        - operations_avec_flotteur: nombre d'opérations ayant au moins 1 flotteur
    """
    q = f"""
    SELECT
        COUNT(*) AS flotteurs_total,
        COUNT(DISTINCT f.operation_id) AS operations_avec_flotteur
    FROM flotteurs f
    WHERE {where_sql};
    """
    return pd.read_sql(q, _engine, params=params).iloc[0]


@st.cache_data(ttl=300)
def get_operations_by_category(_engine, where_sql: str, params: dict) -> pd.DataFrame:
    """
    Retourne le nombre d'opérations et flotteurs par catégorie de flotteur.
    
    Returns:
        DataFrame avec colonnes:
        - categorie_flotteur
        - operations: nombre d'opérations distinctes
        - flotteurs_impliques: nombre total de flotteurs
    """
    q = f"""
    SELECT
        NULLIF(TRIM(f.categorie_flotteur),'') AS categorie_flotteur,
        COUNT(DISTINCT f.operation_id) AS operations,
        COUNT(*) AS flotteurs_impliques
    FROM flotteurs f
    WHERE {where_sql}
        AND NULLIF(TRIM(f.categorie_flotteur),'') IS NOT NULL
    GROUP BY 1
    ORDER BY operations DESC
    LIMIT %(topn)s;
    """
    return pd.read_sql(q, _engine, params=params)


@st.cache_data(ttl=300)
def get_charge_humaine_by_category(_engine, where_sql: str, params: dict) -> pd.DataFrame:
    """
    Retourne la charge humaine (personnes impliquées) par catégorie de flotteur.
    
    Returns:
        DataFrame avec colonnes:
        - categorie_flotteur
        - operations
        - personnes_impliquees: total
        - impliquees_par_operation: moyenne
    """
    q = f"""
    SELECT
        NULLIF(TRIM(f.categorie_flotteur),'') AS categorie_flotteur,
        COUNT(DISTINCT f.operation_id) AS operations,
        SUM(COALESCE(os.nombre_personnes_impliquees,0)) AS personnes_impliquees,
        ROUND(
            SUM(COALESCE(os.nombre_personnes_impliquees,0))::numeric
            / NULLIF(COUNT(DISTINCT f.operation_id),0),
            2
        ) AS impliquees_par_operation
    FROM flotteurs f
    JOIN operations_stats os
        ON os.operation_id = f.operation_id
    WHERE {where_sql}
        AND NULLIF(TRIM(f.categorie_flotteur),'') IS NOT NULL
    GROUP BY 1
    HAVING COUNT(DISTINCT f.operation_id) >= %(min_ops)s
    ORDER BY impliquees_par_operation DESC
    LIMIT %(topn)s;
    """
    return pd.read_sql(q, _engine, params=params)


@st.cache_data(ttl=300)
def get_criticite_by_category(_engine, where_sql: str, params: dict) -> pd.DataFrame:
    """
    Retourne la criticité (taux de décès) par catégorie de flotteur.
    
    Returns:
        DataFrame avec colonnes:
        - categorie_flotteur
        - operations
        - personnes_impliquees
        - deces
        - taux_deces_pct
    """
    q = f"""
    SELECT
        NULLIF(TRIM(f.categorie_flotteur),'') AS categorie_flotteur,
        COUNT(DISTINCT f.operation_id) AS operations,
        SUM(COALESCE(os.nombre_personnes_impliquees,0)) AS personnes_impliquees,
        SUM(COALESCE(os.nombre_personnes_decedees,0)) AS deces,
        ROUND(
            100.0 * SUM(COALESCE(os.nombre_personnes_decedees,0))::numeric
            / NULLIF(SUM(COALESCE(os.nombre_personnes_impliquees,0)),0),
            2
        ) AS taux_deces_pct
    FROM flotteurs f
    JOIN operations_stats os
        ON os.operation_id = f.operation_id
    WHERE {where_sql}
        AND NULLIF(TRIM(f.categorie_flotteur),'') IS NOT NULL
    GROUP BY 1
    HAVING COUNT(DISTINCT f.operation_id) >= %(min_ops)s
    ORDER BY taux_deces_pct DESC
    LIMIT %(topn)s;
    """
    return pd.read_sql(q, _engine, params=params)


@st.cache_data(ttl=300)
def get_top_categories_for_outcomes(_engine, where_sql: str, params: dict) -> pd.DataFrame:
    """
    Retourne les catégories de flotteurs les plus fréquentes (pour analyse des issues matérielles).
    
    Returns:
        DataFrame avec colonnes:
        - categorie_flotteur
        - flotteurs: nombre de flotteurs
    """
    q = f"""
    SELECT
        NULLIF(TRIM(f.categorie_flotteur),'') AS categorie_flotteur,
        COUNT(*) AS flotteurs
    FROM flotteurs f
    WHERE {where_sql}
        AND NULLIF(TRIM(f.categorie_flotteur),'') IS NOT NULL
    GROUP BY 1
    ORDER BY flotteurs DESC
    LIMIT %(topn)s;
    """
    return pd.read_sql(q, _engine, params=params)


@st.cache_data(ttl=300)
def get_outcomes_by_category(_engine, where_sql: str, params: dict, top_cats: list) -> pd.DataFrame:
    """
    Retourne les issues matérielles (résultat_flotteur) pour les catégories spécifiées.
    
    Args:
        top_cats: Liste des catégories de flotteur à analyser
    
    Returns:
        DataFrame avec colonnes:
        - categorie_flotteur
        - resultat_flotteur
        - nb: nombre de flotteurs
    """
    q = f"""
    SELECT
        NULLIF(TRIM(f.categorie_flotteur),'') AS categorie_flotteur,
        NULLIF(TRIM(f.resultat_flotteur),'') AS resultat_flotteur,
        COUNT(*) AS nb
    FROM flotteurs f
    WHERE {where_sql}
        AND NULLIF(TRIM(f.categorie_flotteur),'') IS NOT NULL
        AND NULLIF(TRIM(f.resultat_flotteur),'') IS NOT NULL
        AND NULLIF(TRIM(f.categorie_flotteur),'') = ANY(%(topcats)s::text[])
    GROUP BY 1,2;
    """
    params_with_cats = dict(params)
    params_with_cats["topcats"] = top_cats
    return pd.read_sql(q, _engine, params=params_with_cats)


@st.cache_data(ttl=300)
def get_pavillons_stats(_engine, where_sql: str, params: dict) -> pd.DataFrame:
    """
    Retourne les statistiques par pavillon.
    
    Returns:
        DataFrame avec colonnes:
        - pavillon
        - flotteurs: nombre de flotteurs
    """
    q = f"""
    SELECT
        NULLIF(TRIM(f.pavillon),'') AS pavillon,
        COUNT(*) AS flotteurs
    FROM flotteurs f
    WHERE {where_sql}
        AND NULLIF(TRIM(f.pavillon),'') IS NOT NULL
    GROUP BY 1
    ORDER BY flotteurs DESC
    LIMIT 15;
    """
    return pd.read_sql(q, _engine, params=params)
