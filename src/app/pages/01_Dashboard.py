import streamlit as st
import pandas as pd
import sys
import os

# Add src to python path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from db.database import get_db_connection

st.set_page_config(page_title="Dashboard - Grass Squad", page_icon="📊", layout="wide")

st.title("📊 Operational Dashboard")

try:
    conn = get_db_connection()
    
    db_info = pd.read_sql("SELECT current_database(), inet_server_addr(), inet_server_port();", conn)
    st.warning(f"Connecté à la base : {db_info['current_database'][0]} sur le serveur IP : {db_info['inet_server_addr'][0]}")
    # --------------------------
    # KPIs
    # --------------------------
    st.subheader("Key Performance Indicators (KPIs)")
    
    # We aggregate data from operations_stats for people statistics
    query_stats = """
    SELECT 
        SUM(nombre_personnes_secourues) as total_secourus,
        SUM(nombre_personnes_tous_deces) as total_deces,
        SUM(nombre_personnes_impliquees) as total_impliques,
        COUNT(DISTINCT operation_id) as total_operations
    FROM operations_stats
    """
    
    df_stats = pd.read_sql(query_stats, conn)
    
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
        
        col1.metric("Total Operations", f"{total_ops:,}")
        col2.metric("Total People Involved", f"{total_involved:,}")
        col3.metric("Total Saved", f"{total_saved:,}")
        col4.metric("Success Rate", f"{success_rate:.2f}%")
        
    else:
        st.info("No stats data available.")

    # --------------------------
    # Map
    # --------------------------
    st.subheader("Operational Map")
    
    # Get coordinates for map
    query_map = """
    SELECT operation_id, latitude, longitude, evenement 
    FROM operations 
    WHERE latitude IS NOT NULL AND longitude IS NOT NULL
    LIMIT 1000
    """
    df_map = pd.read_sql(query_map, conn)
    
    if not df_map.empty:
        st.map(df_map)
    else:
        st.info("No GPS data available for map.")
        
    conn.close()

except Exception as e:
    st.error(f"Error loading dashboard: {e}")
