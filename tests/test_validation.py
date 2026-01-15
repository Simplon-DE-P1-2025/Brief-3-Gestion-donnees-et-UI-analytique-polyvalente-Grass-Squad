import pytest
import pandas as pd
from pathlib import Path
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.etl.validation import validate_operations

def test_validate_operations_valid():
    data = {
        "operation_id": [1, 2],
        "latitude": [45.0, -45.0],
        "longitude": [10.0, -10.0],
        "vent_direction": [180, 0]
    }
    df = pd.DataFrame(data)
    # Should not raise exception
    validated = validate_operations(df)
    assert validated is not None

def test_validate_operations_invalid_range():
    data = {
        "operation_id": [1],
        "latitude": [100.0], # Invalid > 90
        "longitude": [0.0],
        "vent_direction": [0]
    }
    df = pd.DataFrame(data)
    
    with pytest.raises(pa.errors.SchemaError):
        validate_operations(df)

def test_validate_operations_missing_col():
    data = {
        "latitude": [45.0]
        # Missing operation_id
    }
    df = pd.DataFrame(data)
    
    with pytest.raises(pa.errors.SchemaError): # Note: SchemaError for missing col/type mismatch
        validate_operations(df)
