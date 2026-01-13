# Grass Squad - Gestion de Données et UI Analytique

Ce projet s'inscrit dans le cadre du **Brief 3 : Gestion de données et UI analytique polyvalente**.  
L'objectif est de concevoir une chaîne de traitement de données (ETL) et de mettre en place des outils d'analyse pour explorer des données d'opérations de sauvetage et de surveillance maritime (CROSS / SNSM).

## 🚀 Fonctionnalités

- **Ingestion de données (ETL)** : Pipeline automatisé pour charger des fichiers CSV bruts (`operations`, `flotteurs`, `résultats humains`) vers une base de données PostgreSQL.
- **Base de données** : Structuration des données en SQL (tables Bronze/Raw).
- **Environnement moderne** : Utilisation de `uv` pour une gestion ultra-rapide des dépendances Python.
- **Analyse** : Environnement prêt pour l'analyse de données avec Pandas et Jupyter.

## 🛠️ Pré-requis

Avant de commencer, assurez-vous d'avoir installé :
- **Python** (version 3.13 ou supérieure recommandée)
- **PostgreSQL** (serveur local ou accessible)
- **[uv](https://github.com/astral-sh/uv)** (notre gestionnaire de paquets et de projet)

## 📦 Installation et Configuration

1. **Cloner le projet**
   ```bash
   git clone <votre-url-repo>
   cd Brief-3-Gestion-donnees-et-UI-analytique-polyvalente-Grass-Squad
   ```

2. **Installer les dépendances**
   Grâce à `uv`, une seule commande suffit pour créer l'environnement virtuel et installer toutes les bibliothèques :
   ```bash
   uv sync
   ```

3. **Configuration Base de Données (.env)**
   
   Créez un fichier nommé `.env` à la racine du projet pour configurer l'accès à votre base de données PostgreSQL. 
   
   Exemple de contenu pour le fichier `.env` :
   ```ini
   DB_NAME=db_operations
   DB_USER=postgres
   DB_PASSWORD=root
   DB_HOST=localhost
   ```
   > **Important** : Assurez-vous que vos identifiants correspondent à votre installation locale de PostgreSQL.

## ▶️ Utilisation

### 1. Ingestion des Données (ETL)
Pour créer la base de données `db_operations`, créer les tables et importer les fichiers CSV situés dans `data/raw/` :

```bash
uv run src/ingestion/run_full_ingestion.py
```
> **Note** : Ce script gère automatiquement la création de la base de données si elle n'existe pas.

### 2. Lancer Jupyter Lab
Pour accéder aux notebooks et effectuer des analyses exploratoires :

```bash
uv run jupyter lab
```

## 📂 Structure du Projet

```
.
├── data/
│   └── raw/                   # Données brutes (CSV : operations, flotteurs, etc.)
├── docs/                      # Documentation du projet
├── src/
│   ├── analysis/              # Scripts d'analyse
│   ├── cleaning/              # Scripts de nettoyage (si séparés)
│   ├── database/              # Scripts SQL (ex: create_bronze_tables.sql)
│   └── ingestion/             # Scripts Python pour l'ETL (run_full_ingestion.py)
├── pyproject.toml             # Configuration du projet et dépendances (géré par uv)
├── uv.lock                    # Fichier de verrouillage des versions exactes
└── README.md                  # Ce fichier
```

## 👥 Auteurs

**Grass Squad** - Simplon Dev Data