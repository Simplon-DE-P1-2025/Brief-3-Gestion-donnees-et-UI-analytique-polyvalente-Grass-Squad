import os
import pandera as pa

from src.ingestion.load_raw_data import load_all_raw_data
from src.validation.schemas_validation import (
    schema_operations,
    schema_operations_stats,
    schema_flotteurs,
    schema_resultats_humain
)
from src.cleaning.transformation import (
    clean_operations,
    clean_operations_stats,
    clean_flotteurs,
    clean_resultats_humain
)

# ======================================================
# PIPELINE : VALIDATE RAW -> CLEAN -> VALIDATE CLEANED
# ======================================================
def validate_clean_pipeline(
    dataframes: dict,
    rejected_path: str = "data/rejected",
    lazy_config_raw: dict | None = None,
    lazy_config_clean: dict | None = None
):
    """
    Pipeline Data Engineer :
    
    RAW
      -> VALIDATE (souple)
      -> CLEAN
      -> VALIDATE (strict)
      -> CURATED
      -> rejected.csv
    """

    os.makedirs(rejected_path, exist_ok=True)

    # Par défaut, la validation RAW est en lazy (souple) pour toutes
    if lazy_config_raw is None:
        lazy_config_raw = {
            "operations": True,
            "operations_stats": True,
            "flotteurs": True,
            "resultats_humain": True
        }

    # Validation après nettoyage est stricte par défaut
    if lazy_config_clean is None:
        lazy_config_clean = {
            "operations": False,
            "operations_stats": False,
            "flotteurs": False,
            "resultats_humain": False
        }

    schemas = {
        "operations": schema_operations,
        "operations_stats": schema_operations_stats,
        "flotteurs": schema_flotteurs,
        "resultats_humain": schema_resultats_humain
    }

    cleaners = {
        "operations": clean_operations,
        "operations_stats": clean_operations_stats,
        "flotteurs": clean_flotteurs,
        "resultats_humain": clean_resultats_humain
    }

    results = {}

    for table_name, df_raw in dataframes.items():
        schema = schemas[table_name]
        clean_fn = cleaners[table_name]
        lazy_raw = lazy_config_raw.get(table_name, True)
        lazy_clean = lazy_config_clean.get(table_name, False)

        print(f"\n--- Pipeline pour : {table_name} ---")

        # 1️⃣ Validation RAW (souple)
        try:
            df_valid_raw = schema.validate(df_raw, lazy=lazy_raw)
            print(f"Validation RAW OK pour {table_name}")
        except pa.errors.SchemaErrors as err:
            rejected_file_raw = os.path.join(rejected_path, f"{table_name}_rejected_raw.csv")
            err.failure_cases.to_csv(rejected_file_raw, index=False)
            df_valid_raw = err.data
            print(f"   ➜ RAW rejected sauvegardé dans : {rejected_file_raw}")

        # 2️⃣ Nettoyage
        df_clean = clean_fn(df_valid_raw)
        print(f"Nettoyage terminé pour {table_name}")

        # 3️⃣ Validation après nettoyage (stricte)
        try:
            df_valid_clean = schema.validate(df_clean, lazy=lazy_clean)
            results[table_name] = {"curated": df_valid_clean, "rejected": None}
            print(f"Validation CLEAN OK pour {table_name}")
        except pa.errors.SchemaErrors as err:
            rejected_file_clean = os.path.join(rejected_path, f"{table_name}_rejected_clean.csv")
            err.failure_cases.to_csv(rejected_file_clean, index=False)
            results[table_name] = {"curated": err.data, "rejected": err.failure_cases}
            print(f"   ➜ CLEAN rejected sauvegardé dans : {rejected_file_clean}")

    return results