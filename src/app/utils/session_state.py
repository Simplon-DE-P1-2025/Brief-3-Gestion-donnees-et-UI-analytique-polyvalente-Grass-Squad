"""
Gestion centralisée du session_state de Streamlit
"""
import streamlit as st


def init_session_state():
    """Initialise toutes les variables de session_state nécessaires"""
    
    # État de navigation
    if 'action' not in st.session_state:
        st.session_state.action = 'list'
    
    if 'selected_operation_id' not in st.session_state:
        st.session_state.selected_operation_id = None
    
    # Pagination
    if 'page_number' not in st.session_state:
        st.session_state.page_number = 1
    
    if 'items_per_page' not in st.session_state:
        st.session_state.items_per_page = 10

    # Tri
    if 'sort_column' not in st.session_state:
        st.session_state.sort_column = "date_heure_reception_alerte"
    if 'sort_direction' not in st.session_state:
        st.session_state.sort_direction = "DESC"
    
    # Recherche
    if 'search_operation_id' not in st.session_state:
        st.session_state.search_operation_id = ""
    
    if 'search_column' not in st.session_state:
        st.session_state.search_column = "operation_id"
    
    # Confirmation de suppression
    if 'show_delete_confirmation' not in st.session_state:
        st.session_state.show_delete_confirmation = False
    
    # Suivi de la page active pour détecter les changements de page
    if 'current_page' not in st.session_state:
        st.session_state.current_page = None


def reset_pagination():
    """Réinitialise la pagination à la page 1"""
    st.session_state.page_number = 1


def navigate_to(action: str, operation_id: int = None):
    """
    Change l'état de navigation
    
    Args:
        action: Action à effectuer ('list', 'view', 'edit', 'create', 'delete')
        operation_id: ID de l'opération (optionnel)
    """
    st.session_state.action = action
    if operation_id is not None:
        st.session_state.selected_operation_id = operation_id
    st.rerun()


def clear_search():
    """Efface la recherche et réinitialise la pagination"""
    st.session_state.search_operation_id = ""
    reset_pagination()
