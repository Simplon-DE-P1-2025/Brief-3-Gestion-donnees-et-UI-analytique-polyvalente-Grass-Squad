# -*- coding: utf-8 -*-
"""
Tests unitaires pour le module cleaning/transformation.py
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.cleaning.transformation import (
    clean_operations,
    clean_operations_stats,
    clean_flotteurs,
    clean_resultats_humain
)


# ==============================================================================
# FIXTURES
# ==============================================================================

@pytest.fixture
def raw_operations():
    """DataFrame operations brut (non nettoyé)"""
    return pd.DataFrame({
        "operation_id": ["123", "456", "789"],
        "cross": [" CROSS MED ", "CROSS AG", "  CROSS ATL  "],
        "evenement": ["  Naufrage  ", "Avarie", None],
        "numero_sitrep": ["0", "1234", "5678"],
        "date_heure_reception_alerte": ["2023-01-01", "2023-02-01", "2023-03-01"]
    })


@pytest.fixture
def raw_operations_stats():
    """DataFrame operations_stats brut"""
    return pd.DataFrame({
        "operation_id": [123, 456, 789],
        "date": ["2023-01-01", "2023-02-01", "2023-03-01"],
        "annee": ["2023", "2023", "2024"],
        "mois": ["1", "2", "3"]
    })


@pytest.fixture
def raw_flotteurs():
    """DataFrame flotteurs brut"""
    return pd.DataFrame({
        "operation_id": [123, 456, 789],
        "numero_ordre": ["1", "2", "1"],
        "pavillon": ["  France  ", "Spain", None]
    })


@pytest.fixture
def raw_resultats_humain():
    """DataFrame resultats_humain brut"""
    return pd.DataFrame({
        "operation_id": [123, 456, 789],
        "categorie_personne": ["  Plaisancier  ", "Pêcheur", None],
        "nombre": ["3", "2", "5"]
    })


# ==============================================================================
# TESTS CLEAN_OPERATIONS
# ==============================================================================

def test_clean_operations_returns_dataframe(raw_operations):
    """Vérifie que clean_operations retourne un DataFrame"""
    result = clean_operations(raw_operations)
    assert isinstance(result, pd.DataFrame), "Le résultat devrait être un DataFrame"


def test_clean_operations_preserves_valid_rows(raw_operations):
    """Vérifie que les lignes valides sont préservées"""
    result = clean_operations(raw_operations)
    # Au moins une ligne devrait être conservée
    assert len(result) > 0, "Aucune ligne conservée après nettoyage"


def test_clean_operations_has_operation_id_column(raw_operations):
    """Vérifie que operation_id est présent après nettoyage"""
    result = clean_operations(raw_operations)
    assert "operation_id" in result.columns, "operation_id manquant après nettoyage"


def test_clean_operations_cleans_strings(raw_operations):
    """Vérifie que les chaînes sont nettoyées (espaces retirés)"""
    result = clean_operations(raw_operations)
    if "cross" in result.columns and len(result) > 0:
        # Vérifier qu'il n'y a pas d'espaces en début/fin
        first_cross = str(result["cross"].iloc[0])
        assert first_cross == first_cross.strip(), "Les espaces n'ont pas été retirés"


def test_clean_operations_removes_invalid_sitrep(raw_operations):
    """Vérifie que numero_sitrep = 0 est remplacé par None"""
    result = clean_operations(raw_operations)
    # La première ligne avec sitrep=0 devrait être remplacée par None
    assert result["numero_sitrep"].iloc[0] is None or pd.isna(result["numero_sitrep"].iloc[0]), "numero_sitrep=0 devrait être remplacé par None"


# ==============================================================================
# TESTS CLEAN_OPERATIONS_STATS
# ==============================================================================

def test_clean_operations_stats_returns_dataframe(raw_operations_stats):
    """Vérifie que clean_operations_stats retourne un DataFrame"""
    result = clean_operations_stats(raw_operations_stats)
    assert isinstance(result, pd.DataFrame), "Le résultat devrait être un DataFrame"


def test_clean_operations_stats_preserves_data(raw_operations_stats):
    """Vérifie que les données sont préservées"""
    result = clean_operations_stats(raw_operations_stats)
    assert len(result) > 0, "Aucune ligne conservée"
    assert len(result.columns) > 0, "Aucune colonne conservée"


def test_clean_operations_stats_has_operation_id(raw_operations_stats):
    """Vérifie que operation_id est présent"""
    result = clean_operations_stats(raw_operations_stats)
    assert "operation_id" in result.columns, "operation_id manquant"


def test_clean_operations_stats_has_date_columns(raw_operations_stats):
    """Vérifie que les colonnes de date sont présentes"""
    result = clean_operations_stats(raw_operations_stats)
    date_columns = ["date", "annee", "mois"]
    for col in date_columns:
        if col in raw_operations_stats.columns:
            assert col in result.columns, f"Colonne {col} manquante après nettoyage"


def test_clean_operations_stats_filters_invalid_operation_id():
    """Vérifie que les operation_id invalides sont filtrés"""
    df_with_invalid = pd.DataFrame({
        "operation_id": [123, -1, 0, None, 456],
        "date": ["2023-01-01", "2023-02-01", "2023-03-01", "2023-04-01", "2023-05-01"]
    })
    result = clean_operations_stats(df_with_invalid)
    # Seuls les operation_id > 0 doivent rester (123 et 456)
    assert len(result) == 2, "Les operation_id invalides devraient être filtrés"
    assert all(result["operation_id"] > 0), "Tous les operation_id doivent être > 0"


# ==============================================================================
# TESTS CLEAN_FLOTTEURS
# ==============================================================================

def test_clean_flotteurs_returns_dataframe(raw_flotteurs):
    """Vérifie que clean_flotteurs retourne un DataFrame"""
    result = clean_flotteurs(raw_flotteurs)
    assert isinstance(result, pd.DataFrame), "Le résultat devrait être un DataFrame"


def test_clean_flotteurs_has_operation_id(raw_flotteurs):
    """Vérifie que operation_id est présent"""
    result = clean_flotteurs(raw_flotteurs)
    assert "operation_id" in result.columns, "operation_id manquant"


def test_clean_flotteurs_cleans_strings(raw_flotteurs):
    """Vérifie que les chaînes sont nettoyées"""
    result = clean_flotteurs(raw_flotteurs)
    if "pavillon" in result.columns and len(result) > 0:
        # Vérifier au moins une valeur non-NULL
        non_null_values = result["pavillon"].dropna()
        if len(non_null_values) > 0:
            first_pavillon = str(non_null_values.iloc[0])
            assert first_pavillon == first_pavillon.strip(), "Les espaces n'ont pas été retirés"


def test_clean_flotteurs_preserves_data(raw_flotteurs):
    """Vérifie que les données sont préservées"""
    result = clean_flotteurs(raw_flotteurs)
    assert len(result) > 0, "Aucune ligne conservée"


def test_clean_flotteurs_filters_invalid_operation_id():
    """Vérifie que les operation_id invalides sont filtrés"""
    df_with_invalid = pd.DataFrame({
        "operation_id": [123, -5, 0, None, 789],
        "numero_ordre": [1, 2, 3, 4, 5],
        "pavillon": ["Français", "Étranger", "Français", "Étranger", "Français"]
    })
    result = clean_flotteurs(df_with_invalid)
    # Seuls les operation_id > 0 doivent rester (123 et 789)
    assert len(result) == 2, "Les operation_id invalides devraient être filtrés"
    assert all(result["operation_id"] > 0), "Tous les operation_id doivent être > 0"


# ==============================================================================
# TESTS CLEAN_RESULTATS_HUMAIN
# ==============================================================================

def test_clean_resultats_humain_returns_dataframe(raw_resultats_humain):
    """Vérifie que clean_resultats_humain retourne un DataFrame"""
    result = clean_resultats_humain(raw_resultats_humain)
    assert isinstance(result, pd.DataFrame), "Le résultat devrait être un DataFrame"


def test_clean_resultats_humain_has_operation_id(raw_resultats_humain):
    """Vérifie que operation_id est présent"""
    result = clean_resultats_humain(raw_resultats_humain)
    assert "operation_id" in result.columns, "operation_id manquant"


def test_clean_resultats_humain_cleans_strings(raw_resultats_humain):
    """Vérifie que les chaînes sont nettoyées"""
    result = clean_resultats_humain(raw_resultats_humain)
    if "categorie_personne" in result.columns and len(result) > 0:
        non_null_values = result["categorie_personne"].dropna()
        if len(non_null_values) > 0:
            first_cat = str(non_null_values.iloc[0])
            assert first_cat == first_cat.strip(), "Les espaces n'ont pas été retirés"


def test_clean_resultats_humain_preserves_data(raw_resultats_humain):
    """Vérifie que les données sont préservées"""
    result = clean_resultats_humain(raw_resultats_humain)
    assert len(result) > 0, "Aucune ligne conservée"


def test_clean_resultats_humain_filters_invalid_operation_id():
    """Vérifie que les operation_id invalides sont filtrés"""
    df_with_invalid = pd.DataFrame({
        "operation_id": [123, -10, 0, None, 456],
        "categorie_personne": ["Plaisancier", "Pêcheur", "Commercial", "Autre", "Plaisancier"],
        "nombre": [3, 2, 1, 5, 4]
    })
    result = clean_resultats_humain(df_with_invalid)
    # Seuls les operation_id > 0 doivent rester (123 et 456)
    assert len(result) == 2, "Les operation_id invalides devraient être filtrés"
    assert all(result["operation_id"] > 0), "Tous les operation_id doivent être > 0"

