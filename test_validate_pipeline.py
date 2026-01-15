#!/usr/bin/env python3
"""
Script de test pour la fonction validate_clean_pipeline
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.ingestion.load_raw_data import load_all_raw_data
from src.validation.run_validation import validate_clean_pipeline

if __name__ == "__main__":
    print("=" * 60)
    print("TEST : validate_clean_pipeline")
    print("=" * 60)
    
    # Charger les données brutes
    print("\n📥 Chargement des données brutes...")
    dataframes = load_all_raw_data()
    
    print(f"\nDonnées chargées :")
    for table_name, df in dataframes.items():
        print(f"  - {table_name}: {len(df)} lignes, {len(df.columns)} colonnes")
    
    # Exécuter le pipeline
    print("\n" + "=" * 60)
    print("Exécution du pipeline de validation/nettoyage...")
    print("=" * 60)
    
    results = validate_clean_pipeline(
        dataframes,
        rejected_path="data/rejected",
        lazy_config_raw={
            "operations": True,
            "operations_stats": True,
            "flotteurs": True,
            "resultats_humain": True
        },
        lazy_config_clean={
            "operations": True,
            "operations_stats": True,
            "flotteurs": True,
            "resultats_humain": True
        }
    )
    
    # Afficher les résultats
    print("\n" + "=" * 60)
    print("RÉSULTATS DU PIPELINE")
    print("=" * 60)
    
    for table_name, result in results.items():
        curated_df = result["curated"]
        rejected_df = result["rejected"]
        
        print(f"\n📊 {table_name.upper()}")
        print(f"  ✓ Curated: {len(curated_df)} lignes")
        
        if rejected_df is not None and len(rejected_df) > 0:
            print(f"  ⚠️  Rejected: {len(rejected_df)} lignes")
        else:
            print(f"  ✓ Rejected: 0 lignes (aucun rejet)")
    
    print("\n" + "=" * 60)
    print("✅ TEST TERMINÉ AVEC SUCCÈS")
    print("=" * 60)
