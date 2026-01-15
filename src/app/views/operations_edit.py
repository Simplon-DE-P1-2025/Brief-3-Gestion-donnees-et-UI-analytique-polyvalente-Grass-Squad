"""
Vue pour la modification d'une opération existante

Ce module contient le formulaire de modification d'une opération
avec ses données liées (flotteurs, résultats humains, statistiques).
"""

import streamlit as st
import pandas as pd
from src.database.load_database import get_db_connection, engine
from src.crud.operations_crud import update_operation
from src.crud.flotteurs_crud import insert_flotteur
from src.crud.resultat_humain_crud import insert_resultat_humain
from src.crud.operations_stats_crud import update_operations_stats
from src.crud.audit_crud import log_action
from src.app.utils.data_loader import (
    get_operation_by_id,
    get_flotteurs_by_operation,
    get_resultats_humain_by_operation,
    get_stats_by_operation,
    get_reference_list_cached
)




def edit_operation(operation_id):
    """Formulaire de modification d'une opération avec toutes ses données liées"""
    st.subheader(f"✏️ Modifier l'Opération #{operation_id}")
    
    # Afficher le message de succès s'il existe
    if 'edit_success_message' in st.session_state:
        st.success(st.session_state.edit_success_message)
        del st.session_state.edit_success_message
    
    if st.button("⬅️ Retour à la liste"):
        st.session_state.action = 'list'
        st.rerun()
    
    try:
        # Récupérer l'opération avec cache
        df_op = get_operation_by_id(operation_id)
        
        if len(df_op) == 0:
            st.error(f"Opération #{operation_id} introuvable")
            return
        
        # Récupérer les données liées avec cache
        df_flotteurs = get_flotteurs_by_operation(operation_id)
        df_humain = get_resultats_humain_by_operation(operation_id)
        df_stats = get_stats_by_operation(operation_id)
        
        # Onglets pour modifier les différentes sections
        tab1, tab2, tab3, tab4 = st.tabs(["🚢 Opération", "⛵ Flotteurs", "👥 Résultats Humains", "📊 Statistiques"])
        
        with tab1:
            st.markdown("### Modifier les données de l'opération")
            st.info("💡 Modifiez les valeurs directement dans le tableau ci-dessous")
            
            edited_op = st.data_editor(
                df_op, 
                use_container_width=True, 
                num_rows="fixed", 
                key="edit_op",
                column_config={
                    "operation_id": st.column_config.NumberColumn("Operation ID", disabled=True, help="ID non modifiable"),
                }
            )
            
            if st.button("💾 Sauvegarder l'opération", type="primary", key="save_op"):
                try:
                    if edited_op['cross'].isna().any():
                        st.error("❌ Le champ CROSS ne peut pas être vide")
                    else:
                        # Préparer les données modifiées
                        data_to_update = {}
                        for col in edited_op.columns:
                            if col != 'operation_id':
                                value = edited_op[col].iloc[0]
                                # Convertir NaN en None pour la base de données
                                if pd.isna(value):
                                    data_to_update[col] = None
                                else:
                                    data_to_update[col] = value
                        
                        # Utiliser la fonction CRUD qui tracke automatiquement dans l'audit
                        update_operation(operation_id, data_to_update)
                        
                        # Stocker le message dans session_state pour l'afficher après rerun
                        st.session_state.edit_success_message = f"✅ Opération #{operation_id} modifiée avec succès ! La modification a été enregistrée dans l'audit."
                        st.rerun()
                
                except Exception as e:
                    st.error(f"❌ Erreur lors de la modification : {e}")
                    st.exception(e)
        
        with tab2:
            st.markdown("### Modifier les flotteurs")
            st.caption("⚠️ Champs obligatoires : Résultat flotteur*, Type flotteur*, Catégorie flotteur*")
            
            if len(df_flotteurs) > 0:
                st.info(f"📊 {len(df_flotteurs)} flotteur(s) trouvé(s)")
                
                edited_flotteurs = st.data_editor(
                    df_flotteurs, 
                    use_container_width=True, 
                    num_rows="dynamic",
                    key="edit_flotteurs",
                    column_config={
                        "operation_id": st.column_config.NumberColumn("Operation ID", disabled=True),
                        "resultat_flotteur": st.column_config.TextColumn("Résultat flotteur*", required=True, help="Obligatoire"),
                        "type_flotteur": st.column_config.TextColumn("Type flotteur*", required=True, help="Obligatoire"),
                        "categorie_flotteur": st.column_config.TextColumn("Catégorie flotteur*", required=True, help="Obligatoire"),
                    }
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 Sauvegarder les flotteurs", type="primary", key="save_flotteurs"):
                        try:
                            # Vérifier qu'il n'y a pas de champs obligatoires vides
                            invalid_rows = []
                            for idx, row in edited_flotteurs.iterrows():
                                if (pd.isna(row['resultat_flotteur']) or 
                                    pd.isna(row['type_flotteur']) or 
                                    pd.isna(row['categorie_flotteur'])):
                                    invalid_rows.append(idx + 1)
                            
                            if invalid_rows:
                                st.error(f"❌ Les champs obligatoires (Résultat*, Type*, Catégorie*) doivent être remplis pour toutes les lignes. Lignes incomplètes : {', '.join(map(str, invalid_rows))}")
                            else:
                                # Supprimer tous les flotteurs existants (avec audit)
                                conn = get_db_connection()
                                cur = conn.cursor()
                                
                                # Récupérer les flotteurs existants pour l'audit
                                cur.execute("SELECT * FROM flotteurs WHERE operation_id = %s", (operation_id,))
                                old_flotteurs = cur.fetchall()
                                old_columns = [desc[0] for desc in cur.description]
                                
                                # Supprimer avec audit
                                delete_query = f"DELETE FROM flotteurs WHERE operation_id = {operation_id}"
                                cur.execute("DELETE FROM flotteurs WHERE operation_id = %s", (operation_id,))
                                
                                if old_flotteurs:
                                    log_action(
                                        table='flotteurs',
                                        action='DELETE',
                                        record_id=str(operation_id),
                                        old_values={f"flotteur_{i}": dict(zip(old_columns, row)) for i, row in enumerate(old_flotteurs)},
                                        details=f"Suppression de {len(old_flotteurs)} flotteur(s) avant réinsertion - Opération: {operation_id}",
                                        sql_query=delete_query
                                    )
                                
                                conn.commit()
                                cur.close()
                                conn.close()
                                
                                # Réinsérer les flotteurs modifiés (avec audit via insert_flotteur)
                                for idx, row in edited_flotteurs.iterrows():
                                    flotteur_data = {
                                        'operation_id': operation_id,
                                        'numero_ordre': row['numero_ordre'],
                                        'pavillon': row['pavillon'] if pd.notna(row['pavillon']) else None,
                                        'resultat_flotteur': row['resultat_flotteur'],
                                        'type_flotteur': row['type_flotteur'],
                                        'categorie_flotteur': row['categorie_flotteur'],
                                        'numero_immatriculation': row['numero_immatriculation'] if pd.notna(row['numero_immatriculation']) else None
                                    }
                                    insert_flotteur(flotteur_data)
                                
                                st.session_state.edit_success_message = f"✅ Flotteurs de l'opération #{operation_id} modifiés avec succès !"
                                st.rerun()
                        
                        except Exception as e:
                            st.error(f"❌ Erreur : {e}")
                            st.exception(e)
                
                with col2:
                    if st.button("🗑️ Supprimer tous les flotteurs", key="delete_flotteurs"):
                        try:
                            # Récupérer les flotteurs existants pour l'audit avant suppression
                            conn = get_db_connection()
                            cur = conn.cursor()
                            cur.execute("SELECT * FROM flotteurs WHERE operation_id = %s", (operation_id,))
                            old_flotteurs = cur.fetchall()
                            old_columns = [desc[0] for desc in cur.description]
                            
                            # Supprimer avec audit
                            delete_query = f"DELETE FROM flotteurs WHERE operation_id = {operation_id}"
                            cur.execute("DELETE FROM flotteurs WHERE operation_id = %s", (operation_id,))
                            
                            if old_flotteurs:
                                log_action(
                                    table='flotteurs',
                                    action='DELETE',
                                    record_id=str(operation_id),
                                    old_values={f"flotteur_{i}": dict(zip(old_columns, row)) for i, row in enumerate(old_flotteurs)},
                                    details=f"Suppression de tous les flotteurs ({len(old_flotteurs)}) - Opération: {operation_id}",
                                    sql_query=delete_query
                                )
                            
                            conn.commit()
                            cur.close()
                            conn.close()
                            st.session_state.edit_success_message = f"✅ Tous les flotteurs de l'opération #{operation_id} ont été supprimés !"
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Erreur : {e}")
            else:
                st.info("Aucun flotteur enregistré pour cette opération")
                st.markdown("**Ajouter un flotteur :**")
                
                with st.form("add_flotteur"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        numero_ordre = st.number_input("Numéro d'ordre", min_value=1, value=1)
                        pavillon_options_edit = get_reference_list_cached('pavillon')
                        pavillon = st.selectbox("Pavillon", pavillon_options_edit,
                                              format_func=lambda x: "Non spécifié" if x is None else x,
                                              key="edit_pavillon")
                    with col2:
                        type_flotteur = st.text_input("Type", placeholder="Voilier")
                        categorie_flotteur_options_edit = get_reference_list_cached('categorie_flotteur')
                        categorie_flotteur = st.selectbox("Catégorie", categorie_flotteur_options_edit,
                                                        format_func=lambda x: "Non spécifié" if x is None else x,
                                                        key="edit_categorie_flotteur")
                    with col3:
                        resultat_flotteur_options_edit = get_reference_list_cached('resultat_flotteur')
                        resultat_flotteur = st.selectbox("Résultat", resultat_flotteur_options_edit,
                                                       format_func=lambda x: "Non spécifié" if x is None else x,
                                                       key="edit_resultat_flotteur")
                        numero_immat = st.text_input("N° immatriculation", placeholder="ABC123")
                    
                    if st.form_submit_button("➕ Ajouter le flotteur", type="primary"):
                        try:
                            flotteur_data = {
                                "operation_id": operation_id,
                                "numero_ordre": numero_ordre,
                                "pavillon": pavillon,
                                "type_flotteur": type_flotteur,
                                "categorie_flotteur": categorie_flotteur,
                                "resultat_flotteur": resultat_flotteur,
                                "numero_immatriculation": numero_immat
                            }
                            insert_flotteur(flotteur_data)
                            st.success("✅ Flotteur ajouté !")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Erreur : {e}")
        
        with tab3:
            st.markdown("### Modifier les résultats humains")
            
            if len(df_humain) > 0:
                st.info(f"📊 {len(df_humain)} résultat(s) trouvé(s)")
                
                edited_humain = st.data_editor(
                    df_humain, 
                    use_container_width=True, 
                    num_rows="dynamic",
                    key="edit_humain",
                    column_config={
                        "operation_id": st.column_config.NumberColumn("Operation ID", disabled=True),
                    }
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 Sauvegarder les résultats humains", type="primary", key="save_humain"):
                        try:
                            # Récupérer les résultats existants pour l'audit
                            conn = get_db_connection()
                            cur = conn.cursor()
                            cur.execute("SELECT * FROM resultats_humain WHERE operation_id = %s", (operation_id,))
                            old_resultats = cur.fetchall()
                            old_columns = [desc[0] for desc in cur.description]
                            
                            # Supprimer avec audit
                            delete_query = f"DELETE FROM resultats_humain WHERE operation_id = {operation_id}"
                            cur.execute("DELETE FROM resultats_humain WHERE operation_id = %s", (operation_id,))
                            
                            if old_resultats:
                                log_action(
                                    table='resultats_humain',
                                    action='DELETE',
                                    record_id=str(operation_id),
                                    old_values={f"resultat_{i}": dict(zip(old_columns, row)) for i, row in enumerate(old_resultats)},
                                    details=f"Suppression de {len(old_resultats)} résultat(s) humain(s) avant réinsertion - Opération: {operation_id}",
                                    sql_query=delete_query
                                )
                            
                            conn.commit()
                            cur.close()
                            conn.close()
                            
                            # Réinsérer avec audit via insert_resultat_humain
                            for idx, row in edited_humain.iterrows():
                                resultat_data = {
                                    'operation_id': operation_id,
                                    'numero_ordre': row['numero_ordre'],
                                    'categorie_personne': row['categorie_personne'],
                                    'resultat_humain': row['resultat_humain'],
                                    'nombre': row['nombre']
                                }
                                insert_resultat_humain(resultat_data)
                            
                            st.session_state.edit_success_message = f"✅ Résultats humains de l'opération #{operation_id} modifiés avec succès !"
                            st.rerun()
                        
                        except Exception as e:
                            st.error(f"❌ Erreur : {e}")
                            st.exception(e)
                
                with col2:
                    if st.button("🗑️ Supprimer tous les résultats", key="delete_humain"):
                        try:
                            # Récupérer pour l'audit
                            conn = get_db_connection()
                            cur = conn.cursor()
                            cur.execute("SELECT * FROM resultats_humain WHERE operation_id = %s", (operation_id,))
                            old_resultats = cur.fetchall()
                            old_columns = [desc[0] for desc in cur.description]
                            
                            # Supprimer avec audit
                            delete_query = f"DELETE FROM resultats_humain WHERE operation_id = {operation_id}"
                            cur.execute("DELETE FROM resultats_humain WHERE operation_id = %s", (operation_id,))
                            
                            if old_resultats:
                                log_action(
                                    table='resultats_humain',
                                    action='DELETE',
                                    record_id=str(operation_id),
                                    old_values={f"resultat_{i}": dict(zip(old_columns, row)) for i, row in enumerate(old_resultats)},
                                    details=f"Suppression de tous les résultats humains ({len(old_resultats)}) - Opération: {operation_id}",
                                    sql_query=delete_query
                                )
                            
                            conn.commit()
                            cur.close()
                            conn.close()
                            st.success("✅ Résultats supprimés !")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Erreur : {e}")
            else:
                st.info("Aucun résultat humain enregistré pour cette opération")
                st.markdown("**Ajouter un résultat humain :**")
                
                with st.form("add_humain"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        numero_ordre_h = st.number_input("Numéro d'ordre", min_value=1, value=1, key="no_humain")
                    with col2:
                        categorie_personne = st.text_input("Catégorie", placeholder="Plaisancier")
                        resultat_humain = st.text_input("Résultat", placeholder="Secouru")
                    with col3:
                        nombre = st.number_input("Nombre", min_value=1, value=1)
                    
                    if st.form_submit_button("➕ Ajouter le résultat", type="primary"):
                        try:
                            humain_data = {
                                "operation_id": operation_id,
                                "numero_ordre": numero_ordre_h,
                                "categorie_personne": categorie_personne,
                                "resultat_humain": resultat_humain,
                                "nombre": nombre
                            }
                            insert_resultat_humain(humain_data)
                            st.success("✅ Résultat humain ajouté !")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Erreur : {e}")
        
        with tab4:
            st.markdown("### Modifier les statistiques")
            
            if len(df_stats) > 0:
                st.info("📊 Statistiques disponibles")
                
                edited_stats = st.data_editor(
                    df_stats, 
                    use_container_width=True, 
                    num_rows="fixed",
                    key="edit_stats",
                    column_config={
                        "operation_id": st.column_config.NumberColumn("Operation ID", disabled=True),
                    }
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 Sauvegarder les statistiques", type="primary", key="save_stats"):
                        try:
                            conn = get_db_connection()
                            cur = conn.cursor()
                            
                            # Récupérer les anciennes valeurs pour l'audit
                            cur.execute("SELECT * FROM operations_stats WHERE operation_id = %s", (operation_id,))
                            old_stats = cur.fetchone()
                            old_columns = [desc[0] for desc in cur.description]
                            old_values_dict = dict(zip(old_columns, old_stats)) if old_stats else None
                            
                            # Préparer les nouvelles valeurs
                            new_values_dict = {'operation_id': operation_id}
                            for col in edited_stats.columns:
                                if col != 'operation_id':
                                    new_values_dict[col] = edited_stats[col].iloc[0]
                            
                            # Utiliser update_operations_stats avec audit
                            update_operations_stats(operation_id, new_values_dict)
                            
                            st.session_state.edit_success_message = f"✅ Statistiques de l'opération #{operation_id} modifiées avec succès !"
                            st.rerun()
                        
                        except Exception as e:
                            st.error(f"❌ Erreur : {e}")
                            st.exception(e)
                
                with col2:
                    if st.button("🗑️ Supprimer les statistiques", key="delete_stats"):
                        try:
                            # Récupérer pour l'audit
                            conn = get_db_connection()
                            cur = conn.cursor()
                            cur.execute("SELECT * FROM operations_stats WHERE operation_id = %s", (operation_id,))
                            old_stats = cur.fetchone()
                            old_columns = [desc[0] for desc in cur.description]
                            
                            # Supprimer avec audit
                            delete_query = f"DELETE FROM operations_stats WHERE operation_id = {operation_id}"
                            cur.execute("DELETE FROM operations_stats WHERE operation_id = %s", (operation_id,))
                            
                            if old_stats:
                                log_action(
                                    table='operations_stats',
                                    action='DELETE',
                                    record_id=str(operation_id),
                                    old_values=dict(zip(old_columns, old_stats)),
                                    details=f"Suppression des statistiques - Opération: {operation_id}",
                                    sql_query=delete_query
                                )
                            
                            conn.commit()
                            cur.close()
                            conn.close()
                            st.success("✅ Statistiques supprimées !")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Erreur : {e}")
            else:
                st.info("Aucune statistique enregistrée pour cette opération")
                st.markdown("**💡 Conseil :** Les statistiques peuvent être ajoutées via le formulaire de création.")
    
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement de l'opération : {e}")
        st.exception(e)
