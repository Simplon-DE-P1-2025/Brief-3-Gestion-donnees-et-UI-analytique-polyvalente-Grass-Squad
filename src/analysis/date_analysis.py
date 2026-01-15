# -*- coding: utf-8 -*-
"""
Fonctions d'analyse temporelle (dates, saisonnalité)
Optimisé avec cache Streamlit pour améliorer les performances
"""

import pandas as pd
import streamlit as st
from sqlalchemy import Engine


@st.cache_data(ttl=300)
def get_global_kpis(_engine: Engine, where_sql: str = "1=1", params: dict = None) -> pd.Series:
    """
    Récupère les KPIs globaux pour l'analyse temporelle
    
    Args:
        engine: Connexion à la base de données
        where_sql: Clause WHERE SQL (default "1=1")
        params: Paramètres pour la requête SQL
    
    Returns:
        pd.Series: KPIs avec operations, personnes_impliquees, personnes_secourues, 
                   personnes_decedees, impliquees_par_operation
    """
    if params is None:
        params = {}
    
    query = f"""
    SELECT
        COUNT(DISTINCT os.operation_id) AS operations,
        COALESCE(SUM(os.nombre_personnes_impliquees),0) AS personnes_impliquees,
        COALESCE(SUM(os.nombre_personnes_secourues),0) AS personnes_secourues,
        COALESCE(SUM(os.nombre_personnes_decedees),0) AS personnes_decedees,
        ROUND(
            COALESCE(SUM(os.nombre_personnes_impliquees),0)::numeric
            / NULLIF(COUNT(DISTINCT os.operation_id),0),
            2
        ) AS impliquees_par_operation
    FROM operations_stats os
    WHERE {where_sql};
    """
    df = pd.read_sql(query, _engine, params=params)
    return df.iloc[0] if not df.empty else pd.Series()


@st.cache_data(ttl=300)
def get_day_of_week_analysis(_engine: Engine, where_sql: str = "1=1", params: dict = None) -> pd.DataFrame:
    """
    Analyse de l'activité par jour de la semaine
    
    Args:
        _engine: Connexion à la base de données
        where_sql: Clause WHERE SQL (default "1=1")
        params: Paramètres pour la requête SQL
    
    Returns:
        pd.DataFrame: Colonnes jour_semaine, ordre, operations, personnes_impliquees, 
                      impliquees_par_operation
    """
    if params is None:
        params = {}
    
    query = f"""
    SELECT
        CASE EXTRACT(DOW FROM os.date::date)
            WHEN 0 THEN 'Dimanche'
            WHEN 1 THEN 'Lundi'
            WHEN 2 THEN 'Mardi'
            WHEN 3 THEN 'Mercredi'
            WHEN 4 THEN 'Jeudi'
            WHEN 5 THEN 'Vendredi'
            WHEN 6 THEN 'Samedi'
        END AS jour_semaine,
        EXTRACT(DOW FROM os.date::date)::int AS ordre,
        COUNT(DISTINCT os.operation_id) AS operations,
        COALESCE(SUM(os.nombre_personnes_impliquees),0) AS personnes_impliquees,
        ROUND(
            COALESCE(SUM(os.nombre_personnes_impliquees),0)::numeric
            / NULLIF(COUNT(DISTINCT os.operation_id),0),
            2
        ) AS impliquees_par_operation
    FROM operations_stats os
    WHERE {where_sql}
        AND os.date IS NOT NULL
    GROUP BY 1, 2
    ORDER BY ordre;
    """
    return pd.read_sql(query, _engine, params=params)


@st.cache_data(ttl=300)
def get_vacation_summer_analysis(_engine: Engine, where_sql: str = "1=1", params: dict = None) -> pd.DataFrame:
    """
    Analyse croisée des périodes de vacances et d'été
    
    Args:
        _engine: Connexion à la base de données
        where_sql: Clause WHERE SQL (default "1=1")
        params: Paramètres pour la requête SQL
    
    Returns:
        pd.DataFrame: Colonnes est_vacances, est_ete, operations, personnes_impliquees, 
                      impliquees_par_operation
    """
    if params is None:
        params = {}
    
    query = f"""
    WITH base AS (
        SELECT
            os.operation_id,
            COALESCE(os.nombre_personnes_impliquees,0) AS impliquees,
            (os.est_vacances_scolaires = TRUE) AS est_vacances,
            (os.mois IN (7,8)) AS est_ete
        FROM operations_stats os
        WHERE {where_sql}
    )
    SELECT
        est_vacances,
        est_ete,
        COUNT(DISTINCT operation_id) AS operations,
        COALESCE(SUM(impliquees),0) AS personnes_impliquees,
        ROUND(COALESCE(SUM(impliquees),0)::numeric / NULLIF(COUNT(DISTINCT operation_id),0), 2) AS impliquees_par_operation
    FROM base
    GROUP BY est_vacances, est_ete
    ORDER BY est_vacances, est_ete;
    """
    return pd.read_sql(query, _engine, params=params)
