import streamlit as st
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(PROJECT_ROOT))

from src.app.utils.session_state import init_session_state
from src.app.utils.data_loader import get_stats_totals, get_map_data, get_db_info

st.set_page_config(page_title="Dashboard - Grass Squad", page_icon="📊", layout="wide")

init_session_state()
st.session_state.current_page = 'dashboard'

st.title("📊 Dashboard Opérationnel")

try:
    db_info = get_db_info()
    st.success(f"✅ Connecté à la base : {db_info['current_database'][0]}")
    
    st.subheader("📈 Indicateurs Clés de Performance (KPIs)")
    
    df_stats = get_stats_totals()
    
    if not df_stats.empty:
        col1, col2, col3, col4 = st.columns(4)
        
        total_ops = df_stats['total_operations'].iloc[0] or 0
        total_saved = df_stats['total_secourus'].iloc[0] or 0
        total_involved = df_stats['total_impliques'].iloc[0] or 0
        
        success_rate = 0
        if total_involved > 0:
            success_rate = (total_saved / total_involved) * 100
        
        col1.metric("🚢 Total Opérations", f"{total_ops:,}")
        col2.metric("👥 Personnes Impliquées", f"{total_involved:,}")
        col3.metric("✅ Personnes Secourues", f"{total_saved:,}")
        col4.metric("📊 Taux de Réussite", f"{success_rate:.2f}%")
    else:
        st.info("Aucune donnée statistique disponible.")

    st.subheader("🗺️ Carte des Opérations")
    
    df_map = get_map_data(1000)
    
    if not df_map.empty:
        st.map(df_map)
    else:
        st.info("Aucune donnée GPS disponible pour la carte.")

except Exception as e:
    st.error(f"❌ Erreur lors du chargement du dashboard : {e}")

