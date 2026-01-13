"""
Module pour charger les données dans PostgreSQL en utilisant database.sql
Contient des fonctions réutilisables pour un ETL global.
"""
import os
import sys
from pathlib import Path
import psycopg2
from dotenv import load_dotenv
from io import StringIO
import pandas as pd

# Ajouter le répertoire parent au path pour importer src
sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.config import PROJECT_ROOT
from src.ingestion.load_raw_data import load_all_raw_data
from src.validation.run_validation import clean_then_validate_pipeline

# Charger les variables d'environnement depuis .env
load_dotenv(PROJECT_ROOT / ".env")

# Configuration de la base de données
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres"),
    "database": os.getenv("DB_DATABASE") or os.getenv("DB_NAME", "secmar_db")
}

SQL_SCRIPT_PATH = PROJECT_ROOT / "src" / "database" / "database.sql"


def get_db_connection(config=DB_CONFIG):
    """
    Retourne une connexion PostgreSQL
    """
    return psycopg2.connect(
        host=config["host"],
        port=config["port"],
        user=config["user"],
        password=config["password"],
        database=config["database"],
        connect_timeout=300
    )


def create_tables(conn):
    """Crée les tables en utilisant database.sql"""
    cursor = conn.cursor()
    try:
        with open(SQL_SCRIPT_PATH, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        cursor.execute(sql_script)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise
    finally:
        cursor.close()


def insert_with_copy(df, table_name, conn):
    """Insère un dataframe avec COPY (ultra-rapide)"""
    buffer = StringIO()
    df.to_csv(buffer, index=False, header=False, sep='\t', na_rep='\\N')
    buffer.seek(0)

    cursor = conn.cursor()
    try:
        cursor.execute(f"TRUNCATE TABLE {table_name} CASCADE")
        
        # Échapper les noms de colonnes et utiliser copy_expert pour supporter les schémas
        columns_str = ', '.join([f'"{col}"' for col in df.columns])
        copy_sql = f"COPY {table_name} ({columns_str}) FROM STDIN WITH (FORMAT CSV, DELIMITER E'\\t', NULL '\\N')"
        cursor.copy_expert(copy_sql, buffer)
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise
    finally:
        cursor.close()


def prepare_dataframe_for_db(df, table_name):
    """
    Prépare un dataframe pour l'insertion PostgreSQL
    Convertit les types pandas en types Python compatibles
    """
    df_copy = df.copy()

    integer_columns = {
        'operations': ['operation_id', 'numero_sitrep'],
        'operations_stats': [
            'operation_id', 'annee', 'mois', 'jour', 'semaine', 'distance_cote_metres',
            'maree_coefficient', 'nombre_personnes_blessees', 'nombre_personnes_assistees',
            'nombre_personnes_decedees', 'nombre_personnes_decedees_accidentellement',
            'nombre_personnes_decedees_naturellement', 'nombre_personnes_disparues',
            'nombre_personnes_impliquees_dans_fausse_alerte', 'nombre_personnes_retrouvees',
            'nombre_personnes_secourues', 'nombre_personnes_tirees_daffaire_seule',
            'nombre_personnes_tous_deces', 'nombre_personnes_tous_deces_ou_disparues',
            'nombre_personnes_impliquees', 'nombre_flotteurs_commerce_impliques',
            'nombre_flotteurs_peche_impliques', 'nombre_flotteurs_plaisance_impliques',
            'nombre_flotteurs_loisirs_nautiques_impliques', 'nombre_aeronefs_impliques',
            'nombre_flotteurs_autre_impliques', 'nombre_flotteurs_annexe_impliques',
            'nombre_flotteurs_autre_loisir_nautique_impliques',
            'nombre_flotteurs_canoe_kayak_aviron_impliques',
            'nombre_flotteurs_engin_de_plage_impliques', 'nombre_flotteurs_kitesurf_impliques',
            'nombre_flotteurs_plaisance_voile_legere_impliques',
            'nombre_flotteurs_plaisance_a_moteur_impliques',
            'nombre_flotteurs_plaisance_a_moteur_moins_8m_impliques',
            'nombre_flotteurs_plaisance_a_moteur_plus_8m_impliques',
            'nombre_flotteurs_plaisance_a_voile_impliques',
            'nombre_flotteurs_planche_a_voile_impliques',
            'nombre_flotteurs_ski_nautique_impliques', 'nombre_flotteurs_surf_impliques',
            'nombre_flotteurs_vehicule_nautique_a_moteur_impliques',
            # Colonnes "_sans_clandestins"
            'nombre_personnes_blessees_sans_clandestins',
            'nombre_personnes_assistees_sans_clandestins',
            'nombre_personnes_decedees_sans_clandestins',
            'nombre_personnes_decedees_accidentellement_sans_clandestins',
            'nombre_personnes_decedees_naturellement_sans_clandestins',
            'nombre_personnes_disparues_sans_clandestins',
            'nombre_personnes_impliquees_dans_fausse_alerte_sans_clandestins',
            'nombre_personnes_retrouvees_sans_clandestins',
            'nombre_personnes_secourues_sans_clandestins',
            'nombre_personnes_tirees_daffaire_seule_sans_clandestins',
            'nombre_personnes_tous_deces_sans_clandestins',
            'nombre_personnes_tous_deces_ou_disparues_sans_clandestins',
            'nombre_personnes_impliquees_sans_clandestins'
        ],
        'flotteurs': ['operation_id', 'numero_ordre'],
        'resultats_humain': ['operation_id', 'nombre', 'dont_nombre_blesse']
    }

    for col in df_copy.columns:
        if df_copy[col].dtype == 'Int64':
            if col in integer_columns.get(table_name, []):
                df_copy[col] = df_copy[col].apply(lambda x: str(int(x)) if pd.notna(x) else None)
            else:
                df_copy[col] = df_copy[col].apply(lambda x: int(x) if pd.notna(x) else None)
        elif df_copy[col].dtype in ['boolean', 'bool']:
            df_copy[col] = df_copy[col].apply(lambda x: bool(x) if pd.notna(x) else None)
        elif df_copy[col].dtype == 'float64':
            if col in integer_columns.get(table_name, []):
                df_copy[col] = df_copy[col].apply(lambda x: str(int(x)) if pd.notna(x) else None)

    return df_copy


def load_and_prepare_all_data(rejected_path="data/rejected"):
    """
    Charge toutes les données brutes, les valide et retourne les DataFrames prêts pour PostgreSQL.
    """
    df_operations, df_operations_stats, df_flotteurs, df_resultats_humain = load_all_raw_data()
    dataframes = {
        "operations": df_operations,
        "operations_stats": df_operations_stats,
        "flotteurs": df_flotteurs,
        "resultats_humain": df_resultats_humain
    }

    validated_data = clean_then_validate_pipeline(
        dataframes=dataframes,
        rejected_path=rejected_path
    )

    # Préparer les DataFrames pour PostgreSQL
    prepared_data = {}
    for table_name, df_dict in validated_data.items():
        df_curated = df_dict.get("curated")
        if df_curated is not None and len(df_curated) > 0:
            prepared_data[table_name] = prepare_dataframe_for_db(df_curated, table_name)
        else:
            prepared_data[table_name] = pd.DataFrame()  # empty df si rien à insérer

    return prepared_data
