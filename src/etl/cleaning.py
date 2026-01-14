import pandas as pd
import numpy as np

def clean_coordinates(coord):
    """
    Cleans coordinate values.
    - Converts to numeric.
    - Handles various formats if needed (text).
    - Returns NaN for invalid values.
    """
    if pd.isna(coord):
        return np.nan
        
    try:
        val = float(coord)
        # Check range? Lat -90 to 90, Lon -180 to 180?
        # Let's assume generic cleaning for now
        return val
    except ValueError:
        return np.nan

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply standard cleaning to the operations dataframe.
    """
    df = df.copy()
    if 'latitude' in df.columns:
        df['latitude'] = df['latitude'].apply(clean_coordinates)
    if 'longitude' in df.columns:
        df['longitude'] = df['longitude'].apply(clean_coordinates)
        
    # Example: Clean string columns (strip whitespace)
    for col in df.select_dtypes(include='object').columns:
        df[col] = df[col].str.strip()
        
    return df
