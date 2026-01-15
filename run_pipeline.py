"""
Pipeline ETL - Données de Sauvetage Maritime
Ingestion → Nettoyage → Validation → Base de données PostgreSQL
"""

import sys
from pathlib import Path
import psycopg2
from dotenv import load_dotenv
import os

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.config import PROJECT_ROOT
from src.ingestion.load_raw_data import load_all_raw_data
from src.validation.run_validation import validate_clean_pipeline
from src.database.load_database import create_tables, insert_with_copy, prepare_dataframe_for_db


def run_pipeline():
    """Execute le pipeline ETL complet"""
    
    try:
        # Étape 1: Ingestion
        print("\n[1/4] Ingestion des données...")
        dataframes = load_all_raw_data()
        print(f"      {sum(len(df) for df in dataframes.values()):,} lignes chargées")
        
        # Étape 2: Nettoyage et Validation
        print("\n[2/4] Nettoyage et validation...")
        results = validate_clean_pipeline(
            dataframes,
            rejected_path=str(PROJECT_ROOT / "data" / "rejected")
        )
        
        validated_dfs = {name: data["curated"] for name, data in results.items()}
        print(f"      {sum(len(df) for df in validated_dfs.values()):,} lignes validées")
        
        # Étape 3: Chargement dans PostgreSQL
        print("\n[3/4] Chargement dans PostgreSQL...")
        
        load_dotenv(PROJECT_ROOT / ".env")
        
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_DATABASE"),
            connect_timeout=300
        )
        
        create_tables(conn)
        
        for table_name in ['operations', 'operations_stats', 'flotteurs', 'resultats_humain']:
            if table_name in validated_dfs:
                df_prepared = prepare_dataframe_for_db(validated_dfs[table_name], table_name)
                insert_with_copy(df_prepared, table_name, conn)
        
        conn.close()
        print(f"{sum(len(df) for df in validated_dfs.values()):,} lignes insérées")
    
        print("\n[4/4] Pipeline terminé avec succès\n")
        return 0
        
    except Exception as e:
        print(f"\n Erreur: {e}\n")
        return 1


if __name__ == "__main__":
    sys.exit(run_pipeline())

