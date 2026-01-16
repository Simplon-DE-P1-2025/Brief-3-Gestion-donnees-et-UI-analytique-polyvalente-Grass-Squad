"""
Composant de pagination réutilisable
"""
import streamlit as st
from typing import List, Union


def render_pagination(
    page_number: int,
    total_pages: int,
    total_items: int,
    items_per_page: int,
    offset: int
) -> None:
    """
    Affiche le composant de pagination avec navigation
    
    Args:
        page_number: Numéro de page actuel
        total_pages: Nombre total de pages
        total_items: Nombre total d'éléments
        items_per_page: Nombre d'éléments par page
        offset: Offset actuel pour la pagination
    """
    # Séparateur
    st.markdown(
        '<hr style="margin: 0.5rem 0; border: none; border-top: 1px solid rgba(255,255,255,0.1);">',
        unsafe_allow_html=True
    )
    
    # Calcul des éléments affichés
    start_item = offset + 1
    end_item = min(offset + items_per_page, total_items)
    
    # Affichage des informations
    st.markdown(
        f"<div style='text-align: center; margin-bottom: 1rem; color: rgba(255, 255, 255, 0.8);'>"
        f"<small>📄 Affichage {start_item}-{end_item} sur <strong>{total_items}</strong> opération(s)</small>"
        f"</div>",
        unsafe_allow_html=True
    )
    
    # Navigation par pages avec icônes
    pagination_cols = st.columns([0.8, 0.5, 3, 0.5, 0.8])
    
    # Bouton Première page
    with pagination_cols[0]:
        if page_number > 1:
            if st.button("⏮️", width="stretch", help="Première page", key="first_page"):
                st.session_state.page_number = 1
                st.rerun()
    
    # Bouton Précédent
    with pagination_cols[1]:
        if page_number > 1:
            if st.button("◀️", width="stretch", help="Page précédente", key="prev_page"):
                st.session_state.page_number = page_number - 1
                st.rerun()
    
    # Numéros de pages
    with pagination_cols[2]:
        _render_page_numbers(page_number, total_pages)
    
    # Bouton Suivant
    with pagination_cols[3]:
        if page_number < total_pages:
            if st.button("▶️", width="stretch", help="Page suivante", key="next_page"):
                st.session_state.page_number = page_number + 1
                st.rerun()
    
    # Bouton Dernière page
    with pagination_cols[4]:
        if page_number < total_pages:
            if st.button("⏭️", width="stretch", help="Dernière page", key="last_page"):
                st.session_state.page_number = total_pages
                st.rerun()


def _render_page_numbers(page_number: int, total_pages: int, max_visible: int = 5) -> None:
    """
    Affiche les numéros de pages avec ellipse si nécessaire
    
    Args:
        page_number: Numéro de page actuel
        total_pages: Nombre total de pages
        max_visible: Nombre maximum de pages visibles
    """
    # Déterminer quelles pages afficher
    if total_pages <= max_visible:
        pages_to_show: List[Union[int, str]] = list(range(1, total_pages + 1))
    else:
        pages_to_show = []
        pages_to_show.append(1)
        
        start = max(2, page_number - 1)
        end = min(total_pages - 1, page_number + 1)
        
        if start > 2:
            pages_to_show.append('...')
        
        for p in range(start, end + 1):
            pages_to_show.append(p)
        
        if end < total_pages - 1:
            pages_to_show.append('...')
        
        if total_pages > 1:
            pages_to_show.append(total_pages)
    
    # Créer les boutons de pages
    page_cols = st.columns(len(pages_to_show))
    
    for idx, page in enumerate(pages_to_show):
        with page_cols[idx]:
            if page == '...':
                st.markdown(
                    "<div style='text-align: center; padding: 0.3rem; color: #adb5bd; font-weight: bold;'>⋯</div>",
                    unsafe_allow_html=True
                )
            elif page == page_number:
                st.button(
                    str(page),
                    key=f"page_{page}_active",
                    disabled=True,
                    width="stretch",
                    type="primary"
                )
            else:
                if st.button(
                    str(page),
                    key=f"page_{page}",
                    width="stretch"
                ):
                    st.session_state.page_number = page
                    st.rerun()
