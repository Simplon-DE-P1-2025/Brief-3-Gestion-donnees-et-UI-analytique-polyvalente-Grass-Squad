import streamlit as st
import pandas as pd
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(PROJECT_ROOT))

from src.database.load_database import engine
from src.crud.operations_crud import delete_operation
from src.crud.audit_crud import log_action, get_audit_logs
from src.app.utils.session_state import init_session_state
from src.app.views.operations_list import show_operations_grid
from src.app.views.operations_create import create_operation
from src.app.views.operations_edit import edit_operation
from src.app.views.operations_delete import delete_operation as delete_operation_view
from src.app.utils.data_loader import get_reference_list_cached, get_operation_by_id, get_flotteurs_by_operation, get_resultats_humain_by_operation, get_stats_by_operation

st.set_page_config(page_title="Gestion des Opérations", page_icon="🚢", layout="wide")

init_session_state()

# Réinitialiser la liste si on revient de l'extérieur
if st.session_state.current_page != 'operations':
    st.session_state.action = 'list'
    st.session_state.selected_operation_id = None

st.session_state.current_page = 'operations'

st.title("🚢 Gestion des Opérations")


# ========================================
# FONCTION: CONSULTER UNE OPÉRATION
# ========================================
def view_operation(operation_id):
    """Affiche les détails complets d'une opération"""
    st.subheader(f"👁️ Consultation de l'Opération #{operation_id}")
    
    # CSS pour les boutons colorés
    st.markdown("""
    <style>
    div[data-testid="column"]:nth-child(3) button {
        background-color: #28a745 !important;
        color: white !important;
        border: 1px solid #28a745 !important;
    }
    div[data-testid="column"]:nth-child(3) button:hover {
        background-color: #218838 !important;
        border-color: #1e7e34 !important;
    }
    div[data-testid="column"]:nth-child(4) button {
        background-color: #dc3545 !important;
        color: white !important;
        border: 1px solid #dc3545 !important;
    }
    div[data-testid="column"]:nth-child(4) button:hover {
        background-color: #c82333 !important;
        border-color: #bd2130 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Boutons de navigation alignés
    col_btn1, col_btn2, col_btn3, col_btn4 = st.columns([1.5, 4, 1.5, 1.5])
    with col_btn1:
        if st.button("⬅️ Retour à la liste", width="stretch"):
            st.session_state.action = 'list'
            st.rerun()
    with col_btn3:
        if st.button("✏️ Modifier", type="primary", key="btn_modify", width="stretch"):
            st.session_state.action = 'edit'
            st.session_state.selected_operation_id = operation_id
            st.rerun()
    with col_btn4:
        if st.button("🗑️ Supprimer", type="secondary", key="btn_delete", width="stretch"):
            st.session_state.show_delete_confirmation = True
    
    # Modal de confirmation de suppression
    if st.session_state.get('show_delete_confirmation', False):
        st.warning(f"⚠️ **Confirmer la suppression de l'opération #{operation_id}**")
        st.markdown("Cette action est **irréversible** et supprimera également :")
        st.markdown("- Tous les flotteurs associés")
        st.markdown("- Tous les résultats humains associés")
        st.markdown("- Toutes les statistiques associées")
        
        col_confirm1, col_confirm2, col_confirm3 = st.columns([1, 1, 3])
        with col_confirm1:
            if st.button("✅ Confirmer la suppression", type="primary", key="btn_confirm_delete"):
                try:
                    # Enregistrer dans l'audit avant suppression
                    try:
                        log_action(
                            table='operations',
                            action='DELETE',
                            record_id=str(operation_id),
                            user_name=st.session_state.get('user_name', 'system'),
                            details=f"Suppression de l'opération {operation_id}"
                        )
                    except Exception as audit_error:
                        st.warning(f"⚠️ Audit non enregistré: {audit_error}")
                    
                    delete_operation(operation_id)
                    st.success(f"✅ Opération #{operation_id} supprimée avec succès!")
                    st.session_state.show_delete_confirmation = False
                    st.session_state.action = 'list'
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Erreur lors de la suppression : {e}")
        with col_confirm2:
            if st.button("❌ Annuler", key="btn_cancel_delete"):
                st.session_state.show_delete_confirmation = False
                st.rerun()
    
    try:
        df_op = get_operation_by_id(operation_id)
        
        if len(df_op) == 0:
            st.error(f"Opération #{operation_id} introuvable")
            return
        
        log_action(
            table='operations',
            action='VIEW',
            record_id=str(operation_id),
            details=f"Consultation détaillée de l'opération {operation_id}",
            sql_query=f"SELECT * FROM operations WHERE operation_id = {operation_id}"
        )
        
        # Afficher les infos principales
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("CROSS", df_op['cross'].iloc[0])
        col2.metric("Événement", df_op['evenement'].iloc[0] if pd.notna(df_op['evenement'].iloc[0]) else "N/A")
        col3.metric("Département", df_op['departement'].iloc[0] if pd.notna(df_op['departement'].iloc[0]) else "N/A")
        col4.metric("Date", df_op['date_heure_reception_alerte'].iloc[0].strftime('%Y-%m-%d %H:%M'))
        
        # Onglets pour les différentes tables
        tab1, tab2, tab3, tab4 = st.tabs(["🚢 Opération", "⛵ Flotteurs", "👥 Résultats Humains", "📊 Statistiques"])
        
        with tab1:
            st.markdown("### Données complètes de l'opération")
            # Transposer pour affichage vertical
            df_transpose = df_op.T
            df_transpose.columns = ['Valeur']
            st.dataframe(df_transpose, width="stretch")
            
            # Afficher l'historique d'audit pour cette opération
            st.markdown("---")
            st.markdown("### 📝 Historique d'audit de cette opération")
            
            # Récupérer les logs d'audit pour cette opération
            audit_logs = get_audit_logs(
                table_name='operations',
                record_id=str(operation_id)
            )
            
            if audit_logs and len(audit_logs) > 0:
                # Créer un DataFrame pour l'affichage
                audit_data = []
                for log in audit_logs:
                    # log est un dictionnaire avec les colonnes de audit_log
                    audit_data.append({
                        'Date': log['created_at'].strftime('%Y-%m-%d %H:%M:%S') if log.get('created_at') else 'N/A',
                        'Action': log.get('action', ''),
                        'Utilisateur': log.get('user_name', 'system') or 'system',
                        'Détails': log.get('details', ''),
                        'SQL': log.get('sql_query', ''),
                        'Anciennes valeurs': str(log.get('old_values', '')) if log.get('old_values') else '',
                        'Nouvelles valeurs': str(log.get('new_values', '')) if log.get('new_values') else ''
                    })
                
                df_audit = pd.DataFrame(audit_data)
                st.dataframe(df_audit, width="stretch", hide_index=True)
                st.info(f"📊 {len(audit_logs)} action(s) enregistrée(s) dans l'audit")
            else:
                st.info("Aucun historique d'audit disponible pour cette opération")
        
        with tab2:
            df_flotteurs = get_flotteurs_by_operation(operation_id)
            
            if len(df_flotteurs) > 0:
                st.dataframe(df_flotteurs, width="stretch", hide_index=True)
                st.success(f"✅ {len(df_flotteurs)} flotteur(s) trouvé(s)")
            else:
                st.info("Aucun flotteur enregistré pour cette opération")
        
        with tab3:
            df_humain = get_resultats_humain_by_operation(operation_id)
            
            if len(df_humain) > 0:
                st.dataframe(df_humain, width="stretch", hide_index=True)
                st.success(f"✅ {len(df_humain)} résultat(s) trouvé(s)")
            else:
                st.info("Aucun résultat humain enregistré pour cette opération")
        
        with tab4:
            df_stats = get_stats_by_operation(operation_id)
            
            if len(df_stats) > 0:
                col_s1, col_s2, col_s3, col_s4 = st.columns(4)
                col_s1.metric("👥 Impliqués", int(df_stats['nombre_personnes_impliquees'].iloc[0]) if pd.notna(df_stats['nombre_personnes_impliquees'].iloc[0]) else 0)
                col_s2.metric("✅ Secourus", int(df_stats['nombre_personnes_secourues'].iloc[0]) if pd.notna(df_stats['nombre_personnes_secourues'].iloc[0]) else 0)
                col_s3.metric("💔 Décès", int(df_stats['nombre_personnes_tous_deces'].iloc[0]) if pd.notna(df_stats['nombre_personnes_tous_deces'].iloc[0]) else 0)
                col_s4.metric("🚑 Blessés", int(df_stats['nombre_personnes_blessees'].iloc[0]) if pd.notna(df_stats['nombre_personnes_blessees'].iloc[0]) else 0)
                
                st.dataframe(df_stats, width="stretch", hide_index=True)
            else:
                st.info("Aucune statistique enregistrée pour cette opération")
    
    except Exception as e:
        st.error(f"❌ Erreur : {e}")
        st.exception(e)


# ========================================
# ROUTAGE PRINCIPAL
# ========================================
if st.session_state.action == 'list':
    show_operations_grid()

elif st.session_state.action == 'view':
    if st.session_state.selected_operation_id:
        view_operation(st.session_state.selected_operation_id)
    else:
        st.error("❌ Aucune opération sélectionnée")
        st.session_state.action = 'list'
        st.rerun()

elif st.session_state.action == 'create':
    create_operation()

elif st.session_state.action == 'edit':
    if st.session_state.selected_operation_id:
        edit_operation(st.session_state.selected_operation_id)
    else:
        st.error("❌ Aucune opération sélectionnée")
        st.session_state.action = 'list'
        st.rerun()

elif st.session_state.action == 'delete':
    if st.session_state.selected_operation_id:
        delete_operation_view(st.session_state.selected_operation_id)
    else:
        st.error("❌ Aucune opération sélectionnée")
        st.session_state.action = 'list'
        st.rerun()
