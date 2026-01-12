import psycopg2
import pandas as pd
from psycopg2.extras import execute_values
import os
import numpy as np

# --------------------------
# CONFIGURATION
# --------------------------
DB_NAME = "db_operations"
DB_USER = "postgres"
DB_PASSWORD = "root"
DB_HOST = "localhost"

# Chemins CSV
CSV_OPERATIONS = "../../data/raw/operations.csv"
CSV_FLOTTEURS = "../../data/raw/flotteurs.csv"
CSV_RESULTATS_HUMAIN = "../../data/raw/resultats_humain.csv"
CSV_OPERATIONS_STATS = "../../data/raw/operations_stats.csv"

# Chemin SQL pour créer les tables Bronze
SQL_CREATE_TABLES = "../database/create_bronze_tables.sql"

# --------------------------
# 1️⃣ Créer la base si besoin
# --------------------------
conn = psycopg2.connect(host=DB_HOST, database="postgres", user=DB_USER, password=DB_PASSWORD)
conn.autocommit = True
cur = conn.cursor()

cur.execute(f"SELECT 1 FROM pg_database WHERE datname='{DB_NAME}';")
exists = cur.fetchone()
if not exists:
    cur.execute(f"CREATE DATABASE {DB_NAME};")
    print(f"Base {DB_NAME} créée !")
else:
    print(f"Base {DB_NAME} existe déjà.")

cur.close()
conn.close()

# --------------------------
# 2️⃣ Créer les tables Bronze
# --------------------------
conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)
cur = conn.cursor()

with open(SQL_CREATE_TABLES, "r") as f:
    sql = f.read()
cur.execute(sql)
conn.commit()
print("Tables Bronze créées !")

# --------------------------
# 3️⃣ Fonction pour ingérer un CSV
# --------------------------
def ingest_csv(csv_path, table_name, conn):
    """
    Ingest CSV into a PostgreSQL table.

    Args:
        csv_path (str): Path to the CSV file
        table_name (str): Name of the SQL table
        conn: psycopg2 database connection
    """

    # Lire le CSV
    df = pd.read_csv(csv_path, low_memory=False)

    # --------------------------
    # Colonnes numériques à nettoyer
    # --------------------------
    numeric_cols = [
        "operation_id", "numero_sitrep",
        "vent_direction", "vent_force", "mer_force",
        "latitude", "longitude",
        # ajouter d'autres colonnes numériques de ton CSV si besoin
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")  # Non-numériques → NaN

    # Remplacer NaN par None pour PostgreSQL
    df = df.replace({np.nan: None})

    # --------------------------
    # Colonnes réservées PostgreSQL
    # --------------------------
    reserved_words = ['cross']  # ajouter d'autres si nécessaire
    cols = ','.join([f'"{c}"' if c.lower() in reserved_words else c for c in df.columns])

    # Préparer les valeurs à insérer
    values = [tuple(x) for x in df.to_numpy()]
    query = f"INSERT INTO {table_name} ({cols}) VALUES %s"


    # Exécuter l'insertion
    cur = conn.cursor()
    execute_values(cur, query, values)
    conn.commit()
    cur.close()
    print(f"{len(df)} lignes insérées dans {table_name} depuis {csv_path}")

ingest_csv(CSV_OPERATIONS, "bronze_operations", conn)
ingest_csv(CSV_OPERATIONS_STATS, "bronze_operations_stats", conn)
ingest_csv(CSV_RESULTATS_HUMAIN, "bronze_resultats_humain", conn)
ingest_csv(CSV_FLOTTEURS, "bronze_flotteurs", conn)