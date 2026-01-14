import pandas as pd
pd.set_option('future.no_silent_downcasting', True)


# Fonction générique pour créer les colonnes manquantes avec type et valeur par défaut
def ensure_columns(df: pd.DataFrame, columns: dict) -> pd.DataFrame:
    for col, (dtype, default) in columns.items():
        if col not in df.columns:
            df[col] = default
        if dtype == "Int64":
            df[col] = df[col].astype("Int64")
        elif dtype == "float":
            df[col] = df[col].astype(float)
        elif dtype == "bool":
            if default is not None:
                df[col] = df[col].fillna(default).infer_objects(copy =False)
                df[col] = df[col].astype(bool)
            # Si default est None, on laisse les valeurs nullable
        elif dtype == "str":
            if default is not None:
                df[col] = df[col].fillna(default).infer_objects(copy =False)
                df[col] = df[col].astype(str)
            # Si default est None, on garde les NaN/None tels quels
        elif dtype == "datetime":
            df[col] = pd.to_datetime(df[col], errors="coerce")
            # Supprimer timezone si présente
            if hasattr(df[col].dtype, 'tz') and df[col].dtype.tz is not None:
                df[col] = df[col].dt.tz_localize(None)
    return df

# -----------------------------
# Nettoyage robuste df_operations
# -----------------------------
def clean_operations(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy().drop_duplicates()

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
        "date_heure_reception_alerte": ("datetime", pd.NaT),
        "date_heure_fin_operation": ("datetime", pd.NaT),
        "numero_sitrep": ("Int64", None),  # Doit être None ou >= 1
        "cross_sitrep": ("str", None),
        "fuseau_horaire": ("str", None),
        "systeme_source": ("str", None)
    }

    df = ensure_columns(df, columns)
    
    # Remplacer les 0 par None dans numero_sitrep (contrainte >= 1)
    df.loc[df['numero_sitrep'] == 0, 'numero_sitrep'] = None
    
    return df

# -----------------------------
# Nettoyage robuste df_operations_stats
# -----------------------------
def clean_operations_stats(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy().drop_duplicates()

    columns = {
        "operation_id": ("Int64", 0),
        "date": ("datetime", pd.NaT),
        "annee": ("Int64", None),
        "mois": ("Int64", None),
        "jour": ("Int64", None),
        "mois_texte": ("str", None),
        "semaine": ("Int64", None),
        "annee_semaine": ("str", None),
        "jour_semaine": ("str", None),
        "est_weekend": ("bool", False),
        "est_jour_ferie": ("bool", False),
        "est_vacances_scolaires": ("bool", False),  # Changé de None à False
        "phase_journee": ("str", None),
        "concerne_plongee": ("bool", False),
        "implique_wingfoil": ("bool", False),
        "avec_clandestins": ("bool", False),
        "distance_cote_metres": ("Int64", None),
        "distance_cote_milles_nautiques": ("float", None),
        "est_dans_stm": ("bool", False),
        "nom_stm": ("str", None),
        "est_dans_dst": ("bool", False),
        "nom_dst": ("str", None),
        "prefecture_maritime": ("str", None),
        "maree_port": ("str", None),
        "maree_coefficient": ("Int64", None),
        "maree_categorie": ("str", None),
        # Colonnes de nombre de personnes
        "nombre_personnes_blessees": ("Int64", 0),
        "nombre_personnes_assistees": ("Int64", 0),
        "nombre_personnes_decedees": ("Int64", 0),
        "nombre_personnes_decedees_accidentellement": ("Int64", 0),
        "nombre_personnes_decedees_naturellement": ("Int64", 0),
        "nombre_personnes_disparues": ("Int64", 0),
        "nombre_personnes_impliquees_dans_fausse_alerte": ("Int64", 0),
        "nombre_personnes_retrouvees": ("Int64", 0),
        "nombre_personnes_secourues": ("Int64", 0),
        "nombre_personnes_tirees_daffaire_seule": ("Int64", 0),
        "nombre_personnes_tous_deces": ("Int64", 0),
        "nombre_personnes_tous_deces_ou_disparues": ("Int64", 0),
        "nombre_personnes_impliquees": ("Int64", 0),
        # Colonnes flotteurs
        "nombre_flotteurs_commerce_impliques": ("Int64", 0),
        "nombre_flotteurs_peche_impliques": ("Int64", 0),
        "nombre_flotteurs_plaisance_impliques": ("Int64", 0),
        "nombre_flotteurs_loisirs_nautiques_impliques": ("Int64", 0),
        "nombre_aeronefs_impliques": ("Int64", 0),
        "nombre_flotteurs_autre_impliques": ("Int64", 0),
        "nombre_flotteurs_annexe_impliques": ("Int64", 0),
        "nombre_flotteurs_autre_loisir_nautique_impliques": ("Int64", 0),
        "nombre_flotteurs_canoe_kayak_aviron_impliques": ("Int64", 0),
        "nombre_flotteurs_engin_de_plage_impliques": ("Int64", 0),
        "nombre_flotteurs_kitesurf_impliques": ("Int64", 0),
        "nombre_flotteurs_plaisance_voile_legere_impliques": ("Int64", 0),
        "nombre_flotteurs_plaisance_a_moteur_impliques": ("Int64", 0),
        "nombre_flotteurs_plaisance_a_moteur_moins_8m_impliques": ("Int64", 0),
        "nombre_flotteurs_plaisance_a_moteur_plus_8m_impliques": ("Int64", 0),
        "nombre_flotteurs_plaisance_a_voile_impliques": ("Int64", 0),
        "nombre_flotteurs_planche_a_voile_impliques": ("Int64", 0),
        "nombre_flotteurs_ski_nautique_impliques": ("Int64", 0),
        "nombre_flotteurs_surf_impliques": ("Int64", 0),
        "nombre_flotteurs_vehicule_nautique_a_moteur_impliques": ("Int64", 0),
        "sans_flotteur_implique": ("bool", False)
    }

    df = ensure_columns(df, columns)
    # Convert date column to date only
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date
    return df

# -----------------------------
# Nettoyage robuste df_flotteurs
# -----------------------------
def clean_flotteurs(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy().drop_duplicates()

    columns = {
        "operation_id": ("Int64", 0),
        "numero_ordre": ("Int64", 1),  # numero_ordre doit être >= 1
        "pavillon": ("str", None),
        "resultat_flotteur": ("str", "Non renseigné"),  # Non-nullable
        "type_flotteur": ("str", "Non renseigné"),  # Non-nullable
        "categorie_flotteur": ("str", "Non renseigné"),  # Non-nullable
        "numero_immatriculation": ("str", None)
    }

    df = ensure_columns(df, columns)
    
    # Remplacer les NULL dans les colonnes non-nullables
    df.loc[:, 'resultat_flotteur'] = df['resultat_flotteur'].fillna("Non renseigné")
    df.loc[:, 'type_flotteur'] = df['type_flotteur'].fillna("Non renseigné")
    df.loc[:, 'categorie_flotteur'] = df['categorie_flotteur'].fillna("Non renseigné")
    
    # Gérer les numero_ordre NULL (colonne non-nullable)
    df.loc[:, 'numero_ordre'] = df['numero_ordre'].fillna(1)

    # Normalisation pavillon
    df.loc[:, 'pavillon'] = df['pavillon'].apply(
        lambda x: "Français" if pd.notna(x) and str(x).lower() == "français"
        else "Étranger" if pd.notna(x) and str(x).lower() == "étranger"
        else None
    )

    return df

# -----------------------------
# Nettoyage robuste df_resultats_humain
# -----------------------------
def clean_resultats_humain(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy().drop_duplicates()

    columns = {
        "operation_id": ("Int64", 0),
        "categorie_personne": ("str", None),
        "resultat_humain": ("str", None),
        "nombre": ("Int64", 0),
        "dont_nombre_blesse": ("Int64", 0)
    }

    df = ensure_columns(df, columns)
    return df
