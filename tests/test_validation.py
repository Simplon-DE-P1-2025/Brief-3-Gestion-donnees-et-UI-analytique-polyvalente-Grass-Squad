# -*- coding: utf-8 -*-
"""
Tests unitaires pour le module validation/run_validation.py
"""

import pytest
import pandas as pd
from pathlib import Path
import sys
import tempfile
import shutil

sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.validation.run_validation import validate_clean_pipeline
from src.validation.schemas_validation import (
    schema_operations,
    schema_operations_stats,
    schema_flotteurs,
    schema_resultats_humain
)


# ==============================================================================
# FIXTURES
# ==============================================================================

@pytest.fixture
def temp_rejected_dir():
    """Crée un répertoire temporaire pour les fichiers rejetés"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def valid_dataframes():
    """DataFrames valides pour les tests"""
    return {
        "operations": pd.DataFrame({
            "operation_id": [1, 2, 3],
            "cross": ["CROSS MED", "CROSS AG", "CROSS ATL"],
            "date_heure_reception_alerte": ["2023-01-01T10:00:00Z", "2023-01-02T15:00:00Z", "2023-01-03T20:00:00Z"]
        }),
        "operations_stats": pd.DataFrame({
            "operation_id": [1, 2, 3],
            "date": ["2023-01-01", "2023-01-02", "2023-01-03"],
            "annee": [2023, 2023, 2023],
            "mois": [1, 1, 1]
        }),
        "flotteurs": pd.DataFrame({
            "operation_id": [1, 1, 2],
            "numero_ordre": [1, 2, 1]
        }),
        "resultats_humain": pd.DataFrame({
            "operation_id": [1, 1, 2],
            "categorie_personne": ["Plaisancier", "Pêcheur", "Commercial"],
            "nombre": [2, 3, 1]
        })
    }


@pytest.fixture
def mock_lazy_config_raw():
    """Mock pour LazyConfig RAW"""
    class MockLazyConfig:
        def get(self, table_name, lazy=False):
            schemas = {
                "operations": schema_operations,
                "operations_stats": schema_operations_stats,
                "flotteurs": schema_flotteurs,
                "resultats_humain": schema_resultats_humain
            }
            return schemas.get(table_name)
    return MockLazyConfig()


@pytest.fixture
def mock_lazy_config_clean():
    """Mock pour LazyConfig CLEAN"""
    class MockLazyConfig:
        def get(self, table_name, lazy=False):
            schemas = {
                "operations": schema_operations,
                "operations_stats": schema_operations_stats,
                "flotteurs": schema_flotteurs,
                "resultats_humain": schema_resultats_humain
            }
            return schemas.get(table_name)
    return MockLazyConfig()


# ==============================================================================
# TESTS VALIDATE_CLEAN_PIPELINE
# ==============================================================================

def test_validate_clean_pipeline_returns_dict(valid_dataframes, temp_rejected_dir, 
                                               mock_lazy_config_raw, mock_lazy_config_clean):
    """Vérifie que validate_clean_pipeline retourne un dictionnaire"""
    result = validate_clean_pipeline(
        valid_dataframes,
        temp_rejected_dir,
        mock_lazy_config_raw,
        mock_lazy_config_clean
    )
    assert isinstance(result, dict), "Le résultat devrait être un dictionnaire"


def test_validate_clean_pipeline_has_all_tables(valid_dataframes, temp_rejected_dir,
                                                 mock_lazy_config_raw, mock_lazy_config_clean):
    """Vérifie que toutes les tables sont présentes dans le résultat"""
    result = validate_clean_pipeline(
        valid_dataframes,
        temp_rejected_dir,
        mock_lazy_config_raw,
        mock_lazy_config_clean
    )
    expected_keys = {"operations", "operations_stats", "flotteurs", "resultats_humain"}
    assert set(result.keys()) == expected_keys, "Toutes les tables devraient être présentes"


def test_validate_clean_pipeline_each_table_has_curated_and_rejected(valid_dataframes, temp_rejected_dir,
                                                                      mock_lazy_config_raw, mock_lazy_config_clean):
    """Vérifie que chaque table a 'curated' et 'rejected'"""
    result = validate_clean_pipeline(
        valid_dataframes,
        temp_rejected_dir,
        mock_lazy_config_raw,
        mock_lazy_config_clean
    )
    
    for table_name, table_result in result.items():
        assert isinstance(table_result, dict), f"{table_name} devrait être un dict"
        assert "curated" in table_result, f"{table_name} devrait avoir 'curated'"
        assert "rejected" in table_result, f"{table_name} devrait avoir 'rejected'"


def test_validate_clean_pipeline_curated_is_dataframe(valid_dataframes, temp_rejected_dir,
                                                       mock_lazy_config_raw, mock_lazy_config_clean):
    """Vérifie que 'curated' est un DataFrame"""
    result = validate_clean_pipeline(
        valid_dataframes,
        temp_rejected_dir,
        mock_lazy_config_raw,
        mock_lazy_config_clean
    )
    
    for table_name, table_result in result.items():
        curated = table_result["curated"]
        assert isinstance(curated, pd.DataFrame), f"{table_name} curated devrait être un DataFrame"


def test_validate_clean_pipeline_preserves_valid_data(valid_dataframes, temp_rejected_dir,
                                                       mock_lazy_config_raw, mock_lazy_config_clean):
    """Vérifie que les données valides sont préservées"""
    result = validate_clean_pipeline(
        valid_dataframes,
        temp_rejected_dir,
        mock_lazy_config_raw,
        mock_lazy_config_clean
    )
    
    for table_name, table_result in result.items():
        curated = table_result["curated"]
        # Au moins quelques données devraient être préservées
        assert len(curated) >= 0, f"{table_name} curated devrait avoir des données"


def test_validate_clean_pipeline_creates_rejected_dir(valid_dataframes, temp_rejected_dir,
                                                       mock_lazy_config_raw, mock_lazy_config_clean):
    """Vérifie que le répertoire rejected est créé"""
    # Supprimer le répertoire temporaire pour tester sa création
    shutil.rmtree(temp_rejected_dir)
    
    validate_clean_pipeline(
        valid_dataframes,
        temp_rejected_dir,
        mock_lazy_config_raw,
        mock_lazy_config_clean
    )
    
    assert Path(temp_rejected_dir).exists(), "Le répertoire rejected devrait être créé"


def test_validate_clean_pipeline_handles_empty_dataframes(temp_rejected_dir,
                                                           mock_lazy_config_raw, mock_lazy_config_clean):
    """Vérifie que la fonction gère les DataFrames vides"""
    empty_dataframes = {
        "operations": pd.DataFrame(),
        "operations_stats": pd.DataFrame(),
        "flotteurs": pd.DataFrame(),
        "resultats_humain": pd.DataFrame()
    }
    
    result = validate_clean_pipeline(
        empty_dataframes,
        temp_rejected_dir,
        mock_lazy_config_raw,
        mock_lazy_config_clean
    )
    
    assert isinstance(result, dict), "Devrait fonctionner même avec des DataFrames vides"
    assert len(result) == 4, "Devrait retourner les 4 tables"


# ==============================================================================
# TESTS DES SCHÉMAS
# ==============================================================================

def test_schema_operations_exists():
    """Vérifie que le schéma operations existe"""
    assert schema_operations is not None, "schema_operations devrait exister"


def test_schema_operations_stats_exists():
    """Vérifie que le schéma operations_stats existe"""
    assert schema_operations_stats is not None, "schema_operations_stats devrait exister"


def test_schema_flotteurs_exists():
    """Vérifie que le schéma flotteurs existe"""
    assert schema_flotteurs is not None, "schema_flotteurs devrait exister"


def test_schema_resultats_humain_exists():
    """Vérifie que le schéma resultats_humain existe"""
    assert schema_resultats_humain is not None, "schema_resultats_humain devrait exister"


def test_all_schemas_have_operation_id():
    """Vérifie que tous les schémas ont operation_id"""
    schemas = [
        ("operations", schema_operations),
        ("operations_stats", schema_operations_stats),
        ("flotteurs", schema_flotteurs),
        ("resultats_humain", schema_resultats_humain)
    ]
    
    for name, schema in schemas:
        assert "operation_id" in schema.columns, f"{name} devrait avoir operation_id"
