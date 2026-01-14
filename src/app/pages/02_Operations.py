import streamlit as st
import pandas as pd
from pathlib import Path
import sys
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode
from datetime import datetime, date, time

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(PROJECT_ROOT))

from src.database.load_database import get_db_connection, engine
from src.crud.operations_crud import insert_operation, delete_operation
from src.crud.flotteurs_crud import insert_flotteur
from src.crud.resultat_humain_crud import insert_resultat_humain
from src.crud.operations_stats_crud import insert_operations_stats

st.set_page_config(page_title="Gestion des Opérations", page_icon="🚢", layout="wide")

# Initialiser session_state
if 'action' not in st.session_state:
    st.session_state.action = 'list'
if 'selected_operation_id' not in st.session_state:
    st.session_state.selected_operation_id = None

st.title("🚢 Gestion des Opérations")

# ========================================
# FONCTION: AFFICHER LA TABLE GRID
# ========================================
def show_operations_grid():
    """Affiche la table avec boutons d'action dans chaque ligne"""
    st.subheader("📋 Liste des Opérations")
    
    # Boutons d'action
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 4])
    with col_btn1:
        if st.button("➕ Créer une nouvelle opération", type="primary", use_container_width=True):
            st.session_state.action = 'create'
            st.rerun()
    
    with col_btn2:
        if st.button("🔄 Rafraîchir", use_container_width=True):
            st.rerun()
    
    # Récupérer toutes les opérations
    try:
        query = """
        SELECT 
            operation_id,
            "cross",
            evenement,
            date_heure_reception_alerte,
            departement,
            pourquoi_alerte,
            latitude,
            longitude
        FROM operations 
        ORDER BY date_heure_reception_alerte DESC
        LIMIT 500
        """
        df_operations = pd.read_sql(query, engine)
        
        if len(df_operations) == 0:
            st.info("Aucune opération trouvée dans la base de données")
            return
        
        # Formater la date pour l'affichage
        df_operations['date_heure_reception_alerte'] = pd.to_datetime(
            df_operations['date_heure_reception_alerte']
        ).dt.strftime('%Y-%m-%d %H:%M')
        
        # ====== AFFICHAGE DU TABLEAU ======
        st.markdown("---")
        
        # EN-TÊTE DU TABLEAU
        st.markdown("#### 📋 Tableau des Opérations")
        col1, col2, col3, col4, col5, col6, col7 = st.columns([0.6, 0.8, 1.2, 1.2, 0.6, 0.8, 1.0])
        
        with col1:
            st.markdown("**ID**")
        with col2:
            st.markdown("**CROSS**")
        with col3:
            st.markdown("**Événement**")
        with col4:
            st.markdown("**Date/Heure**")
        with col5:
            st.markdown("**Dépt**")
        with col6:
            st.markdown("**Coordonnées**")
        with col7:
            st.markdown("**Actions**")
        
        st.markdown("---")
        
        # LIGNES DU TABLEAU
        for idx, row in df_operations.iterrows():
            col1, col2, col3, col4, col5, col6, col7 = st.columns([0.6, 0.8, 1.2, 1.2, 0.6, 0.8, 1.0])
            
            with col1:
                st.text(row['operation_id'])
            with col2:
                st.text(row['cross'])
            with col3:
                evenement = row['evenement'] if pd.notna(row['evenement']) else "-"
                st.text(evenement[:20] + "..." if len(str(evenement)) > 20 else evenement)
            with col4:
                st.text(row['date_heure_reception_alerte'])
            with col5:
                st.text(row['departement'] if pd.notna(row['departement']) else "-")
            with col6:
                if pd.notna(row['latitude']) and pd.notna(row['longitude']):
                    st.text(f"{row['latitude']:.2f}, {row['longitude']:.2f}")
                else:
                    st.text("-")
            with col7:
                btn_col1, btn_col2, btn_col3 = st.columns(3)
                with btn_col1:
                    if st.button("👁️", key=f"view_{row['operation_id']}", help="Consulter"):
                        st.session_state.selected_operation_id = row['operation_id']
                        st.session_state.action = 'view'
                        st.rerun()
                with btn_col2:
                    if st.button("✏️", key=f"edit_{row['operation_id']}", help="Modifier"):
                        st.session_state.selected_operation_id = row['operation_id']
                        st.session_state.action = 'edit'
                        st.rerun()
                with btn_col3:
                    if st.button("🗑️", key=f"delete_{row['operation_id']}", help="Supprimer"):
                        st.session_state.selected_operation_id = row['operation_id']
                        st.session_state.action = 'delete'
                        st.rerun()
            
            # Ligne de séparation légère
            if idx < len(df_operations) - 1:
                st.markdown("<hr style='margin: 0.3rem 0; border: none; border-top: 1px solid #e0e0e0;'>", unsafe_allow_html=True)
        
        # Statistiques
        st.markdown("---")
        col_s1, col_s2, col_s3 = st.columns(3)
        col_s1.metric("📊 Total opérations", len(df_operations))
        
        # Compter par CROSS
        cross_counts = df_operations['cross'].value_counts()
        if len(cross_counts) > 0:
            col_s2.metric("🏆 CROSS le plus actif", f"{cross_counts.index[0]} ({cross_counts.values[0]})")
        
        # Opérations affichées
        col_s3.metric("🆕 Opérations affichées", len(df_operations))
    
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement des opérations : {e}")
        st.exception(e)


# ========================================
# FONCTION: CONSULTER UNE OPÉRATION
# ========================================
def view_operation(operation_id):
    """Affiche les détails complets d'une opération"""
    st.subheader(f"👁️ Consultation de l'Opération #{operation_id}")
    
    if st.button("⬅️ Retour à la liste"):
        st.session_state.action = 'list'
        st.rerun()
    
    try:
        # Récupérer les données de l'opération
        query_op = f"SELECT * FROM operations WHERE operation_id = {operation_id}"
        df_op = pd.read_sql(query_op, engine)
        
        if len(df_op) == 0:
            st.error(f"Opération #{operation_id} introuvable")
            return
        
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
            st.dataframe(df_transpose, use_container_width=True)
        
        with tab2:
            query_flotteurs = f"SELECT * FROM flotteurs WHERE operation_id = {operation_id}"
            df_flotteurs = pd.read_sql(query_flotteurs, engine)
            
            if len(df_flotteurs) > 0:
                st.dataframe(df_flotteurs, use_container_width=True, hide_index=True)
                st.success(f"✅ {len(df_flotteurs)} flotteur(s) trouvé(s)")
            else:
                st.info("Aucun flotteur enregistré pour cette opération")
        
        with tab3:
            query_humain = f"SELECT * FROM resultats_humain WHERE operation_id = {operation_id}"
            df_humain = pd.read_sql(query_humain, engine)
            
            if len(df_humain) > 0:
                st.dataframe(df_humain, use_container_width=True, hide_index=True)
                st.success(f"✅ {len(df_humain)} résultat(s) trouvé(s)")
            else:
                st.info("Aucun résultat humain enregistré pour cette opération")
        
        with tab4:
            query_stats = f"SELECT * FROM operations_stats WHERE operation_id = {operation_id}"
            df_stats = pd.read_sql(query_stats, engine)
            
            if len(df_stats) > 0:
                # KPIs importants
                col_s1, col_s2, col_s3, col_s4 = st.columns(4)
                col_s1.metric("👥 Impliqués", int(df_stats['nombre_personnes_impliquees'].iloc[0]) if pd.notna(df_stats['nombre_personnes_impliquees'].iloc[0]) else 0)
                col_s2.metric("✅ Secourus", int(df_stats['nombre_personnes_secourues'].iloc[0]) if pd.notna(df_stats['nombre_personnes_secourues'].iloc[0]) else 0)
                col_s3.metric("💔 Décès", int(df_stats['nombre_personnes_tous_deces'].iloc[0]) if pd.notna(df_stats['nombre_personnes_tous_deces'].iloc[0]) else 0)
                col_s4.metric("🚑 Blessés", int(df_stats['nombre_personnes_blessees'].iloc[0]) if pd.notna(df_stats['nombre_personnes_blessees'].iloc[0]) else 0)
                
                st.dataframe(df_stats, use_container_width=True, hide_index=True)
            else:
                st.info("Aucune statistique enregistrée pour cette opération")
    
    except Exception as e:
        st.error(f"❌ Erreur : {e}")
        st.exception(e)


# ========================================
# FONCTION: CRÉER UNE OPÉRATION
# ========================================
def create_operation():
    """Formulaire de création d'une nouvelle opération"""
    st.subheader("➕ Créer une nouvelle opération")
    
    if st.button("⬅️ Retour à la liste"):
        st.session_state.action = 'list'
        st.rerun()
    
    # Récupérer le prochain ID
    try:
        query_next_id = "SELECT COALESCE(MAX(operation_id), 0) + 1 FROM operations"
        df_next_id = pd.read_sql(query_next_id, engine)
        next_operation_id = int(df_next_id.iloc[0, 0])
    except:
        next_operation_id = 1
    
    with st.form("form_create_operation"):
        # ===========================================
        # SECTION 1: INFORMATIONS ESSENTIELLES
        # ===========================================
        st.markdown("### 🚢 Informations essentielles")
        st.caption("Champs obligatoires marqués par *")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.number_input("ID Opération", value=next_operation_id, disabled=True, 
                          help="Auto-généré - Prochain ID disponible")
        with col2:
            cross = st.text_input("CROSS*", placeholder="Ex: Med", help="Obligatoire")
        with col3:
            type_operation = st.text_input("Type d'opération", placeholder="Ex: SAR", max_chars=3)
        with col4:
            pass
        
        col1, col2, col3 = st.columns(3)
        with col1:
            date_alerte = st.date_input("Date de l'alerte*", value=date.today(), help="Obligatoire")
            heure_alerte = st.time_input("Heure de l'alerte*", value=datetime.now().time(), help="Obligatoire")
        with col2:
            date_fin = st.date_input("Date de fin", value=None)
            heure_fin = st.time_input("Heure de fin", value=None) if date_fin else None
        with col3:
            pass
        
        # ===========================================
        # SECTION 2: ÉVÉNEMENT
        # ===========================================
        st.markdown("### 📋 Événement")
        
        col1, col2 = st.columns(2)
        with col1:
            evenement = st.text_input("Événement", placeholder="Ex: Naufrage, Avarie")
        with col2:
            categorie_evenement = st.text_input("Catégorie", placeholder="Ex: Accident, Assistance")
        
        # ===========================================
        # SECTION 3: ALERTE
        # ===========================================
        st.markdown("### 🚨 Détails de l'alerte")
        
        pourquoi_alerte = st.text_area("Raison de l'alerte", placeholder="Description détaillée de la situation", height=100)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            moyen_alerte = st.text_input("Moyen d'alerte", placeholder="Ex: VHF canal 16, Téléphone")
        with col2:
            qui_alerte = st.text_input("Qui donne l'alerte", placeholder="Ex: Pêcheur, SNSM, Plaisancier")
        with col3:
            categorie_qui_alerte = st.text_input("Catégorie émetteur", placeholder="Ex: Professionnel, Particulier")
        
        # ===========================================
        # SECTION 4: LOCALISATION
        # ===========================================
        st.markdown("### 📍 Localisation géographique")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            latitude = st.number_input("Latitude (WGS84)", value=0.0, format="%.6f", step=0.000001, 
                                      help="Exemple: 43.296482 (format décimal)")
            departement = st.text_input("Département", placeholder="Ex: 06, 13")
        with col2:
            longitude = st.number_input("Longitude (WGS84)", value=0.0, format="%.6f", step=0.000001,
                                       help="Exemple: 5.369780 (format décimal)")
            zone_responsabilite = st.text_input("Zone de responsabilité", placeholder="Ex: Atlantique, Méditerranée")
        with col3:
            fuseau_horaire = st.text_input("Fuseau horaire", placeholder="Ex: UTC+1, Europe/Paris")
            est_metropolitain = st.selectbox("Zone métropolitaine", [None, True, False], 
                                            format_func=lambda x: "Non spécifié" if x is None else ("Oui" if x else "Non"))
        
        # ===========================================
        # SECTION 5: CONDITIONS MÉTÉO/MER
        # ===========================================
        st.markdown("### 🌊 Conditions météorologiques et maritimes")
        
        col1, col2 = st.columns(2)
        with col1:
            st.caption("🌬️ Vent")
            vent_direction = st.number_input("Direction (degrés)", min_value=0.0, max_value=360.0, value=0.0, format="%.2f",
                                            help="0-360° (0=Nord, 90=Est, 180=Sud, 270=Ouest)")
            vent_direction_categorie = st.text_input("Direction (cardinal)", placeholder="Ex: Nord, Sud-Ouest, NNE")
            vent_force = st.number_input("Force (Beaufort ou m/s)", min_value=0.0, value=0.0, format="%.2f")
        with col2:
            st.caption("🌊 Mer")
            mer_force = st.number_input("État de la mer", min_value=0.0, value=0.0, format="%.2f",
                                       help="Échelle Douglas (0-9)")
        
        # ===========================================
        # SECTION 6: AUTORITÉS IMPLIQUÉES
        # ===========================================
        st.markdown("### 👮 Autorités et coordination")
        
        col1, col2 = st.columns(2)
        with col1:
            autorite = st.text_input("Autorité principale", placeholder="Ex: Préfecture maritime Méditerranée")
        with col2:
            seconde_autorite = st.text_input("Autorité secondaire", placeholder="Ex: Gendarmerie maritime")
        
        # ===========================================
        # SECTION 7: RAPPORTS ET SYSTÈME
        # ===========================================
        st.markdown("### 📄 Rapports et système")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            numero_sitrep = st.number_input("Numéro SITREP", min_value=0, value=0,
                                           help="Numéro de rapport de situation")
        with col2:
            cross_sitrep = st.text_input("CROSS SITREP", placeholder="Ex: Med-SITREP-2024-001")
        with col3:
            systeme_source = st.text_input("Système source", placeholder="Ex: SPATIONAV, SNSM-OS")
        
        st.divider()
        
        # ===========================================
        # SECTION 8: FLOTTEUR (OPTIONNEL)
        # ===========================================
        st.markdown("### ⛵ Flotteur impliqué")
        add_flotteur = st.checkbox("➕ Ajouter un flotteur à cette opération")
        
        if add_flotteur:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                pavillon = st.text_input("Pavillon", placeholder="Ex: France, Italie")
            with col2:
                type_flotteur = st.text_input("Type", placeholder="Ex: Voilier, Chalutier")
            with col3:
                resultat_flotteur = st.selectbox("Résultat", ["", "Récupéré", "Perdu", "Coulé", "Assisté"])
            with col4:
                numero_immat = st.text_input("N° immatriculation", placeholder="Ex: ABC123")
        
        st.divider()
        
        # ===========================================
        # SECTION 9: RÉSULTATS HUMAINS (OPTIONNEL)
        # ===========================================
        st.markdown("### 👥 Résultats humains")
        add_humain = st.checkbox("➕ Ajouter des résultats humains à cette opération")
        
        if add_humain:
            col1, col2, col3 = st.columns(3)
            with col1:
                categorie_personne = st.text_input("Catégorie", placeholder="Ex: Plaisancier, Pêcheur, Passager")
            with col2:
                resultat_humain = st.selectbox("Résultat", ["", "Secouru", "Décédé", "Blessé", "Sain et sauf", "Disparu"])
            with col3:
                nombre = st.number_input("Nombre de personnes", min_value=0, value=1)
        
        st.divider()
        
        # ===========================================
        # SECTION 10: STATISTIQUES (OPTIONNEL)
        # ===========================================
        st.markdown("### 📊 Statistiques de l'opération")
        add_stats = st.checkbox("➕ Ajouter des statistiques à cette opération")
        
        if add_stats:
            st.caption("Bilan global de l'opération")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                nb_impliques = st.number_input("Nb impliqués", min_value=0, value=0, help="Personnes impliquées")
            with col2:
                nb_secourues = st.number_input("Nb secourus", min_value=0, value=0, help="Personnes secourues")
            with col3:
                nb_deces = st.number_input("Nb décès", min_value=0, value=0, help="Nombre de décès")
            with col4:
                nb_blesses = st.number_input("Nb blessés", min_value=0, value=0, help="Nombre de blessés")
        
        st.divider()
        
        submitted = st.form_submit_button("✅ Créer l'opération", type="primary", use_container_width=True)
        
        if submitted:
            if not cross:
                st.error("❌ Le champ CROSS est obligatoire")
            else:
                try:
                    date_heure_alerte = datetime.combine(date_alerte, heure_alerte)
                    date_heure_fin = None
                    if date_fin and heure_fin:
                        date_heure_fin = datetime.combine(date_fin, heure_fin)
                    
                    operation_data = {
                        "cross": cross,
                        "date_heure_reception_alerte": date_heure_alerte,
                        "date_heure_fin_operation": date_heure_fin,
                        "type_operation": type_operation if type_operation else None,
                        "evenement": evenement if evenement else None,
                        "categorie_evenement": categorie_evenement if categorie_evenement else None,
                        "departement": departement if departement else None,
                        "est_metropolitain": est_metropolitain,
                        "pourquoi_alerte": pourquoi_alerte if pourquoi_alerte else None,
                        "moyen_alerte": moyen_alerte if moyen_alerte else None,
                        "qui_alerte": qui_alerte if qui_alerte else None,
                        "categorie_qui_alerte": categorie_qui_alerte if categorie_qui_alerte else None,
                        "latitude": latitude if latitude != 0.0 else None,
                        "longitude": longitude if longitude != 0.0 else None,
                        "zone_responsabilite": zone_responsabilite if zone_responsabilite else None,
                        "fuseau_horaire": fuseau_horaire if fuseau_horaire else None,
                        "autorite": autorite if autorite else None,
                        "seconde_autorite": seconde_autorite if seconde_autorite else None,
                        "vent_direction": vent_direction if vent_direction != 0.0 else None,
                        "vent_direction_categorie": vent_direction_categorie if vent_direction_categorie else None,
                        "vent_force": vent_force if vent_force != 0.0 else None,
                        "mer_force": mer_force if mer_force != 0.0 else None,
                        "numero_sitrep": numero_sitrep if numero_sitrep != 0 else None,
                        "cross_sitrep": cross_sitrep if cross_sitrep else None,
                        "systeme_source": systeme_source if systeme_source else None,
                    }
                    
                    with st.spinner("Création en cours..."):
                        operation_id = insert_operation(operation_data)
                        
                        if operation_id:
                            st.success(f"✅ Opération créée ! ID: {operation_id}")
                            
                            if add_flotteur and pavillon:
                                flotteur_data = {
                                    "operation_id": operation_id,
                                    "pavillon": pavillon,
                                    "type_flotteur": type_flotteur if type_flotteur else None,
                                    "resultat_flotteur": resultat_flotteur if resultat_flotteur else None,
                                    "numero_immatriculation": numero_immat if numero_immat else None,
                                }
                                insert_flotteur(flotteur_data)
                                st.success("✅ Flotteur ajouté")
                            
                            if add_humain and categorie_personne:
                                humain_data = {
                                    "operation_id": operation_id,
                                    "categorie_personne": categorie_personne,
                                    "resultat_humain": resultat_humain if resultat_humain else None,
                                    "nombre": nombre,
                                }
                                insert_resultat_humain(humain_data)
                                st.success("✅ Résultat humain ajouté")
                            
                            if add_stats:
                                stats_data = {
                                    "operation_id": operation_id,
                                    "nombre_personnes_impliquees": nb_impliques,
                                    "nombre_personnes_secourues": nb_secourues,
                                    "nombre_personnes_tous_deces": nb_deces,
                                    "nombre_personnes_blessees": nb_blesses,
                                }
                                insert_operations_stats(stats_data)
                                st.success("✅ Statistiques ajoutées")
                            
                            st.balloons()
                            st.success("🎉 Création terminée ! Retour à la liste dans 3 secondes...")
                            import time
                            time.sleep(3)
                            st.session_state.action = 'list'
                            st.rerun()
                        else:
                            st.error("❌ Erreur lors de la création")
                
                except Exception as e:
                    st.error(f"❌ Erreur : {e}")
                    st.exception(e)


# ========================================
# FONCTION: MODIFIER UNE OPÉRATION
# ========================================
def edit_operation(operation_id):
    """Formulaire de modification d'une opération avec toutes ses données liées"""
    st.subheader(f"✏️ Modifier l'Opération #{operation_id}")
    
    if st.button("⬅️ Retour à la liste"):
        st.session_state.action = 'list'
        st.rerun()
    
    try:
        # Récupérer l'opération
        query_op = f"SELECT * FROM operations WHERE operation_id = {operation_id}"
        df_op = pd.read_sql(query_op, engine)
        
        if len(df_op) == 0:
            st.error(f"Opération #{operation_id} introuvable")
            return
        
        # Récupérer les données liées
        query_flotteurs = f"SELECT * FROM flotteurs WHERE operation_id = {operation_id}"
        df_flotteurs = pd.read_sql(query_flotteurs, engine)
        
        query_humain = f"SELECT * FROM resultats_humain WHERE operation_id = {operation_id}"
        df_humain = pd.read_sql(query_humain, engine)
        
        query_stats = f"SELECT * FROM operations_stats WHERE operation_id = {operation_id}"
        df_stats = pd.read_sql(query_stats, engine)
        
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
                        conn = get_db_connection()
                        cur = conn.cursor()
                        
                        for col in edited_op.columns:
                            if col != 'operation_id':
                                value = edited_op[col].iloc[0]
                                if col == "cross":
                                    query = f'UPDATE operations SET "{col}" = %s WHERE operation_id = %s'
                                else:
                                    query = f'UPDATE operations SET {col} = %s WHERE operation_id = %s'
                                cur.execute(query, (value, operation_id))
                        
                        conn.commit()
                        cur.close()
                        conn.close()
                        
                        st.success("✅ Opération modifiée avec succès !")
                        st.rerun()
                
                except Exception as e:
                    st.error(f"❌ Erreur : {e}")
                    st.exception(e)
        
        with tab2:
            st.markdown("### Modifier les flotteurs")
            
            if len(df_flotteurs) > 0:
                st.info(f"📊 {len(df_flotteurs)} flotteur(s) trouvé(s)")
                
                edited_flotteurs = st.data_editor(
                    df_flotteurs, 
                    use_container_width=True, 
                    num_rows="dynamic",
                    key="edit_flotteurs",
                    column_config={
                        "operation_id": st.column_config.NumberColumn("Operation ID", disabled=True),
                    }
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 Sauvegarder les flotteurs", type="primary", key="save_flotteurs"):
                        try:
                            conn = get_db_connection()
                            cur = conn.cursor()
                            
                            # Supprimer tous les flotteurs existants
                            cur.execute("DELETE FROM flotteurs WHERE operation_id = %s", (operation_id,))
                            
                            # Réinsérer les flotteurs modifiés
                            for idx, row in edited_flotteurs.iterrows():
                                cur.execute("""
                                    INSERT INTO flotteurs (operation_id, numero_ordre, pavillon, resultat_flotteur, 
                                                          type_flotteur, categorie_flotteur, numero_immatriculation)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                                """, (
                                    operation_id,
                                    row['numero_ordre'],
                                    row['pavillon'],
                                    row['resultat_flotteur'],
                                    row['type_flotteur'],
                                    row['categorie_flotteur'],
                                    row['numero_immatriculation']
                                ))
                            
                            conn.commit()
                            cur.close()
                            conn.close()
                            
                            st.success("✅ Flotteurs modifiés avec succès !")
                            st.rerun()
                        
                        except Exception as e:
                            st.error(f"❌ Erreur : {e}")
                            st.exception(e)
                
                with col2:
                    if st.button("🗑️ Supprimer tous les flotteurs", key="delete_flotteurs"):
                        try:
                            conn = get_db_connection()
                            cur = conn.cursor()
                            cur.execute("DELETE FROM flotteurs WHERE operation_id = %s", (operation_id,))
                            conn.commit()
                            cur.close()
                            conn.close()
                            st.success("✅ Flotteurs supprimés !")
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
                        pavillon = st.text_input("Pavillon", placeholder="France")
                    with col2:
                        type_flotteur = st.text_input("Type", placeholder="Voilier")
                        categorie_flotteur = st.text_input("Catégorie", placeholder="Plaisance")
                    with col3:
                        resultat_flotteur = st.text_input("Résultat", placeholder="Récupéré")
                        numero_immat = st.text_input("N° immatriculation", placeholder="ABC123")
                    
                    if st.form_submit_button("➕ Ajouter le flotteur", type="primary"):
                        try:
                            from src.crud.flotteurs_crud import insert_flotteur
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
                            conn = get_db_connection()
                            cur = conn.cursor()
                            
                            # Supprimer tous les résultats existants
                            cur.execute("DELETE FROM resultats_humain WHERE operation_id = %s", (operation_id,))
                            
                            # Réinsérer les résultats modifiés
                            for idx, row in edited_humain.iterrows():
                                cur.execute("""
                                    INSERT INTO resultats_humain (operation_id, numero_ordre, categorie_personne, 
                                                                  resultat_humain, nombre)
                                    VALUES (%s, %s, %s, %s, %s)
                                """, (
                                    operation_id,
                                    row['numero_ordre'],
                                    row['categorie_personne'],
                                    row['resultat_humain'],
                                    row['nombre']
                                ))
                            
                            conn.commit()
                            cur.close()
                            conn.close()
                            
                            st.success("✅ Résultats humains modifiés avec succès !")
                            st.rerun()
                        
                        except Exception as e:
                            st.error(f"❌ Erreur : {e}")
                            st.exception(e)
                
                with col2:
                    if st.button("🗑️ Supprimer tous les résultats", key="delete_humain"):
                        try:
                            conn = get_db_connection()
                            cur = conn.cursor()
                            cur.execute("DELETE FROM resultats_humain WHERE operation_id = %s", (operation_id,))
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
                            from src.crud.resultat_humain_crud import insert_resultat_humain
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
                            
                            # Mettre à jour les statistiques
                            for col in edited_stats.columns:
                                if col != 'operation_id':
                                    value = edited_stats[col].iloc[0]
                                    query = f'UPDATE operations_stats SET {col} = %s WHERE operation_id = %s'
                                    cur.execute(query, (value, operation_id))
                            
                            conn.commit()
                            cur.close()
                            conn.close()
                            
                            st.success("✅ Statistiques modifiées avec succès !")
                            st.rerun()
                        
                        except Exception as e:
                            st.error(f"❌ Erreur : {e}")
                            st.exception(e)
                
                with col2:
                    if st.button("🗑️ Supprimer les statistiques", key="delete_stats"):
                        try:
                            conn = get_db_connection()
                            cur = conn.cursor()
                            cur.execute("DELETE FROM operations_stats WHERE operation_id = %s", (operation_id,))
                            conn.commit()
                            cur.close()
                            conn.close()
                            st.success("✅ Statistiques supprimées !")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Erreur : {e}")
            else:
                st.info("Aucune statistique enregistrée pour cette opération")
                st.markdown("**Ajouter des statistiques :**")
                
                with st.form("add_stats"):
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        nb_impliques = st.number_input("Nb impliqués", min_value=0, value=0)
                    with col2:
                        nb_secourues = st.number_input("Nb secourus", min_value=0, value=0)
                    with col3:
                        nb_deces = st.number_input("Nb décès", min_value=0, value=0)
                    with col4:
                        nb_blesses = st.number_input("Nb blessés", min_value=0, value=0)
                    
                    if st.form_submit_button("➕ Ajouter les statistiques", type="primary"):
                        try:
                            from src.crud.operations_stats_crud import insert_operations_stats
                            stats_data = {
                                "operation_id": operation_id,
                                "nombre_personnes_impliquees": nb_impliques,
                                "nombre_personnes_secourues": nb_secourues,
                                "nombre_personnes_tous_deces": nb_deces,
                                "nombre_personnes_blessees": nb_blesses
                            }
                            insert_operations_stats(stats_data)
                            st.success("✅ Statistiques ajoutées !")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Erreur : {e}")
    
    except Exception as e:
        st.error(f"❌ Erreur : {e}")
        st.exception(e)


# ========================================
# FONCTION: SUPPRIMER UNE OPÉRATION
# ========================================
def delete_operation_confirm(operation_id):
    """Confirmation et suppression d'une opération"""
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
                    
                    import time
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
        delete_operation_confirm(st.session_state.selected_operation_id)
    else:
        st.error("❌ Aucune opération sélectionnée")
        st.session_state.action = 'list'
        st.rerun()
