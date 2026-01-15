import streamlit as st
import pandas as pd
import sys
import json
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(PROJECT_ROOT))

from src.app.utils.session_state import init_session_state
from src.crud.audit_crud import get_audit_logs

st.set_page_config(page_title="Audit - Grass Squad", page_icon="🛡️", layout="wide")

init_session_state()
st.session_state.current_page = 'audit'

st.title("🛡️ Historique des Transactions (Audit)")

st.markdown("""
Cette page affiche l'**historique complet des transactions** effectuées sur la base de données.
Chaque opération (INSERT, UPDATE, DELETE) est enregistrée automatiquement dans la table `audit_log`.
""")

st.divider()

# Filtres
st.subheader("🔍 Filtres de Recherche")
col1, col2, col3, col4 = st.columns(4)

with col1:
    limit = st.selectbox("Nombre de lignes", [100, 250, 500, 1000, 2000], index=1)

with col2:
    table_filter = st.selectbox(
        "Table",
        ["Toutes", "operations", "flotteurs", "resultats_humain", "operations_stats", "reference_lists"]
    )

with col3:
    action_filter = st.selectbox(
        "Action",
        ["Toutes", "INSERT", "UPDATE", "DELETE", "VIEW"]
    )

with col4:
    record_id_filter = st.text_input("ID enregistrement", placeholder="Ex: 123")

# Recherche avancée
col_s1, col_s2, col_s3 = st.columns([2, 2, 1])
with col_s1:
    search_user = st.text_input("🔍 Rechercher utilisateur", placeholder="Ex: system")
with col_s2:
    search_details = st.text_input("🔍 Rechercher dans détails", placeholder="Ex: opération")
with col_s3:
    st.write("")
    st.write("")
    if st.button("🔄 Rafraîchir", use_container_width=True, type="primary"):
        st.rerun()

st.divider()

# Récupération et affichage des données
try:
    # Préparer les filtres
    table_name = None if table_filter == "Toutes" else table_filter
    action = None if action_filter == "Toutes" else action_filter
    record_id = record_id_filter if record_id_filter else None
    
    # Récupérer les logs
    logs = get_audit_logs(
        limit=limit,
        table_name=table_name,
        action=action,
        record_id=record_id
    )
    
    if logs:
        df_audit = pd.DataFrame(logs)
        
        # Appliquer les filtres de recherche additionnels
        if search_user:
            df_audit = df_audit[df_audit['user_name'].str.contains(search_user, case=False, na=False)]
        
        if search_details:
            df_audit = df_audit[df_audit['details'].astype(str).str.contains(search_details, case=False, na=False)]
        
        # Fonction pour extraire uniquement les champs modifiés
        def get_changed_fields_only(row):
            """Extrait uniquement les champs qui ont changé entre old_values et new_values"""
            try:
                old_vals = json.loads(row['old_values']) if row['old_values'] and isinstance(row['old_values'], str) else row['old_values']
                new_vals = json.loads(row['new_values']) if row['new_values'] and isinstance(row['new_values'], str) else row['new_values']
                
                if not old_vals or not new_vals:
                    return row['old_values'], row['new_values']
                
                # Identifier les champs modifiés
                changed_old = {}
                changed_new = {}
                
                # Comparer les clés communes
                if isinstance(old_vals, dict) and isinstance(new_vals, dict):
                    all_keys = set(old_vals.keys()) | set(new_vals.keys())
                    for key in all_keys:
                        old_val = old_vals.get(key)
                        new_val = new_vals.get(key)
                        if old_val != new_val:
                            changed_old[key] = old_val
                            changed_new[key] = new_val
                    
                    # Retourner en JSON formaté
                    return json.dumps(changed_old, ensure_ascii=False, default=str) if changed_old else None, \
                           json.dumps(changed_new, ensure_ascii=False, default=str) if changed_new else None
                else:
                    return row['old_values'], row['new_values']
                    
            except:
                return row['old_values'], row['new_values']
        
        # Créer des colonnes optimisées pour l'affichage
        df_audit[['old_values_display', 'new_values_display']] = df_audit.apply(
            lambda row: pd.Series(get_changed_fields_only(row)), axis=1
        )
        
        # Affichage du nombre de résultats
        st.markdown(f"### 📊 {len(df_audit)} transaction(s) trouvée(s)")
        
        # Préparer le DataFrame pour l'affichage (avec les colonnes optimisées)
        df_display = df_audit.copy()
        df_display['old_values'] = df_display['old_values_display']
        df_display['new_values'] = df_display['new_values_display']
        
        # Réorganiser les colonnes dans l'ordre souhaité
        columns_order = ['id', 'created_at', 'table_name', 'record_id', 'action', 'user_name', 'sql_query', 'old_values', 'new_values', 'details']
        
        # Affichage de la table
        st.dataframe(
            df_display[columns_order],
            use_container_width=True,
            height=600,
            column_config={
                "id": st.column_config.NumberColumn("ID", width="small", help="ID unique de l'enregistrement"),
                "created_at": st.column_config.DatetimeColumn(
                    "Date/Heure", 
                    format="DD/MM/YYYY HH:mm:ss", 
                    width="medium",
                    help="Date et heure de la transaction"
                ),
                "table_name": st.column_config.TextColumn("Table", width="medium", help="Nom de la table concernée"),
                "record_id": st.column_config.TextColumn("Record ID", width="medium", help="ID de l'enregistrement modifié"),
                "action": st.column_config.TextColumn("Action", width="small", help="Type d'action: INSERT, UPDATE, DELETE, VIEW"),
                "user_name": st.column_config.TextColumn("Utilisateur", width="small", help="Utilisateur ayant effectué l'action"),
                "sql_query": st.column_config.TextColumn("Requête SQL", width="large", help="Requête SQL exécutée"),
                "old_values": st.column_config.TextColumn("Anciennes valeurs (modifiées)", width="large", help="Seulement les champs modifiés (JSON)"),
                "new_values": st.column_config.TextColumn("Nouvelles valeurs (modifiées)", width="large", help="Seulement les champs modifiés (JSON)"),
                "details": st.column_config.TextColumn("Détails", width="large", help="Description de l'action"),
            }
        )
        
        # Section d'export
        st.divider()
        st.markdown("### 💾 Exporter les données")
        col_d1, col_d2, col_d3 = st.columns([2, 1, 1])
        
        with col_d1:
            st.info(f"📥 Vous pouvez exporter les {len(df_audit)} transaction(s) affichée(s)")
        
        with col_d2:
            csv = df_audit.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Télécharger CSV",
                data=csv,
                file_name=f"audit_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col_d3:
            json_data = df_audit.to_json(orient='records', indent=2)
            st.download_button(
                label="📥 Télécharger JSON",
                data=json_data,
                file_name=f"audit_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
        
        # Affichage détaillé d'un enregistrement
        with st.expander("🔍 Voir les détails complets d'une transaction"):
            selected_id = st.number_input("Entrez l'ID de la transaction", min_value=1, step=1, key="selected_audit_id")
            
            if st.button("Afficher les détails", key="show_details_btn"):
                selected_row = df_audit[df_audit['id'] == selected_id]
                
                if not selected_row.empty:
                    row = selected_row.iloc[0]
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**📋 Informations générales**")
                        st.info(f"**ID:** {row['id']}")
                        st.info(f"**Table:** {row['table_name']}")
                        st.info(f"**Action:** {row['action']}")
                        st.info(f"**Record ID:** {row['record_id']}")
                        st.info(f"**Utilisateur:** {row['user_name']}")
                        st.info(f"**Date/Heure:** {row['created_at']}")
                    
                    with col2:
                        st.markdown("**📝 Détails**")
                        st.text_area("Description", row['details'], height=200, disabled=True, key="details_area")
                    
                    # Affichage de la requête SQL
                    if 'sql_query' in row and row['sql_query']:
                        st.markdown("**💻 Requête SQL exécutée**")
                        st.code(row['sql_query'], language="sql")
                    
                    # Comparer et afficher uniquement les champs modifiés
                    st.markdown("---")
                    
                    try:
                        old_vals = json.loads(row['old_values']) if row['old_values'] and isinstance(row['old_values'], str) else row['old_values']
                        new_vals = json.loads(row['new_values']) if row['new_values'] and isinstance(row['new_values'], str) else row['new_values']
                        
                        if old_vals and new_vals and isinstance(old_vals, dict) and isinstance(new_vals, dict):
                            # Identifier les champs modifiés
                            changed_fields = {}
                            all_keys = set(old_vals.keys()) | set(new_vals.keys())
                            
                            for key in all_keys:
                                old_val = old_vals.get(key)
                                new_val = new_vals.get(key)
                                if old_val != new_val:
                                    changed_fields[key] = {
                                        'old': old_val,
                                        'new': new_val
                                    }
                            
                            if changed_fields:
                                st.markdown(f"**🔄 Champs modifiés ({len(changed_fields)})**")
                                
                                # Afficher sous forme de tableau comparatif
                                comparison_data = []
                                for field, values in changed_fields.items():
                                    comparison_data.append({
                                        'Champ': field,
                                        'Ancienne valeur': str(values['old']) if values['old'] is not None else 'NULL',
                                        'Nouvelle valeur': str(values['new']) if values['new'] is not None else 'NULL'
                                    })
                                
                                df_comparison = pd.DataFrame(comparison_data)
                                st.dataframe(df_comparison, use_container_width=True, hide_index=True)
                            else:
                                st.info("✅ Aucun changement détecté entre les anciennes et nouvelles valeurs")
                        
                        else:
                            # Affichage classique si pas de comparaison possible
                            col_old, col_new = st.columns(2)
                            
                            with col_old:
                                if row['old_values']:
                                    st.markdown("**🔙 Anciennes valeurs**")
                                    try:
                                        old_vals_display = json.loads(row['old_values']) if isinstance(row['old_values'], str) else row['old_values']
                                        st.json(old_vals_display)
                                    except:
                                        st.code(row['old_values'])
                            
                            with col_new:
                                if row['new_values']:
                                    st.markdown("**✨ Nouvelles valeurs**")
                                    try:
                                        new_vals_display = json.loads(row['new_values']) if isinstance(row['new_values'], str) else row['new_values']
                                        st.json(new_vals_display)
                                    except:
                                        st.code(row['new_values'])
                    
                    except Exception as e:
                        st.error(f"Erreur lors de la comparaison: {e}")
                        
                        if row['new_values']:
                            st.markdown("**✨ Nouvelles valeurs**")
                            st.code(row['new_values'])
                else:
                    st.warning(f"❌ Aucune transaction trouvée avec l'ID {selected_id}")
    
    else:
        st.info("📭 Aucune transaction trouvée avec ces filtres")
        st.markdown("""
        **💡 Conseils :**
        - Vérifiez que la table `audit_log` contient des données
        - Essayez de modifier les filtres de recherche
        - Effectuez des opérations (création, modification, suppression) pour générer des logs
        """)

except Exception as e:
    st.error(f"❌ Erreur lors de la récupération des transactions : {e}")
    st.exception(e)
    st.markdown("""
    **🔧 Solution possible :**
    - Vérifiez que la table `audit_log` existe dans la base de données
    - Exécutez le script : `python3 recreate_audit_table.py`
    """)
