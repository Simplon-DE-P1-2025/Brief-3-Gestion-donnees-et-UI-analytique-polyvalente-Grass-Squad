"""
Fonctions de formatage pour l'affichage des données
"""
import pandas as pd
from typing import Any


def format_datetime(value: Any) -> str:
    """
    Formate une date/heure pour l'affichage
    
    Args:
        value: Valeur à formater (datetime ou None)
        
    Returns:
        Chaîne formatée ou "-"
    """
    if pd.isna(value):
        return "-"
    if isinstance(value, pd.Timestamp):
        return value.strftime('%Y-%m-%d %H:%M')
    return str(value)


def format_coordinates(lat: Any, lon: Any) -> str:
    """
    Formate des coordonnées géographiques
    
    Args:
        lat: Latitude
        lon: Longitude
        
    Returns:
        Coordonnées formatées ou "-"
    """
    if pd.notna(lat) and pd.notna(lon):
        return f"{float(lat):.2f}, {float(lon):.2f}"
    return "-"


def format_text(value: Any, max_length: int = 20) -> str:
    """
    Formate un texte avec troncature optionnelle
    
    Args:
        value: Valeur à formater
        max_length: Longueur maximale avant troncature
        
    Returns:
        Texte formaté
    """
    if pd.isna(value):
        return "-"
    
    text = str(value)
    if len(text) > max_length:
        return text[:max_length] + "..."
    return text


def format_metric(value: Any, default: Any = 0) -> Any:
    """
    Formate une valeur métrique pour l'affichage
    
    Args:
        value: Valeur à formater
        default: Valeur par défaut si None
        
    Returns:
        Valeur formatée
    """
    if pd.isna(value):
        return default
    if isinstance(value, (int, float)):
        return int(value)
    return value
