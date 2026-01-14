# 📋 Application Streamlit de Gestion des Opérations Maritimes - Guide Complet

## ✅ Application Créée avec Succès !

Votre application Streamlit complète pour la gestion des opérations maritimes SECMAR est maintenant opérationnelle.

---

## 🌐 Accès à l'Application

L'application est accessible à l'adresse :
- **Local** : http://localhost:8502
- **Réseau** : http://192.168.1.80:8502

---

## 📱 Structure de l'Application

### 🏠 **Page d'Accueil** (home.py)
- **Titre** : Grass Squad - Gestion des Opérations Maritimes SECMAR
- **Contenu** :
  - Présentation détaillée des fonctionnalités
  - 4 métriques clés : Opérations, Personnes Secourues, Flotteurs, Logs d'Audit
  - Tableau des 5 dernières opérations enregistrées
  - Instructions d'utilisation
  
### 📊 **Page 1 - Dashboard**
- Indicateurs clés de performance (KPIs)
- Carte géolocalisée des opérations
- Statistiques globales
- Visualisations avec graphiques

### 📝 **Page 2 - Gestion Données**
- Édition rapide via `st.data_editor`
- Modification des cellules en temps réel
- Sauvegarde avec validation

### 🛡️ **Page 3 - Audit**
- Logs de toutes les modifications
- Diagramme ERD de la base de données
- Traçabilité complète

### 🔍 **Page 4 - Consultation des Opérations** (NOUVEAU)
- **Fonctionnalités** :
  - Filtrage par opération spécifique ou par CROSS
  - Affichage de toutes les opérations (limit 100)
  - Détails complets d'une opération avec onglets :
    - 🚢 Données de l'opération
    - ⛵ Flotteurs impliqués
    - 👥 Résultats humains
    - 📊 Statistiques
  - Export CSV de toutes les opérations

### ✏️ **Page 5 - CRUD Complet** (NOUVEAU)
- **3 modes d'utilisation via sidebar** :

#### 1. ➕ Créer une opération complète
- **Formulaire complet** avec tous les champs
- **Données de l'opération** :
  - CROSS* (obligatoire)
  - Date et heure de l'alerte* (obligatoire)
  - Événement, département, raison alerte, etc.
- **Flotteur (optionnel)** :
  - Pavillon, type, résultat, n° immatriculation
- **Résultats humains (optionnel)** :
  - Catégorie, résultat, nombre de personnes
- **Statistiques (optionnel)** :
  - Nb impliqués, secourus, décès, blessés
- **Validation Pandera** : Vérification des types et contraintes avant insertion
- **Insertion automatique** dans toutes les tables liées

#### 2. ✏️ Modifier une opération
- Sélection d'une opération dans la liste
- **4 onglets éditables** :
  - Opération (avec `st.data_editor`)
  - Flotteurs
  - Résultats humains
  - Statistiques
- Bouton "Sauvegarder" pour chaque onglet
- Validation des champs obligatoires (CROSS)

#### 3. 🗑️ Supprimer une opération
- Sélection de l'opération à supprimer
- **Aperçu détaillé** de ce qui sera supprimé
- **Comptage** :
  - Nombre de flotteurs liés
  - Nombre de résultats humains liés
  - Nombre de statistiques liées
- **Confirmation obligatoire** via checkbox
- **Suppression en cascade** : supprime toutes les données liées

---

## 🔐 Validation des Données

### Schémas Pandera créés

Un nouveau fichier `src/validation/pandera_schemas.py` a été créé avec :

1. **operations_schema** :
   - `cross` : str, min 1 char, max 50, NOT NULL
   - `date_heure_reception_alerte` : DateTime, NOT NULL
   - `latitude` : float, entre -90 et 90
   - `longitude` : float, entre -180 et 180
   - `distance_cote_metres` : float >= 0

2. **flotteurs_schema** :
   - `operation_id` : int, NOT NULL
   - `longueur`, `largeur` : float > 0
   - `puissance_max_moteur_ch` : float >= 0

3. **resultats_humain_schema** :
   - `operation_id` : int, NOT NULL
   - `nombre` : int >= 0

4. **operations_stats_schema** :
   - `operation_id` : int, NOT NULL
   - Tous les compteurs : int >= 0

### Fonctions de validation
- `validate_operations_data(data_dict)` : Valide une opération
- `validate_flotteur_data(data_dict)` : Valide un flotteur
- `validate_resultat_humain_data(data_dict)` : Valide un résultat humain
- `validate_operations_stats_data(data_dict)` : Valide les statistiques

---

## 🗄️ Tables PostgreSQL Gérées

### Relations entre tables

```
operations (1) ←→ (N) flotteurs
           (1) ←→ (N) resultats_humain
           (1) ←→ (N) operations_stats
```

Toutes les tables enfants ont une clé étrangère `operation_id` avec **ON DELETE CASCADE**.

### Champs clés

**operations** :
- `operation_id` : SERIAL PRIMARY KEY
- `"cross"` : VARCHAR(50) NOT NULL (mot-clé SQL échappé)
- `date_heure_reception_alerte` : TIMESTAMP NOT NULL
- 20+ autres champs (événement, département, latitude, longitude, etc.)

**flotteurs** :
- `flotteur_id` : SERIAL PRIMARY KEY
- `operation_id` : INTEGER NOT NULL (FK)
- Pavillon, type, résultat, caractéristiques techniques

**resultats_humain** :
- `resultat_humain_id` : SERIAL PRIMARY KEY
- `operation_id` : INTEGER NOT NULL (FK)
- Catégorie, résultat, nombre

**operations_stats** :
- `stat_id` : SERIAL PRIMARY KEY
- `operation_id` : INTEGER NOT NULL (FK)
- 12 compteurs (impliqués, secourus, décès, blessés, etc.)

**audit_log** :
- Logs automatiques de toutes les modifications

---

## 🚀 Comment Utiliser l'Application

### Scénario 1 : Créer une opération complète

1. Aller dans **05_CRUD_Complet**
2. Sélectionner **➕ Créer une opération complète** dans la sidebar
3. Remplir les champs obligatoires :
   - CROSS (ex: "Med")
   - Date de l'alerte
   - Heure de l'alerte
4. (Optionnel) Cocher "Ajouter un flotteur" et remplir les infos
5. (Optionnel) Cocher "Ajouter des résultats humains"
6. (Optionnel) Cocher "Ajouter des statistiques"
7. Cliquer sur **✅ Créer l'opération complète**
8. L'opération est créée avec un ID auto-généré
9. Les données liées sont automatiquement insérées avec le même `operation_id`

### Scénario 2 : Consulter une opération

1. Aller dans **04_Consultation_Operations**
2. Dans la sidebar, sélectionner une opération spécifique
3. Consulter les 4 onglets :
   - Opération : vue détaillée transposée
   - Flotteurs : tous les flotteurs liés
   - Résultats Humains : tous les résultats
   - Statistiques : KPIs et tableau complet
4. Exporter en CSV si nécessaire (bouton dans sidebar)

### Scénario 3 : Modifier rapidement une donnée

**Méthode 1 : Édition rapide (Page 2)**
1. Aller dans **02_Gestion_Donnees**
2. Double-cliquer sur une cellule pour modifier
3. Cliquer sur **💾 Sauvegarder les modifications**

**Méthode 2 : Modification structurée (Page 5)**
1. Aller dans **05_CRUD_Complet**
2. Sélectionner **✏️ Modifier une opération**
3. Choisir l'opération dans la liste
4. Aller dans l'onglet concerné
5. Modifier les données dans `st.data_editor`
6. Cliquer sur **💾 Sauvegarder**

### Scénario 4 : Supprimer une opération

1. Aller dans **05_CRUD_Complet**
2. Sélectionner **🗑️ Supprimer une opération**
3. Choisir l'opération dans la liste
4. Lire l'aperçu et le nombre de données liées
5. Cocher "Je confirme vouloir supprimer..."
6. Cliquer sur **🗑️ SUPPRIMER DÉFINITIVEMENT**
7. ⚠️ **Toutes les données liées sont supprimées en cascade !**

---

## 📦 Dépendances Installées

Les packages suivants ont été ajoutés à `requirements.txt` :

```
pandera==0.20.4           # Validation de données avec schémas
streamlit==1.40.2         # Framework web
streamlit-mermaid==0.1.0  # Diagrammes ERD
```

Tous les autres packages étaient déjà présents (pandas, SQLAlchemy, psycopg2, etc.)

---

## 🎨 Interface Utilisateur

### Sidebar
- Navigation automatique entre les pages
- Filtres contextuels par page :
  - Page 4 : Filtres par opération et CROSS
  - Page 5 : Radio button pour choisir l'action (Créer/Modifier/Supprimer)

### Composants Streamlit utilisés
- `st.dataframe()` : Affichage de tableaux en lecture seule
- `st.data_editor()` : Tableaux éditables
- `st.form()` : Formulaires de création
- `st.tabs()` : Onglets pour organiser les données
- `st.metric()` : Affichage de KPIs
- `st.selectbox()`, `st.text_input()`, `st.number_input()` : Champs de formulaire
- `st.success()`, `st.error()`, `st.warning()`, `st.info()` : Messages
- `st.balloons()` : Animation de succès

---

## 🛠️ Technologies

### Backend
- **SQLAlchemy** : ORM pour pandas (évite les warnings)
- **psycopg2** : Connexion directe pour les CRUD
- **Pandera** : Validation de schémas DataFrame

### Frontend
- **Streamlit** : Framework web Python
- **Pandas** : Manipulation de données
- **Streamlit-Mermaid** : Diagrammes ERD

### Base de données
- **PostgreSQL 14+** : SGBD relationnel

---

## ⚠️ Points d'Attention

### Mot-clé SQL "cross"
Le champ `cross` est un mot-clé réservé SQL, il **DOIT** être échappé avec des guillemets doubles :

✅ **Correct** :
```sql
SELECT "cross" FROM operations;
INSERT INTO operations ("cross", ...) VALUES (%s, ...);
```

❌ **Incorrect** :
```sql
SELECT cross FROM operations;  -- ERREUR de syntaxe !
```

Tous les fichiers CRUD ont été corrigés pour échapper correctement `"cross"`.

### Validation des champs obligatoires

Dans les formulaires, les champs obligatoires sont marqués avec un astérisque (*) :
- `cross`*
- `date_heure_reception_alerte`* (combinaison de date + heure)

Si un champ obligatoire est vide, un message d'erreur s'affiche :
```
❌ Le champ CROSS est obligatoire
```

### Suppression en cascade

Quand vous supprimez une opération, **toutes les données liées sont automatiquement supprimées** :
- Tous les flotteurs avec cet `operation_id`
- Tous les résultats humains avec cet `operation_id`
- Toutes les statistiques avec cet `operation_id`

**Cette action est irréversible !**

---

## 📝 Fichiers Créés/Modifiés

### Nouveaux fichiers
1. `src/app/pages/04_Consultation_Operations.py` : Page de consultation complète
2. `src/app/pages/05_CRUD_Complet.py` : Interface CRUD avec validation Pandera
3. `src/validation/pandera_schemas.py` : Schémas de validation
4. `README_APPLICATION.md` : Documentation complète de l'application
5. `GUIDE_UTILISATION.md` : Ce guide

### Fichiers modifiés
1. `src/app/home.py` : Page d'accueil améliorée avec plus de métriques
2. `requirements.txt` : Ajout de pandera, streamlit, streamlit-mermaid

---

## 🧪 Tests à Effectuer

### Test 1 : Créer une opération complète
- [ ] Créer une opération avec uniquement les champs obligatoires
- [ ] Créer une opération avec un flotteur
- [ ] Créer une opération avec résultats humains
- [ ] Créer une opération avec statistiques
- [ ] Créer une opération avec TOUT (flotteur + humain + stats)
- [ ] Vérifier que les ID sont auto-générés correctement
- [ ] Vérifier les messages de succès

### Test 2 : Consultation
- [ ] Filtrer par opération spécifique
- [ ] Filtrer par CROSS
- [ ] Vérifier que tous les onglets s'affichent
- [ ] Vérifier les métriques (personnes impliquées, secourues, etc.)
- [ ] Exporter en CSV

### Test 3 : Modification
- [ ] Modifier une opération (champ texte)
- [ ] Modifier une opération (champ numérique)
- [ ] Tenter de vider le champ CROSS (doit échouer)
- [ ] Vérifier le message de succès

### Test 4 : Suppression
- [ ] Afficher l'aperçu de l'opération
- [ ] Vérifier le comptage des données liées
- [ ] Supprimer sans confirmation (bouton désactivé)
- [ ] Supprimer avec confirmation
- [ ] Vérifier que toutes les données liées ont disparu

### Test 5 : Validation
- [ ] Créer une opération sans CROSS (doit échouer)
- [ ] Créer une opération sans date (doit échouer)
- [ ] Créer une opération avec latitude > 90 (doit échouer avec Pandera)
- [ ] Créer une opération avec nombre négatif (doit échouer)

---

## 🎯 Résumé des Fonctionnalités Livrées

✅ **1. Consulter les données**
- Page dédiée avec filtres par opération et CROSS
- Affichage des tables liées dans des onglets
- Export CSV

✅ **2. Ajouter une opération**
- Formulaire complet avec tous les champs
- Ajout de données liées (flotteurs, résultats, stats)
- Validation Pandera avant insertion
- Messages de confirmation

✅ **3. Modifier des cellules**
- Édition rapide (Page 2 - Gestion Données)
- Édition structurée (Page 5 - CRUD Complet)
- Validation avant sauvegarde

✅ **4. Supprimer une opération**
- Aperçu avant suppression
- Confirmation obligatoire
- Suppression en cascade des données liées

✅ **5. Valider les données**
- Schémas Pandera pour toutes les tables
- Vérification des types
- Contraintes NOT NULL
- Contraintes métier (plages, valeurs positives)
- Messages d'erreur détaillés

✅ **Interface simple et intuitive**
- Navigation claire par sidebar
- Formulaires guidés
- Tableaux éditables
- Messages visuels (success, error, warning, info)
- Animations (balloons)

✅ **SQLAlchemy pour interactions DB**
- Engine SQLAlchemy créé dans load_database.py
- Utilisé pour pandas (évite les warnings)
- Connexions psycopg2 pour CRUD directs

---

## 🚀 Prochaines Étapes Suggérées

### Améliorations possibles
1. **Recherche avancée** : Filtres multiples combinés (date, département, événement)
2. **Graphiques interactifs** : Plotly pour visualisations dynamiques
3. **Export PDF** : Rapports d'opérations en PDF
4. **Import CSV** : Upload de fichiers CSV pour insertion en masse
5. **Authentification** : Système de login pour sécuriser l'accès
6. **Notifications** : Emails automatiques lors de créations/modifications
7. **API REST** : Endpoints pour intégrations externes
8. **Tests unitaires** : Pytest pour les fonctions CRUD et validation

### Optimisations
1. **Cache Streamlit** : `@st.cache_data` pour requêtes répétitives
2. **Pagination** : Pour grandes quantités de données
3. **Index DB** : Index sur `operation_id`, `cross`, `date_heure_reception_alerte`
4. **Async** : Requêtes asynchrones pour meilleures performances

---

## 📞 Support

Pour toute question ou problème :
1. Consulter le `README_APPLICATION.md` pour la documentation complète
2. Vérifier les logs dans le terminal
3. Tester la connexion à PostgreSQL : `psql -U postgres -d secmar_db`
4. Vérifier le fichier `.env`

---

**🎉 Application Opérationnelle !**

Votre système de gestion des opérations maritimes est maintenant complet et fonctionnel.

**URL d'accès** : http://localhost:8502

**Développé par Grass Squad** 🌊 | **Simplon DE P1 2025**

