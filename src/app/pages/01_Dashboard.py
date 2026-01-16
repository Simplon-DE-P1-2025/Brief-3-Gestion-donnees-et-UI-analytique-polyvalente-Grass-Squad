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
from src.analysis.dashboard_analytics import get_global_kpis, get_operations_map_data, get_database_info

st.set_page_config(page_title="Dashboard - Grass Squad", page_icon="📊", layout="wide")

# =========================
# INIT STATE
# =========================
if "action" not in st.session_state:
    st.session_state.action = "dashboard"


if st.button("⬅️ Retour au dashboard", key="btn_back_to_dashboard_main"):
        st.session_state.action = 'dashboard'
        st.rerun()

# =========================
# ROUTE : ALERTE
# =========================
if st.session_state.action == "alerte":
    try:
        from src.app.views.dashboard_alerte import render
        render(engine)
    except Exception as e:
        st.error(f"❌ Erreur dans la view Alerte : {e}")
        st.exception(e)

    st.stop()

# =========================
# ROUTE : DATE SAISONNALITE
# =========================
if st.session_state.action == "date":
    try:
        from src.app.views.dashboard_date_saisonnalite import render
        render(engine)
    except Exception as e:
        st.error(f"❌ Erreur dans la view Date Saisonnalite : {e}")
        st.exception(e)

    st.stop()

# =========================
# ROUTE : ZONE GEO
# =========================
if st.session_state.action == "zone":
    try:
        from src.app.views.dashboard_zone_geo import render
        render(engine)
    except Exception as e:
        st.error(f"❌ Erreur dans la view Zone Geo : {e}")
        st.exception(e)

    st.stop()

# =========================
# ROUTE : METEO
# =========================
if st.session_state.action == "meteo":
    try:
        from src.app.views.dashboard_meteo import render
        render(engine)
    except Exception as e:
        st.error(f"❌ Erreur dans la view Meteo : {e}")
        st.exception(e)

    st.stop()

# =========================
# ROUTE : FLOTTEURS
# =========================
if st.session_state.action == "flotteurs":
    try:
        from src.app.views.dashboard_flotteurs import render
        render(engine)
    except Exception as e:
        st.error(f"❌ Erreur dans la view Flotteurs : {e}")
        st.exception(e)

    st.stop()

# =========================
# ROUTE : RESULTATS HUMAINS
# =========================
if st.session_state.action == "resultats":
    try:
        from src.app.views.dashboard_resultats_humains import render
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
    db_info = get_database_info(engine)
    st.success(f"✅ Connecté à la base : {db_info['current_database'][0]}")

    st.subheader("📈 Indicateurs Clés de Performance (KPIs)")

    df_stats = get_global_kpis(engine)

    if df_stats is not None and not df_stats.empty:
        col1, col2, col3, col4 = st.columns(4)

        total_ops = df_stats["total_operations"] or 0
        total_saved = df_stats["total_secourus"] or 0
        total_involved = df_stats["total_impliques"] or 0

        success_rate = (total_saved / total_involved) * 100 if total_involved > 0 else 0

        col1.metric("🚢 Total Opérations", f"{int(total_ops):,}")
        col2.metric("👥 Personnes Impliquées", f"{int(total_involved):,}")
        col3.metric("✅ Personnes Secourues", f"{int(total_saved):,}")
        col4.metric("📊 Taux de Réussite", f"{success_rate:.2f}%")
    else:
        st.info("Aucune donnée statistique disponible.")

    st.subheader("🗺️ Carte des Opérations")

    df_map = get_operations_map_data(engine, limit=1000)

    if not df_map.empty:
        st.map(df_map)
    else:
        st.info("Aucune donnée GPS disponible pour la carte.")

    st.subheader("🧭 Explorer par dimensions")

    colA, colB, colC = st.columns(3)

    with colA:
        if st.button("📅 Date & saisonnalité", width="stretch"):
            st.session_state.action = "date"
            st.rerun()

        if st.button("🚨 Alerte (déclencheurs)", width="stretch"):
            st.session_state.action = "alerte"
            st.rerun()

    with colB:
        if st.button("🗺️ Zone géographique", width="stretch"):
            st.session_state.action = "zone"
            st.rerun()

        if st.button("🌦️ Météo & conditions", width="stretch"):
            st.session_state.action = "meteo"
            st.rerun()

    with colC:
        if st.button("🚤 Flotteurs (matériel)", width="stretch"):
            st.session_state.action = "flotteurs"
            st.rerun()

        if st.button("👤 Résultats humains", width="stretch"):
            st.session_state.action = "resultats"
            st.rerun()

except Exception as e:
    st.error(f"❌ Erreur lors du chargement du dashboard : {e}")
    st.exception(e)
