import pandas as pd
from pathlib import Path
from typing import Tuple
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from config import RAW_DATA_DIR
from io_pipeline import load_data


def load_all_raw_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Charge les 4 sources de données brutes et retourne 4 DataFrames
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

    return (
        df_operations,
        df_operations_stats,
        df_flotteurs,
        df_resultats_humain
    )


if __name__ == "__main__":
    (
        df_operations,
        df_operations_stats,
        df_flotteurs,
        df_resultats_humain
    ) = load_all_raw_data()

    print("Aperçu des données chargées :")
    
    print("\ndf_operations shape : :", df_operations.shape)
    print("df_operations :", df_operations.head(5))
    
    print("\ndf_operations_stats shape : :", df_operations_stats.shape)
    print("df_operations_stats :", df_operations_stats.head(5))
    
    print("\ndf_flotteurs shape : :", df_flotteurs.shape)
    print("df_flotteurs :", df_flotteurs.head(5))
    
    print("\ndf_resultats_humain shape : :", df_resultats_humain.shape)
    print("df_resultats_humain :", df_resultats_humain.head(5))

