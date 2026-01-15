import streamlit as st
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

st.set_page_config(
    page_title="Grass Squad - Gestion Opérations Maritimes",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🌊 Grass Squad - Gestion des Opérations Maritimes SECMAR")

st.markdown("""
## Gestion des Opérations Maritimes

### 📋 Fonctionnalités
- **Dashboard** : KPIs et statistiques globales
- **Consultation** : Recherche et filtrage des opérations
- **CRUD** : Créer, modifier, supprimer des opérations
- **Audit** : Traçabilité complète des modifications

### 🗄️ Base de Données
Tables : `operations`, `flotteurs`, `resultats_humain`, `operations_stats`
""")

col1, col2, col3, col4 = st.columns(4)

try:
    from src.app.utils.data_loader import get_operations_count, get_stats_totals
    
    total_ops = get_operations_count()
    stats = get_stats_totals()
    total_saved = stats['total_secourus'].iloc[0] or 0
    
    col1.metric("🚢 Opérations", f"{total_ops:,}")
    col2.metric("✅ Personnes Secourues", f"{total_saved:,}")
    col3.metric("📊 Tables", "4")
    col4.metric("🛡️ Audit", "Actif")

except Exception as e:
    st.error(f"❌ Impossible de charger les statistiques : {e}")

st.info("💡 Utilisez le menu latéral pour naviguer")


