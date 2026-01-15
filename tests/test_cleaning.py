import pytest
import pandas as pd
import numpy as np
import sys
import os

# Ensure src is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.cleaning.transformation import (
    clean_operations,
    clean_operations_stats,
    clean_flotteurs,
    clean_resultats_humain
)

def test_clean_operations():
    data = {
        "operation_id": [1],
        "numero_sitrep": [0],  # Should become None
        "date_heure_reception_alerte": ["2023-01-01 10:00:00"],
        "latitude": ["45.5"],
        "longitude": [None],
        "cross": ["CROSS Med"]
    }
    df = pd.DataFrame(data)
    cleaned = clean_operations(df)
    
    # Use pd.isna for nullable types
    assert pd.isna(cleaned.loc[0, "numero_sitrep"])
    assert cleaned.loc[0, "latitude"] == 45.5
    assert pd.isna(cleaned.loc[0, "longitude"])
    assert "pourquoi_alerte" in cleaned.columns # Ensure missing columns are added

def test_clean_flotteurs():
    data = {
        "operation_id": [1],
        "pavillon": ["français"],  # Should be normalized
    }
    df = pd.DataFrame(data)
    cleaned = clean_flotteurs(df)
    
    assert cleaned.loc[0, "pavillon"] == "Français"
    assert cleaned.loc[0, "resultat_flotteur"] == "Non renseigné" # Default value

def test_clean_operations_stats():
    data = {
        "operation_id": [1],
        "est_vacances_scolaires": [None]
    }
    df = pd.DataFrame(data)
    cleaned = clean_operations_stats(df)
    
    # ensure_columns for bool fills NaNs with default (False)
    assert cleaned.loc[0, "est_vacances_scolaires"] == False 
    
    # ensure_columns for Int64 does NOT fill NaNs with default if column exists!
    # "nombre_personnes_blessees": ("Int64", 0) -> default is 0 if column MISSING.
    # If column present but None, it becomes pd.NA.
    
    # Testing missing column behavior
    # Input has no "nombre_personnes_blessees", so it should be created with 0.
    assert cleaned.loc[0, "nombre_personnes_blessees"] == 0 

def test_clean_resultats_humain():
    data = {
        "operation_id": [1],
        "nombre": [None]
    }
    df = pd.DataFrame(data)
    cleaned = clean_resultats_humain(df)
    
    # "nombre" column exists in input, so default (0) is NOT applied, only type conversion.
    # None -> pd.NA for Int64.
    assert pd.isna(cleaned.loc[0, "nombre"])

def test_clean_resultats_humain_missing_col():
    data = {
        "operation_id": [1]
        # "nombre" missing
    }
    df = pd.DataFrame(data)
    cleaned = clean_resultats_humain(df)
    
    # Missing col -> filled with default 0
    assert cleaned.loc[0, "nombre"] == 0
