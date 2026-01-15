-- =========================
-- TABLE REFERENCE_LISTS
-- Table pour stocker les listes de référence prédéfinies
-- =========================

DROP TABLE IF EXISTS reference_lists CASCADE;
CREATE TABLE reference_lists (
    id SERIAL PRIMARY KEY,
    category VARCHAR(100) NOT NULL,  -- Ex: 'type_operation', 'pavillon', 'categorie_flotteur'
    value VARCHAR(200) NOT NULL,     -- La valeur de l'option
    display_order INTEGER DEFAULT 0,  -- Ordre d'affichage dans les selectbox
    is_active BOOLEAN DEFAULT TRUE,   -- Permet de désactiver sans supprimer
    description TEXT,                 -- Description optionnelle
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(category, value)
);

-- Index pour améliorer les performances
CREATE INDEX idx_reference_lists_category ON reference_lists(category);
CREATE INDEX idx_reference_lists_active ON reference_lists(is_active);

-- =========================
-- DONNÉES INITIALES
-- Insertion des valeurs par défaut selon la documentation SECMAR
-- =========================

-- Type d'opération
INSERT INTO reference_lists (category, value, display_order, description) VALUES
('type_operation', 'SAR', 1, 'Search and rescue - vie humaine en danger'),
('type_operation', 'MAS', 2, 'Maritime assistance service - assistance aux navires'),
('type_operation', 'DIV', 3, 'Divers - autres cas'),
('type_operation', 'SUR', 4, 'Sûreté des navires'),
('type_operation', 'POL', 5, 'Pollutions');

-- Pavillon
INSERT INTO reference_lists (category, value, display_order) VALUES
('pavillon', 'Français', 1),
('pavillon', 'Étranger', 2);

-- Catégorie de flotteur
INSERT INTO reference_lists (category, value, display_order) VALUES
('categorie_flotteur', 'Commerce', 1),
('categorie_flotteur', 'Pêche', 2),
('categorie_flotteur', 'Plaisance', 3),
('categorie_flotteur', 'Loisir nautique', 4),
('categorie_flotteur', 'Aéronef', 5),
('categorie_flotteur', 'Autre', 6);

-- Résultat flotteur
INSERT INTO reference_lists (category, value, display_order) VALUES
('resultat_flotteur', 'Assisté', 1),
('resultat_flotteur', 'Côte rejointe par ses propres moyens', 2),
('resultat_flotteur', 'Difficulté surmontée, reprise de route', 3),
('resultat_flotteur', 'Non assisté, cas de fausse alerte', 4),
('resultat_flotteur', 'Non renseigné', 5),
('resultat_flotteur', 'Perdu / Coulé', 6),
('resultat_flotteur', 'Remorqué', 7),
('resultat_flotteur', 'Retrouvé après recherche', 8),
('resultat_flotteur', 'Échoué', 9);

-- Catégorie de personne
INSERT INTO reference_lists (category, value, display_order) VALUES
('categorie_personne', 'Autre', 1),
('categorie_personne', 'Plaisancier français', 2),
('categorie_personne', 'Pratiquant loisirs nautiques', 3),
('categorie_personne', 'Migrant', 4),
('categorie_personne', 'Clandestin', 5),
('categorie_personne', 'Commerce français', 6),
('categorie_personne', 'Marin étranger', 7),
('categorie_personne', 'Pêcheur français', 8),
('categorie_personne', 'Pêcheur amateur', 9),
('categorie_personne', 'Toutes catégories', 10);

-- Résultat humain
INSERT INTO reference_lists (category, value, display_order) VALUES
('resultat_humain', 'Personne assistée', 1),
('resultat_humain', 'Personne disparue', 2),
('resultat_humain', 'Personne décédée', 3),
('resultat_humain', 'Personne décédée accidentellement', 4),
('resultat_humain', 'Personne décédée naturellement', 5),
('resultat_humain', 'Personne impliquée dans fausse alerte', 6),
('resultat_humain', 'Personne retrouvée', 7),
('resultat_humain', 'Personne secourue', 8),
('resultat_humain', 'Personne tirée d''affaire seule', 9);

-- Direction du vent (cardinale)
INSERT INTO reference_lists (category, value, display_order) VALUES
('vent_direction_categorie', 'nord', 1),
('vent_direction_categorie', 'nord-est', 2),
('vent_direction_categorie', 'est', 3),
('vent_direction_categorie', 'sud-est', 4),
('vent_direction_categorie', 'sud', 5),
('vent_direction_categorie', 'sud-ouest', 6),
('vent_direction_categorie', 'ouest', 7),
('vent_direction_categorie', 'nord-ouest', 8);

-- Système source
INSERT INTO reference_lists (category, value, display_order) VALUES
('systeme_source', 'secmarweb', 1),
('systeme_source', 'seamis_json', 2);

-- Préfecture maritime
INSERT INTO reference_lists (category, value, display_order) VALUES
('prefecture_maritime', 'manche', 1),
('prefecture_maritime', 'atlantique', 2),
('prefecture_maritime', 'mediterranee', 3);

-- Catégorie de marée
INSERT INTO reference_lists (category, value, display_order) VALUES
('maree_categorie', '20-45', 1),
('maree_categorie', '46-70', 2),
('maree_categorie', '71-95', 3),
('maree_categorie', '96-120', 4);

-- CROSS (exemples courants)
INSERT INTO reference_lists (category, value, display_order) VALUES
('cross', 'Gris-Nez', 1),
('cross', 'Jobourg', 2),
('cross', 'Corsen', 3),
('cross', 'Étel', 4),
('cross', 'Med', 5),
('cross', 'Antilles-Guyane', 6),
('cross', 'Réunion', 7);

-- Fonction pour mettre à jour updated_at automatiquement
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_reference_lists_updated_at BEFORE UPDATE
ON reference_lists FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
