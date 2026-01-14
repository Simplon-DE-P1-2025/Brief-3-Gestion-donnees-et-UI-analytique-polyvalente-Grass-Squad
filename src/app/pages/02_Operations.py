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
from src.crud.reference_lists_crud import get_reference_list_values

st.set_page_config(page_title="Gestion des Opérations", page_icon="🚢", layout="wide")

# Initialiser session_state
if 'action' not in st.session_state:
    st.session_state.action = 'list'
if 'selected_operation_id' not in st.session_state:
    st.session_state.selected_operation_id = None

st.title("🚢 Gestion des Opérations")

# ========================================
# HELPER: CHARGER LES LISTES DE RÉFÉRENCE
# ========================================
@st.cache_data(ttl=300)  # Cache pendant 5 minutes
def load_reference_list(category):
    """Charge une liste de référence depuis la DB"""
    try:
        values = get_reference_list_values(category, active_only=True)
        return [None] + [val[1] for val in values]  # Ajouter None pour "Non spécifié"
    except:
        # Fallback en cas d'erreur
        return [None]

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
        if st.button("⬅️ Retour à la liste", use_container_width=True):
            st.session_state.action = 'list'
            st.rerun()
    with col_btn3:
        st.markdown("""
        <style>
        button[kind="primary"] {
            background-color: #28a745 !important;
            color: white !important;
            border: 1px solid #28a745 !important;
        }
        button[kind="primary"]:hover {
            background-color: #218838 !important;
            border-color: #1e7e34 !important;
        }
        </style>
        """, unsafe_allow_html=True)
        if st.button("✏️ Modifier", type="primary", key="btn_modify", use_container_width=True):
            st.session_state.action = 'edit'
            st.session_state.selected_operation_id = operation_id
            st.rerun()
    with col_btn4:
        st.markdown("""
        <style>
        button[kind="secondary"] {
            background-color: #dc3545 !important;
            color: white !important;
            border: 1px solid #dc3545 !important;
        }
        button[kind="secondary"]:hover {
            background-color: #c82333 !important;
            border-color: #bd2130 !important;
        }
        </style>
        """, unsafe_allow_html=True)
        if st.button("🗑️ Supprimer", type="secondary", key="btn_delete", use_container_width=True):
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
            cross_options = load_reference_list('cross')
            cross = st.selectbox("CROSS*", cross_options,
                                format_func=lambda x: "Sélectionner..." if x is None else x,
                                help="Obligatoire")
        with col3:
            type_operation_options = load_reference_list('type_operation')
            type_operation = st.selectbox("Type d'opération", type_operation_options,
                                         format_func=lambda x: "Non spécifié" if x is None else x,
                                         help="SAR: vie humaine en danger, MAS: assistance navires, SUR: sûreté, POL: pollutions, DIV: autres")
        with col4:
            pass
        
        col1, col2, col3 = st.columns(3)
        with col1:
            date_alerte = st.date_input("Date de l'alerte*", value=date.today(), help="Obligatoire")
            heure_alerte = st.time_input("Heure de l'alerte*", value=datetime.now().time(), help="Obligatoire")
        with col2:
            date_fin = st.date_input("Date de fin", value=None)
            heure_fin = st.time_input("Heure de fin", value=None)
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
            vent_direction = st.number_input("Direction (degrés)", min_value=0, max_value=360, value=0, step=1,
                                            help="0-360° (0=Nord, 90=Est, 180=Sud, 270=Ouest)")
            vent_direction_options = load_reference_list('vent_direction_categorie')
            vent_direction_categorie = st.selectbox("Direction (cardinal)", vent_direction_options,
                                                   format_func=lambda x: "Non spécifié" if x is None else x)
            vent_force = st.number_input("Force (Beaufort)", min_value=0, max_value=12, value=0, step=1,
                                        help="Échelle de Beaufort: 0-12")
        with col2:
            st.caption("🌊 Mer")
            mer_force = st.number_input("État de la mer (Douglas)", min_value=0, max_value=9, value=0, step=1,
                                       help="Échelle Douglas: 0-9")
        
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
            systeme_source_options = load_reference_list('systeme_source')
            systeme_source = st.selectbox("Système source", systeme_source_options,
                                         format_func=lambda x: "Non spécifié" if x is None else x)
        
        st.divider()
        
        # ===========================================
        # SECTION 8: FLOTTEUR (OPTIONNEL - EXPANDER)
        # ===========================================
        with st.expander("⛵ Flotteur impliqué (optionnel)", expanded=False):
            st.markdown("*Remplir les informations du flotteur (si applicable)*")
            col1, col2, col3 = st.columns(3)
            with col1:
                pavillon_options = load_reference_list('pavillon')
                pavillon = st.selectbox("Pavillon", pavillon_options,
                                       format_func=lambda x: "Non spécifié" if x is None else x)
                type_flotteur = st.text_input("Type de flotteur", placeholder="Ex: Voilier, Chalutier, Planche à voile")
            with col2:
                categorie_flotteur_options = load_reference_list('categorie_flotteur')
                categorie_flotteur = st.selectbox("Catégorie", categorie_flotteur_options,
                                                 format_func=lambda x: "Non spécifié" if x is None else x)
                resultat_flotteur_options = load_reference_list('resultat_flotteur')
                resultat_flotteur = st.selectbox("Résultat", resultat_flotteur_options,
                    format_func=lambda x: "Non spécifié" if x is None else x)
            with col3:
                numero_immat = st.text_input("N° immatriculation", placeholder="Ex: ABC123")
                numero_ordre = st.number_input("Numéro d'ordre", min_value=1, value=1, help="Ordre du flotteur dans l'opération")
            
            add_flotteur = bool(pavillon or type_flotteur or categorie_flotteur or resultat_flotteur or numero_immat)
        
        # ===========================================
        # SECTION 9: RÉSULTATS HUMAINS (OPTIONNEL - EXPANDER)
        # ===========================================
        with st.expander("👥 Résultats humains (optionnel)", expanded=False):
            st.markdown("*Remplir les résultats humains de l'opération (si applicable)*")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                categorie_personne_options = load_reference_list('categorie_personne')
                categorie_personne = st.selectbox("Catégorie de personne", categorie_personne_options,
                    format_func=lambda x: "Non spécifié" if x is None else x)
            with col2:
                resultat_humain_options = load_reference_list('resultat_humain')
                resultat_humain = st.selectbox("Résultat", resultat_humain_options,
                    format_func=lambda x: "Non spécifié" if x is None else x)
            with col3:
                nombre = st.number_input("Nombre de personnes", min_value=0, value=0)
            with col4:
                dont_nombre_blesse = st.number_input("Dont blessés", min_value=0, value=0, help="Nombre de blessés parmi les personnes")
            
            add_humain = bool(categorie_personne or resultat_humain or nombre > 0)
        
        # ===========================================
        # SECTION 10: STATISTIQUES (OPTIONNEL - EXPANDER)
        # ===========================================
        with st.expander("📊 Statistiques de l'opération (optionnel)", expanded=False):
            st.markdown("*Remplir les statistiques détaillées de l'opération (si applicable)*")
            
            st.markdown("##### 👥 Personnes impliquées")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                nb_impliques = st.number_input("Nb impliqués", min_value=0, value=0, help="Personnes impliquées")
                nb_secourues = st.number_input("Nb secourus", min_value=0, value=0, help="Personnes secourues")
                nb_assistees = st.number_input("Nb assistées", min_value=0, value=0, help="Personnes assistées")
            with col2:
                nb_deces = st.number_input("Nb décès", min_value=0, value=0, help="Total décès")
                nb_deces_accidentel = st.number_input("Dont accidentels", min_value=0, value=0, help="Décès accidentels")
                nb_deces_naturel = st.number_input("Dont naturels", min_value=0, value=0, help="Décès naturels")
            with col3:
                nb_blesses = st.number_input("Nb blessés", min_value=0, value=0, help="Nombre de blessés")
                nb_disparues = st.number_input("Nb disparus", min_value=0, value=0, help="Personnes disparues")
                nb_retrouvees = st.number_input("Nb retrouvées", min_value=0, value=0, help="Personnes retrouvées")
            with col4:
                nb_tirees_affaire = st.number_input("Tirées d'affaire seules", min_value=0, value=0)
                nb_fausse_alerte = st.number_input("Fausse alerte", min_value=0, value=0)
                nb_deces_disparues = st.number_input("Décès ou disparus", min_value=0, value=0)
            
            st.markdown("##### 🚤 Informations flotteurs")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                nb_flotteurs_commerce = st.number_input("Commerce", min_value=0, value=0)
                nb_flotteurs_peche = st.number_input("Pêche", min_value=0, value=0)
            with col2:
                nb_flotteurs_plaisance = st.number_input("Plaisance", min_value=0, value=0)
                nb_flotteurs_loisirs = st.number_input("Loisirs nautiques", min_value=0, value=0)
            with col3:
                nb_aeronefs = st.number_input("Aéronefs", min_value=0, value=0)
                nb_flotteurs_autre = st.number_input("Autre", min_value=0, value=0)
            with col4:
                st.caption("Détails plaisance")
                nb_plaisance_voile = st.number_input("Voile", min_value=0, value=0)
                nb_plaisance_moteur = st.number_input("Moteur", min_value=0, value=0)
            
            st.markdown("##### 🌊 Contexte et localisation")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                concerne_plongee = st.checkbox("Concerne la plongée")
                implique_wingfoil = st.checkbox("Implique wingfoil")
                avec_clandestins = st.checkbox("Avec clandestins")
            with col2:
                est_dans_stm = st.checkbox("Dans STM (Séparation du Trafic Maritime)")
                nom_stm = st.text_input("Nom STM", placeholder="Ex: Ouessant")
            with col3:
                est_dans_dst = st.checkbox("Dans DST (Dispositif de Séparation du Trafic)")
                nom_dst = st.text_input("Nom DST", placeholder="Ex: Pas-de-Calais")
            with col4:
                distance_cote_metres = st.number_input("Distance côte (m)", min_value=0, value=0)
                distance_cote_milles = st.number_input("Distance côte (NM)", min_value=0.0, value=0.0, format="%.2f")
            
            st.markdown("##### 🌊 Marée et contexte")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                maree_port = st.text_input("Port de marée", placeholder="Ex: Brest, Le Havre")
            with col2:
                maree_coefficient = st.number_input("Coefficient", min_value=20, max_value=120, value=70,
                                                   help="Coefficient de marée: 20-120")
            with col3:
                maree_categorie_options = load_reference_list('maree_categorie')
                maree_categorie = st.selectbox("Catégorie marée", maree_categorie_options,
                                              format_func=lambda x: "Non spécifié" if x is None else x)
            with col4:
                prefecture_maritime_options = load_reference_list('prefecture_maritime')
                prefecture_maritime = st.selectbox("Préfecture maritime", prefecture_maritime_options,
                                                  format_func=lambda x: "Non spécifié" if x is None else x)
            
            add_stats = bool(nb_impliques > 0 or nb_secourues > 0 or nb_deces > 0 or nb_blesses > 0 or 
                           nb_flotteurs_commerce > 0 or nb_flotteurs_peche > 0 or nb_flotteurs_plaisance > 0)
        
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
                            
                            if add_flotteur:
                                flotteur_data = {
                                    "operation_id": operation_id,
                                    "numero_ordre": numero_ordre,
                                    "pavillon": pavillon if pavillon else None,
                                    "type_flotteur": type_flotteur if type_flotteur else "Non spécifié",
                                    "categorie_flotteur": categorie_flotteur if categorie_flotteur else "Non spécifié",
                                    "resultat_flotteur": resultat_flotteur if resultat_flotteur else "Non spécifié",
                                    "numero_immatriculation": numero_immat if numero_immat else None,
                                }
                                insert_flotteur(flotteur_data)
                                st.success("✅ Flotteur ajouté")
                            
                            if add_humain:
                                humain_data = {
                                    "operation_id": operation_id,
                                    "categorie_personne": categorie_personne if categorie_personne else "Non spécifié",
                                    "resultat_humain": resultat_humain if resultat_humain else "Non spécifié",
                                    "nombre": nombre,
                                    "dont_nombre_blesse": dont_nombre_blesse if dont_nombre_blesse else 0,
                                }
                                insert_resultat_humain(humain_data)
                                st.success("✅ Résultat humain ajouté")
                            
                            if add_stats:
                                from datetime import date as date_type
                                operation_date = date_alerte
                                
                                stats_data = {
                                    "operation_id": operation_id,
                                    "date": operation_date,
                                    "annee": operation_date.year,
                                    "mois": operation_date.month,
                                    "jour": operation_date.day,
                                    "mois_texte": operation_date.strftime("%B"),
                                    "semaine": operation_date.isocalendar()[1],
                                    "annee_semaine": f"{operation_date.year}-W{operation_date.isocalendar()[1]:02d}",
                                    "jour_semaine": operation_date.strftime("%A"),
                                    "est_weekend": operation_date.weekday() >= 5,
                                    "est_jour_ferie": False,
                                    "est_vacances_scolaires": None,
                                    "phase_journee": None,
                                    "concerne_plongee": concerne_plongee,
                                    "implique_wingfoil": implique_wingfoil,
                                    "avec_clandestins": avec_clandestins,
                                    "distance_cote_metres": distance_cote_metres if distance_cote_metres > 0 else None,
                                    "distance_cote_milles_nautiques": distance_cote_milles if distance_cote_milles > 0 else None,
                                    "est_dans_stm": est_dans_stm,
                                    "nom_stm": nom_stm if nom_stm else None,
                                    "est_dans_dst": est_dans_dst,
                                    "nom_dst": nom_dst if nom_dst else None,
                                    "prefecture_maritime": prefecture_maritime if prefecture_maritime else None,
                                    "maree_port": maree_port if maree_port else None,
                                    "maree_coefficient": maree_coefficient if maree_coefficient else None,
                                    "maree_categorie": maree_categorie if maree_categorie else None,
                                    
                                    # Indicateurs humains
                                    "nombre_personnes_blessees": nb_blesses,
                                    "nombre_personnes_assistees": nb_assistees,
                                    "nombre_personnes_decedees": nb_deces,
                                    "nombre_personnes_decedees_accidentellement": nb_deces_accidentel,
                                    "nombre_personnes_decedees_naturellement": nb_deces_naturel,
                                    "nombre_personnes_disparues": nb_disparues,
                                    "nombre_personnes_impliquees_dans_fausse_alerte": nb_fausse_alerte,
                                    "nombre_personnes_retrouvees": nb_retrouvees,
                                    "nombre_personnes_secourues": nb_secourues,
                                    "nombre_personnes_tirees_daffaire_seule": nb_tirees_affaire,
                                    "nombre_personnes_tous_deces": nb_deces,
                                    "nombre_personnes_tous_deces_ou_disparues": nb_deces_disparues,
                                    "nombre_personnes_impliquees": nb_impliques,
                                    
                                    # Sans clandestins (mêmes valeurs si pas de clandestins)
                                    "nombre_personnes_blessees_sans_clandestins": nb_blesses if not avec_clandestins else 0,
                                    "nombre_personnes_assistees_sans_clandestins": nb_assistees if not avec_clandestins else 0,
                                    "nombre_personnes_decedees_sans_clandestins": nb_deces if not avec_clandestins else 0,
                                    "nombre_personnes_decedees_accidentellement_sans_clandestins": nb_deces_accidentel if not avec_clandestins else 0,
                                    "nombre_personnes_decedees_naturellement_sans_clandestins": nb_deces_naturel if not avec_clandestins else 0,
                                    "nombre_personnes_disparues_sans_clandestins": nb_disparues if not avec_clandestins else 0,
                                    "nombre_personnes_impliquees_dans_fausse_alerte_sans_clandestins": nb_fausse_alerte if not avec_clandestins else 0,
                                    "nombre_personnes_retrouvees_sans_clandestins": nb_retrouvees if not avec_clandestins else 0,
                                    "nombre_personnes_secourues_sans_clandestins": nb_secourues if not avec_clandestins else 0,
                                    "nombre_personnes_tirees_daffaire_seule_sans_clandestins": nb_tirees_affaire if not avec_clandestins else 0,
                                    "nombre_personnes_tous_deces_sans_clandestins": nb_deces if not avec_clandestins else 0,
                                    "nombre_personnes_tous_deces_ou_disparues_sans_clandestins": nb_deces_disparues if not avec_clandestins else 0,
                                    "nombre_personnes_impliquees_sans_clandestins": nb_impliques if not avec_clandestins else 0,
                                    
                                    # Flotteurs
                                    "nombre_flotteurs_commerce_impliques": nb_flotteurs_commerce,
                                    "nombre_flotteurs_peche_impliques": nb_flotteurs_peche,
                                    "nombre_flotteurs_plaisance_impliques": nb_flotteurs_plaisance,
                                    "nombre_flotteurs_loisirs_nautiques_impliques": nb_flotteurs_loisirs,
                                    "nombre_aeronefs_impliques": nb_aeronefs,
                                    "nombre_flotteurs_autre_impliques": nb_flotteurs_autre,
                                    "nombre_flotteurs_annexe_impliques": 0,
                                    "nombre_flotteurs_autre_loisir_nautique_impliques": 0,
                                    "nombre_flotteurs_canoe_kayak_aviron_impliques": 0,
                                    "nombre_flotteurs_engin_de_plage_impliques": 0,
                                    "nombre_flotteurs_kitesurf_impliques": 0,
                                    "nombre_flotteurs_plaisance_voile_legere_impliques": 0,
                                    "nombre_flotteurs_plaisance_a_moteur_impliques": nb_plaisance_moteur,
                                    "nombre_flotteurs_plaisance_a_moteur_moins_8m_impliques": 0,
                                    "nombre_flotteurs_plaisance_a_moteur_plus_8m_impliques": 0,
                                    "nombre_flotteurs_plaisance_a_voile_impliques": nb_plaisance_voile,
                                    "nombre_flotteurs_planche_a_voile_impliques": 0,
                                    "nombre_flotteurs_ski_nautique_impliques": 0,
                                    "nombre_flotteurs_surf_impliques": 0,
                                    "nombre_flotteurs_vehicule_nautique_a_moteur_impliques": 0,
                                    
                                    # Sans flotteur
                                    "sans_flotteur_implique": not add_flotteur,
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
                        pavillon_options_edit = load_reference_list('pavillon')
                        pavillon = st.selectbox("Pavillon", pavillon_options_edit,
                                              format_func=lambda x: "Non spécifié" if x is None else x,
                                              key="edit_pavillon")
                    with col2:
                        type_flotteur = st.text_input("Type", placeholder="Voilier")
                        categorie_flotteur_options_edit = load_reference_list('categorie_flotteur')
                        categorie_flotteur = st.selectbox("Catégorie", categorie_flotteur_options_edit,
                                                        format_func=lambda x: "Non spécifié" if x is None else x,
                                                        key="edit_categorie_flotteur")
                    with col3:
                        resultat_flotteur_options_edit = load_reference_list('resultat_flotteur')
                        resultat_flotteur = st.selectbox("Résultat", resultat_flotteur_options_edit,
                                                       format_func=lambda x: "Non spécifié" if x is None else x,
                                                       key="edit_resultat_flotteur")
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
