"""
Script de nettoyage du système matricule suspendu
Supprime tous les fichiers de test, documentation et scripts liés au système matricule
"""
import os
import glob

# Liste des fichiers à supprimer
files_to_delete = [
    # Tests matricule
    "test_matricule_*.py",
    "check_matricules_in_db.py",
    "create_matricule_tables_postgresql.py",
    "test_organizational_assignment_service.py",
    "check_assignment_table_structure.py",
    "fix_assignment_table_columns.py",
    "test_real_matricules.py",
    "test_search_debug.py",
    "test_correct_names.py",
    "check_search_vectors.py",
    "test_migration_analysis.py",
    "simple_matricule_analysis.py",
    "debug_matricule_analysis.py",
    "analyze_matricule_migration_data.py",
    "matricule_migration_strategy.py",
    "update_data_model_matricules.py",
    "create_performance_indexes.py",
    "task_4_checkpoint_validation.py",
    "advanced_migration_rollback_service.py",
    "fix_matricule_api_performance.py",
    "optimized_matricule_service.py",
    "diagnose_performance_bottleneck.py",
    "implement_cache_solution.py",
    "create_mock_matricule_service.py",
    "task_8_performance_issue_report.py",
    "fix_encoding_critical_issue.py",
    "fix_database_encoding_issue.py",
    "run_matricule_migration.py",
    
    # Documentation matricule
    "MATRICULE_SYSTEM_*.md",
    "ROLLBACK_MATRICULE_SYSTEM.md",
    "TASK_*_COMPLETION_SUMMARY.md",
    
    # Logs et résultats matricule
    "matricule_*.json",
    "task_4_checkpoint_validation_*.json",
    "task_8_*.json",
    "backend_validation_log_*.json",
    "data_model_update_log_*.json",
    
    # Specs matricule
    ".kiro/specs/matricule-based-organizational-system/*",
]

def cleanup():
    print("=" * 70)
    print("NETTOYAGE DU SYSTÈME MATRICULE SUSPENDU")
    print("=" * 70)
    
    deleted_count = 0
    error_count = 0
    
    for pattern in files_to_delete:
        # Chercher les fichiers correspondant au pattern
        matches = glob.glob(pattern, recursive=True)
        
        for file_path in matches:
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    print(f"✅ Supprimé: {file_path}")
                    deleted_count += 1
                elif os.path.isdir(file_path):
                    import shutil
                    shutil.rmtree(file_path)
                    print(f"✅ Dossier supprimé: {file_path}")
                    deleted_count += 1
            except Exception as e:
                print(f"❌ Erreur lors de la suppression de {file_path}: {e}")
                error_count += 1
    
    print("\n" + "=" * 70)
    print("RÉSUMÉ DU NETTOYAGE")
    print("=" * 70)
    print(f"\n✅ Fichiers supprimés: {deleted_count}")
    print(f"❌ Erreurs: {error_count}")
    
    if error_count == 0:
        print("\n🎉 Nettoyage terminé avec succès !")
    else:
        print(f"\n⚠️ Nettoyage terminé avec {error_count} erreur(s)")
    
    print("\n📝 Fichiers conservés:")
    print("   - MATRICULE_SYSTEM_SUSPENDED.md (documentation de référence)")
    print("   - ROLLBACK_MATRICULE_SYSTEM.md (procédure de rollback)")
    print("\n" + "=" * 70)

if __name__ == "__main__":
    response = input("⚠️  Voulez-vous vraiment supprimer tous les fichiers du système matricule ? (oui/non): ")
    if response.lower() in ['oui', 'yes', 'y', 'o']:
        cleanup()
    else:
        print("❌ Nettoyage annulé")
