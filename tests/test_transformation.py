import pytest
import pandas as pd
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))
from cleaning.transformation import (
    clean_columns, 
    clean_strings, 
    clean_dates
)

# --------------------
# Tests clean_columns
# --------------------
def test_clean_columns(sample_dirty_df):
    df = sample_dirty_df.copy()
    df = clean_columns(df)
    
    # Les noms de colonnes doivent être en minuscules et sans espaces
    assert 'cross' in df.columns
    assert 'CROSS' not in df.columns


def test_clean_columns_espaces():
    df = pd.DataFrame({
        'Nom Complet': [1, 2],
        'Date': [3, 4]
    })
    
    df = clean_columns(df)
    
    assert 'nom_complet' in df.columns
    assert 'date' in df.columns


# --------------------
# Tests clean_strings  
# --------------------
def test_clean_strings():
    df = pd.DataFrame({
        'texte': ['  hello  ', 'WORLD', '  test  '],
        'nombre': [1, 2, 3]
    })
    
    df = clean_strings(df)
    
    # Les espaces en début/fin doivent être supprimés
    assert df.iloc[0]['texte'] == 'hello'
    assert df.iloc[1]['texte'] == 'WORLD'


def test_clean_strings_conserve_types():
    df = pd.DataFrame({
        'texte': ['test1', 'test2'],
        'nombre': [100, 200]
    })
    
    df = clean_strings(df)
    
    # Les colonnes numériques ne doivent pas être affectées
    assert df['nombre'].dtype in ['int64', 'Int64']


# --------------------
# Tests clean_dates
# --------------------
def test_clean_dates():
    df = pd.DataFrame({
        'date_col': ['2023-01-01 10:00:00', '2023-12-31 23:59:59'],
        'autre': [1, 2]
    })
    
    df = clean_dates(df, ['date_col'])
    
    # Les dates doivent être converties en format ISO8601
    assert 'T' in str(df.iloc[0]['date_col'])
    assert 'Z' in str(df.iloc[0]['date_col'])


def test_clean_dates_format_invalide():
    df = pd.DataFrame({
        'date_col': ['invalid_date', '2023-01-01'],
        'autre': [1, 2]
    })
    
    df = clean_dates(df, ['date_col'])
    
    # Les dates invalides doivent devenir NaT
    assert pd.isna(df.iloc[0]['date_col'])
