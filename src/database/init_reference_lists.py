"""
Script pour initialiser la table reference_lists avec les données par défaut
À exécuter après la création de la base de données
"""
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

from src.database.load_database import get_db_connection

def init_reference_lists():
    """Crée la table reference_lists et insère les données initiales"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Lire et exécuter le fichier SQL
        sql_file = PROJECT_ROOT / 'src' / 'database' / 'reference_lists.sql'
        
        if not sql_file.exists():
            print(f"❌ Fichier SQL introuvable: {sql_file}")
            return False
        
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        print("🔄 Création de la table reference_lists...")
        cursor.execute(sql_script)
        conn.commit()
        
        # Vérifier le nombre de lignes insérées
        cursor.execute("SELECT COUNT(*) FROM reference_lists")
        count = cursor.fetchone()[0]
        
        print(f"✅ Table reference_lists créée avec succès!")
        print(f"📊 {count} valeurs insérées")
        
        # Afficher un résumé par catégorie
        cursor.execute("""
            SELECT category, COUNT(*) as count
            FROM reference_lists
            GROUP BY category
            ORDER BY category
        """)
        
        print("\n📋 Résumé par catégorie:")
        for row in cursor.fetchall():
            category, cat_count = row
            print(f"  - {category}: {cat_count} valeur(s)")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        print(f"❌ Erreur lors de l'initialisation: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("INITIALISATION DES LISTES DE RÉFÉRENCE")
    print("=" * 60)
    
    success = init_reference_lists()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ INITIALISATION TERMINÉE AVEC SUCCÈS")
    else:
        print("❌ ÉCHEC DE L'INITIALISATION")
    print("=" * 60)
