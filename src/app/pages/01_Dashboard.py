import streamlit as st
import pandas as pd
import sys
import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(PROJECT_ROOT))

from src.database.load_database import engine

st.set_page_config(page_title="Dashboard - Grass Squad", page_icon="📊", layout="wide")

st.title("📊 Dashboard Opérationnel")

try:
    db_info = pd.read_sql("SELECT current_database(), inet_server_addr(), inet_server_port();", engine)
    st.success(f"✅ Connecté à la base : {db_info['current_database'][0]}")
    
    # --------------------------
    # KPIs
    # --------------------------
    st.subheader("📈 Indicateurs Clés de Performance (KPIs)")
    
    # We aggregate data from operations_stats for people statistics
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
        
        # Handle Potential None values if table is empty or has nulls
        total_ops = df_stats['total_operations'].iloc[0] or 0
        total_saved = df_stats['total_secourus'].iloc[0] or 0
        total_involved = df_stats['total_impliques'].iloc[0] or 0
        
        # Calculate success rate (saved / involved) -- simplified logic
        success_rate = 0
        if total_involved > 0:
            success_rate = (total_saved / total_involved) * 100
        
        col1.metric("🚢 Total Opérations", f"{total_ops:,}")
        col2.metric("👥 Personnes Impliquées", f"{total_involved:,}")
        col3.metric("✅ Personnes Secourues", f"{total_saved:,}")
        col4.metric("📊 Taux de Réussite", f"{success_rate:.2f}%")
        
    else:
        st.info("Aucune donnée statistique disponible.")

    # --------------------------
    # Carte
    # --------------------------
    st.subheader("🗺️ Carte des Opérations")
    
    # Get coordinates for map
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

except Exception as e:
    st.error(f"❌ Erreur lors du chargement du dashboard : {e}")
