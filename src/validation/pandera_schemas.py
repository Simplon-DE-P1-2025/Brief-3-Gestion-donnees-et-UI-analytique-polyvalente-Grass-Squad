"""
Schémas de validation Pandera pour toutes les tables
"""
import pandera as pa
from pandera import Column, Check, DataFrameSchema
from datetime import datetime

# Schéma pour la table operations
operations_schema = DataFrameSchema({
    "operation_id": Column(int, nullable=True),  # Nullable car auto-généré
    "cross": Column(str, Check.str_length(min_value=1, max_value=50), nullable=False),
    "date_heure_reception_alerte": Column(pa.DateTime, nullable=False),
    "evenement": Column(str, nullable=True),
    "departement": Column(str, nullable=True),
    "pourquoi_alerte": Column(str, nullable=True),
    "moyen_alerte": Column(str, nullable=True),
    "categorie_qui_alerte": Column(str, nullable=True),
    "qui_est_alerte": Column(str, nullable=True),
    "numero_sitrep": Column(str, nullable=True),
    "latitude": Column(float, Check.in_range(-90, 90), nullable=True),
    "longitude": Column(float, Check.in_range(-180, 180), nullable=True),
    "zone_responsabilite": Column(str, nullable=True),
    "fuseau_horaire": Column(str, nullable=True),
    "distance_cote_metres": Column(float, Check.greater_than_or_equal_to(0), nullable=True),
    "prefecture_maritime": Column(str, nullable=True),
}, strict=False)

# Schéma pour la table flotteurs
flotteurs_schema = DataFrameSchema({
    "flotteur_id": Column(int, nullable=True),
    "operation_id": Column(int, nullable=False),
    "pavillon": Column(str, nullable=True),
    "resultat_flotteur": Column(str, nullable=True),
    "type_flotteur": Column(str, nullable=True),
    "numero_immatriculation": Column(str, nullable=True),
    "marque": Column(str, nullable=True),
    "nom_serie": Column(str, nullable=True),
    "assurance": Column(str, nullable=True),
    "longueur": Column(float, Check.greater_than(0), nullable=True),
    "largeur": Column(float, Check.greater_than(0), nullable=True),
    "jauge": Column(float, nullable=True),
    "puissance_max_moteur_ch": Column(float, Check.greater_than_or_equal_to(0), nullable=True),
}, strict=False)

# Schéma pour la table resultats_humain
resultats_humain_schema = DataFrameSchema({
    "resultat_humain_id": Column(int, nullable=True),
    "operation_id": Column(int, nullable=False),
    "categorie_personne": Column(str, nullable=True),
    "resultat_humain": Column(str, nullable=True),
    "nombre": Column(int, Check.greater_than_or_equal_to(0), nullable=True),
}, strict=False)

# Schéma pour la table operations_stats
operations_stats_schema = DataFrameSchema({
    "stat_id": Column(int, nullable=True),
    "operation_id": Column(int, nullable=False),
    "nombre_personnes_tous_deces": Column(int, Check.greater_than_or_equal_to(0), nullable=True),
    "nombre_personnes_disparues": Column(int, Check.greater_than_or_equal_to(0), nullable=True),
    "nombre_personnes_impliquees": Column(int, Check.greater_than_or_equal_to(0), nullable=True),
    "nombre_personnes_blessees": Column(int, Check.greater_than_or_equal_to(0), nullable=True),
    "nombre_personnes_assistees": Column(int, Check.greater_than_or_equal_to(0), nullable=True),
    "nombre_personnes_decedees_accidentellement": Column(int, Check.greater_than_or_equal_to(0), nullable=True),
    "nombre_personnes_decedees_naturellement": Column(int, Check.greater_than_or_equal_to(0), nullable=True),
    "nombre_personnes_indemnes": Column(int, Check.greater_than_or_equal_to(0), nullable=True),
    "nombre_personnes_retrouvees": Column(int, Check.greater_than_or_equal_to(0), nullable=True),
    "nombre_personnes_tirees_daffaire_seule": Column(int, Check.greater_than_or_equal_to(0), nullable=True),
    "nombre_personnes_secourues": Column(int, Check.greater_than_or_equal_to(0), nullable=True),
    "nombre_personnes_autres": Column(int, Check.greater_than_or_equal_to(0), nullable=True),
}, strict=False)


def validate_dataframe(df, schema):
    """
    Valide un DataFrame avec un schéma Pandera
    
    Args:
        df: DataFrame à valider
        schema: Schéma Pandera à utiliser
        
    Returns:
        tuple: (validated_df, errors)
        - validated_df: DataFrame validé si succès, None sinon
        - errors: Liste des erreurs si échec, None sinon
    """
    try:
        validated_df = schema.validate(df, lazy=True)
        return validated_df, None
    except pa.errors.SchemaErrors as e:
        error_messages = []
        for error in e.failure_cases.itertuples():
            error_messages.append({
                'column': error.column,
                'check': error.check,
                'value': error.failure_case,
                'index': error.index
            })
        return None, error_messages
    except Exception as e:
        return None, [{'error': str(e)}]


def validate_operations_data(data_dict):
    """
    Valide les données d'une opération avant insertion
    
    Args:
        data_dict: Dictionnaire contenant les données de l'opération
        
    Returns:
        tuple: (is_valid, errors)
    """
    import pandas as pd
    
    # Convertir en DataFrame
    df = pd.DataFrame([data_dict])
    
    # Valider
    return validate_dataframe(df, operations_schema)


def validate_flotteur_data(data_dict):
    """Valide les données d'un flotteur"""
    import pandas as pd
    df = pd.DataFrame([data_dict])
    return validate_dataframe(df, flotteurs_schema)


def validate_resultat_humain_data(data_dict):
    """Valide les données d'un résultat humain"""
    import pandas as pd
    df = pd.DataFrame([data_dict])
    return validate_dataframe(df, resultats_humain_schema)


def validate_operations_stats_data(data_dict):
    """Valide les données de statistiques"""
    import pandas as pd
    df = pd.DataFrame([data_dict])
    return validate_dataframe(df, operations_stats_schema)
