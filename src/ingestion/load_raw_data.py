import pandas as pd
from pathlib import Path
from typing import Tuple
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from config import RAW_DATA_DIR
from io_pipeline import load_data


def load_all_raw_data() -> dict:
    """
    Charge les 4 sources de données brutes et retourne un dictionnaire de DataFrames
    
    Returns:
        dict: Dictionnaire avec les clés 'operations', 'operations_stats', 'flotteurs', 'resultats_humain'
    """

    # Définition des paths des sources
    operations_path = RAW_DATA_DIR / "operations.csv"
    operations_stats_path = RAW_DATA_DIR / "operations_stats.csv"
    flotteurs_path = RAW_DATA_DIR / "flotteurs.csv"
    resultats_humain_path = RAW_DATA_DIR / "resultats_humain.csv"

    # Lecture des données
    df_operations = load_data("csv", operations_path)
    df_operations_stats = load_data("csv", operations_stats_path)
    df_flotteurs = load_data("csv", flotteurs_path)
    df_resultats_humain = load_data("csv", resultats_humain_path)

    return {
        'operations': df_operations,
        'operations_stats': df_operations_stats,
        'flotteurs': df_flotteurs,
        'resultats_humain': df_resultats_humain
    }

