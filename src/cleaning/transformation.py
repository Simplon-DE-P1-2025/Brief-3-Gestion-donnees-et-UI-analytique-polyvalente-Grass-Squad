import pandas as pd
pd.set_option('future.no_silent_downcasting', True)

# -----------------------------
# Fonctions génériques de nettoyage
# -----------------------------

def clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)
        .str.replace("'", "", regex=False)
        .str.replace("-", "_", regex=False)
    )
    return df

def drop_empty_rows(df: pd.DataFrame) -> pd.DataFrame:
    return df.dropna(how="all")

def clean_strings(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in df.select_dtypes(include="object").columns:
        # Vérifier que la colonne contient des strings avant d'appliquer .str
        if df[col].dtype == 'object':
            # Convertir en string avant de nettoyer
            df[col] = df[col].astype(str)
            df[col] = df[col].str.strip().replace({"": None, "NA": None, "N/A": None, "nan": None})
    return df



def clean_numeric_columns(df: pd.DataFrame, cols: list) -> pd.DataFrame:
    for col in cols:
        if col in df.columns:
            df[col] = df[col].fillna(0).astype("Int64")
    return df

def fix_negative_values(df: pd.DataFrame, cols: list) -> pd.DataFrame:
    for col in cols:
        if col in df.columns:
            df.loc[df[col] < 0, col] = 0
    return df

def clean_dates(df: pd.DataFrame, cols: list) -> pd.DataFrame:
    for col in cols:
        if col in df.columns:
            # Convertir en datetime puis en string ISO8601 format
            dt = pd.to_datetime(df[col], errors="coerce")
            df[col] = dt.dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    return df

def ensure_columns(df: pd.DataFrame, columns: dict) -> pd.DataFrame:
    for col, (dtype, default) in columns.items():
        if col not in df.columns:
            df[col] = default
        if dtype == "Int64":
            df[col] = df[col].astype("Int64")
        elif dtype == "float":
            df[col] = df[col].astype(float)
        elif dtype == "bool":
            df[col] = df[col].fillna(default if default is not None else False).astype(bool)
        elif dtype == "str":
            if default is not None:
                df[col] = df[col].fillna(default).astype(str)
        elif dtype == "datetime":
            df[col] = pd.to_datetime(df[col], errors="coerce")
            if hasattr(df[col].dtype, 'tz') and df[col].dtype.tz is not None:
                df[col] = df[col].dt.tz_localize(None)
    return df

def clean_operation_id(df: pd.DataFrame):
    """
    Nettoyage métier SECMAR :
    - operation_id doit être strictement positif
    - séparation données valides / rejetées
    """
    if "operation_id" not in df.columns:
        return df, pd.DataFrame()

    df = df.copy()

    df["operation_id"] = pd.to_numeric(df["operation_id"], errors="coerce")

    rejected = df[df["operation_id"].isna() | (df["operation_id"] <= 0)].copy()
    valid = df[df["operation_id"] > 0].copy()

    if not rejected.empty:
        rejected["rejection_reason"] = "operation_id invalid (<=0 or NaN)"

    valid["operation_id"] = valid["operation_id"].astype("Int64")

    return valid, rejected

# -----------------------------
# Normalisations spécifiques
# -----------------------------
RESULTAT_HUMAIN_MAP = {
    "personne secourue": "Personne secourue",
    "secourue": "Personne secourue",
    "decedee": "Personne décédée",
    "décédée": "Personne décédée",
    "disparue": "Personne disparue"
}

def normalize_resultat_humain(df: pd.DataFrame) -> pd.DataFrame:
    if "resultat_humain" in df.columns:
        df["resultat_humain"] = df["resultat_humain"].str.lower().map(RESULTAT_HUMAIN_MAP)
    return df

def normalize_pavillon(df: pd.DataFrame) -> pd.DataFrame:
    if "pavillon" in df.columns:
        df["pavillon"] = df["pavillon"].apply(
            lambda x: "Français" if pd.notna(x) and str(x).lower() == "français"
            else "Étranger" if pd.notna(x) and str(x).lower() == "étranger"
            else None
        )
    return df

# -----------------------------
# Nettoyage spécifique par DataFrame
# -----------------------------
import os
import pandas as pd

def clean_operations(
    df: pd.DataFrame,
    rejected_path: str = "data/rejected"
) -> pd.DataFrame:
    """
    Nettoyage complet de la table operations
    + traçabilité des lignes rejetées
    """

    os.makedirs(rejected_path, exist_ok=True)

    rejected_frames = []

    # Nettoyage operation_id
    df, rejected_op_id = clean_operation_id(df)
    if not rejected_op_id.empty:
        rejected_op_id["rejection_reason"] = "invalid_operation_id"
        rejected_op_id["rejection_step"] = "clean_operation_id"
        rejected_frames.append(rejected_op_id)


    # Duplicats
    duplicated = df[df.duplicated()].copy()
    if not duplicated.empty:
        duplicated["rejection_reason"] = "duplicate_row"
        duplicated["rejection_step"] = "drop_duplicates"
        rejected_frames.append(duplicated)

    df = df.drop_duplicates()


    # Nettoyages généraux
    df = clean_columns(df)
    df = drop_empty_rows(df)
    df = clean_strings(df)


    # Dates
    df = clean_dates(
        df,
        ["date_heure_reception_alerte", "date_heure_fin_operation"]
    )


    # Typage / colonnes attendues
    columns = {
        "operation_id": ("Int64", 0),
        "type_operation": ("str", None),
        "pourquoi_alerte": ("str", None),
        "moyen_alerte": ("str", None),
        "qui_alerte": ("str", None),
        "categorie_qui_alerte": ("str", None),
        "cross": ("str", None),
        "departement": ("str", None),
        "est_metropolitain": ("bool", None),
        "evenement": ("str", None),
        "categorie_evenement": ("str", None),
        "autorite": ("str", None),
        "seconde_autorite": ("str", None),
        "zone_responsabilite": ("str", None),
        "latitude": ("float", None),
        "longitude": ("float", None),
        "vent_direction": ("float", None),
        "vent_direction_categorie": ("str", None),
        "vent_force": ("float", None),
        "mer_force": ("float", None),
        "numero_sitrep": ("Int64", None),
        "cross_sitrep": ("str", None),
        "fuseau_horaire": ("str", None),
        "systeme_source": ("str", None)
    }

    df = ensure_columns(df, columns)

    df.loc[df["numero_sitrep"] == 0, "numero_sitrep"] = None

   
    # Cohérence métier des dates
    if (
        "date_heure_reception_alerte" in df.columns
        and "date_heure_fin_operation" in df.columns
    ):
        date_debut = pd.to_datetime(df["date_heure_reception_alerte"], errors="coerce")
        date_fin = pd.to_datetime(df["date_heure_fin_operation"], errors="coerce")

        invalid_dates = (
            date_debut.notna()
            & date_fin.notna()
            & (date_fin < date_debut)
        )

        if invalid_dates.any():
            rejected_dates = df[invalid_dates].copy()
            rejected_dates["rejection_reason"] = "date_fin < date_debut"
            rejected_dates["rejection_step"] = "date_coherence"
            rejected_frames.append(rejected_dates)

            df.loc[invalid_dates, "date_heure_fin_operation"] = None


    # Sauvegarde des rejets
    if rejected_frames:
        rejected_all = pd.concat(rejected_frames, ignore_index=True)
        rejected_file = os.path.join(
            rejected_path, "operations_cleaning_rejected.csv"
        )
        rejected_all.to_csv(rejected_file, index=False)
        print(f"➜ lignes rejetées sauvegardées : {rejected_file}")

    return df


def clean_operations_stats(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy().drop_duplicates()
    df = clean_columns(df)
    df = drop_empty_rows(df)
    df = clean_strings(df)
    
    # Nettoyage operation_id
    df, rejected_op_id = clean_operation_id(df)
    if not rejected_op_id.empty:
        os.makedirs("data/rejected", exist_ok=True)
        rejected_file = "data/rejected/operations_stats_rejected_raw.csv"
        rejected_op_id.to_csv(rejected_file, index=False)
        print(f"➜ lignes rejetées (operation_id invalide) sauvegardées : {rejected_file}")
    
    df = clean_dates(df, ["date"])
    
    # Convertir les colonnes float qui devraient être int en int64
    float_to_int_cols = ["distance_cote_metres", "maree_coefficient"]
    for col in float_to_int_cols:
        if col in df.columns:
            # Convertir float en int, en gérant les NaN
            df[col] = df[col].astype("Int64", errors="ignore")

    columns = {
        "operation_id": ("Int64", 0),
        "date": ("str", None),
        "annee": ("Int64", None),
        "mois": ("Int64", None),
        "jour": ("Int64", None),
        "mois_texte": ("str", None),
        "semaine": ("Int64", None),
        "annee_semaine": ("str", None),
        "jour_semaine": ("str", None),
        "est_weekend": ("bool", False),
        "est_jour_ferie": ("bool", False),
        "est_vacances_scolaires": ("bool", False)
    }

    df = ensure_columns(df, columns)
    return df

def clean_flotteurs(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy().drop_duplicates()
    df = clean_columns(df)
    df = drop_empty_rows(df)
    df = clean_strings(df)
    
    # Nettoyage operation_id
    df, rejected_op_id = clean_operation_id(df)
    if not rejected_op_id.empty:
        os.makedirs("data/rejected", exist_ok=True)
        rejected_file = "data/rejected/flotteurs_rejected_raw.csv"
        rejected_op_id.to_csv(rejected_file, index=False)
        print(f"➜ lignes rejetées (operation_id invalide) sauvegardées : {rejected_file}")
    
    df = normalize_pavillon(df)

    columns = {
        "operation_id": ("Int64", 0),
        "numero_ordre": ("Int64", 1),
        "pavillon": ("str", None),
        "resultat_flotteur": ("str", "Non renseigné"),
        "type_flotteur": ("str", "Non renseigné"),
        "categorie_flotteur": ("str", "Non renseigné"),
        "numero_immatriculation": ("str", None)
    }

    df = ensure_columns(df, columns)
    
    # Remplir les colonnes non-nullables
    df.loc[:, 'resultat_flotteur'] = df['resultat_flotteur'].fillna("Non renseigné")
    df.loc[:, 'type_flotteur'] = df['type_flotteur'].fillna("Non renseigné")
    df.loc[:, 'categorie_flotteur'] = df['categorie_flotteur'].fillna("Non renseigné")
    df.loc[:, 'numero_ordre'] = df['numero_ordre'].fillna(1)
    
    # Contrainte d'unicité : supprimer doublons sur (operation_id, numero_ordre)
    # Garder la première occurrence
    df = df.drop_duplicates(subset=['operation_id', 'numero_ordre'], keep='first')

    return df

def clean_resultats_humain(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy().drop_duplicates()
    df = clean_columns(df)
    df = drop_empty_rows(df)
    df = clean_strings(df)
    
    # Nettoyage operation_id
    df, rejected_op_id = clean_operation_id(df)
    if not rejected_op_id.empty:
        os.makedirs("data/rejected", exist_ok=True)
        rejected_file = "data/rejected/resultats_humain_rejected_raw.csv"
        rejected_op_id.to_csv(rejected_file, index=False)
        print(f"➜ lignes rejetées (operation_id invalide) sauvegardées : {rejected_file}")
    
    df = normalize_resultat_humain(df)
    df = clean_numeric_columns(df, ["nombre", "dont_nombre_blesse"])
    df = fix_negative_values(df, ["nombre", "dont_nombre_blesse"])

    columns = {
        "operation_id": ("Int64", 0),
        "categorie_personne": ("str", "Non renseigné"),
        "resultat_humain": ("str", "Non renseigné"),
        "nombre": ("Int64", 0),
        "dont_nombre_blesse": ("Int64", 0)
    }
    
    df = ensure_columns(df, columns)
    
    # Remplir les NULL dans les colonnes qui font partie de la clé primaire
    df.loc[:, 'categorie_personne'] = df['categorie_personne'].fillna("Non renseigné")
    df.loc[:, 'resultat_humain'] = df['resultat_humain'].fillna("Non renseigné")
    
    # Contrainte d'unicité : supprimer doublons sur (operation_id, categorie_personne, resultat_humain)
    # Agréger les nombres pour les doublons
    df = df.groupby(['operation_id', 'categorie_personne', 'resultat_humain'], as_index=False).agg({
        'nombre': 'sum',
        'dont_nombre_blesse': 'sum'
    })
    
    # Assurer dont_nombre_blesse <= nombre
    df.loc[df['dont_nombre_blesse'] > df['nombre'], 'dont_nombre_blesse'] = df['nombre']
    
    return df
