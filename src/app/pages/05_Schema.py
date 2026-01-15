import streamlit as st
import pandas as pd
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(PROJECT_ROOT))

from src.app.utils.session_state import init_session_state
from src.database.load_database import get_db_connection

st.set_page_config(page_title="Schéma - Grass Squad", page_icon="📐", layout="wide")

init_session_state()
st.session_state.current_page = 'schema'

st.title("📐 Schéma de Base de Données")

st.markdown("""
Cette page affiche la structure complète de la base de données avec:
- **Diagramme ER**: Relations entre toutes les tables
- **Détails des tables**: Colonnes, types, constraints (PK/FK/NOT NULL)
""")

st.divider()

# ========================================
# SECTION 1: DIAGRAMME ER (ASCII ART)
# ========================================
st.subheader("🔗 Diagramme Entité-Relation (ER)")

# Afficher le diagramme ER en ASCII art
er_diagram = """
```
┌─────────────────────────────────────────────────────────────────┐
│                              SCHEMA ER                          │
└─────────────────────────────────────────────────────────────────┘

                         ┌──────────────────┐
                         │   OPERATIONS     │
                         │  (Principal)     │
                         ├──────────────────┤
                         │ PK: operation_id │
                         │    cross         │
                         │    type_op       │
                         │    event         │
                         │    date_alerte   │
                         │    ... (+40 cols)│
                         └────────┬─────────┘
                                  │
                  ┌───────────────┼───────────────┐
                  │               │               │
                  ▼               ▼               ▼
        ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
        │   FLOTTEURS      │ │ RESULTATS_HUMAIN │ │ OPERATIONS_STATS │
        │  (1:N relation)  │ │  (1:N relation)  │ │  (1:1 relation)  │
        ├──────────────────┤ ├──────────────────┤ ├──────────────────┤
        │ PK: flotteur_id  │ │ PK: resultat_id  │ │ PK: stats_id     │
        │ FK: operation_id │ │ FK: operation_id │ │ FK: operation_id │
        │    numero_ordre  │ │    categorie     │ │    date          │
        │    pavillon      │ │    resultat      │ │    nombre_...    │
        │    type          │ │    nombre        │ │    ... (+50 cols)│
        │    ... (8 cols)  │ │    ... (4 cols)  │ │                  │
        └──────────────────┘ └──────────────────┘ └──────────────────┘

                         ┌──────────────────┐
                         │  REFERENCE_LISTS │
                         │  (Lookup tables) │
                         ├──────────────────┤
                         │ PK: id           │
                         │    category      │
                         │    value         │
                         │    is_active     │
                         └──────────────────┘

                         ┌──────────────────┐
                         │   AUDIT_LOG      │
                         │  (Audit trail)   │
                         ├──────────────────┤
                         │ PK: audit_id     │
                         │    table_name    │
                         │    action        │
                         │    old_values    │
                         │    new_values    │
                         │    created_at    │
                         └──────────────────┘
```
"""

st.code(er_diagram, language="text")

# ========================================
# SECTION 2: DÉTAILS DES TABLES
# ========================================
st.subheader("📋 Détails des Tables")

st.markdown("**Sélectionnez une table pour voir les détails des colonnes:**")

# Tables disponibles
tables_info = {
    "operations": {
        "description": "Table principale - Opérations de sauvetage maritime",
        "columns": [
            {"name": "operation_id", "type": "INTEGER", "pk": True, "fk": False, "null": False, "description": "Identifiant unique de l'opération"},
            {"name": "cross", "type": "VARCHAR(50)", "pk": False, "fk": False, "null": False, "description": "Centre régional opérationnel"},
            {"name": "type_operation", "type": "VARCHAR(100)", "pk": False, "fk": False, "null": True, "description": "Type d'opération (SAR, MAS, SUR, POL, DIV)"},
            {"name": "evenement", "type": "VARCHAR(100)", "pk": False, "fk": False, "null": True, "description": "Type d'événement"},
            {"name": "categorie_evenement", "type": "VARCHAR(100)", "pk": False, "fk": False, "null": True, "description": "Catégorie d'événement"},
            {"name": "date_heure_reception_alerte", "type": "TIMESTAMP", "pk": False, "fk": False, "null": False, "description": "Date et heure de l'alerte"},
            {"name": "date_heure_fin_operation", "type": "TIMESTAMP", "pk": False, "fk": False, "null": True, "description": "Date et heure de fin"},
            {"name": "pourquoi_alerte", "type": "TEXT", "pk": False, "fk": False, "null": True, "description": "Raison de l'alerte"},
            {"name": "moyen_alerte", "type": "VARCHAR(100)", "pk": False, "fk": False, "null": True, "description": "Moyen d'alerte (VHF, téléphone, etc.)"},
            {"name": "qui_alerte", "type": "VARCHAR(100)", "pk": False, "fk": False, "null": True, "description": "Qui a donné l'alerte"},
            {"name": "categorie_qui_alerte", "type": "VARCHAR(100)", "pk": False, "fk": False, "null": True, "description": "Catégorie de l'émetteur"},
            {"name": "latitude", "type": "NUMERIC(10,6)", "pk": False, "fk": False, "null": True, "description": "Latitude (WGS84)"},
            {"name": "longitude", "type": "NUMERIC(10,6)", "pk": False, "fk": False, "null": True, "description": "Longitude (WGS84)"},
            {"name": "departement", "type": "VARCHAR(100)", "pk": False, "fk": False, "null": True, "description": "Département concerné"},
            {"name": "est_metropolitain", "type": "BOOLEAN", "pk": False, "fk": False, "null": True, "description": "Zone métropolitaine"},
            {"name": "zone_responsabilite", "type": "VARCHAR(100)", "pk": False, "fk": False, "null": True, "description": "Zone de responsabilité"},
            {"name": "vent_direction", "type": "NUMERIC(5,2)", "pk": False, "fk": False, "null": True, "description": "Direction du vent (degrés)"},
            {"name": "vent_direction_categorie", "type": "VARCHAR(20)", "pk": False, "fk": False, "null": True, "description": "Direction cardinale (N, NE, E, etc.)"},
            {"name": "vent_force", "type": "NUMERIC(4,2)", "pk": False, "fk": False, "null": True, "description": "Force du vent (Beaufort)"},
            {"name": "mer_force", "type": "NUMERIC(3,2)", "pk": False, "fk": False, "null": True, "description": "État de la mer (Douglas)"},
            {"name": "autorite", "type": "VARCHAR(100)", "pk": False, "fk": False, "null": True, "description": "Autorité principale"},
            {"name": "seconde_autorite", "type": "VARCHAR(100)", "pk": False, "fk": False, "null": True, "description": "Autorité secondaire"},
            {"name": "numero_sitrep", "type": "INTEGER", "pk": False, "fk": False, "null": True, "description": "Numéro SITREP"},
            {"name": "cross_sitrep", "type": "VARCHAR(100)", "pk": False, "fk": False, "null": True, "description": "Référence CROSS SITREP"},
            {"name": "fuseau_horaire", "type": "VARCHAR(50)", "pk": False, "fk": False, "null": True, "description": "Fuseau horaire"},
            {"name": "systeme_source", "type": "VARCHAR(50)", "pk": False, "fk": False, "null": True, "description": "Système source des données"},
            {"name": "created_at", "type": "TIMESTAMP", "pk": False, "fk": False, "null": False, "description": "Date de création"},
            {"name": "updated_at", "type": "TIMESTAMP", "pk": False, "fk": False, "null": False, "description": "Date de dernière modification"},
        ]
    },
    "flotteurs": {
        "description": "Navires/embarcations impliquées dans les opérations",
        "columns": [
            {"name": "flotteur_id", "type": "INTEGER", "pk": True, "fk": False, "null": False, "description": "Identifiant unique"},
            {"name": "operation_id", "type": "INTEGER", "pk": False, "fk": True, "null": False, "description": "FK vers operations"},
            {"name": "numero_ordre", "type": "NUMERIC(5,2)", "pk": False, "fk": False, "null": True, "description": "Numéro d'ordre du flotteur"},
            {"name": "pavillon", "type": "VARCHAR(50)", "pk": False, "fk": False, "null": True, "description": "Pavillon du navire (FR, ES, IT, etc.)"},
            {"name": "type_flotteur", "type": "VARCHAR(100)", "pk": False, "fk": False, "null": True, "description": "Type de flotteur"},
            {"name": "categorie_flotteur", "type": "VARCHAR(100)", "pk": False, "fk": False, "null": True, "description": "Catégorie (commerce, pêche, plaisance)"},
            {"name": "resultat_flotteur", "type": "VARCHAR(100)", "pk": False, "fk": False, "null": True, "description": "Résultat (secouru, disparu, naufragé)"},
            {"name": "numero_immatriculation", "type": "VARCHAR(100)", "pk": False, "fk": False, "null": True, "description": "Numéro d'immatriculation"},
        ]
    },
    "resultats_humain": {
        "description": "Résultats humains des opérations",
        "columns": [
            {"name": "resultat_humain_id", "type": "INTEGER", "pk": True, "fk": False, "null": False, "description": "Identifiant unique"},
            {"name": "operation_id", "type": "INTEGER", "pk": False, "fk": True, "null": False, "description": "FK vers operations"},
            {"name": "numero_ordre", "type": "NUMERIC(5,2)", "pk": False, "fk": False, "null": True, "description": "Numéro d'ordre"},
            {"name": "categorie_personne", "type": "VARCHAR(100)", "pk": False, "fk": False, "null": False, "description": "Catégorie (plaisancier, pêcheur, etc.)"},
            {"name": "resultat_humain", "type": "VARCHAR(100)", "pk": False, "fk": False, "null": False, "description": "Résultat (secouru, décédé, disparu)"},
            {"name": "nombre", "type": "INTEGER", "pk": False, "fk": False, "null": False, "description": "Nombre de personnes"},
            {"name": "dont_nombre_blesse", "type": "INTEGER", "pk": False, "fk": False, "null": False, "description": "Dont nombre de blessés"},
        ]
    },
    "operations_stats": {
        "description": "Statistiques agrégées des opérations",
        "columns": [
            {"name": "stats_id", "type": "INTEGER", "pk": True, "fk": False, "null": False, "description": "Identifiant unique"},
            {"name": "operation_id", "type": "INTEGER", "pk": False, "fk": True, "null": False, "description": "FK vers operations (UNIQUE)"},
            {"name": "date", "type": "DATE", "pk": False, "fk": False, "null": True, "description": "Date de l'opération"},
            {"name": "annee", "type": "INTEGER", "pk": False, "fk": False, "null": True, "description": "Année"},
            {"name": "mois", "type": "INTEGER", "pk": False, "fk": False, "null": True, "description": "Mois (1-12)"},
            {"name": "jour", "type": "INTEGER", "pk": False, "fk": False, "null": True, "description": "Jour du mois"},
            {"name": "jour_semaine", "type": "VARCHAR(20)", "pk": False, "fk": False, "null": True, "description": "Jour de la semaine"},
            {"name": "est_weekend", "type": "BOOLEAN", "pk": False, "fk": False, "null": True, "description": "Est un week-end"},
            {"name": "nombre_personnes_impliquees", "type": "INTEGER", "pk": False, "fk": False, "null": False, "description": "Total personnes impliquées"},
            {"name": "nombre_personnes_secourues", "type": "INTEGER", "pk": False, "fk": False, "null": False, "description": "Personnes secourues"},
            {"name": "nombre_personnes_blessees", "type": "INTEGER", "pk": False, "fk": False, "null": False, "description": "Personnes blessées"},
            {"name": "nombre_personnes_decedees", "type": "INTEGER", "pk": False, "fk": False, "null": False, "description": "Personnes décédées"},
            {"name": "nombre_personnes_disparues", "type": "INTEGER", "pk": False, "fk": False, "null": False, "description": "Personnes disparues"},
            {"name": "nombre_flotteurs_commerce", "type": "INTEGER", "pk": False, "fk": False, "null": False, "description": "Flotteurs commerce"},
            {"name": "nombre_flotteurs_peche", "type": "INTEGER", "pk": False, "fk": False, "null": False, "description": "Flotteurs pêche"},
            {"name": "nombre_flotteurs_plaisance", "type": "INTEGER", "pk": False, "fk": False, "null": False, "description": "Flotteurs plaisance"},
            {"name": "avec_clandestins", "type": "BOOLEAN", "pk": False, "fk": False, "null": False, "description": "Opération avec clandestins"},
            {"name": "distance_cote_metres", "type": "INTEGER", "pk": False, "fk": False, "null": True, "description": "Distance côte (mètres)"},
            {"name": "est_dans_stm", "type": "BOOLEAN", "pk": False, "fk": False, "null": False, "description": "Dans Séparation Trafic Maritime"},
            {"name": "est_dans_dst", "type": "BOOLEAN", "pk": False, "fk": False, "null": False, "description": "Dans Dispositif Séparation Trafic"},
            {"name": "concerne_plongee", "type": "BOOLEAN", "pk": False, "fk": False, "null": False, "description": "Concerne plongée sous-marine"},
        ]
    },
    "reference_lists": {
        "description": "Listes de valeurs de référence (lookup tables)",
        "columns": [
            {"name": "id", "type": "INTEGER", "pk": True, "fk": False, "null": False, "description": "Identifiant unique"},
            {"name": "category", "type": "VARCHAR(100)", "pk": False, "fk": False, "null": False, "description": "Catégorie (cross, type_operation, etc.)"},
            {"name": "value", "type": "VARCHAR(500)", "pk": False, "fk": False, "null": False, "description": "Valeur de la référence"},
            {"name": "display_order", "type": "INTEGER", "pk": False, "fk": False, "null": True, "description": "Ordre d'affichage"},
            {"name": "is_active", "type": "BOOLEAN", "pk": False, "fk": False, "null": False, "description": "Actif/Inactif"},
            {"name": "description", "type": "TEXT", "pk": False, "fk": False, "null": True, "description": "Description de la valeur"},
            {"name": "created_at", "type": "TIMESTAMP", "pk": False, "fk": False, "null": False, "description": "Date de création"},
        ]
    },
    "audit_log": {
        "description": "Journal d'audit - Historique de toutes les transactions",
        "columns": [
            {"name": "audit_id", "type": "BIGINT", "pk": True, "fk": False, "null": False, "description": "Identifiant unique du log"},
            {"name": "table_name", "type": "VARCHAR(100)", "pk": False, "fk": False, "null": False, "description": "Table affectée"},
            {"name": "action", "type": "VARCHAR(10)", "pk": False, "fk": False, "null": False, "description": "Action (INSERT, UPDATE, DELETE, VIEW)"},
            {"name": "record_id", "type": "VARCHAR(100)", "pk": False, "fk": False, "null": False, "description": "ID du record affecté"},
            {"name": "old_values", "type": "JSONB", "pk": False, "fk": False, "null": True, "description": "Anciennes valeurs (JSON)"},
            {"name": "new_values", "type": "JSONB", "pk": False, "fk": False, "null": True, "description": "Nouvelles valeurs (JSON)"},
            {"name": "user_name", "type": "VARCHAR(100)", "pk": False, "fk": False, "null": True, "description": "Utilisateur"},
            {"name": "details", "type": "TEXT", "pk": False, "fk": False, "null": True, "description": "Détails de l'action"},
            {"name": "sql_query", "type": "TEXT", "pk": False, "fk": False, "null": True, "description": "Requête SQL exécutée"},
            {"name": "created_at", "type": "TIMESTAMP", "pk": False, "fk": False, "null": False, "description": "Date de l'action"},
        ]
    }
}

# Sélection de la table
selected_table = st.selectbox(
    "Choisir une table:",
    list(tables_info.keys()),
    format_func=lambda x: f"{x.upper()} - {tables_info[x]['description']}"
)

if selected_table:
    table_data = tables_info[selected_table]
    
    st.markdown(f"### {selected_table.upper()}")
    st.info(table_data['description'])
    
    # Créer le DataFrame avec les détails
    columns_data = []
    for col in table_data['columns']:
        columns_data.append({
            'Colonne': col['name'],
            'Type': col['type'],
            'PK': '🔑' if col['pk'] else '',
            'FK': '🔗' if col['fk'] else '',
            'Nullable': '✓' if col['null'] else '',
            'Description': col['description']
        })
    
    df_cols = pd.DataFrame(columns_data)
    
    st.dataframe(df_cols, use_container_width=True, hide_index=True)
    
    # Statistiques de la table
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Colonnes", len(table_data['columns']))
    with col2:
        pk_count = sum(1 for c in table_data['columns'] if c['pk'])
        st.metric("Clés Primaires", pk_count)
    with col3:
        fk_count = sum(1 for c in table_data['columns'] if c['fk'])
        st.metric("Clés Étrangères", fk_count)

st.divider()

# ========================================
# SECTION 3: INFORMATIONS BD EN DIRECT
# ========================================
st.subheader("📊 Informations en Direct de la Base de Données")

try:
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Récupérer les statistiques des tables
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Nombre de lignes par table:**")
        
        tables_to_check = ['operations', 'flotteurs', 'resultats_humain', 'operations_stats', 'audit_log', 'reference_lists']
        row_counts = {}
        
        for table in tables_to_check:
            try:
                cur.execute(f"SELECT COUNT(*) FROM {table}")
                count = cur.fetchone()[0]
                row_counts[table] = count
            except:
                row_counts[table] = "N/A"
        
        df_stats = pd.DataFrame({
            'Table': list(row_counts.keys()),
            'Lignes': list(row_counts.values())
        })
        
        st.dataframe(df_stats, use_container_width=True, hide_index=True)
    
    with col2:
        st.markdown("**Taille des tables:**")
        
        sizes = {}
        for table in tables_to_check:
            try:
                cur.execute(f"SELECT pg_size_pretty(pg_total_relation_size('{table}')) AS size")
                size = cur.fetchone()[0]
                sizes[table] = size
            except:
                sizes[table] = "N/A"
        
        df_sizes = pd.DataFrame({
            'Table': list(sizes.keys()),
            'Taille': list(sizes.values())
        })
        
        st.dataframe(df_sizes, use_container_width=True, hide_index=True)
    
    cur.close()
    conn.close()
    
except Exception as e:
    st.warning(f"⚠️ Impossible de récupérer les informations BD: {e}")

st.divider()

# ========================================
# SECTION 4: LÉGENDE
# ========================================
st.subheader("📚 Légende")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    **Symboles:**
    - 🔑 Clé Primaire (PK)
    - 🔗 Clé Étrangère (FK)
    - ✓ Accepte les valeurs NULL
    """)

with col2:
    st.markdown("""
    **Types de données courants:**
    - INTEGER: Nombres entiers
    - VARCHAR(n): Texte de longueur variable
    - NUMERIC(m,d): Nombres décimaux
    - BOOLEAN: Vrai/Faux
    """)

with col3:
    st.markdown("""
    **Types de données (suite):**
    - TIMESTAMP: Date et heure
    - DATE: Date uniquement
    - TEXT: Texte long
    - JSONB: Données JSON
    """)

st.info("""
💡 **Note technique:**
- Les relations 1:N sont implémentées via les clés étrangères (FK)
- La relation 1:1 entre operations et operations_stats est UNIQUE
- audit_log enregistre toutes les modifications avec old/new values
- reference_lists fournit les valeurs pour les dropdowns
""")
