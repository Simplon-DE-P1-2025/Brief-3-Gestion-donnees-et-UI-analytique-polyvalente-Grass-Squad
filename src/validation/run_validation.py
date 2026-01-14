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
# PIPELINE : CLEAN -> VALIDATE
# ======================================================
def clean_then_validate_pipeline(
    dataframes: dict,
    rejected_path: str = "data/rejected",
    lazy_config: dict | None = None
):
    """
    Pipeline Data Engineer :

    RAW
      -> CLEAN
      -> VALIDATE
         -> rejected.csv
      -> CURATED
    """

    os.makedirs(rejected_path, exist_ok=True)

    if lazy_config is None:
        lazy_config = {
            "operations": False,
            "operations_stats": False,
            "flotteurs": True,
            "resultats_humain": True
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
        lazy = lazy_config.get(table_name, True)

        df_clean = clean_fn(df_raw)

        try:
            df_valid = schema.validate(df_clean, lazy=lazy)
            results[table_name] = {"curated": df_valid, "rejected": None}

        except pa.errors.SchemaErrors as err:
            rejected_file = os.path.join(rejected_path, f"{table_name}_rejected.csv")
            err.failure_cases.to_csv(rejected_file, index=False)
            results[table_name] = {"curated": err.valid_data, "rejected": err.failure_cases}
            print(f"   ➜ fichier : {rejected_file}")

    return results
