import pandera.pandas as pa
from pandera import Column, Check
import datetime
import pandas as pd
# -----------------------------
# Schéma pour df_operations
# -----------------------------

schema_operations = pa.DataFrameSchema({
    "operation_id": Column(pd.Int64Dtype(), nullable=False),
    "type_operation": Column(str, Check.isin(["SAR", "MAS", "DIV", "SUR", "POL"]), nullable=True),
    "pourquoi_alerte": Column(str, nullable=True),
    "moyen_alerte": Column(str, nullable=True),
    "qui_alerte": Column(str, nullable=True),
    "categorie_qui_alerte": Column(str, nullable=True),
    "cross": Column(str, nullable=False),
    "departement": Column(str, nullable=True),
    "est_metropolitain": Column(bool, nullable=True),
    "evenement": Column(str, nullable=True),
    "categorie_evenement": Column(str, nullable=True),
    "autorite": Column(str, nullable=True),
    "seconde_autorite": Column(str, nullable=True),
    "zone_responsabilite": Column(str, nullable=True),
    "latitude": Column(float, Check(lambda x: (-90 <= x) & (x <= 90)), nullable=True),
    "longitude": Column(float, Check(lambda x: (-180 <= x) & (x <= 180)), nullable=True),
    "vent_direction": Column(float, Check(lambda x: (0 <= x) & (x <= 360)), nullable=True),
    "vent_direction_categorie": Column(str, Check.isin(["nord", "nord-est", "est", "sud-est", "sud", "sud-ouest", "ouest", "nord-ouest"]), nullable=True),
    "vent_force": Column(float, Check(lambda x: (0 <= x) & (x <= 12)), nullable=True),
    "mer_force": Column(float, Check(lambda x: (0 <= x) & (x <= 9)), nullable=True),
    "date_heure_reception_alerte": Column(str, nullable=False),
    "date_heure_fin_operation": Column(str, nullable=True),
    "numero_sitrep": Column(pd.Int64Dtype(), Check.greater_than_or_equal_to(1), nullable=True),
    "cross_sitrep": Column(str, nullable=True),
    "fuseau_horaire": Column(str, nullable=True),   
    "systeme_source": Column(str, Check.isin(["secmarweb", "seamis_json"]), nullable=True)
})

# -----------------------------
# Schéma pour df_operations_stats
# -----------------------------
schema_operations_stats = pa.DataFrameSchema({
    "operation_id": Column(int, nullable=False),
    "date": Column(str, nullable=False),
    "annee": Column(int, Check.ge(1980), nullable=False),
    "mois": Column(int, Check.in_range(1,12), nullable=False),
    "jour": Column(int, Check.in_range(1,31), nullable=False),
    "mois_texte": Column(str, Check.isin(["Janvier","Février","Mars","Avril","Mai","Juin","Juillet","Août","Septembre","Octobre","Novembre","Décembre"]), nullable=False),
    "semaine": Column(int, Check.in_range(1,53), nullable=False),
    "annee_semaine": Column(str, nullable=False),
    "jour_semaine": Column(str, Check.isin(["Lundi","Mardi","Mercredi","Jeudi","Vendredi","Samedi","Dimanche"]), nullable=False),
    "est_weekend": Column(bool, nullable=False),
    "est_jour_ferie": Column(bool, nullable=False),
    "est_vacances_scolaires": Column(bool, nullable=True),
    "phase_journee": Column(str, Check.isin(["matinée","déjeuner","après-midi","nuit"]), nullable=True),
    "concerne_plongee": Column(bool, nullable=False),
    "implique_wingfoil": Column(bool, nullable=False),
    "avec_clandestins": Column(bool, nullable=False),
    "distance_cote_metres": Column(int, nullable=True),
    "distance_cote_milles_nautiques": Column(float, nullable=True),
    "est_dans_stm": Column(bool, nullable=False),
    "nom_stm": Column(str, nullable=True),
    "est_dans_dst": Column(bool, nullable=False),
    "nom_dst": Column(str, nullable=True),
    "prefecture_maritime": Column(str, Check.isin(["manche","atlantique","mediterranee"]), nullable=True),
    "maree_port": Column(str, nullable=True),
    "maree_coefficient": Column(int, Check.in_range(20,120), nullable=True),
    "maree_categorie": Column(str, Check.isin(["20-45","46-70","71-95","96-120"]), nullable=True),
    # Colonnes de nombre de personnes
    "nombre_personnes_blessees": Column(int, Check.ge(0)),
    "nombre_personnes_assistees": Column(int, Check.ge(0)),
    "nombre_personnes_decedees": Column(int, Check.ge(0)),
    "nombre_personnes_decedees_accidentellement": Column(int, Check.ge(0)),
    "nombre_personnes_decedees_naturellement": Column(int, Check.ge(0)),
    "nombre_personnes_disparues": Column(int, Check.ge(0)),
    "nombre_personnes_impliquees_dans_fausse_alerte": Column(int, Check.ge(0)),
    "nombre_personnes_retrouvees": Column(int, Check.ge(0)),
    "nombre_personnes_secourues": Column(int, Check.ge(0)),
    "nombre_personnes_tirees_daffaire_seule": Column(int, Check.ge(0)),
    "nombre_personnes_tous_deces": Column(int, Check.ge(0)),
    "nombre_personnes_tous_deces_ou_disparues": Column(int, Check.ge(0)),
    "nombre_personnes_impliquees": Column(int, Check.ge(0)),
    # Colonnes flotteurs
    "nombre_flotteurs_commerce_impliques": Column(int, Check.ge(0)),
    "nombre_flotteurs_peche_impliques": Column(int, Check.ge(0)),
    "nombre_flotteurs_plaisance_impliques": Column(int, Check.ge(0)),
    "nombre_flotteurs_loisirs_nautiques_impliques": Column(int, Check.ge(0)),
    "nombre_aeronefs_impliques": Column(int, Check.ge(0)),
    "nombre_flotteurs_autre_impliques": Column(int, Check.ge(0)),
    "nombre_flotteurs_annexe_impliques": Column(int, Check.ge(0)),
    "nombre_flotteurs_autre_loisir_nautique_impliques": Column(int, Check.ge(0)),
    "nombre_flotteurs_canoe_kayak_aviron_impliques": Column(int, Check.ge(0)),
    "nombre_flotteurs_engin_de_plage_impliques": Column(int, Check.ge(0)),
    "nombre_flotteurs_kitesurf_impliques": Column(int, Check.ge(0)),
    "nombre_flotteurs_plaisance_voile_legere_impliques": Column(int, Check.ge(0)),
    "nombre_flotteurs_plaisance_a_moteur_impliques": Column(int, Check.ge(0)),
    "nombre_flotteurs_plaisance_a_moteur_moins_8m_impliques": Column(int, Check.ge(0)),
    "nombre_flotteurs_plaisance_a_moteur_plus_8m_impliques": Column(int, Check.ge(0)),
    "nombre_flotteurs_plaisance_a_voile_impliques": Column(int, Check.ge(0)),
    "nombre_flotteurs_planche_a_voile_impliques": Column(int, Check.ge(0)),
    "nombre_flotteurs_ski_nautique_impliques": Column(int, Check.ge(0)),
    "nombre_flotteurs_surf_impliques": Column(int, Check.ge(0)),
    "nombre_flotteurs_vehicule_nautique_a_moteur_impliques": Column(int, Check.ge(0)),
    "sans_flotteur_implique": Column(bool, nullable=False),
})

# -----------------------------
# Schéma pour df_flotteurs
# -----------------------------
schema_flotteurs = pa.DataFrameSchema({
    "operation_id": Column(int, nullable=False),
    "numero_ordre": Column(int, Check.ge(1), nullable=False),
    "pavillon": Column(str, Check.isin(["Français","Étranger"]), nullable=True),
    "resultat_flotteur": Column(str, nullable=False),
    "type_flotteur": Column(str, nullable=False),
    "categorie_flotteur": Column(str, nullable=False),
    "numero_immatriculation": Column(str, nullable=True)
})

# -----------------------------
# Schéma pour df_resultats_humain
# -----------------------------
schema_resultats_humain = pa.DataFrameSchema({
    "operation_id": Column(int, nullable=False),
    "categorie_personne": Column(str, nullable=False),
    "resultat_humain": Column(str, nullable=True),
    "nombre": Column(int, Check.ge(0), nullable=False),
    "dont_nombre_blesse": Column(int, Check.ge(0), nullable=True)
})
# -----------------------------