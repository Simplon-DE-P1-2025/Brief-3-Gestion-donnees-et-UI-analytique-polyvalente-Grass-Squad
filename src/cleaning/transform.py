from src.ingestion.load_raw_data import load_all_raw_data
from src.validation.schemas_validation import validate_flotteurs , validate_resultats_humain


df_interventions, df_moyens, df_flotteurs, df_bilan_humain = load_all_raw_data()
