import pytest
import pandas as pd
import numpy as np
import sys
import os

# Ensure src is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.etl.cleaning import clean_coordinates, clean_dataframe

def test_clean_coordinates_valid():
    assert clean_coordinates(45.5) == 45.5
    assert clean_coordinates("45.5") == 45.5
    assert clean_coordinates("-10") == -10.0

def test_clean_coordinates_invalid():
    assert np.isnan(clean_coordinates("invalid"))
    assert np.isnan(clean_coordinates(None))

def test_clean_dataframe():
    data = {
        'latitude': ["45.5", "invalid", 40.0],
        'longitude': [5.5, 6.0, " 7.0 "],
        'text_col': ["  abc ", "def", "ghi  "]
    }
    df = pd.DataFrame(data)
    cleaned = clean_dataframe(df)
    
    assert cleaned['latitude'][0] == 45.5
    assert np.isnan(cleaned['latitude'][1])
    # check strip
    assert cleaned['text_col'][0] == "abc"
    assert cleaned['text_col'][2] == "ghi"
