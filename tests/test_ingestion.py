# -*- coding: utf-8 -*-
"""
Tests unitaires pour le module ingestion/load_raw_data.py
"""

import pytest
import pandas as pd
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.ingestion.load_raw_data import load_all_raw_data


# ==============================================================================
# TESTS LOAD_ALL_RAW_DATA
# ==============================================================================

def test_load_all_raw_data_returns_dict():
    """Vérifie que load_all_raw_data retourne un dictionnaire"""
    result = load_all_raw_data()
    assert isinstance(result, dict), "Le résultat devrait être un dictionnaire"


def test_load_all_raw_data_has_four_tables():
    """Vérifie que le dictionnaire contient les 4 tables attendues"""
    result = load_all_raw_data()
    expected_keys = {"operations", "operations_stats", "flotteurs", "resultats_humain"}
    assert set(result.keys()) == expected_keys, f"Tables manquantes. Attendu: {expected_keys}, Obtenu: {result.keys()}"


def test_load_all_raw_data_returns_dataframes():
    """Vérifie que chaque valeur est un DataFrame pandas"""
    result = load_all_raw_data()
    for table_name, df in result.items():
        assert isinstance(df, pd.DataFrame), f"{table_name} devrait être un DataFrame"


def test_load_all_raw_data_non_empty():
    """Vérifie que les DataFrames chargés ne sont pas vides"""
    result = load_all_raw_data()
    for table_name, df in result.items():
        assert len(df) > 0, f"{table_name} est vide"
        assert len(df.columns) > 0, f"{table_name} n'a pas de colonnes"


def test_operations_has_required_columns():
    """Vérifie que operations contient les colonnes essentielles"""
    result = load_all_raw_data()
    operations_df = result["operations"]
    
    required_columns = ["operation_id", "cross"]
    for col in required_columns:
        assert col in operations_df.columns, f"Colonne manquante dans operations: {col}"


def test_operations_stats_has_required_columns():
    """Vérifie que operations_stats contient les colonnes essentielles"""
    result = load_all_raw_data()
    stats_df = result["operations_stats"]
    
    required_columns = ["operation_id", "date"]
    for col in required_columns:
        assert col in stats_df.columns, f"Colonne manquante dans operations_stats: {col}"


def test_flotteurs_has_required_columns():
    """Vérifie que flotteurs contient les colonnes essentielles"""
    result = load_all_raw_data()
    flotteurs_df = result["flotteurs"]
    
    required_columns = ["operation_id"]
    for col in required_columns:
        assert col in flotteurs_df.columns, f"Colonne manquante dans flotteurs: {col}"


def test_resultats_humain_has_required_columns():
    """Vérifie que resultats_humain contient les colonnes essentielles"""
    result = load_all_raw_data()
    humain_df = result["resultats_humain"]
    
    required_columns = ["operation_id"]
    for col in required_columns:
        assert col in humain_df.columns, f"Colonne manquante dans resultats_humain: {col}"


def test_operation_id_exists_in_all_tables():
    """Vérifie que operation_id existe dans toutes les tables"""
    result = load_all_raw_data()
    
    for table_name, df in result.items():
        assert "operation_id" in df.columns, f"operation_id manquant dans {table_name}"


def test_data_loaded_successfully():
    """Test d'intégration : vérifie le chargement complet"""
    result = load_all_raw_data()
    
    # Vérifier que toutes les tables ont des données
    total_rows = sum(len(df) for df in result.values())
    assert total_rows > 0, "Aucune donnée chargée"
    
    # Vérifier que operations a le plus de lignes (normalement)
    assert len(result["operations"]) > 0, "Aucune opération chargée"
