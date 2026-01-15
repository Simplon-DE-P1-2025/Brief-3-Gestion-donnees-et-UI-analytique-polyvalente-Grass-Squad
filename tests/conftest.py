import pytest
import pandas as pd
from pathlib import Path
import sys

# Ajouter src au chemin Python
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

# --------------------
# Fixtures pour fichiers temporaires
# --------------------
@pytest.fixture
def csv_operations_content():
    return """cross,operation,pourquoi_alerte,qui_alerte,date_heure_reception_alerte
CROSS-MED,OP001,Détresse,Personne,2023-01-01T10:00:00Z
CROSS-ATL,OP002,Avarie,Capitaine,2023-01-02T11:00:00Z"""

@pytest.fixture
def csv_operations_stats_content():
    return """operation,ev_id,date,departement
OP001,1,2023-01-01,13
OP002,2,2023-01-02,29"""

@pytest.fixture
def csv_flotteurs_content():
    return """operation,numero_ordre,pavillon
OP001,1,FR
OP002,2,UK"""

@pytest.fixture
def csv_resultats_humain_content():
    return """operation,numero_ordre,resultat_humain
OP001,1,Assisté
OP002,2,"""

@pytest.fixture
def sample_operations_df():
    return pd.DataFrame({
        'cross': ['CROSS-MED', 'CROSS-ATL'],
        'operation': ['OP001', 'OP002'],
        'pourquoi_alerte': ['Détresse', 'Avarie'],
        'date_heure_reception_alerte': ['2023-01-01T10:00:00Z', '2023-01-02T11:00:00Z']
    })

@pytest.fixture
def sample_dirty_df():
    return pd.DataFrame({
        'CROSS': ['  cross1  ', 'CROSS2'],
        'Date Heure': ['2023-01-01 10:00:00', '2023-01-02'],
        'Numero': [1.0, 2.0]
    })
