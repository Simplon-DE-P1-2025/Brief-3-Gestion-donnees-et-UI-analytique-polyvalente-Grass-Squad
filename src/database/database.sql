-- =========================
-- TYPES ENUM
-- =========================

DROP TYPE IF EXISTS mois_francais CASCADE;
CREATE TYPE mois_francais AS ENUM (
    'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
    'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'
);

DROP TYPE IF EXISTS jours_semaine_francais CASCADE;
CREATE TYPE jours_semaine_francais AS ENUM (
    'Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche'
);

DROP TYPE IF EXISTS phase_journee CASCADE;
CREATE TYPE phase_journee AS ENUM (
    'matinée', 'déjeuner', 'après-midi', 'nuit'
);

-- =========================
-- TABLE OPERATIONS
-- =========================

DROP TABLE IF EXISTS operations CASCADE;
CREATE TABLE operations (
    operation_id BIGINT PRIMARY KEY,
    type_operation VARCHAR(3),
    pourquoi_alerte VARCHAR(100),
    moyen_alerte VARCHAR(100),
    qui_alerte VARCHAR(100),
    categorie_qui_alerte VARCHAR(100),
    "cross" VARCHAR(50) NOT NULL,
    departement VARCHAR(100),
    est_metropolitain BOOLEAN,
    evenement VARCHAR(100),
    categorie_evenement VARCHAR(100),
    autorite VARCHAR(100),
    seconde_autorite VARCHAR(100),
    zone_responsabilite VARCHAR(100),
    latitude NUMERIC(7,4),
    longitude NUMERIC(7,4),
    vent_direction NUMERIC(5,2),
    vent_direction_categorie VARCHAR(20),
    vent_force NUMERIC(4,2),
    mer_force NUMERIC(3,2),
    date_heure_reception_alerte TIMESTAMP NOT NULL,
    date_heure_fin_operation TIMESTAMP,
    numero_sitrep INTEGER,
    cross_sitrep VARCHAR(100),
    fuseau_horaire VARCHAR(50),
    systeme_source VARCHAR(50)
);

CREATE INDEX idx_operations_type_operation ON operations(type_operation);
CREATE INDEX idx_operations_pourquoi_alerte ON operations(pourquoi_alerte);
CREATE INDEX idx_operations_cross ON operations("cross");
CREATE INDEX idx_operations_departement ON operations(departement);
CREATE INDEX idx_operations_date_reception ON operations(date_heure_reception_alerte);
CREATE INDEX idx_operations_date_fin ON operations(date_heure_fin_operation);

-- =========================
-- TABLE FLOTTEURS
-- =========================

DROP TABLE IF EXISTS flotteurs;
CREATE TABLE flotteurs (
    operation_id BIGINT REFERENCES operations(operation_id) ON DELETE CASCADE,
    numero_ordre INTEGER NOT NULL,
    pavillon VARCHAR(50),
    resultat_flotteur VARCHAR(100) NOT NULL,
    type_flotteur VARCHAR(100) NOT NULL,
    categorie_flotteur VARCHAR(100) NOT NULL,
    numero_immatriculation VARCHAR(100)
);

CREATE INDEX idx_flotteurs_operation_id ON flotteurs(operation_id);
CREATE INDEX idx_flotteurs_resultat ON flotteurs(resultat_flotteur);
CREATE INDEX idx_flotteurs_type ON flotteurs(type_flotteur);
CREATE INDEX idx_flotteurs_categorie ON flotteurs(categorie_flotteur);

-- =========================
-- TABLE RESULTATS HUMAIN
-- =========================

DROP TABLE IF EXISTS resultats_humain;
CREATE TABLE resultats_humain (
    operation_id BIGINT REFERENCES operations(operation_id) ON DELETE CASCADE,
    categorie_personne VARCHAR(100) NOT NULL,
    resultat_humain VARCHAR(100) NOT NULL,
    nombre INTEGER NOT NULL,
    dont_nombre_blesse INTEGER
);

CREATE INDEX idx_resultats_humain_operation_id ON resultats_humain(operation_id);
CREATE INDEX idx_resultats_humain_resultat ON resultats_humain(resultat_humain);

-- =========================
-- TABLE OPERATIONS_STATS
-- =========================

DROP TABLE IF EXISTS operations_stats;
CREATE TABLE operations_stats (
    operation_id BIGINT PRIMARY KEY REFERENCES operations(operation_id) ON DELETE CASCADE,
    date DATE NOT NULL,
    annee INTEGER NOT NULL,
    mois INTEGER NOT NULL,
    jour INTEGER NOT NULL,
    mois_texte VARCHAR(20) NOT NULL,
    semaine INTEGER NOT NULL,
    annee_semaine VARCHAR(10) NOT NULL,
    jour_semaine VARCHAR(20) NOT NULL,
    est_weekend BOOLEAN NOT NULL,
    est_jour_ferie BOOLEAN NOT NULL,
    est_vacances_scolaires BOOLEAN,
    phase_journee VARCHAR(20),
    concerne_plongee BOOLEAN NOT NULL,
    implique_wingfoil BOOLEAN NOT NULL,
    avec_clandestins BOOLEAN NOT NULL,
    distance_cote_metres INTEGER,
    distance_cote_milles_nautiques NUMERIC(10,2),
    est_dans_stm BOOLEAN NOT NULL,
    nom_stm VARCHAR(100),
    est_dans_dst BOOLEAN NOT NULL,
    nom_dst VARCHAR(100),
    prefecture_maritime VARCHAR(50),
    maree_port VARCHAR(100),
    maree_coefficient INTEGER,
    maree_categorie VARCHAR(20),

    -- Indicateurs humains
    nombre_personnes_blessees INTEGER NOT NULL,
    nombre_personnes_assistees INTEGER NOT NULL,
    nombre_personnes_decedees INTEGER NOT NULL,
    nombre_personnes_decedees_accidentellement INTEGER NOT NULL,
    nombre_personnes_decedees_naturellement INTEGER NOT NULL,
    nombre_personnes_disparues INTEGER NOT NULL,
    nombre_personnes_impliquees_dans_fausse_alerte INTEGER NOT NULL,
    nombre_personnes_retrouvees INTEGER NOT NULL,
    nombre_personnes_secourues INTEGER NOT NULL,
    nombre_personnes_tirees_daffaire_seule INTEGER NOT NULL,
    nombre_personnes_tous_deces INTEGER NOT NULL,
    nombre_personnes_tous_deces_ou_disparues INTEGER NOT NULL,
    nombre_personnes_impliquees INTEGER NOT NULL,

    -- Sans clandestins
    nombre_personnes_blessees_sans_clandestins INTEGER NOT NULL,
    nombre_personnes_assistees_sans_clandestins INTEGER NOT NULL,
    nombre_personnes_decedees_sans_clandestins INTEGER NOT NULL,
    nombre_personnes_decedees_accidentellement_sans_clandestins INTEGER NOT NULL,
    nombre_personnes_decedees_naturellement_sans_clandestins INTEGER NOT NULL,
    nombre_personnes_disparues_sans_clandestins INTEGER NOT NULL,
    nombre_personnes_impliquees_dans_fausse_alerte_sans_clandestins INTEGER NOT NULL,
    nombre_personnes_retrouvees_sans_clandestins INTEGER NOT NULL,
    nombre_personnes_secourues_sans_clandestins INTEGER NOT NULL,
    nombre_personnes_tirees_daffaire_seule_sans_clandestins INTEGER NOT NULL,
    nombre_personnes_tous_deces_sans_clandestins INTEGER NOT NULL,
    nombre_personnes_tous_deces_ou_disparues_sans_clandestins INTEGER NOT NULL,
    nombre_personnes_impliquees_sans_clandestins INTEGER NOT NULL,

    -- Flotteurs
    nombre_flotteurs_commerce_impliques INTEGER NOT NULL,
    nombre_flotteurs_peche_impliques INTEGER NOT NULL,
    nombre_flotteurs_plaisance_impliques INTEGER NOT NULL,
    nombre_flotteurs_loisirs_nautiques_impliques INTEGER NOT NULL,
    nombre_aeronefs_impliques INTEGER NOT NULL,
    nombre_flotteurs_autre_impliques INTEGER NOT NULL,
    nombre_flotteurs_annexe_impliques INTEGER NOT NULL,
    nombre_flotteurs_autre_loisir_nautique_impliques INTEGER NOT NULL,
    nombre_flotteurs_canoe_kayak_aviron_impliques INTEGER NOT NULL,
    nombre_flotteurs_engin_de_plage_impliques INTEGER NOT NULL,
    nombre_flotteurs_kitesurf_impliques INTEGER NOT NULL,
    nombre_flotteurs_plaisance_voile_legere_impliques INTEGER NOT NULL,
    nombre_flotteurs_plaisance_a_moteur_impliques INTEGER NOT NULL,
    nombre_flotteurs_plaisance_a_moteur_moins_8m_impliques INTEGER NOT NULL,
    nombre_flotteurs_plaisance_a_moteur_plus_8m_impliques INTEGER NOT NULL,
    nombre_flotteurs_plaisance_a_voile_impliques INTEGER NOT NULL,
    nombre_flotteurs_planche_a_voile_impliques INTEGER NOT NULL,
    nombre_flotteurs_ski_nautique_impliques INTEGER NOT NULL,
    nombre_flotteurs_surf_impliques INTEGER NOT NULL,
    nombre_flotteurs_vehicule_nautique_a_moteur_impliques INTEGER NOT NULL,

    sans_flotteur_implique BOOLEAN NOT NULL
);

CREATE INDEX idx_operations_stats_date ON operations_stats(date);
CREATE INDEX idx_operations_stats_annee ON operations_stats(annee);
CREATE INDEX idx_operations_stats_phase_journee ON operations_stats(phase_journee);
CREATE INDEX idx_operations_stats_plongee ON operations_stats(concerne_plongee);

-- =========================
-- TABLE AUDIT_LOG (Historique complet des opérations)
-- =========================
-- Cette table enregistre toutes les transactions (INSERT, UPDATE, DELETE, VIEW)
-- effectuées sur les tables principales de la base de données.

DROP TABLE IF EXISTS audit_log CASCADE;
CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    table_name TEXT NOT NULL,           -- Nom de la table concernée
    action TEXT NOT NULL,                -- Type d'action: INSERT, UPDATE, DELETE, VIEW
    record_id TEXT NOT NULL,             -- ID de l'enregistrement concerné
    user_name TEXT DEFAULT 'system',     -- Utilisateur ayant effectué l'action
    old_values JSONB,                    -- Valeurs avant modification (pour UPDATE/DELETE)
    new_values JSONB,                    -- Nouvelles valeurs (pour INSERT/UPDATE)
    details TEXT,                        -- Détails supplémentaires sur l'action
    sql_query TEXT,                      -- Requête SQL exécutée
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Date et heure de l'action
);

-- Index pour améliorer les performances des requêtes d'audit
CREATE INDEX idx_audit_log_table_name ON audit_log(table_name);
CREATE INDEX idx_audit_log_action ON audit_log(action);
CREATE INDEX idx_audit_log_created_at ON audit_log(created_at DESC);
CREATE INDEX idx_audit_log_record_id ON audit_log(record_id);
CREATE INDEX idx_audit_log_user_name ON audit_log(user_name);
