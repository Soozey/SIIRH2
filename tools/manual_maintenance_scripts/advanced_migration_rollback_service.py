#!/usr/bin/env python3
"""
Service avancé de rollback et validation post-migration
Task 5.3: Implémenter la capacité de rollback et validation post-migration
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'siirh-backend'))

import sqlite3
from datetime import datetime, date
import json
from typing import List, Dict, Any, Optional

class AdvancedMigrationRollbackService:
    """Service avancé pour rollback et validation post-migration"""
    
    def __init__(self, db_path: str = "siirh-backend/siirh.db"):
        self.db_path = db_path
    
    def list_available_backups(self) -> List[Dict[str, Any]]:
        """Lister toutes les sauvegardes disponibles"""
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            # Rechercher les tables de sauvegarde
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name LIKE '%backup%workers'
                ORDER BY name DESC
            """)
            
            backup_tables = cursor.fetchall()
            backups = []
            
            for table in backup_tables:
                table_name = table["name"]
                backup_name = table_name.replace("_workers", "")
                
                # Récupérer les informations de la sauvegarde
                cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
                count = cursor.fetchone()["count"]
                
                # Essayer de récupérer la date de création
                try:
                    cursor.execute(f"""
                        SELECT sql FROM sqlite_master 
                        WHERE name = '{table_name}'
                    """)
                    # Extraire la date du nom si possible
                    if "_" in backup_name:
                        date_part = backup_name.split("_")[-1]
                        if len(date_part) >= 8:
                            created_date = f"{date_part[:4]}-{date_part[4:6]}-{date_part[6:8]}"
                        else:
                            created_date = "Date inconnue"
                    else:
                        created_date = "Date inconnue"
                except:
                    created_date = "Date inconnue"
                
                backups.append({
                    "backup_name": backup_name,
                    "table_name": table_name,
                    "worker_count": count,
                    "created_date": created_date,
                    "status": "Available"
                })
            
            return backups
            
        except Exception as e:
            print(f"Erreur lors de la liste des sauvegardes: {e}")
            return []
        
        finally:
            conn.close()
    
    def validate_backup_integrity(self, backup_name: str) -> Dict[str, Any]:
        """Valider l'intégrité d'une sauvegarde"""
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        validation = {
            "backup_name": backup_name,
            "timestamp": datetime.now().isoformat(),
            "is_valid": True,
            "issues": [],
            "statistics": {}
        }
        
        try:
            # Vérifier l'existence des tables de sauvegarde
            required_tables = [
                f"{backup_name}_workers",
                f"{backup_name}_worker_organizational_assignments"
            ]
            
            for table in required_tables:
                cursor.execute(f"""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='{table}'
                """)
                
                if not cursor.fetchone():
                    validation["is_valid"] = False
                    validation["issues"].append(f"Table manquante: {table}")
            
            if validation["is_valid"]:
                # Statistiques de la sauvegarde workers
                cursor.execute(f"""
                    SELECT COUNT(*) as total,
                           COUNT(CASE WHEN matricule IS NOT NULL AND matricule != '' THEN 1 END) as with_matricule
                    FROM {backup_name}_workers
                """)
                
                workers_stats = cursor.fetchone()
                validation["statistics"]["workers"] = {
                    "total": workers_stats["total"],
                    "with_matricule": workers_stats["with_matricule"],
                    "completion_rate": (workers_stats["with_matricule"] / workers_stats["total"] * 100) if workers_stats["total"] > 0 else 0
                }
                
                # Statistiques des affectations
                cursor.execute(f"""
                    SELECT COUNT(*) as total
                    FROM {backup_name}_worker_organizational_assignments
                """)
                
                assignments_stats = cursor.fetchone()
                validation["statistics"]["assignments"] = {
                    "total": assignments_stats["total"]
                }
            
            return validation
            
        except Exception as e:
            validation["is_valid"] = False
            validation["issues"].append(f"Erreur de validation: {e}")
            return validation
        
        finally:
            conn.close()

def main():
    """Interface interactive pour rollback et validation"""
    
    print("🔄 SERVICE AVANCÉ DE ROLLBACK ET VALIDATION")
    print("=" * 50)
    
    service = AdvancedMigrationRollbackService()
    
    while True:
        print("\n📋 OPTIONS DISPONIBLES:")
        print("1. Lister les sauvegardes disponibles")
        print("2. Valider l'intégrité d'une sauvegarde")
        print("3. Effectuer un rollback")
        print("4. Validation post-migration complète")
        print("5. Quitter")
        
        choice = input("\nChoisissez une option (1-5): ").strip()
        
        if choice == "1":
            print("\n📋 SAUVEGARDES DISPONIBLES:")
            backups = service.list_available_backups()
            
            if backups:
                for i, backup in enumerate(backups, 1):
                    print(f"{i}. {backup['backup_name']}")
                    print(f"   Date: {backup['created_date']}")
                    print(f"   Workers: {backup['worker_count']}")
                    print(f"   Statut: {backup['status']}")
            else:
                print("Aucune sauvegarde trouvée")
        
        elif choice == "2":
            backups = service.list_available_backups()
            if not backups:
                print("Aucune sauvegarde disponible")
                continue
            
            print("\nSauvegardes disponibles:")
            for i, backup in enumerate(backups, 1):
                print(f"{i}. {backup['backup_name']}")
            
            try:
                backup_idx = int(input("Choisissez une sauvegarde: ")) - 1
                if 0 <= backup_idx < len(backups):
                    backup_name = backups[backup_idx]["backup_name"]
                    validation = service.validate_backup_integrity(backup_name)
                    
                    print(f"\n🔍 VALIDATION DE {backup_name}:")
                    print(f"Statut: {'✅ VALIDE' if validation['is_valid'] else '❌ INVALIDE'}")
                    
                    if validation["statistics"]:
                        stats = validation["statistics"]
                        if "workers" in stats:
                            print(f"Workers: {stats['workers']['total']} ({stats['workers']['completion_rate']:.1f}% avec matricule)")
                        if "assignments" in stats:
                            print(f"Affectations: {stats['assignments']['total']}")
                    
                    if validation["issues"]:
                        print("Problèmes détectés:")
                        for issue in validation["issues"]:
                            print(f"  - {issue}")
                else:
                    print("Choix invalide")
            except ValueError:
                print("Veuillez entrer un nombre valide")
        
        elif choice == "5":
            print("Au revoir!")
            break
        
        else:
            print("Option non implémentée ou invalide")

if __name__ == "__main__":
    main()