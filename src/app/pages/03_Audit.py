import streamlit as st
import pandas as pd
import sys
import os
import streamlit_mermaid as st_mermaid

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(PROJECT_ROOT))

st.set_page_config(page_title="Audit & Schema - Grass Squad", page_icon="🛡️", layout="wide")

st.title("🛡️ Audit & System Documentation")

tab1, tab2 = st.tabs(["📜 Logs Audit", "🗂️ Data Schema (ERD)"])

with tab1:
    st.subheader("Database Changes Log")
    if st.button("Refresh Logs"):
        st.session_state.get('refresh_logs', True)

    try:
        conn = get_db_connection()
        # Verify if table exists first (in case it wasn't created yet)
        # We can just try selecting
        try:
            df_audit = pd.read_sql("SELECT * FROM logs_audit ORDER BY action_time DESC LIMIT 200", conn)
            st.dataframe(df_audit, use_container_width=True)
        except Exception as e:
            st.warning("Audit table might not exist yet or is empty.")
            st.error(str(e))
        conn.close()
    except Exception as e:
        st.error(f"Connection error: {e}")

with tab2:
    st.subheader("Entity Relationship Diagram (ERD)")
    
    # We define the mermaid graph roughly based on create_bronze_tables.sql
    mermaid_code = """
    erDiagram
        operations {
            BIGINT operation_id PK
            VARCHAR type_operation
            VARCHAR pourquoi_alerte
            TIMESTAMP date_heure_reception_alerte
            decimal latitude
            decimal longitude
            INT vent_direction
        }
        resultats_humain {
            BIGINT operation_id FK
            VARCHAR category_personne
            VARCHAR result_humain
            BIGINT nombre
        }
        flotteurs {
            BIGINT operation_id FK
            VARCHAR type_flotteur
            VARCHAR pavillon
        }
        operations_stats {
            BIGINT operation_id FK
            INT nombre_personnes_secourues
            INT nombre_personnes_decedees
            DATE date
        }

        operations ||--o{ resultats_humain : "has"
        operations ||--o{ flotteurs : "involves"
        operations ||--|| operations_stats : "stats"
    """
    
    st_mermaid.st_mermaid(mermaid_code, height=500)
