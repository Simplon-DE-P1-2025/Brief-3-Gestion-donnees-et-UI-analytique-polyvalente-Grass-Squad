"""
Vue pour la suppression d'une opération

Ce module contient l'interface de confirmation et de suppression
d'une opération avec toutes ses données associées.
"""

import streamlit as st
import pandas as pd
import time
from src.database.load_database import get_db_connection, engine


def delete_operation(operation_id):
    """Affiche l'interface de confirmation et supprime une opération"""
    st.subheader(f"🗑️ Supprimer l'Opération #{operation_id}")
    
    if st.button("⬅️ Annuler et retourner à la liste"):
        st.session_state.action = 'list'
        st.rerun()
    
    st.warning("⚠️ **Attention** : Cette action est irréversible et supprimera toutes les données associées !")
    
    try:
        query_op = f"SELECT * FROM operations WHERE operation_id = {operation_id}"
        df_op = pd.read_sql(query_op, engine)
        
        st.info("📄 **Aperçu de l'opération à supprimer :**")
        st.dataframe(df_op, use_container_width=True, hide_index=True)
        
        # Compter les données liées
        query_flot = f"SELECT COUNT(*) as nb FROM flotteurs WHERE operation_id = {operation_id}"
        nb_flot = pd.read_sql(query_flot, engine)['nb'].iloc[0]
        
        query_hum = f"SELECT COUNT(*) as nb FROM resultats_humain WHERE operation_id = {operation_id}"
        nb_hum = pd.read_sql(query_hum, engine)['nb'].iloc[0]
        
        query_stats = f"SELECT COUNT(*) as nb FROM operations_stats WHERE operation_id = {operation_id}"
        nb_stats = pd.read_sql(query_stats, engine)['nb'].iloc[0]
        
        st.warning(f"""
        **Cette opération contient :**
        - {nb_flot} flotteur(s)
        - {nb_hum} résultat(s) humain(s)
        - {nb_stats} statistique(s)
        
        **Toutes ces données seront supprimées de manière définitive.**
        """)
        
        confirm = st.checkbox("✅ Je confirme vouloir supprimer cette opération et toutes ses données")
        
        if confirm:
            if st.button("🗑️ SUPPRIMER DÉFINITIVEMENT", type="primary"):
                try:
                    conn = get_db_connection()
                    cur = conn.cursor()
                    
                    cur.execute(f"DELETE FROM operations_stats WHERE operation_id = {operation_id}")
                    cur.execute(f"DELETE FROM resultats_humain WHERE operation_id = {operation_id}")
                    cur.execute(f"DELETE FROM flotteurs WHERE operation_id = {operation_id}")
                    cur.execute(f"DELETE FROM operations WHERE operation_id = {operation_id}")
                    
                    conn.commit()
                    cur.close()
                    conn.close()
                    
                    st.success(f"✅ Opération #{operation_id} supprimée avec succès !")
                    st.balloons()
                    
                    time.sleep(2)
                    
                    st.session_state.action = 'list'
                    st.session_state.selected_operation_id = None
                    st.rerun()
                
                except Exception as e:
                    st.error(f"❌ Erreur lors de la suppression : {e}")
                    st.exception(e)
    
    except Exception as e:
        st.error(f"❌ Erreur : {e}")
        st.exception(e)
