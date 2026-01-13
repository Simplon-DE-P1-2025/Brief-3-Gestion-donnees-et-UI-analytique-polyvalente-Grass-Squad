CREATE TABLE IF NOT EXISTS bronze_operations (
    operation_id BIGINT PRIMARY KEY,
    type_operation VARCHAR(10),              
    pourquoi_alerte VARCHAR(255),
    moyen_alerte VARCHAR(100),
    qui_alerte VARCHAR(100),
    categorie_qui_alerte VARCHAR(100),
    "cross" VARCHAR(100),
    departement VARCHAR(100) NULL,
    est_metropolitain BOOLEAN,
    evenement VARCHAR(255),
    categorie_evenement VARCHAR(255),
    autorite VARCHAR(100),
    seconde_autorite VARCHAR(100) NULL,
    zone_responsabilite VARCHAR(100),
    latitude DECIMAL(10,6) NULL,
    longitude DECIMAL(10,6) NULL,
    vent_direction INT CHECK(vent_direction >= 0 AND vent_direction <= 360),
    vent_direction_categorie VARCHAR (100),
    vent_force INT CHECK(vent_force >= 0 AND vent_force <= 12),
    mer_force INT CHECK(mer_force >= 0 AND mer_force <= 9),
    date_heure_reception_alerte TIMESTAMP,
    date_heure_fin_operation TIMESTAMP,
    numero_sitrep BIGINT,
    cross_sitrep VARCHAR(100),
    fuseau_horaire VARCHAR(50),
    systeme_source VARCHAR(50)
);


CREATE TABLE IF NOT EXISTS bronze_resultats_humain (
    operation_id BIGINT NOT NULL,                                          -- ID de l'opération
    categorie_personne VARCHAR(50),                               -- catégorie de personne
    resultat_humain VARCHAR(50),                                  -- type de résultat humain
    nombre BIGINT CHECK(nombre >= 0),                                -- nombre total
    dont_nombre_blesse BIGINT CHECK(dont_nombre_blesse >= 0)         -- nombre de blessés

);

CREATE TABLE IF NOT EXISTS bronze_flotteurs (
    operation_id BIGINT NOT NULL,                                        -- ID de l'opération
    numero_ordre INT,                                           -- ordre du flotteur dans l'opération
    pavillon VARCHAR(20),                                       -- pavillon Français/Étranger
    resultat_flotteur VARCHAR(100),                             -- état final du flotteur
    type_flotteur VARCHAR(50),                                  -- type précis du flotteur
    categorie_flotteur VARCHAR(50),                             -- grande catégorie
    numero_immatriculation VARCHAR(100)                         -- immatriculation chiffrée
);


CREATE TABLE IF NOT EXISTS bronze_operations_stats (
    operation_id BIGINT,                        -- identifiant de l'opération
    date DATE,                                  -- date de l'opération
    annee INT,
    mois INT,
    jour INT,
    mois_texte VARCHAR(20),
    semaine INT,
    annee_semaine VARCHAR(10),
    jour_semaine VARCHAR(10),
    est_weekend BOOLEAN,
    est_jour_ferie BOOLEAN,
    est_vacances_scolaires BOOLEAN NULL,
    phase_journee VARCHAR(20) NULL,
    concerne_plongee BOOLEAN,
    implique_wingfoil BOOLEAN,
    avec_clandestins BOOLEAN,
    distance_cote_metres INT,
    distance_cote_milles_nautiques DECIMAL(10,2) NULL,
    est_dans_stm BOOLEAN,
    nom_stm VARCHAR(50) NULL,
    est_dans_dst BOOLEAN,
    nom_dst VARCHAR(50) NULL,
    prefecture_maritime VARCHAR(50) NULL,
    maree_port VARCHAR(50) NULL,
    maree_coefficient INT,
    maree_categorie VARCHAR(20) NULL,
    nombre_personnes_blessees INT,
    nombre_personnes_assistees INT,
    nombre_personnes_decedees INT,
    nombre_personnes_decedees_accidentellement INT,
    nombre_personnes_decedees_naturellement INT,
    nombre_personnes_disparues INT,
    nombre_personnes_impliquees_dans_fausse_alerte INT,
    nombre_personnes_retrouvees INT,
    nombre_personnes_secourues INT,
    nombre_personnes_tirees_daffaire_seule INT,
    nombre_personnes_tous_deces INT,
    nombre_personnes_tous_deces_ou_disparues INT,
    nombre_personnes_impliquees INT,
    nombre_personnes_blessees_sans_clandestins INT,
    nombre_personnes_assistees_sans_clandestins INT,
    nombre_personnes_decedees_sans_clandestins INT,
    nombre_personnes_decedees_accidentellement_sans_clandestins INT,
    nombre_personnes_decedees_naturellement_sans_clandestins INT,
    nombre_personnes_disparues_sans_clandestins INT,
    nombre_personnes_impliquees_dans_fausse_alerte_sans_clandestins INT,
    nombre_personnes_retrouvees_sans_clandestins INT,
    nombre_personnes_secourues_sans_clandestins INT,
    nombre_personnes_tirees_daffaire_seule_sans_clandestins INT,
    nombre_personnes_tous_deces_sans_clandestins INT,
    nombre_personnes_tous_deces_ou_disparues_sans_clandestins INT,
    nombre_personnes_impliquees_sans_clandestins INT,
    nombre_flotteurs_commerce_impliques INT,
    nombre_flotteurs_peche_impliques INT,
    nombre_flotteurs_plaisance_impliques INT,
    nombre_flotteurs_loisirs_nautiques_impliques INT,
    nombre_aeronefs_impliques INT,
    nombre_flotteurs_autre_impliques INT,
    nombre_flotteurs_annexe_impliques INT,
    nombre_flotteurs_autre_loisir_nautique_impliques INT,
    nombre_flotteurs_canoe_kayak_aviron_impliques INT,
    nombre_flotteurs_engin_de_plage_impliques INT,
    nombre_flotteurs_kitesurf_impliques INT,
    nombre_flotteurs_plaisance_voile_legere_impliques INT,
    nombre_flotteurs_plaisance_a_moteur_impliques INT,
    nombre_flotteurs_plaisance_a_moteur_moins_8m_impliques INT,
    nombre_flotteurs_plaisance_a_moteur_plus_8m_impliques INT,
    nombre_flotteurs_plaisance_a_voile_impliques INT,
    nombre_flotteurs_planche_a_voile_impliques INT,
    nombre_flotteurs_ski_nautique_impliques INT,
    nombre_flotteurs_surf_impliques INT,
    nombre_flotteurs_vehicule_nautique_a_moteur_impliques INT,
    sans_flotteur_implique BOOLEAN
);
