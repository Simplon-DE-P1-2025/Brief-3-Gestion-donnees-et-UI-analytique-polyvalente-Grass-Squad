"""
Vue optimisée pour la liste des opérations
Sépare la logique de présentation pour améliorer les performances
"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Ajouter le chemin du projet
PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(PROJECT_ROOT))

from src.database.load_database import engine
from src.app.utils.queries import OperationsQueries
from src.app.utils.session_state import init_session_state, reset_pagination, clear_search
from src.app.utils.formatters import format_datetime
from src.app.components.styles import get_compact_table_css, get_separator_html
from src.app.components.pagination import render_pagination
from src.app.components.table import (
    render_table_header,
    render_table_row,
    render_table_statistics
)


def show_operations_grid():
    """Affiche la table des opérations avec pagination optimisée"""
    st.subheader("📋 Liste des Opérations")
    
    # Initialiser le session state
    init_session_state()
    
    # Afficher les contrôles
    _render_controls()
    _render_sort_controls()
    
    # Sélecteur d'éléments par page
    _render_items_per_page_selector()
    
    # Charger et afficher les données
    try:
        # Récupérer les paramètres
        search_id = st.session_state.search_operation_id
        search_column = st.session_state.search_column
        items_per_page = st.session_state.items_per_page
        page_number = st.session_state.page_number
        sort_column = st.session_state.sort_column
        sort_direction = st.session_state.sort_direction
        
        # Compter le total d'opérations
        search_pattern = search_id.strip() if search_id and search_id.strip() else None
        total_operations = OperationsQueries.count_operations(engine, search_pattern, search_column)
        
        # Calculer le nombre de pages
        total_pages = max(1, (total_operations + items_per_page - 1) // items_per_page)
        
        # Vérifier que le numéro de page est valide
        if page_number > total_pages:
            st.session_state.page_number = total_pages
            page_number = total_pages
        
        # Calculer l'offset
        offset = (page_number - 1) * items_per_page
        
        # Récupérer les opérations avec pagination
        df_operations = OperationsQueries.get_operations_paginated(
            engine,
            limit=items_per_page,
            offset=offset,
            search_pattern=search_pattern,
            search_column=search_column,
            sort_column=sort_column,
            sort_direction=sort_direction
        )
        
        # Afficher indicateur de recherche
        if search_pattern and len(df_operations) > 0:
            st.info(f"🔍 {len(df_operations)} opération(s) trouvée(s) - {search_column}: '{search_id}'")
        elif search_pattern and len(df_operations) == 0:
            st.warning(f"❌ Aucune opération trouvée avec {search_column} contenant '{search_id}'")
            return
        
        if len(df_operations) == 0:
            st.info("Aucune opération trouvée dans la base de données")
            return
        
        # Formater la date pour l'affichage
        df_operations['date_heure_reception_alerte'] = pd.to_datetime(
            df_operations['date_heure_reception_alerte']
        ).dt.strftime('%Y-%m-%d %H:%M')
        
        # Afficher le tableau
        _render_operations_table(df_operations)
        
        # Afficher la pagination
        render_pagination(
            page_number=page_number,
            total_pages=total_pages,
            total_items=total_operations,
            items_per_page=items_per_page,
            offset=offset
        )
        
        # Afficher les statistiques
        render_table_statistics(df_operations, total_operations)
    
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement des opérations : {e}")
        st.exception(e)


def _render_controls():
    """Affiche les boutons de contrôle et la recherche"""
    col_btn1, col_btn2, col_search = st.columns([1, 1, 2])
    
    with col_btn1:
        if st.button("➕ Créer une nouvelle opération", type="primary", use_container_width=True):
            st.session_state.action = 'create'
            st.rerun()
    
    with col_btn2:
        if st.button("🔄 Rafraîchir", use_container_width=True, help="Actualise la page et réinitialise tous les filtres et recherches"):
            # Réinitialiser tous les filtres et recherches
            clear_search()
            st.session_state.search_operation_id = ""
            st.session_state.search_column = "operation_id"
            st.session_state.sort_column = "operation_id"
            st.session_state.sort_direction = "DESC"
            reset_pagination()
            st.rerun()
    
    with col_search:
        col_search_select, col_search_input = st.columns([1, 2])
        with col_search_select:
            search_column = st.selectbox(
                "Colonne",
                options=["operation_id", "cross", "type_operation", "evenement", "autorite", "departement"],
                index=0,
                key="search_column_select",
                label_visibility="collapsed"
            )
            if 'search_column' not in st.session_state or search_column != st.session_state.search_column:
                st.session_state.search_column = search_column
                st.session_state.search_operation_id = ""
                reset_pagination()
        
        with col_search_input:
            search_id = st.text_input(
                "Recherche",
                value=st.session_state.search_operation_id,
                placeholder=f"🔍 Rechercher par {search_column}...",
                key="search_input",
                help="La recherche se met à jour automatiquement pendant que vous tapez",
                label_visibility="collapsed"
            )
            if search_id != st.session_state.search_operation_id:
                reset_pagination()
            st.session_state.search_operation_id = search_id


def _render_sort_controls():
    """Contrôles de tri pour la table des opérations"""
    options = [
        ("Date alerte", "date_heure_reception_alerte"),
        ("ID", "operation_id"),
        ("Cross", "cross"),
        ("Évènement", "evenement"),
        ("Département", "departement"),
    ]
    labels = {value: label for label, value in options}
    col_sort1, col_sort2 = st.columns([2, 1])

    with col_sort1:
        selected_column = st.selectbox(
            "Trier par",
            options=[value for _, value in options],
            index=[value for _, value in options].index(st.session_state.sort_column)
            if st.session_state.sort_column in [value for _, value in options]
            else 0,
            format_func=lambda v: labels.get(v, v),
            key="sort_column_select",
            help="Choisissez la colonne utilisée pour trier la liste"
        )
        st.session_state.sort_column = selected_column

    with col_sort2:
        selected_direction = st.radio(
            "Ordre",
            options=["DESC", "ASC"],
            index=["DESC", "ASC"].index(st.session_state.sort_direction)
            if st.session_state.sort_direction in ["DESC", "ASC"]
            else 0,
            horizontal=True,
            key="sort_direction_radio",
            help="Ordre de tri croissant ou décroissant"
        )
        st.session_state.sort_direction = selected_direction


def _render_items_per_page_selector():
    """Affiche le sélecteur d'éléments par page"""
    col_pagination1, col_pagination2 = st.columns([1, 3])
    
    with col_pagination1:
        items_per_page = st.selectbox(
            "Éléments par page",
            options=[10, 25, 50, 100],
            index=[10, 25, 50, 100].index(st.session_state.items_per_page),
            key="items_per_page_select"
        )
        if items_per_page != st.session_state.items_per_page:
            st.session_state.items_per_page = items_per_page
            reset_pagination()


def _render_operations_table(df_operations: pd.DataFrame):
    """
    Affiche le tableau des opérations
    
    Args:
        df_operations: DataFrame des opérations à afficher
    """
    # Appliquer le CSS compact
    st.markdown(get_compact_table_css(), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # En-tête du tableau
    render_table_header()
    
    # Lignes du tableau
    for idx, (_, row) in enumerate(df_operations.iterrows()):
        is_last = (idx == len(df_operations) - 1)
        render_table_row(row, is_last=is_last)
