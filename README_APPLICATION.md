# 🌊 Grass Squad - Application de Gestion des Opérations Maritimes SECMAR

Application Streamlit complète pour la gestion des opérations maritimes avec CRUD, validation des données et visualisations.

## 📋 Fonctionnalités

### 1. 🏠 **Page d'Accueil**
- Aperçu rapide de la base de données
- Statistiques clés (opérations, personnes secourues, flotteurs, logs d'audit)
- Liste des 5 dernières opérations enregistrées

### 2. 📊 **Dashboard**
- Indicateurs clés de performance (KPIs)
- Carte géolocalisée des opérations
- Statistiques globales

### 3. 📝 **Gestion des Données**
- Édition rapide des opérations via `st.data_editor`
- Modification des cellules en temps réel
- Validation avant sauvegarde

### 4. 🛡️ **Audit & Logs**
- Traçabilité de toutes les modifications
- Logs des opérations CREATE, UPDATE, DELETE
- Diagramme ERD (Entity Relationship Diagram)

### 5. 🔍 **Consultation des Opérations**
- Filtrage par opération ou CROSS
- Affichage des données liées :
  - 🚢 Opération principale
  - ⛵ Flotteurs impliqués
  - 👥 Résultats humains
  - 📊 Statistiques détaillées
- Export CSV

### 6. ✏️ **CRUD Complet**
- **Créer** : Ajouter une nouvelle opération avec toutes ses données liées (flotteurs, résultats humains, statistiques)
- **Modifier** : Éditer les données existantes avec validation Pandera
- **Supprimer** : Supprimer une opération et toutes ses données associées (avec confirmation)
- **Validation** : Contrôle des types, contraintes NOT NULL, validation métier

## 🗄️ Structure de la Base de Données

### Tables gérées :
- `operations` : Données principales des opérations maritimes
- `flotteurs` : Embarcations impliquées dans les opérations
- `resultats_humain` : Résultats concernant les personnes
- `operations_stats` : Statistiques détaillées des opérations
- `audit_log` : Logs de toutes les modifications

**Relation** : Toutes les tables sont liées par `operation_id` (clé étrangère)

## 🚀 Installation et Lancement

### Prérequis

- Python 3.10+
- PostgreSQL 14+
- `uv` (gestionnaire de packages recommandé) ou `pip`

### Étape 1 : Cloner le projet

```bash
git clone <url-du-repo>
cd Brief-3-Gestion-donnees-et-UI-analytique-polyvalente-Grass-Squad
```

### Étape 2 : Créer et activer l'environnement virtuel

```bash
# Avec uv (recommandé)
uv venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate  # Windows

# Avec pip
python -m venv .venv
source .venv/bin/activate
```

### Étape 3 : Installer les dépendances

```bash
# Avec uv
uv pip install -r requirements.txt

# Avec pip
pip install -r requirements.txt
```

### Étape 4 : Configuration de la base de données

Créez un fichier `.env` à la racine du projet avec les informations suivantes :

```env
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=votre_mot_de_passe
DB_NAME=secmar_db
```

### Étape 5 : Créer les tables dans PostgreSQL

```bash
# Lancer le script de création des tables
python src/database/load_database.py
```

### Étape 6 : Charger les données (optionnel)

Si vous avez des fichiers CSV dans `data/raw/`, vous pouvez les charger :

```bash
python run_pipeline.py
```

### Étape 7 : Lancer l'application Streamlit

```bash
# Avec uv
uv run streamlit run src/app/home.py

# Avec pip
streamlit run src/app/home.py
```

L'application sera accessible à l'adresse : **http://localhost:8501**

## 📁 Structure du Projet

```
Brief-3-Gestion-donnees-et-UI-analytique-polyvalente-Grass-Squad/
│
├── src/
│   ├── app/
│   │   ├── home.py                          # 🏠 Page d'accueil
│   │   └── pages/
│   │       ├── 01_Dashboard.py              # 📊 Dashboard avec KPIs
│   │       ├── 02_Gestion_Donnees.py        # 📝 Édition rapide
│   │       ├── 03_Audit.py                  # 🛡️ Logs et ERD
│   │       ├── 04_Consultation_Operations.py # 🔍 Consultation
│   │       └── 05_CRUD_Complet.py           # ✏️ CRUD complet
│   │
│   ├── crud/                                 # Fonctions CRUD pour chaque table
│   │   ├── operations_crud.py
│   │   ├── flotteurs_crud.py
│   │   ├── resultat_humain_crud.py
│   │   ├── operations_stats_crud.py
│   │   └── audit_crud.py
│   │
│   ├── database/
│   │   ├── database.sql                     # Schéma complet de la BDD
│   │   ├── load_database.py                 # Connexion et création tables
│   │   └── audit.sql                        # Triggers d'audit
│   │
│   └── validation/
│       ├── schemas_validation.py            # Schémas de validation originaux
│       └── pandera_schemas.py               # 🆕 Schémas Pandera pour validation
│
├── data/
│   ├── raw/                                  # Fichiers CSV bruts
│   ├── processed/                            # Données transformées
│   └── rejected/                             # Données rejetées
│
├── requirements.txt                          # Dépendances Python
├── .env                                      # Variables d'environnement (à créer)
└── README_APPLICATION.md                     # Ce fichier
```

## 🔐 Validation des Données

L'application utilise **Pandera** pour valider les données avant insertion/modification :

- ✅ Vérification des types (str, int, float, datetime)
- ✅ Contraintes NOT NULL sur les champs obligatoires
- ✅ Validation de plages (latitude, longitude, nombres positifs)
- ✅ Messages d'erreur clairs et détaillés

### Exemple de validation

```python
from src.validation.pandera_schemas import validate_operations_data

data = {
    "cross": "Med",
    "date_heure_reception_alerte": datetime.now(),
    "evenement": "Naufrage"
}

validated_df, errors = validate_operations_data(data)

if errors:
    print("Erreurs de validation:", errors)
else:
    print("Données valides !")
```

## 🎯 Utilisation de l'Application

### Créer une nouvelle opération

1. Aller dans **05_CRUD_Complet**
2. Sélectionner **➕ Créer une opération complète**
3. Remplir le formulaire (champs obligatoires marqués avec *)
4. Cocher les options pour ajouter des flotteurs, résultats humains, statistiques
5. Cliquer sur **✅ Créer l'opération complète**

### Modifier une opération

1. Aller dans **05_CRUD_Complet**
2. Sélectionner **✏️ Modifier une opération**
3. Choisir l'opération dans la liste
4. Modifier les données dans les onglets (Opération, Flotteurs, Résultats, Stats)
5. Cliquer sur **💾 Sauvegarder les modifications**

### Supprimer une opération

1. Aller dans **05_CRUD_Complet**
2. Sélectionner **🗑️ Supprimer une opération**
3. Choisir l'opération à supprimer
4. Cocher la case de confirmation
5. Cliquer sur **🗑️ SUPPRIMER DÉFINITIVEMENT**

⚠️ **Attention** : La suppression est définitive et supprime toutes les données liées !

### Consulter les données

1. Aller dans **04_Consultation_Operations**
2. Utiliser les filtres dans la sidebar (par opération ou CROSS)
3. Consulter les données dans les onglets
4. Exporter en CSV si nécessaire

### Édition rapide

1. Aller dans **02_Gestion_Donnees**
2. Modifier directement les cellules dans le tableau interactif
3. Cliquer sur **💾 Sauvegarder les modifications**

## 🛠️ Technologies Utilisées

- **Streamlit** : Framework web pour l'interface utilisateur
- **PostgreSQL** : Base de données relationnelle
- **SQLAlchemy** : ORM Python pour les interactions avec la BDD
- **Pandera** : Validation de données avec schémas
- **Pandas** : Manipulation de données
- **psycopg2** : Connecteur PostgreSQL

## 📝 Notes Importantes

### Champs obligatoires

- **operations** :
  - `cross` (VARCHAR 50) : CROSS responsable
  - `date_heure_reception_alerte` (TIMESTAMP) : Date et heure de l'alerte

### Mot-clé réservé SQL

Le champ `cross` est un mot-clé réservé en SQL, il est donc échappé avec des guillemets doubles dans toutes les requêtes :
```sql
SELECT "cross" FROM operations;
```

### Cascade DELETE

Lorsqu'une opération est supprimée, **toutes les données liées sont automatiquement supprimées** grâce aux contraintes de clés étrangères ON DELETE CASCADE.

## 🐛 Résolution de Problèmes

### Erreur de connexion à PostgreSQL

```
❌ Erreur de connexion à la base de données
```

**Solutions** :
1. Vérifier que PostgreSQL est bien lancé : `sudo systemctl status postgresql`
2. Vérifier le fichier `.env` (host, port, user, password, database)
3. Vérifier que la base `secmar_db` existe : `psql -U postgres -l`

### Erreur "relation does not exist"

**Solution** : Créer les tables avec :
```bash
python src/database/load_database.py
```

### Pandas FutureWarning

Les warnings concernant `pd.read_sql` avec une connexion psycopg2 sont normaux. Pour les éviter, utiliser l'engine SQLAlchemy :
```python
df = pd.read_sql(query, engine)  # ✅ Pas de warning
df = pd.read_sql(query, conn)    # ⚠️ Warning
```

## 📧 Support

Pour toute question ou problème, contactez l'équipe Grass Squad.

---

**Développé par Grass Squad** 🌊 | **Simplon DE P1 2025** | Brief 3 - Gestion de données et UI analytique

