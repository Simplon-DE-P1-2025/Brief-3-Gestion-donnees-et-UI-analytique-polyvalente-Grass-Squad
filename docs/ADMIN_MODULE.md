# Module d'Administration - Listes de Référence

## Description

Le module d'administration permet de gérer dynamiquement les listes de référence utilisées dans les formulaires de l'application SECMAR. Au lieu d'avoir des valeurs codées en dur, les listes déroulantes (selectbox) sont alimentées par une table de base de données.

## Architecture

### 1. Base de données

**Table: `reference_lists`**
- `id`: Identifiant unique (SERIAL PRIMARY KEY)
- `category`: Catégorie de la liste (ex: 'type_operation', 'pavillon')
- `value`: Valeur de l'option
- `display_order`: Ordre d'affichage dans les listes
- `is_active`: Statut actif/inactif (permet de masquer sans supprimer)
- `description`: Description optionnelle
- `created_at`: Date de création
- `updated_at`: Date de dernière modification

### 2. Fichiers créés

```
src/
├── database/
│   ├── reference_lists.sql          # Schéma SQL et données initiales
│   └── init_reference_lists.py      # Script d'initialisation
├── crud/
│   └── reference_lists_crud.py      # Fonctions CRUD pour la table
└── app/
    └── pages/
        ├── 02_Operations.py         # Formulaire adapté (charge depuis DB)
        └── 04_Admin.py              # Interface d'administration
```

## Installation

### Étape 1: Initialiser la table

Exécutez le script d'initialisation pour créer la table et insérer les données par défaut :

```bash
uv run python src/database/init_reference_lists.py
```

Sortie attendue :
```
============================================================
INITIALISATION DES LISTES DE RÉFÉRENCE
============================================================
🔄 Création de la table reference_lists...
✅ Table reference_lists créée avec succès!
📊 100+ valeurs insérées

📋 Résumé par catégorie:
  - categorie_flotteur: 6 valeur(s)
  - categorie_personne: 10 valeur(s)
  - cross: 7 valeur(s)
  - maree_categorie: 4 valeur(s)
  - pavillon: 2 valeur(s)
  - prefecture_maritime: 3 valeur(s)
  - resultat_flotteur: 9 valeur(s)
  - resultat_humain: 9 valeur(s)
  - systeme_source: 2 valeur(s)
  - type_operation: 5 valeur(s)
  - vent_direction_categorie: 8 valeur(s)

============================================================
✅ INITIALISATION TERMINÉE AVEC SUCCÈS
============================================================
```

### Étape 2: Vérifier l'application

L'application Streamlit doit être redémarrée pour prendre en compte les nouvelles fonctionnalités :

```bash
uv run streamlit run src/app/home.py --server.port 8502
```

## Utilisation

### Interface d'Administration

Accédez à la page **Admin** (4ème page de l'application)

#### 1. Vue des catégories

La page d'accueil affiche toutes les catégories disponibles sous forme de cartes :
- Nom de la catégorie
- Description
- Nombre de valeurs

#### 2. Gestion d'une catégorie

Cliquez sur **"✏️ Gérer"** pour accéder aux options :

**Actions disponibles :**

- **➕ Ajouter une valeur** : Créer une nouvelle option
  - Saisir la valeur
  - Ajouter une description (optionnel)
  - Définir l'ordre d'affichage
  
- **✏️ Modifier** : Éditer une valeur existante
  - Changer le texte
  - Modifier la description
  - Réorganiser l'ordre
  - Activer/désactiver
  
- **🔄 Activer/Désactiver** : Masquer temporairement une option sans la supprimer

- **🗑️ Supprimer** : Supprimer définitivement une valeur

### Catégories disponibles

| Catégorie | Description | Utilisation |
|-----------|-------------|-------------|
| `type_operation` | Types d'opération (SAR, MAS, etc.) | Formulaire opération |
| `pavillon` | Pavillons des navires | Formulaire flotteur |
| `categorie_flotteur` | Catégories de flotteurs | Formulaire flotteur |
| `resultat_flotteur` | Résultats possibles pour les flotteurs | Formulaire flotteur |
| `categorie_personne` | Catégories de personnes impliquées | Formulaire résultats humains |
| `resultat_humain` | Résultats humains | Formulaire résultats humains |
| `vent_direction_categorie` | Directions cardinales du vent | Formulaire météo |
| `systeme_source` | Systèmes source des données | Formulaire opération |
| `prefecture_maritime` | Préfectures maritimes | Formulaire statistiques |
| `maree_categorie` | Catégories de coefficient de marée | Formulaire statistiques |
| `cross` | CROSS (centres de surveillance) | Formulaire opération |

## Fonctionnalités techniques

### Cache des données

Les listes de référence sont mises en cache pendant 5 minutes pour améliorer les performances :

```python
@st.cache_data(ttl=300)  # Cache pendant 5 minutes
def load_reference_list(category):
    """Charge une liste de référence depuis la DB"""
    try:
        values = get_reference_list_values(category, active_only=True)
        return [None] + [val[1] for val in values]
    except:
        return [None]
```

### Fallback en cas d'erreur

Si la table n'existe pas ou en cas d'erreur de connexion, les selectbox affichent uniquement l'option "Non spécifié" pour éviter les crashs.

### Valeurs inactives

Les valeurs désactivées (`is_active = FALSE`) n'apparaissent pas dans les formulaires mais restent en base de données pour préserver l'historique.

## Avantages

✅ **Flexibilité** : Modifier les listes sans toucher au code
✅ **Évolutivité** : Ajouter de nouvelles catégories facilement
✅ **Traçabilité** : Historique des modifications (created_at, updated_at)
✅ **Performance** : Mise en cache des données
✅ **Maintenance** : Pas de redéploiement nécessaire pour ajouter une valeur
✅ **Conformité** : Respect de la documentation SECMAR avec possibilité d'adaptation

## Exemples d'utilisation

### Ajouter un nouveau CROSS

1. Aller dans Admin → Gérer la catégorie "cross"
2. Cliquer sur "➕ Ajouter une valeur"
3. Saisir : 
   - Valeur: "Nouvelle-Calédonie"
   - Description: "CROSS Nouvelle-Calédonie"
   - Ordre: 8
4. Enregistrer
5. La nouvelle valeur apparaît immédiatement dans le formulaire Operations

### Désactiver temporairement une option

1. Admin → Sélectionner la catégorie concernée
2. Sélectionner la valeur dans la liste
3. Cliquer sur "🔄 Activer/Désactiver"
4. La valeur disparaît des formulaires mais reste en base

### Réorganiser les options

1. Admin → Gérer la catégorie
2. Modifier chaque valeur en changeant son "Ordre d'affichage"
3. Les options apparaîtront dans le nouvel ordre dans les selectbox

## Maintenance

### Ajouter une nouvelle catégorie

1. Insérer les valeurs dans la table :
```sql
INSERT INTO reference_lists (category, value, display_order, description) VALUES
('nouvelle_categorie', 'Valeur 1', 1, 'Description'),
('nouvelle_categorie', 'Valeur 2', 2, 'Description');
```

2. Mettre à jour le dictionnaire dans `04_Admin.py` :
```python
CATEGORY_DESCRIPTIONS = {
    ...
    'nouvelle_categorie': 'Description de la nouvelle catégorie'
}
```

3. Adapter le formulaire dans `02_Operations.py` :
```python
nouvelle_categorie_options = load_reference_list('nouvelle_categorie')
valeur = st.selectbox("Label", nouvelle_categorie_options,
                     format_func=lambda x: "Non spécifié" if x is None else x)
```

### Sauvegarder les listes

Exporter les données actuelles :
```bash
pg_dump -h localhost -U postgres -d secmar_db -t reference_lists > backup_ref_lists.sql
```

### Restaurer les listes

Importer une sauvegarde :
```bash
psql -h localhost -U postgres -d secmar_db < backup_ref_lists.sql
```

## Dépannage

**Problème** : Les listes n'apparaissent pas dans les formulaires

**Solution** : 
1. Vérifier que la table existe : `SELECT * FROM reference_lists LIMIT 5;`
2. Vider le cache Streamlit : cliquer sur "C" dans l'app ou redémarrer
3. Vérifier que les valeurs sont actives : `SELECT * FROM reference_lists WHERE is_active = TRUE;`

**Problème** : Erreur "table reference_lists does not exist"

**Solution** : Exécuter `uv run python src/database/init_reference_lists.py`

## Évolutions futures

- [ ] Import/Export CSV des listes
- [ ] Historique des modifications
- [ ] Gestion des permissions (qui peut modifier quoi)
- [ ] Traductions multilingues
- [ ] Validation des valeurs (regex, contraintes)
