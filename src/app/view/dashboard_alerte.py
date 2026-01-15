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

st.set_page_config(page_title="Dashboard - Grass Squad", page_icon="📊", layout="wide")

# =========================
# INIT STATE
# =========================
if "action" not in st.session_state:
    st.session_state.action = "dashboard"


if st.button("⬅️ Retour au dashboard"):
        st.session_state.action = 'dashboard'
        st.rerun()

# =========================
# ROUTE : VIEW ALERTE
# =========================
if st.session_state.action == "alerte":
    try:
        from src.app.view.dashboard_alerte import render
        render(engine)
    except Exception as e:
        st.error(f"❌ Erreur dans la view Alerte : {e}")
        st.exception(e)

    st.stop()  # empêche d'afficher le dashboard en dessous


# =========================
# ROUTE : DATE SAISONNALITE
# =========================
if st.session_state.action == "date":
    try:
        from src.app.view.dashboard_date_saisonnalite import render
        render(engine)
    except Exception as e:
        st.error(f"❌ Erreur dans la view Date Saisonnalite : {e}")
        st.exception(e)

    st.stop()


# =========================
# ROUTE : ZONE GEOGRAPHIQUE
# =========================
if st.session_state.action == "zone":
    try:
        from src.app.view.dashboard_zone_geo import render
        render(engine)
    except Exception as e:
        st.error(f"❌ Erreur dans la view Zone géographique : {e}")
        st.exception(e)

    st.stop()


# =========================
# ROUTE : FLOTTEURS
# =========================
if st.session_state.action == "flotteurs":
    try:
        from src.app.view.dashboard_flotteurs import render
        render(engine)
    except Exception as e:
        st.error(f"❌ Erreur dans la view Flotteurs : {e}")
        st.exception(e)

    st.stop()


# =========================
# ROUTE : METEO
# =========================
if st.session_state.action == "meteo":
    try:
        from src.app.view.dashboard_meteo import render
        render(engine)
    except Exception as e:
        st.error(f"❌ Erreur dans la view Meteo : {e}")
        st.exception(e)

    st.stop()


# =========================
# ROUTE : RESULTATS HUMAINS
# =========================
if st.session_state.action == "resultats":
    try:
        from src.app.view.dashboard_resultats_humains import render
        render(engine)
    except Exception as e:
        st.error(f"❌ Erreur dans la view Resultats humains  : {e}")
        st.exception(e)

    st.stop()


# =========================
# DASHBOARD NORMAL
# =========================
st.title("📊 Dashboard Opérationnel")

try:
    db_info = pd.read_sql("SELECT current_database(), inet_server_addr(), inet_server_port();", engine)
    st.success(f"✅ Connecté à la base : {db_info['current_database'][0]}")

    st.subheader("📈 Indicateurs Clés de Performance (KPIs)")

    query_stats = """
    SELECT 
        SUM(nombre_personnes_secourues) as total_secourus,
        SUM(nombre_personnes_tous_deces) as total_deces,
        SUM(nombre_personnes_impliquees) as total_impliques,
        COUNT(DISTINCT operation_id) as total_operations
    FROM operations_stats
    """
    df_stats = pd.read_sql(query_stats, engine)

    if not df_stats.empty:
        col1, col2, col3, col4 = st.columns(4)

        total_ops = df_stats["total_operations"].iloc[0] or 0
        total_saved = df_stats["total_secourus"].iloc[0] or 0
        total_involved = df_stats["total_impliques"].iloc[0] or 0

        success_rate = (total_saved / total_involved) * 100 if total_involved > 0 else 0

        col1.metric("🚢 Total Opérations", f"{int(total_ops):,}")
        col2.metric("👥 Personnes Impliquées", f"{int(total_involved):,}")
        col3.metric("✅ Personnes Secourues", f"{int(total_saved):,}")
        col4.metric("📊 Taux de Réussite", f"{success_rate:.2f}%")
    else:
        st.info("Aucune donnée statistique disponible.")

    st.subheader("🗺️ Carte des Opérations")

    query_map = """
    SELECT operation_id, latitude, longitude, evenement 
    FROM operations 
    WHERE latitude IS NOT NULL AND longitude IS NOT NULL
    LIMIT 1000
    """
    df_map = pd.read_sql(query_map, engine)

    if not df_map.empty:
        st.map(df_map)
    else:
        st.info("Aucune donnée GPS disponible pour la carte.")

    st.subheader("🧭 Explorer par dimensions")

    colA, colB, colC = st.columns(3)

    with colA:
        if st.button("📅 Date & saisonnalité", use_container_width=True):
            st.session_state.action = "date"
            st.rerun()

        if st.button("🚨 Alerte (déclencheurs)", use_container_width=True):
            st.session_state.action = "alerte"
            st.rerun()

    with colB:
        if st.button("🗺️ Zone géographique", use_container_width=True):
            st.session_state.action = "zone"
            st.rerun()

        if st.button("🌦️ Météo & conditions", use_container_width=True):
            st.session_state.action = "meteo"
            st.rerun()

    with colC:
        if st.button("🚤 Flotteurs (matériel)", use_container_width=True):
            st.session_state.action = "flotteurs"
            st.rerun()

        if st.button("👤 Résultats humains", use_container_width=True):
            st.session_state.action = "resultats"
            st.rerun()

except Exception as e:
    st.error(f"❌ Erreur lors du chargement du dashboard : {e}")
    st.exception(e)
