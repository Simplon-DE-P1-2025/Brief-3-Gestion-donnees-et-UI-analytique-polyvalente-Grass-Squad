import pandas as pd
import requests

def read_csv(file_path: str, encoding: str = "utf-8", sep: str = ",") -> pd.DataFrame:
    return pd.read_csv(file_path, encoding=encoding, sep=sep)

def read_parquet(file_path: str) -> pd.DataFrame:
    return pd.read_parquet(file_path)

def read_api(url: str, params: dict = None) -> pd.DataFrame:
    response = requests.get(url, params=params)
    response.raise_for_status()
    return pd.DataFrame(response.json())


def load_data(source_type: str, source: str) -> pd.DataFrame:
    """
    Fonction centrale pour charger les données.
    source_type: "csv", "parquet", "api"
    source: chemin du fichier ou URL de l'API
    """
    if source_type == "csv":
        return read_csv(source)
    elif source_type == "parquet":
        return read_parquet(source)
    elif source_type == "api":
        return read_api(source)
    else:
        raise ValueError("Type de source non supporté")