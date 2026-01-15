"""
Composant de table pour l'affichage des opérations
"""
import streamlit as st
import pandas as pd
from ..utils.formatters import format_datetime, format_coordinates, format_text
from .styles import get_row_separator_html


def render_table_header() -> None:
    """Affiche l'en-tête du tableau des opérations"""
    st.markdown('<h4 style="margin-bottom: 0.5rem;">📋 Tableau des Opérations</h4>', unsafe_allow_html=True)
    
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
    
    st.markdown(
        '<hr style="margin: 0.3rem 0; border: none; border-top: 1px solid rgba(255,255,255,0.1);">',
        unsafe_allow_html=True
    )


def render_table_row(row: pd.Series, is_last: bool = False) -> None:
    """
    Affiche une ligne du tableau des opérations
    
    Args:
        row: Série pandas contenant les données de la ligne
        is_last: Indique si c'est la dernière ligne (pas de séparateur)
    """
    col1, col2, col3, col4, col5, col6, col7 = st.columns([0.6, 0.8, 1.2, 1.2, 0.6, 0.8, 1.0])
    
    with col1:
        st.text(row['operation_id'])
    
    with col2:
        st.text(row['cross'])
    
    with col3:
        evenement = format_text(row['evenement'], max_length=20)
        st.text(evenement)
    
    with col4:
        date_formatted = format_datetime(row['date_heure_reception_alerte'])
        st.text(date_formatted)
    
    with col5:
        dept = format_text(row['departement'])
        st.text(dept)
    
    with col6:
        coords = format_coordinates(row['latitude'], row['longitude'])
        st.text(coords)
    
    with col7:
        _render_action_buttons(row['operation_id'])
    
    # Ligne de séparation légère
    if not is_last:
        st.markdown(get_row_separator_html(), unsafe_allow_html=True)


def _render_action_buttons(operation_id: int) -> None:
    """
    Affiche les boutons d'action pour une opération
    
    Args:
        operation_id: ID de l'opération
    """
    btn_col1, btn_col2, btn_col3 = st.columns(3)
    
    with btn_col1:
        if st.button("👁️", key=f"view_{operation_id}", help="Consulter"):
            st.session_state.selected_operation_id = operation_id
            st.session_state.action = 'view'
            st.rerun()
    
    with btn_col2:
        if st.button("✏️", key=f"edit_{operation_id}", help="Modifier"):
            st.session_state.selected_operation_id = operation_id
            st.session_state.action = 'edit'
            st.rerun()
    
    with btn_col3:
        if st.button("🗑️", key=f"delete_{operation_id}", help="Supprimer"):
            st.session_state.selected_operation_id = operation_id
            st.session_state.action = 'delete'
            st.rerun()


def render_table_statistics(df_operations: pd.DataFrame, total_operations: int) -> None:
    """
    Affiche les statistiques sous le tableau
    
    Args:
        df_operations: DataFrame des opérations affichées
        total_operations: Nombre total d'opérations
    """
    st.markdown("---")
    col_s1, col_s2, col_s3 = st.columns(3)
    
    col_s1.metric("📊 Total opérations", total_operations)
    
    # Compter par CROSS
    cross_counts = df_operations['cross'].value_counts()
    if len(cross_counts) > 0:
        col_s2.metric("🏆 CROSS le plus actif", f"{cross_counts.index[0]} ({cross_counts.values[0]})")
    
    # Opérations affichées
    col_s3.metric("🆕 Opérations affichées", len(df_operations))
