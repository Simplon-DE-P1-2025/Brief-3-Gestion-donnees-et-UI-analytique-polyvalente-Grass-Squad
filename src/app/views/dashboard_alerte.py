import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# =========================
# PATH / IMPORTS PROJET
# =========================
PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(PROJECT_ROOT))

from src.database.load_database import engine
from src.analysis.alerte_analysis import (
    get_global_kpi,
    get_top_events,
    get_event_categories,
    get_alert_methods
)


def render(engine):
    """
    Dashboard Alerte & Typologie des événements
    """
    st.title("🚨 Alerte & Typologie — Quels déclencheurs et quelles situations ?")
    st.caption("Objectif : comprendre quels types d'alertes/événements déclenchent le plus d'opérations et de charge humaine.")

    # ----------------------------------
    # Questions métier
    # ----------------------------------
    st.markdown("### ❓ Questions métier")
    st.markdown(
        "- Quels **types d'événements** (evenement, categorie_evenement, moyen_alerte) dominent ?\n"
        "- Lesquels sont associés aux **opérations les plus lourdes** (personnes impliquées) ?\n"
        "- Y a-t-il des déclencheurs particulièrement **critiques** (taux de décès élevé) ?"
    )
    st.divider()
    # ----------------------------------
    # Filtres (si besoin)
    # ----------------------------------
    where_sql = "1=1"
    params = {}

    # ======================================================
    # 1) KPI globaux
    # ======================================================
    st.subheader("📌 Indicateurs clés")
    
    k = get_global_kpi(engine)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("🚢 Opérations totales", f"{int(k['total_operations'] or 0):,}")
    col2.metric("👥 Personnes impliquées", f"{int(k['total_impliques'] or 0):,}")
    col3.metric("⚫ Décès", f"{int(k['total_deces'] or 0):,}")
    
    st.divider()

    # ======================================================
    # 2) Typologie d'événements (top 15)
    # ======================================================
    st.subheader("🏷️ Top événements — volume & charge humaine")
    st.caption("Les événements les plus fréquents et leur charge humaine associée")
    
    df_events = get_top_events(engine, limit=15)
    
    if df_events.empty:
        st.info("Aucune donnée d'événement disponible.")
    else:
        left, right = st.columns([2, 1])
        with left:
            st.bar_chart(df_events.set_index("evenement")[["operations", "personnes_impliquees"]])
        with right:
            st.dataframe(df_events, width="stretch")
    
    st.divider()

    # ======================================================
    # 3) Catégories d'événements
    # ======================================================
    st.subheader("📊 Catégories d'événements")
    
    df_cat = get_event_categories(engine)
    
    if df_cat.empty:
        st.info("Aucune catégorie d'événement disponible.")
    else:
        st.bar_chart(df_cat.set_index("categorie")["operations"])
        st.dataframe(df_cat, width="stretch")
    
    st.divider()

    # ======================================================
    # 4) Moyens d'alerte
    # ======================================================
    st.subheader("📡 Moyens d'alerte")
    st.caption("Par quel canal l'alerte est-elle déclenchée ?")
    
    df_moyen = get_alert_methods(engine)
    
    if df_moyen.empty:
        st.info("Aucune donnée sur les moyens d'alerte.")
    else:
        st.bar_chart(df_moyen.set_index("moyen_alerte")["operations"])
        st.dataframe(df_moyen, width="stretch")

    st.markdown("### ✅ Conclusion")
    st.markdown(
        "Ce dashboard identifie **quels types d'événements** et **quels canaux d'alerte** déclenchent le plus d'opérations.\n"
        "Permet de prioriser les formations, équipements et protocoles sur les typologies les plus fréquentes ou critiques."
    )
