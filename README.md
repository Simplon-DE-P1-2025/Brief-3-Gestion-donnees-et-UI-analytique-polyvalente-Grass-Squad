# 🚢 Pipeline ETL - Données de Sauvetage Maritime

## 📋 Description du Projet

Ce projet implémente un pipeline ETL (Extract, Transform, Load) complet pour traiter et analyser les données de sauvetage maritime provenant des CROSS (Centres Régionaux Opérationnels de Surveillance et de Sauvetage).

Le pipeline automatise l'ingestion, le nettoyage, la validation et le chargement des données dans une base PostgreSQL pour faciliter l'analyse et le reporting des opérations de sauvetage en mer.

## 🎯 Objectifs

- **Centraliser** les données de sauvetage maritime provenant de multiples sources
- **Nettoyer** et **valider** automatiquement les données pour garantir leur qualité
- **Structurer** les informations dans une base de données PostgreSQL performante
- **Tracer** les anomalies et rejets pour un suivi qualité rigoureux

## 📊 Sources de Données

Le pipeline traite 4 fichiers CSV principaux :

| Fichier | Description | Contenu |
|---------|-------------|---------|
| `operations.csv` | Opérations de sauvetage | Détails des interventions (type, localisation, météo, dates) |
| `operations_stats.csv` | Statistiques temporelles | Données agrégées par date (année, mois, semaine, jour) |
| `flotteurs.csv` | Moyens nautiques | Informations sur les bateaux et moyens engagés |
| `resultats_humain.csv` | Résultats humains | Victimes, sauvetés, blessés, décès |

## 🏗️ Architecture du Projet

```
.
├── data/
│   ├── raw/                    # Données brutes source (CSV)
│   ├── processed/              # Données traitées et validées
│   └── rejected/               # Données rejetées lors de la validation
│
├── src/
│   ├── ingestion/              # Chargement des données brutes
│   ├── cleaning/               # Transformation et nettoyage
│   ├── validation/             # Validation avec schémas Pandera
│   ├── database/               # Scripts SQL et chargement PostgreSQL
│   ├── crud/                   # Opérations CRUD par table
│   └── config.py               # Configuration des chemins
│
├── docs/                       # Documentation du projet
├── tests/                      # Tests unitaires et d'intégration
├── run_pipeline.py             # Point d'entrée du pipeline
└── requirements.txt            # Dépendances Python
```

## ⚙️ Fonctionnement du Pipeline

Le pipeline s'exécute en **4 étapes séquentielles** :

### 1️⃣ **Ingestion**
- Chargement des 4 fichiers CSV depuis `data/raw/`
- Lecture avec gestion automatique des encodages
- Création de DataFrames Pandas

### 2️⃣ **Nettoyage**
- Standardisation des types de données
- Conversion des dates et timestamps
- Normalisation des chaînes de caractères
- Traitement des valeurs manquantes

### 3️⃣ **Validation**
- Vérification des schémas avec **Pandera**
- Contrôle de cohérence des données
- Séparation des données valides/invalides
- Export des rejets dans `data/rejected/`

### 4️⃣ **Chargement PostgreSQL**
- Création automatique des tables et schémas
- Insertion en masse avec `COPY` (performant)
- Support des types ENUM PostgreSQL
- Génération d'une table d'audit

## 🗄️ Schéma de Base de Données

Le schéma PostgreSQL `cross_sec` contient :

### Tables Principales

**`operations`** - Interventions de sauvetage
- Clé primaire : `operation_id`
- Contient : type d'opération, localisation GPS, conditions météo, dates

**`operations_stats`** - Statistiques temporelles
- Clé primaire composite : `operation_id`, `date`
- Contient : décomposition temporelle (année, mois, jour, semaine)

**`flotteurs`** - Moyens nautiques engagés
- Clé primaire composite : `operation_id`, `numero`
- Contient : détails des embarcations (type, pavillon, jauge)

**`resultats_humain`** - Bilan humain
- Clé primaire composite : `operation_id`, `resultat_humain`
- Contient : nombre de victimes par catégorie (sauvetés, décédés, blessés)

**`audit_operations`** - Traçabilité
- Enregistrement de toutes les modifications sur les tables

### Types Personnalisés (ENUM)
- `mois_francais` : Janvier à Décembre
- `jours_semaine_francais` : Lundi à Dimanche
- `phase_journee` : matinée, déjeuner, après-midi, nuit

## 🚀 Installation et Configuration

### Prérequis

- Python 3.8+
- PostgreSQL 12+
- Environnement virtuel Python (recommandé)

### Installation

```bash
# 1. Cloner le dépôt
git clone <url-du-repo>
cd Brief-3-Gestion-donnees-et-UI-analytique-polyvalente-Grass-Squad

# 2. Créer et activer l'environnement virtuel
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# 3. Installer les dépendances
pip install -r requirements.txt
```

### Configuration PostgreSQL

Créer un fichier `.env` à la racine du projet :

```env
DB_HOST=localhost
DB_PORT=5432
DB_USER=votre_utilisateur
DB_PASSWORD=votre_mot_de_passe
DB_DATABASE=sauvetage_maritime
```

## 📦 Utilisation

### Exécution du Pipeline Complet

```bash
python run_pipeline.py
```

### Sortie Attendue

```
[1/4] Ingestion des données...
      15,234 lignes chargées

[2/4] Nettoyage et validation...
      14,987 lignes validées

[3/4] Chargement dans PostgreSQL...
      14,987 lignes insérées

[4/4] Pipeline terminé avec succès
```

### Contrôle Qualité

Les données rejetées sont automatiquement exportées dans `data/rejected/` avec horodatage pour analyse ultérieure.

## 📚 Modules Principaux

### `src/ingestion/load_raw_data.py`
Charge les 4 sources CSV et retourne un dictionnaire de DataFrames.

### `src/validation/schemas_validation.py`
Définit les schémas Pandera pour chaque table avec règles de validation strictes.

### `src/cleaning/transformation.py`
Applique les transformations et normalisations nécessaires avant validation.

### `src/database/load_database.py`
Gère la connexion PostgreSQL, création de tables et insertion des données.

### `src/crud/`
Contient les opérations CRUD spécifiques à chaque table pour manipulation après chargement.

## 🧪 Tests

```bash
# Exécuter tous les tests
pytest tests/

# Avec couverture de code
pytest --cov=src tests/
```

## 🛠️ Technologies Utilisées

| Technologie | Usage |
|-------------|-------|
| **Python 3.x** | Langage principal |
| **Pandas** | Manipulation de données |
| **Pandera** | Validation de schémas |
| **PostgreSQL** | Base de données relationnelle |
| **psycopg2** | Connecteur PostgreSQL |
| **python-dotenv** | Gestion des variables d'environnement |
| **pytest** | Framework de tests |

## 👥 Équipe - Grass Squad

Projet réalisé dans le cadre de la formation Data Engineering - Simplon 2025

## 📄 Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

**Contact** : Pour toute question ou suggestion, veuillez ouvrir une issue sur le dépôt GitHub.