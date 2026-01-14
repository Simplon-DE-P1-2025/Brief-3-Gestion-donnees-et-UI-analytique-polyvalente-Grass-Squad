from src.ingestion.load_raw_data import load_all_raw_data
from src.validation.schemas_validation import validate_flotteurs , validate_resultats_humain


df_interventions, df_moyens, df_flotteurs, df_bilan_humain = load_all_raw_data()


#flotteurs
try:
    df_flotteurs = validate_flotteurs(df_flotteurs ,lazy = True)
    print("Validation des données flotteurs réussie.")
    print(df_flotteurs.head())
except Exception as e:
    print("Erreur de validation des données flotteurs :", e)


#resultat_humains
try:
    df_bilan_humain = validate_resultats_humain(df_bilan_humain, lazy=True)
    print("Validation des données résultats humains réussie.")
    print(df_bilan_humain.head())
except Exception as e:
    print("Erreur de validation des données résultats humains :", e)




