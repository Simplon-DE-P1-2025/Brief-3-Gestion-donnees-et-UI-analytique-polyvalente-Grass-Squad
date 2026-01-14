import streamlit as st
from pathlib import Path
import sys

# Configuration du projet
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

# Configuration de la page principale
st.set_page_config(
    page_title="Grass Squad - Gestion Opérations Maritimes",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Page d'accueil
st.title("🌊 Grass Squad - Gestion des Opérations Maritimes SECMAR")

st.markdown("""
## Bienvenue dans le système de gestion des opérations maritimes

Cette application vous permet de gérer l'ensemble du cycle de vie des opérations maritimes 
avec leurs données associées (flotteurs, résultats humains, statistiques).

### 📋 Fonctionnalités

#### 1. 📊 **Dashboard**
Visualisez les indicateurs clés de performance (KPIs) :
- Nombre total d'opérations
- Personnes secourues
- Statistiques globales
- Carte des opérations géolocalisées

#### 2. 🔍 **Consultation des Données**
Consultez les opérations avec leurs données liées :
- Filtrage par ID d'opération
- Affichage des tables liées (flotteurs, résultats humains, stats)
- Export des données

#### 3. ✏️ **Gestion des Données (CRUD)**
Gérez vos opérations de manière complète :
- **Créer** : Ajouter une nouvelle opération avec toutes ses données liées
- **Lire** : Consulter les détails d'une opération
- **Modifier** : Éditer les données existantes avec validation
- **Supprimer** : Supprimer une opération et ses données associées

#### 4. 🛡️ **Audit & Logs**
- Traçabilité de toutes les modifications
- Logs des opérations CREATE, UPDATE, DELETE
- Schéma de la base de données (ERD)

### 🔐 Validation des Données

Toutes les modifications sont validées avant d'être enregistrées :
- Vérification des types de données
- Contrôle des contraintes NOT NULL
- Validation des contraintes métier
- Messages d'erreur clairs en cas de problème

### 🗄️ Base de Données

**Tables gérées :**
- `operations` : Données principales des opérations
- `flotteurs` : Embarcations impliquées
- `resultats_humain` : Résultats concernant les personnes
- `operations_stats` : Statistiques détaillées

**Relation :** Toutes les tables sont liées par `operation_id`

### 🚀 Navigation

Utilisez le menu latéral pour accéder aux différentes fonctionnalités de l'application.

---

""")

# Statistiques rapides
st.subheader("📈 Aperçu Rapide de la Base de Données")

col1, col2, col3, col4 = st.columns(4)

try:
    from src.database.load_database import engine
    import pandas as pd
    
    # Compter les opérations
    query_ops = "SELECT COUNT(*) as total FROM operations"
    result_ops = pd.read_sql(query_ops, engine)
    total_ops = result_ops['total'].iloc[0]
    
    # Compter les personnes secourues
    query_saved = "SELECT SUM(nombre_personnes_secourues) as total FROM operations_stats"
    result_saved = pd.read_sql(query_saved, engine)
    total_saved = result_saved['total'].iloc[0] or 0
    
    # Compter les flotteurs
    query_flotteurs = "SELECT COUNT(*) as total FROM flotteurs"
    result_flotteurs = pd.read_sql(query_flotteurs, engine)
    total_flotteurs = result_flotteurs['total'].iloc[0]
    
    # Compter les logs d'audit
    query_audit = "SELECT COUNT(*) as total FROM audit_log"
    result_audit = pd.read_sql(query_audit, engine)
    total_audit = result_audit['total'].iloc[0]
    
    col1.metric("🚢 Opérations", f"{total_ops:,}")
    col2.metric("👥 Personnes Secourues", f"{int(total_saved):,}")
    col3.metric("⛵ Flotteurs", f"{total_flotteurs:,}")
    col4.metric("📝 Logs d'Audit", f"{total_audit:,}")
    
    st.success("✅ Connexion à la base de données PostgreSQL établie")
    
    # Dernières opérations
    st.subheader("🕐 Dernières Opérations Enregistrées")
    query_recent = """
    SELECT 
        operation_id,
        "cross",
        evenement,
        date_heure_reception_alerte,
        departement
    FROM operations 
    ORDER BY date_heure_reception_alerte DESC 
    LIMIT 5
    """
    df_recent = pd.read_sql(query_recent, engine)
    st.dataframe(df_recent, use_container_width=True, hide_index=True)
    
except Exception as e:
    st.error(f"❌ Erreur de connexion à la base de données : {e}")
    st.info("Vérifiez que PostgreSQL est en cours d'exécution et que les variables d'environnement sont correctement configurées dans le fichier .env")
    st.code("""
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=votre_mot_de_passe
DB_NAME=secmar_db
    """)

