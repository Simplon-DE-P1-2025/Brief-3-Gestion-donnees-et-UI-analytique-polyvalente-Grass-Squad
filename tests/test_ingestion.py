import pytest
import pandas as pd
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))
from io_pipeline import load_data

# --------------------
# Tests load_data
# --------------------
def test_load_data_csv_valide(tmp_path):
    content = "col1,col2\n1,2\n3,4"
    file = tmp_path / "test.csv"
    file.write_text(content)
    
    df = load_data("csv", str(file))
    
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (2, 2)
    assert list(df.columns) == ["col1", "col2"]


def test_load_data_fichier_inexistant():
    # load_data lève une exception si le fichier n'existe pas
    with pytest.raises(FileNotFoundError):
        load_data("csv", "fichier_inexistant.csv")


def test_load_data_retourne_dataframe(tmp_path):
    content = "a,b,c\n1,2,3"
    file = tmp_path / "test.csv"
    file.write_text(content)
    
    result = load_data("csv", str(file))
    
    assert isinstance(result, pd.DataFrame)
    assert not result.empty
