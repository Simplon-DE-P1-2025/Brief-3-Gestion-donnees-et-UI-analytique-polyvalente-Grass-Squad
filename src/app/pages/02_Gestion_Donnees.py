import streamlit as st
import pandas as pd
import sys
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(PROJECT_ROOT))

from src.database.load_database import get_db_connection

from crud.operations import save_changes

st.set_page_config(page_title="Gestion Données - Grass Squad", page_icon="📝", layout="wide")

st.title("📝 Gestion des Opérations Humans (CRUD)")

st.warning("⚠️ Attention : Les modifications sont appliquées directement en Base de Données et auditées.")

# Check initialization
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'original_df' not in st.session_state:
    st.session_state.original_df = None

# Load Data Button
with st.sidebar:
    st.header("Chargement Données")
    limit = st.select_slider("Nombre de lignes à charger", options=[10, 50, 100, 500, 1000], value=50)
    reload_btn = st.button("Charger / Rafraîchir")

def load_data():
    conn = get_db_connection()
    # We load bronze_operations or maybe bronze_resultats_humain. 
    # User mentioned "CRUD (Create, Read, Update, Delete) ... Using st.data_editor"
    # Let's Edit bronze_resultats_humain as it's smaller/more meaningful for 'Sauvetages' maybe?
    # Or bronze_operations (main table).
    # Let's allow editing bronze_operations for now, but limit columns to manageable set?
    # Or just load all.
    
    query = f"SELECT * FROM operations LIMIT {limit}"
    df = pd.read_sql(query, conn)
    conn.close()
    
    # Set operation_id as index for tracking
    if 'operation_id' in df.columns:
        df.set_index('operation_id', inplace=True)
        
    st.session_state.original_df = df
    st.session_state.data_loaded = True

if reload_btn or not st.session_state.data_loaded:
    with st.spinner("Chargement des données..."):
        load_data()
        st.success("Données chargées!")

if st.session_state.data_loaded and st.session_state.original_df is not None:
    original = st.session_state.original_df
    
    # Editor
    st.subheader("Éditeur de Données")
    edited_df = st.data_editor(
        original,
        num_rows="dynamic",
        key="editor"
    )
    
    # Save Button
    if st.button("💾 Sauvegarder les modifications"):
        with st.spinner("Enregistrement en cours..."):
            success, message = save_changes(original, edited_df, table_name="operations", pk_col="operation_id")
            
            if success:
                st.success(message)
                # Update session state to reflect saved state
                st.session_state.original_df = edited_df.copy()
                st.balloons()
            else:
                st.error(f"Erreur lors de la sauvegarde : {message}")
