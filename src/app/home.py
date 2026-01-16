import streamlit as st
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))


# ========================================
# CONFIGURATION DE LA PAGE
# ========================================
st.set_page_config(
    page_title="Gestion Opérations Maritimes",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ========================================
# HEADER
# ========================================
col_logo, col_title = st.columns([1, 5])

with col_title:
    st.title("Plateforme de Gestion des Opérations Maritimes SECMAR")

st.divider()

# ========================================
# STATISTIQUES GLOBALES
# ========================================
st.subheader("📊 Vue d'ensemble")

try:
    from src.app.utils.data_loader import get_operations_count, get_stats_totals
    
    total_ops = get_operations_count()
    stats = get_stats_totals()
    total_saved = stats['total_secourus'].iloc[0] if 'total_secourus' in stats.columns else 0
    total_deceased = stats['total_deces'].iloc[0] if 'total_deces' in stats.columns else 0
    total_missing = stats['total_disparus'].iloc[0] if 'total_disparus' in stats.columns else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🚢 Opérations",
            value=f"{total_ops:,}",
            help="Nombre total d'opérations enregistrées"
        )
    
    with col2:
        st.metric(
            label="✅ Personnes Secourues",
            value=f"{int(total_saved):,}",
            delta="Secourues avec succès",
            help="Nombre total de personnes secourues"
        )
    
    with col3:
        st.metric(
            label="⚠️ Décès",
            value=f"{int(total_deceased):,}",
            delta=None,
            help="Nombre total de décès"
        )
    
    with col4:
        st.metric(
            label="🔍 Disparitions",
            value=f"{int(total_missing):,}",
            help="Nombre total de personnes disparues"
        )

except Exception as e:
    st.warning("⚠️ Impossible de charger les statistiques. Vérifiez la connexion à la base de données.")
    st.caption(f"Détails: {e}")


# ========================================
# NAVIGATION RAPIDE
# ========================================
st.markdown("---")

# Accès rapide en footer
st.markdown("### 🔗 Accès Rapide")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    if st.button("📊 Dashboard", width="stretch", type="secondary"):
        st.switch_page("pages/01_Dashboard.py")

with col2:
    if st.button("🚢 Opérations", width="stretch", type="secondary"):
        st.switch_page("pages/02_Operations.py")

with col3:
    if st.button("🛡️ Audit", width="stretch", type="secondary"):
        st.switch_page("pages/03_Audit.py")

with col4:
    if st.button("⚙️ Admin", width="stretch", type="secondary"):
        st.switch_page("pages/04_Admin.py")

with col5:
    if st.button("📐 Schéma", width="stretch", type="secondary"):
        st.switch_page("pages/05_Schema.py")
st.divider()

# ========================================
# INFORMATIONS SYSTÈME
# ========================================
st.subheader("🗄️ Architecture de la Base de Données")

col1, col2, col3, col4 = st.columns(4)

with col1:
    with st.container():
        st.markdown("""
        <div style="background-color: #e8f4f8; padding: 15px; border-radius: 8px; border-left: 4px solid #2196F3;">
            <h4 style="margin: 0; color: #1976D2;">📋 Operations</h4>
        </div>
        """, unsafe_allow_html=True)
        st.caption("Table principale contenant toutes les opérations maritimes avec leurs détails complets")
        st.metric("Colonnes", "26+", help="Informations complètes sur chaque opération")

with col2:
    with st.container():
        st.markdown("""
        <div style="background-color: #fff3e0; padding: 15px; border-radius: 8px; border-left: 4px solid #FF9800;">
            <h4 style="margin: 0; color: #F57C00;">⚓ Flotteurs</h4>
        </div>
        """, unsafe_allow_html=True)
        st.caption("Informations sur les navires et embarcations impliqués dans les opérations")
        st.metric("Colonnes", "7", help="Types, pavillons, résultats des flotteurs")

with col3:
    with st.container():
        st.markdown("""
        <div style="background-color: #f3e5f5; padding: 15px; border-radius: 8px; border-left: 4px solid #9C27B0;">
            <h4 style="margin: 0; color: #7B1FA2;">👥 Résultats Humain</h4>
        </div>
        """, unsafe_allow_html=True)
        st.caption("Données sur les personnes impliquées et les résultats humains")
        st.metric("Colonnes", "5", help="Catégories, résultats, nombres")

with col4:
    with st.container():
        st.markdown("""
        <div style="background-color: #e8f5e9; padding: 15px; border-radius: 8px; border-left: 4px solid #4CAF50;">
            <h4 style="margin: 0; color: #388E3C;">📊 Operations Stats</h4>
        </div>
        """, unsafe_allow_html=True)
        st.caption("Statistiques et métriques agrégées par opération")
        st.metric("Colonnes", "60+", help="KPIs calculés et agrégations")

st.divider()

# ========================================
# FOOTER
# ========================================


st.markdown("""
<div style="text-align: center; padding: 20px; color: #666; margin-top: 20px;">
    <p><strong>💡 Astuce:</strong> Utilisez le menu latéral pour naviguer entre les différentes sections</p>
</div>
""", unsafe_allow_html=True)


