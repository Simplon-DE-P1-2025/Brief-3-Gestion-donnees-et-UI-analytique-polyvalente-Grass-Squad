import pytest
import pandas as pd
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))
from ingestion.load_raw_data import load_all_raw_data
from validation.run_validation import validate_clean_pipeline

# --------------------
# Tests validate_clean_pipeline
# --------------------
def test_validate_clean_pipeline_retourne_dict():
    # Charger les données brutes d'abord
    dataframes = load_all_raw_data()
    
    result = validate_clean_pipeline(dataframes)
    
    # Doit retourner un dictionnaire avec les 4 tables
    assert isinstance(result, dict)
    assert "operations" in result
    assert "operations_stats" in result
    assert "flotteurs" in result
    assert "resultats_humain" in result


def test_validate_clean_pipeline_dataframes_valides():
    dataframes = load_all_raw_data()
    result = validate_clean_pipeline(dataframes)
    
    # Chaque table doit avoir 'curated' comme clé
    for table_name, data in result.items():
        assert isinstance(data, dict), f"{table_name} n'est pas un dictionnaire"
        assert "curated" in data, f"{table_name} n'a pas la clé 'curated'"
        assert isinstance(data["curated"], (pd.DataFrame, type(None))), f"{table_name}['curated'] n'est pas un DataFrame"


def test_validate_clean_pipeline_pas_vide():
    dataframes = load_all_raw_data()
    result = validate_clean_pipeline(dataframes)
    
    # Au moins la table operations curated ne doit pas être vide
    assert not result["operations"]["curated"].empty
