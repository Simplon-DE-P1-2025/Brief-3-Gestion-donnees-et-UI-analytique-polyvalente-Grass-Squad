"""
Page d'administration pour gérer les listes de référence prédéfinies
"""
import streamlit as st
import pandas as pd
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(PROJECT_ROOT))

from src.app.utils.session_state import init_session_state
from src.crud.reference_lists_crud import (
    get_reference_list_values,
    get_all_categories,
    insert_reference_list_value,
    update_reference_list_value,
    delete_reference_list_value,
    toggle_reference_list_status,
    get_reference_list_by_id
)
from src.database.load_database import get_db_connection

init_session_state()
st.session_state.current_page = 'admin'

@st.cache_data(ttl=120)
def get_categories_with_counts():
    """Récupère toutes les catégories avec leur nombre de valeurs en une seule requête"""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT category, COUNT(*) as count
            FROM reference_lists
            GROUP BY category
            ORDER BY category
        """)
        return {row[0]: row[1] for row in cur.fetchall()}
    finally:
        cur.close()
        conn.close()

st.set_page_config(page_title="Administration", page_icon="⚙️", layout="wide")

# Initialiser session_state
if 'admin_action' not in st.session_state:
    st.session_state.admin_action = 'list'
if 'selected_category' not in st.session_state:
    st.session_state.selected_category = None
if 'selected_ref_id' not in st.session_state:
    st.session_state.selected_ref_id = None

st.title("⚙️ Administration - Listes de Référence")

# Menu de navigation
menu = st.radio(
    "Navigation",
    ["📚 Listes de Référence", "🛡️ Gestion Audit"],
    horizontal=True,
    label_visibility="collapsed"
)

# Descriptions des catégories
CATEGORY_DESCRIPTIONS = {
    'type_operation': 'Types d\'opération (SAR, MAS, etc.)',
    'pavillon': 'Pavillons des navires (Français, Étranger)',
    'categorie_flotteur': 'Catégories de flotteurs (Commerce, Pêche, etc.)',
    'resultat_flotteur': 'Résultats possibles pour les flotteurs',
    'categorie_personne': 'Catégories de personnes impliquées',
    'resultat_humain': 'Résultats humains (Secouru, Décédé, etc.)',
    'vent_direction_categorie': 'Directions cardinales du vent',
    'systeme_source': 'Systèmes source des données',
    'prefecture_maritime': 'Préfectures maritimes',
    'maree_categorie': 'Catégories de coefficient de marée',
    'cross': 'Centres régionaux opérationnels de surveillance et de sauvetage'
}

# ========================================
# FONCTION: AFFICHER LA LISTE DES CATÉGORIES
# ========================================
def show_categories_list():
    """Affiche toutes les catégories disponibles"""
    st.subheader("📚 Gestion des Listes de Référence")
    
    st.info("💡 Sélectionnez une catégorie pour gérer ses valeurs")
    
    try:
        categories = get_all_categories()
        
        if not categories:
            st.warning("Aucune catégorie trouvée. Exécutez le script de création de la base de données.")
            return
        
        # Récupérer tous les compteurs en une seule requête
        category_counts = get_categories_with_counts()
        
        # Afficher les catégories en cartes
        cols = st.columns(3)
        for idx, category in enumerate(categories):
            with cols[idx % 3]:
                description = CATEGORY_DESCRIPTIONS.get(category, "Aucune description")
                values_count = category_counts.get(category, 0)
                
                st.markdown(f"""
                <div style="border: 1px solid #ddd; border-radius: 5px; padding: 15px; margin: 10px 0;">
                    <h4 style="margin-top: 0;">{category}</h4>
                    <p style="font-size: 0.9em; color: #666;">{description}</p>
                    <p style="font-size: 0.85em;"><strong>{values_count}</strong> valeur(s)</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"✏️ Gérer", key=f"manage_{category}", use_container_width=True):
                    st.session_state.admin_action = 'manage_category'
                    st.session_state.selected_category = category
                    st.rerun()
    
    except Exception as e:
        st.error(f"Erreur lors du chargement des catégories: {e}")

# ========================================
# FONCTION: GÉRER UNE CATÉGORIE
# ========================================
def manage_category():
    """Affiche et gère les valeurs d'une catégorie"""
    category = st.session_state.selected_category
    
    # Bouton retour
    if st.button("← Retour aux catégories"):
        st.session_state.admin_action = 'list'
        st.session_state.selected_category = None
        st.rerun()
    
    st.subheader(f"📝 Gestion: {category}")
    st.caption(CATEGORY_DESCRIPTIONS.get(category, ""))
    
    # Bouton pour ajouter une nouvelle valeur
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("➕ Ajouter une valeur", type="primary", use_container_width=True):
            st.session_state.admin_action = 'add_value'
            st.rerun()
    
    # Récupérer toutes les valeurs (actives et inactives)
    try:
        values = get_reference_list_values(category, active_only=False)
        
        if not values:
            st.info("Aucune valeur dans cette catégorie. Ajoutez-en une!")
            return
        
        # Créer un DataFrame pour affichage
        df_data = []
        for val in values:
            if len(val) == 4:  # avec is_active
                ref_id, value, description, is_active = val
            else:
                ref_id, value, description = val
                is_active = True
            
            df_data.append({
                'ID': ref_id,
                'Valeur': value,
                'Description': description or '',
                'Statut': '🟢 Actif' if is_active else '🔴 Inactif'
            })
        
        df = pd.DataFrame(df_data)
        
        # Afficher le tableau
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Actions sur les valeurs
        st.markdown("---")
        st.subheader("Actions")
        
        # Sélectionner une valeur pour la modifier/supprimer
        selected_value = st.selectbox(
            "Sélectionner une valeur à modifier ou supprimer:",
            options=[val[1] for val in values],
            format_func=lambda x: x
        )
        
        if selected_value:
            # Trouver l'ID correspondant
            selected_id = next(val[0] for val in values if val[1] == selected_value)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("✏️ Modifier", key=f"edit_{selected_id}", use_container_width=True):
                    st.session_state.admin_action = 'edit_value'
                    st.session_state.selected_ref_id = selected_id
                    st.rerun()
            
            with col2:
                if st.button("🔄 Activer/Désactiver", key=f"toggle_{selected_id}", use_container_width=True):
                    if toggle_reference_list_status(selected_id):
                        get_categories_with_counts.clear()
                        st.success("Statut modifié avec succès!")
                        st.rerun()
                    else:
                        st.error("Erreur lors du changement de statut")
            
            with col3:
                if st.button("🗑️ Supprimer", key=f"delete_{selected_id}", type="secondary", use_container_width=True):
                    if delete_reference_list_value(selected_id):
                        get_categories_with_counts.clear()
                        st.success(f"Valeur '{selected_value}' supprimée!")
                        st.rerun()
                    else:
                        st.error("Erreur lors de la suppression")
    
    except Exception as e:
        st.error(f"Erreur lors du chargement des valeurs: {e}")

# ========================================
# FONCTION: AJOUTER UNE VALEUR
# ========================================
def add_value_form():
    """Formulaire pour ajouter une nouvelle valeur"""
    category = st.session_state.selected_category
    
    # Bouton retour
    if st.button("← Retour"):
        st.session_state.admin_action = 'manage_category'
        st.rerun()
    
    st.subheader(f"➕ Ajouter une valeur à: {category}")
    
    with st.form("add_value_form"):
        value = st.text_input("Valeur*", placeholder="Ex: SAR, Français, etc.", help="Valeur obligatoire")
        description = st.text_area("Description (optionnel)", placeholder="Description de cette valeur")
        
        # Récupérer le dernier display_order
        existing_values = get_reference_list_values(category, active_only=False)
        max_order = len(existing_values)
        
        display_order = st.number_input("Ordre d'affichage", min_value=0, value=max_order + 1, 
                                        help="Ordre dans lequel cette valeur apparaîtra dans les listes")
        
        submitted = st.form_submit_button("💾 Enregistrer", type="primary", use_container_width=True)
        
        if submitted:
            if not value:
                st.error("La valeur est obligatoire!")
            else:
                result = insert_reference_list_value(category, value, display_order, description)
                if result:
                    get_categories_with_counts.clear()
                    st.success(f"Valeur '{value}' ajoutée avec succès!")
                    st.session_state.admin_action = 'manage_category'
                    st.rerun()
                else:
                    st.error("Erreur lors de l'ajout (la valeur existe peut-être déjà)")

# ========================================
# FONCTION: MODIFIER UNE VALEUR
# ========================================
def edit_value_form():
    """Formulaire pour modifier une valeur existante"""
    ref_id = st.session_state.selected_ref_id
    
    # Bouton retour
    if st.button("← Retour"):
        st.session_state.admin_action = 'manage_category'
        st.session_state.selected_ref_id = None
        st.rerun()
    
    st.subheader("✏️ Modifier une valeur")
    
    # Charger les données actuelles
    current_data = get_reference_list_by_id(ref_id)
    if not current_data:
        st.error("Valeur introuvable")
        return
    
    ref_id, category, current_value, current_order, current_active, current_desc = current_data
    
    with st.form("edit_value_form"):
        st.info(f"Catégorie: **{category}**")
        
        value = st.text_input("Valeur*", value=current_value)
        description = st.text_area("Description", value=current_desc or "")
        display_order = st.number_input("Ordre d'affichage", min_value=0, value=current_order)
        is_active = st.checkbox("Actif", value=current_active)
        
        submitted = st.form_submit_button("💾 Enregistrer les modifications", type="primary", use_container_width=True)
        
        if submitted:
            if not value:
                st.error("La valeur est obligatoire!")
            else:
                result = update_reference_list_value(ref_id, value, display_order, is_active, description)
                if result:
                    get_categories_with_counts.clear()
                    st.success("Valeur modifiée avec succès!")
                    st.session_state.admin_action = 'manage_category'
                    st.session_state.selected_ref_id = None
                    st.rerun()
                else:
                    st.error("Erreur lors de la modification")

# ========================================
# FONCTION: GESTION DE LA TABLE AUDIT
# ========================================
def manage_audit_table():
    """Interface de gestion de la table audit"""
    st.subheader("🛡️ Gestion de la Table Audit")
    
    st.warning("⚠️ **ATTENTION**: Les opérations ci-dessous sont sensibles et irréversibles!")
    
    # Récupérer les statistiques de la table audit
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Récupérer toutes les stats en une seule requête optimisée
        cur.execute("""
            SELECT 
                COUNT(*) as total,
                MIN(created_at) as first_log,
                MAX(created_at) as last_log
            FROM audit_log
        """)
        stats = cur.fetchone()
        count, first_log, last_log = stats if stats else (0, None, None)
        
        # Compter par type d'action
        cur.execute("""
            SELECT action, COUNT(*) 
            FROM audit_log 
            GROUP BY action 
            ORDER BY COUNT(*) DESC
        """)
        actions_count = cur.fetchall()
        
        cur.close()
        conn.close()
        
        # Afficher les statistiques
        st.markdown("### 📊 Statistiques de la table audit_log")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total d'enregistrements", count)
        with col2:
            st.metric("Premier log", first_log.strftime("%d/%m/%Y %H:%M") if first_log else "N/A")
        with col3:
            st.metric("Dernier log", last_log.strftime("%d/%m/%Y %H:%M") if last_log else "N/A")
        
        if actions_count:
            st.markdown("**Répartition par type d'action:**")
            df_actions = pd.DataFrame(actions_count, columns=['Action', 'Nombre'])
            st.dataframe(df_actions, use_container_width=True, hide_index=True)
        
        st.divider()
        
        # Section de vider la table audit
        st.markdown("### 🗑️ Vider la table audit")
        st.info("""
        Cette opération supprimera **tous les enregistrements** de la table audit_log.
        - ✅ La structure de la table sera préservée
        - ❌ Toutes les données d'audit seront perdues
        - ⚠️ **Cette action est irréversible!**
        """)
        
        # Initialiser l'état de confirmation
        if 'confirm_clear_audit' not in st.session_state:
            st.session_state.confirm_clear_audit = False
        
        col_btn1, col_btn2 = st.columns([1, 3])
        
        with col_btn1:
            if not st.session_state.confirm_clear_audit:
                if st.button("🗑️ Vider la table", type="secondary", use_container_width=True):
                    st.session_state.confirm_clear_audit = True
                    st.rerun()
            else:
                st.warning("⚠️ Confirmer?")
                col_yes, col_no = st.columns(2)
                
                with col_yes:
                    if st.button("✅ Oui", type="primary", use_container_width=True):
                        try:
                            conn = get_db_connection()
                            cur = conn.cursor()
                            cur.execute("TRUNCATE TABLE audit_log RESTART IDENTITY CASCADE")
                            conn.commit()
                            cur.close()
                            conn.close()
                            st.success("✅ Table audit_log vidée avec succès!")
                            st.session_state.confirm_clear_audit = False
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Erreur: {e}")
                            st.session_state.confirm_clear_audit = False
                
                with col_no:
                    if st.button("❌ Non", use_container_width=True):
                        st.session_state.confirm_clear_audit = False
                        st.rerun()
        
        st.divider()
        
        # Section de réinitialisation complète
        st.markdown("### 🔄 Réinitialiser la table audit")
        st.info("""
        Cette opération va:
        - 🗑️ Supprimer la table audit_log existante
        - ✨ Recréer la table avec sa structure d'origine
        - 🔄 Réinitialiser les index et contraintes
        - ⚠️ **Cette action est irréversible!**
        """)
        
        # Initialiser l'état de confirmation pour réinitialisation
        if 'confirm_reset_audit' not in st.session_state:
            st.session_state.confirm_reset_audit = False
        
        col_btn3, col_btn4 = st.columns([1, 3])
        
        with col_btn3:
            if not st.session_state.confirm_reset_audit:
                if st.button("🔄 Réinitialiser", type="secondary", use_container_width=True):
                    st.session_state.confirm_reset_audit = True
                    st.rerun()
            else:
                st.warning("⚠️ Confirmer la réinitialisation?")
                col_yes2, col_no2 = st.columns(2)
                
                with col_yes2:
                    if st.button("✅ Confirmer", type="primary", use_container_width=True, key="confirm_reset"):
                        try:
                            conn = get_db_connection()
                            cur = conn.cursor()
                            
                            # Supprimer et recréer la table
                            cur.execute("DROP TABLE IF EXISTS audit_log CASCADE")
                            cur.execute("""
                                CREATE TABLE audit_log (
                                    id SERIAL PRIMARY KEY,
                                    table_name TEXT NOT NULL,
                                    action TEXT NOT NULL,
                                    record_id TEXT NOT NULL,
                                    user_name TEXT DEFAULT 'system',
                                    old_values JSONB,
                                    new_values JSONB,
                                    details TEXT,
                                    sql_query TEXT,
                                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                                )
                            """)
                            
                            # Recréer les index
                            cur.execute("CREATE INDEX idx_audit_log_table_name ON audit_log(table_name)")
                            cur.execute("CREATE INDEX idx_audit_log_action ON audit_log(action)")
                            cur.execute("CREATE INDEX idx_audit_log_created_at ON audit_log(created_at DESC)")
                            cur.execute("CREATE INDEX idx_audit_log_record_id ON audit_log(record_id)")
                            cur.execute("CREATE INDEX idx_audit_log_user_name ON audit_log(user_name)")
                            
                            conn.commit()
                            cur.close()
                            conn.close()
                            
                            st.success("✅ Table audit_log réinitialisée avec succès!")
                            st.session_state.confirm_reset_audit = False
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Erreur: {e}")
                            st.session_state.confirm_reset_audit = False
                
                with col_no2:
                    if st.button("❌ Annuler", use_container_width=True, key="cancel_reset"):
                        st.session_state.confirm_reset_audit = False
                        st.rerun()
    
    except Exception as e:
        st.error(f"❌ Erreur lors de la récupération des statistiques: {e}")
        st.exception(e)

# ========================================
# ROUTING PRINCIPAL
# ========================================
if menu == "📚 Listes de Référence":
    if st.session_state.admin_action == 'list':
        show_categories_list()
    elif st.session_state.admin_action == 'manage_category':
        manage_category()
    elif st.session_state.admin_action == 'add_value':
        add_value_form()
    elif st.session_state.admin_action == 'edit_value':
        edit_value_form()
elif menu == "🛡️ Gestion Audit":
    manage_audit_table()
