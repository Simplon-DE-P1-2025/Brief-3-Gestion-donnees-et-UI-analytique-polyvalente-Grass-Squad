import pandera.pandas as pa
from pandera.typing import Series
import pandas as pd

# Validations des flotteurs
class FlotteursSchema(pa.DataFrameModel):
    operation_id: Series[int] = pa.Field(nullable=False)
    numero_ordre: Series[float] = pa.Field(nullable=True)
    pavillon: Series[str] = pa.Field(nullable=True)
    resultat_flotteur: Series[str] = pa.Field(nullable=True)
    type_flotteur: Series[str] = pa.Field(nullable=True)
    categorie_flotteur: Series[str] = pa.Field(nullable=True)
    numero_immatriculation: Series[str] = pa.Field(nullable=True)

def validate_flotteurs(df: pd.DataFrame, lazy: bool = False) -> pd.DataFrame:
    """Valide le DataFrame flotteurs avec Pandera"""
    return FlotteursSchema.validate(df, lazy=lazy)

# Validations des flotteurs
class ResultatsHumainSchema(pa.DataFrameModel):
    operation_id: Series[int] = pa.Field(nullable=False)  # doit toujours exister
    categorie_personne: Series[str] = pa.Field(nullable=False)  # obligatoire
    resultat_humain: Series[str] = pa.Field(nullable=False)     # obligatoire
    nombre: Series[int] = pa.Field(nullable=False, ge=0)       # >=0
    dont_nombre_blesse: Series[int] = pa.Field(nullable=False, ge=0)  # >=0
    
    
def validate_resultats_humain(df: pd.DataFrame, lazy: bool = False) -> pd.DataFrame:
    return ResultatsHumainSchema.validate(df, lazy=lazy)