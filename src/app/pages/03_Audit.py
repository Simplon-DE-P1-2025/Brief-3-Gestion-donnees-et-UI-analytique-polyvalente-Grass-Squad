import streamlit as st
import pandas as pd
import sys
import os
import streamlit_mermaid as st_mermaid

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(PROJECT_ROOT))

from src.database.load_database import engine

st.set_page_config(page_title="Audit & Schema - Grass Squad", page_icon="🛡️", layout="wide")

st.title("🛡️ Audit & Documentation Système")

tab1, tab2 = st.tabs(["📜 Logs d'Audit", "🗂️ Schéma de Données (ERD)"])

with tab1:
    st.subheader("📋 Historique des Modifications")
    if st.button("🔄 Rafraîchir les Logs"):
        st.rerun()

    try:
        # Verify if table exists first (in case it wasn't created yet)
        try:
            df_audit = pd.read_sql("SELECT * FROM audit_log ORDER BY created_at DESC LIMIT 200", engine)
            
            if len(df_audit) > 0:
                st.dataframe(df_audit, use_container_width=True, hide_index=True)
                st.info(f"📊 {len(df_audit)} log(s) affiché(s)")
            else:
                st.info("Aucun log d'audit trouvé")
        except Exception as e:
            st.warning("La table d'audit n'existe pas encore ou est vide.")
            st.error(str(e))
    except Exception as e:
        st.error(f"❌ Erreur de connexion : {e}")

with tab2:
    st.subheader("📊 Diagramme Entités-Relations (ERD)")
    st.info("💡 Ce diagramme représente la structure complète de la base de données SECMAR")
    
    # We define the mermaid graph roughly based on create_bronze_tables.sql
    mermaid_code = """
    erDiagram
        operations ||--o{ flotteurs : "a"
        operations ||--o{ resultats_humain : "a"
        operations ||--o{ operations_stats : "a"
        
        operations {
            SERIAL operation_id PK
            VARCHAR cross "NOT NULL"
            TIMESTAMP date_heure_reception_alerte "NOT NULL"
            VARCHAR evenement
            VARCHAR departement
            FLOAT latitude
            FLOAT longitude
            VARCHAR pourquoi_alerte
        }
        
        flotteurs {
            SERIAL flotteur_id PK
            INTEGER operation_id FK
            VARCHAR pavillon
            VARCHAR type_flotteur
            VARCHAR resultat_flotteur
            VARCHAR numero_immatriculation
            FLOAT longueur
            FLOAT largeur
        }
        
        resultats_humain {
            SERIAL resultat_humain_id PK
            INTEGER operation_id FK
            VARCHAR categorie_personne
            VARCHAR resultat_humain
            INTEGER nombre
        }
        
        operations_stats {
            SERIAL stat_id PK
            INTEGER operation_id FK
            INTEGER nombre_personnes_impliquees
            INTEGER nombre_personnes_secourues
            INTEGER nombre_personnes_tous_deces
            INTEGER nombre_personnes_blessees
        }
    """
    
    st_mermaid.st_mermaid(mermaid_code, height=600)
