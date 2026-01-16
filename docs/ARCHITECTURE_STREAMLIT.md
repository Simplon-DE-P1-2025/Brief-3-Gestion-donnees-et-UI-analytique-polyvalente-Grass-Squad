# 📱 Architecture Application Streamlit - SECMAR

**Version:** 1.0 | **Date:** Janvier 2026 | **Framework:** Streamlit 1.39+

---

## 🎯 Qu'est-ce que cette application ?

L'application SECMAR est une **plateforme web interactive** pour la gestion et l'analyse des opérations maritimes. Elle permet aux utilisateurs de :

- Visualiser des tableaux de bord avec des analyses métier
- Gérer les opérations maritimes (création, modification, suppression)
- Consulter l'historique des actions (audit)
- Administrer les listes de référence
- Accéder aux données de manière intuitive

L'application est construite avec **Streamlit**, un framework Python qui transforme des scripts Python en applications web interactives sans nécessiter de connaissances en développement web front-end.

---

## 🏗️ Architecture générale : Le modèle MVC

Notre application suit une architecture **Model-View-Controller (MVC)** adaptée à Streamlit. Ce modèle sépare le code en trois parties distinctes :

### 📊 **Model (Données)**

Le **Model** est responsable de la gestion des données et de la base de données. Il contient :

- **Fichiers CRUD** : Opérations de base de données (Create, Read, Update, Delete)
  - `src/crud/operations_crud.py` → Gère les opérations maritimes
  - `src/crud/flotteurs_crud.py` → Gère les flotteurs
  - `src/crud/audit_crud.py` → Gère l'audit des actions
  
- **Fichiers de base de données** : Configuration et initialisation
  - `src/database/load_database.py` → Connexion à PostgreSQL
  - `src/database/database.sql` → Schéma de la base

Le **Model** est isolé de l'interface utilisateur et ne sait rien de Streamlit.

### 👁️ **View (Présentation)**

La **View** gère l'affichage des données et l'interface utilisateur. Elle contient :

- **Pages principales** : Points d'entrée de l'application
  - `src/app/home.py` → Page d'accueil
  - `src/app/pages/01_Dashboard.py` → Tableaux de bord
  - `src/app/pages/02_Operations.py` → Gestion opérations
  - `src/app/pages/03_Audit.py` → Logs d'audit
  
- **Vues métier** : Logique de présentation spécifique
  - `src/app/views/dashboard_alerte.py` → Analyse des alertes
  - `src/app/views/operations_list.py` → Liste des opérations
  - `src/app/views/operations_create.py` → Créer une opération
  
- **Composants réutilisables** : Briques d'interface
  - `src/app/components/pagination.py` → Navigation pagination
  - `src/app/components/table.py` → Affichage de tableaux
  - `src/app/components/styles.py` → Styles CSS

La **View** utilise Streamlit (`st`) pour créer l'interface et interagir avec l'utilisateur.

### ⚙️ **Controller (Logique métier)**

Le **Controller** coordonne la communication entre View et Model. Il contient :

- **Utilitaires de données** : Chargement et formatting
  - `src/app/utils/data_loader.py` → Récupère les données (avec cache)
  - `src/app/utils/formatters.py` → Formate dates, nombres, texte
  - `src/app/utils/queries.py` → Construit les requêtes SQL
  
- **Gestion de l'état** : Conserve les variables entre interactions
  - `src/app/utils/session_state.py` → Initialise l'état de l'application

Le **Controller** traite les requêtes utilisateur, formate les données et met à jour l'état.

### Schéma du flux MVC

```
┌─────────────────────┐
│  UTILISATEUR        │
│  (navigateur web)   │
└──────────┬──────────┘
           │
           ▼ (clique, saisit)
┌─────────────────────────────────────────┐
│  VIEW (Streamlit - Présentation)        │
│  • Pages & Vues                         │
│  • Widgets (boutons, formulaires)       │
│  • Affichage des données                │
└──────────┬──────────────────────────────┘
           │
           ▼ (demande données formatées)
┌─────────────────────────────────────────┐
│  CONTROLLER (Logique métier)            │
│  • Utils (data_loader, formatters)      │
│  • Session state                        │
│  • Formatte les données                 │
└──────────┬──────────────────────────────┘
           │
           ▼ (requête SQL)
┌─────────────────────────────────────────┐
│  MODEL (Base de données)                │
│  • CRUD operations                      │
│  • PostgreSQL                           │
│  • Stockage des données                 │
└─────────────────────────────────────────┘
```

---

## 🔄 Comment Streamlit et Python interagissent

### Le cycle de vie d'une interaction utilisateur

Streamlit fonctionne différemment des applications web traditionnelles. Voici comment une interaction se déroule :

**1. Chargement initial**
- L'utilisateur accède à l'application
- Streamlit exécute le script Python de haut en bas
- Les widgets (boutons, formulaires) sont créés
- La page HTML est envoyée au navigateur

**2. Interaction utilisateur**
- L'utilisateur clique sur un bouton ou remplit un formulaire
- Streamlit détecte l'événement

**3. Réexécution du script**
- Le script Python s'exécute **entièrement à nouveau**
- Les variables sont recalculées
- Les données sont rechargées (sauf si en cache)

**4. Session state**
- `st.session_state` conserve les valeurs entre réexécutions
- Permet de maintenir l'état de l'application
- Exemple : `st.session_state.page_number = 2`

**5. Affichage du résultat**
- Streamlit affiche la nouvelle interface
- L'utilisateur voit les modifications

### Exemple concret : Créer une opération

```
Utilisateur → Clique "Créer une opération"
                 ↓
Streamlit → Détecte le clic, réexécute le script
                 ↓
Python (Controller) → Récupère action='create' depuis session_state
                 ↓
Python (View) → Appelle views/operations_create.py
                 ↓
Streamlit → Affiche le formulaire (st.form, st.text_input, st.button)
                 ↓
Utilisateur → Remplit le formulaire et clique "Enregistrer"
                 ↓
Streamlit → Récupère les valeurs du formulaire
                 ↓
Python (Controller) → Valide les données
                 ↓
Python (Model) → Appelle crud/operations_crud.py
                 ↓
Model → INSERT INTO operations VALUES (...)
                 ↓
Python → st.success("Opération créée !")
                 ↓
Streamlit → Affiche le message de succès
                 ↓
Utilisateur → Voit la confirmation
```

---

## 📂 Structure du projet

### Hiérarchie des dossiers

```
src/app/                           # Application Streamlit
├── home.py                         # Page d'accueil (point d'entrée)
├── pages/                          # Pages principales (Multi-Page App)
├── components/                     # Composants réutilisables
├── views/                          # Vues métier
├── utils/                          # Utilitaires (services)
└── assets/                         # Ressources CSS

src/crud/                           # Opérations base de données (Model)
├── operations_crud.py
├── flotteurs_crud.py
└── audit_crud.py

src/database/                       # Configuration base de données
└── load_database.py

src/analysis/                       # Analyses métier
└── dashboard_analytics.py

src/ingestion/                      # Chargement des données brutes
src/validation/                     # Validation des données
src/cleaning/                       # Nettoyage des données
```

### Description détaillée des répertoires

**`pages/` - Pages principales**

Les pages sont les points d'entrée de la multi-page app de Streamlit. Chaque fichier crée automatiquement une page accessible via la sidebar :

- `01_Dashboard.py` → Route vers différents tableaux de bord
- `02_Operations.py` → Gère la liste, création, modification, suppression
- `03_Audit.py` → Affiche l'historique des actions
- `04_Admin.py` → Gère les listes de référence
- `05_Schema.py` → Visualise le schéma des données

Rôle : **Orchestration et routing**

**`views/` - Vues métier**

Les vues contiennent la logique de présentation spécifique à un domaine. Chaque vue a une responsabilité métier :

- `dashboard_*.py` → Analyses spécialisées (alerte, zone géographique, etc.)
- `operations_list.py` → Affichage de la liste avec tri et pagination
- `operations_create.py` → Formulaire de création
- `operations_edit.py` → Formulaire de modification
- `operations_delete.py` → Confirmation de suppression

Rôle : **Présentation métier**

**`components/` - Composants réutilisables**

Les composants sont des éléments UI génériques utilisés dans plusieurs vues :

- `pagination.py` → Boutons de navigation entre pages
- `table.py` → Affichage standardisé de tableaux
- `styles.py` → Fonctions pour ajouter du CSS personnalisé

Rôle : **UI réutilisable**

**`utils/` - Utilitaires**

Les utilitaires fournissent des services utilisés partout dans l'application :

- `data_loader.py` → Récupère les données depuis la base (avec cache)
- `formatters.py` → Transforme les dates, nombres, texte pour l'affichage
- `queries.py` → Construit les requêtes SQL complexes
- `session_state.py` → Initialise les variables de session

Rôle : **Services transversaux**

**`src/crud/` - Opérations base de données**

Les fichiers CRUD sont responsables de toutes les opérations sur la base de données. Ils ne contiennent aucune logique Streamlit.

- Créer, lire, mettre à jour, supprimer des données
- Exécuter les requêtes SQL
- Gérer les transactions

Rôle : **Accès aux données (Model)**

---

## 🧩 Composants Streamlit utilisés

Streamlit fournit une variété de composants pour construire l'interface. Voici les principaux utilisés dans le projet :

### Affichage d'informations

- **`st.metric`** : Affiche une métrique avec valeur (ex: "1,234 opérations")
- **`st.dataframe`** : Affiche un tableau interactif à partir d'un DataFrame pandas
- **`st.table`** : Affiche un tableau statique (HTML simple)
- **`st.markdown`** : Affiche du texte formaté en Markdown
- **`st.write`** : Affiche du texte simple

### Entrée utilisateur

- **`st.button`** : Bouton cliquable pour déclencher une action
- **`st.text_input`** : Champ de saisie texte
- **`st.selectbox`** : Menu déroulant pour sélection unique
- **`st.multiselect`** : Sélection multiple d'options
- **`st.number_input`** : Champ de saisie nombre
- **`st.date_input`** : Sélecteur de date
- **`st.form`** : Groupe de champs pour soumettre ensemble

### Mise en page

- **`st.columns`** : Crée des colonnes pour organiser horizontalement
- **`st.tabs`** : Crée des onglets
- **`st.expander`** : Section repliable
- **`st.divider`** : Ligne de séparation

### Visualisations

- **`st.bar_chart`** : Graphique en barres
- **`st.line_chart`** : Graphique en ligne
- **`st.map`** : Carte géographique

### Notifications

- **`st.success`** : Message de succès (vert)
- **`st.error`** : Message d'erreur (rouge)
- **`st.warning`** : Message d'avertissement (orange)
- **`st.info`** : Message informatif (bleu)

### Gestion de l'état

- **`st.session_state`** : Dictionnaire persistant entre réexécutions
- **`st.rerun`** : Force la réexécution du script
- **`st.switch_page`** : Navigation programmatique vers une autre page

### Performance

- **`@st.cache_data`** : Cache les résultats pour éviter les recalculs

---

## 🚀 Comment l'application fonctionne

### Flux complet d'une opération

Prenons l'exemple d'un utilisateur qui liste les opérations :

**1. Accès à la page**
- Utilisateur clique sur "Opérations" dans la sidebar
- Streamlit charge `pages/02_Operations.py`
- Le script Python s'exécute

**2. Initialisation**
- Session state est initialisé (`page_number=1`, `action='list'`)
- On récupère le numéro de page depuis session_state

**3. Chargement des données**
- `utils/data_loader.py` → `get_operations_count()` 
- Récupère le nombre total d'opérations
- Cache les résultats pour 2 minutes

**4. Affichage**
- `views/operations_list.py` → `show_operations_grid()`
- Calcule l'offset : `offset = (page_number - 1) * 10`
- Appelle data_loader pour récupérer 10 opérations

**5. Formatage**
- `utils/formatters.py` → Formate les dates
- Dates ISO → Format lisible (01/01/2023 10:30)

**6. Rendu interface**
- `components/table.py` → Affiche l'en-tête et les lignes
- `components/pagination.py` → Affiche les boutons de navigation
- Streamlit convertit en HTML

**7. Affichage utilisateur**
- Tableau avec 10 opérations
- Boutons page 1, 2, 3...

**8. Interaction**
- Utilisateur clique "Page 2"
- Streamlit détecte le clic
- Va à l'étape 1 avec `page_number=2`

### Avantages de cette organisation

**Séparation des responsabilités**
- Chaque fichier a un rôle unique et bien défini
- Facilite la maintenance et les modifications

**Réutilisabilité**
- Un composant créé une fois est utilisé partout
- Pagination utilisée dans 5 pages différentes
- Formatage de date identique partout

**Performance**
- Cache centralisé évite les requêtes SQL répétées
- Pagination limite le nombre de données chargées
- Session state minimise les recalculs

**Scalabilité**
- Ajouter une nouvelle page est simple
- Réutiliser les composants et utilitaires existants
- Pas besoin de refactoriser l'existant

**Collaboration**
- Plusieurs développeurs peuvent travailler en parallèle
- Conflits minimisés grâce à la modularité
- Code lisible et documenté

---

## 📋 Guide de démarrage

### Installation et lancement

```bash
# 1. Cloner le projet
git clone <url-repo>

# 2. Créer l'environnement virtuel
python -m venv .venv

# 3. Activer l'environnement
source .venv/bin/activate

# 4. Installer les dépendances
pip install -r requirements.txt

# 5. Lancer l'application
streamlit run src/app/home.py
```

L'application sera accessible sur `http://localhost:8501`

### Structure d'une nouvelle page

Pour ajouter une nouvelle page à l'application :

**Fichier : `src/app/pages/06_Nouvelle_Page.py`**

La première ligne du fichier détermine son nom dans la sidebar :

```python
import streamlit as st

# Configuration
st.set_page_config(page_title="Ma Nouvelle Page", layout="wide")

# Titre
st.title("📌 Ma Nouvelle Page")

# Contenu
st.write("Bienvenue!")
```

### Structure d'une nouvelle vue

Pour créer une nouvelle vue métier :

**Fichier : `src/app/views/ma_vue.py`**

```python
def render():
    """Affiche la vue"""
    st.subheader("Titre de la vue")
    
    # Récupérer les données
    # Afficher les données
    # Gérer les interactions
```

Utilisation dans une page :

```python
from src.app.views.ma_vue import render
render()
```

---

## ✅ Bonnes pratiques

### Code propre et maintenable

- **Séparez la logique de la présentation** : Les views contiennent l'affichage, les utils contiennent la logique
- **Réutilisez les composants** : Ne dupliquez pas le code UI
- **Centralisez les utilitaires** : Une fonction, un seul endroit
- **Commentez votre code** : Les docstrings expliquent le rôle de chaque fonction

### Performance

- **Utilisez le cache** : `@st.cache_data` pour les requêtes SQL
- **Paginagez les listes** : N'affichez que 10-20 éléments par page
- **Évitez les recalculs** : Session state garde l'état entre interactions
- **Limitez les requêtes** : Récupérez uniquement les données nécessaires

### Expérience utilisateur

- **Feedback clair** : Utilisez `st.success`, `st.error` pour confirmer les actions
- **Validation** : Vérifiez les entrées avant de sauvegarder
- **Navigation intuitive** : Buttons pour se déplacer entre les pages
- **Cohérence UI** : Utilisez les mêmes composants partout

### Sécurité

- **Requêtes paramétrées** : Évitez la SQL injection (utiliser `params` dans pandas)
- **Gestion d'erreurs** : Try/except pour capturer les erreurs
- **Audit** : Loggez les actions critiques via `audit_crud.py`

---


## 📊 Résumé : Les 5 couches de l'application

| Couche | Fichiers | Rôle | Exemple |
|--------|----------|------|---------|
| **Pages** | `pages/*.py` | Orchestration et routing | Route vers dashboard ou operations |
| **Views** | `views/*.py` | Présentation métier | Affiche la liste des opérations |
| **Components** | `components/*.py` | UI réutilisable | Boutons pagination, table header |
| **Utils** | `utils/*.py` | Services transversaux | Charger données, formater dates |
| **Model** | `crud/*.py` | Accès base de données | SELECT/INSERT/UPDATE/DELETE |

---
