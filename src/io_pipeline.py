import pandas as pd
import requests
from typing import Optional


def read_csv(
    file_path: str,
    encoding: str = "utf-8",
    sep: str = ",",
    low_memory: bool = False
) -> pd.DataFrame:
    """
    Lecture d'un fichier CSV
    """
    return pd.read_csv(file_path, encoding=encoding, sep=sep, low_memory=low_memory)


def read_parquet(file_path: str) -> pd.DataFrame:
    """
    Lecture d'un fichier Parquet
    """
    return pd.read_parquet(file_path)


def read_api(
    url: str,
    params: Optional[dict] = None,
    timeout: int = 10
) -> pd.DataFrame:
    """
    Lecture de données depuis une API REST
    """
    response = requests.get(url, params=params, timeout=timeout)
    response.raise_for_status()

    data = response.json()
    return pd.DataFrame(data)


def load_data(source_type: str, source: str) -> pd.DataFrame:
    """
    Fonction centrale d'ingestion

    source_type : csv | parquet | api
    source      : chemin du fichier ou URL API
    """
    if source_type == "csv":
        return read_csv(source)
    elif source_type == "parquet":
        return read_parquet(source)
    elif source_type == "api":
        return read_api(source)
    else:
        raise ValueError(f"Type de source non supporté : {source_type}")
