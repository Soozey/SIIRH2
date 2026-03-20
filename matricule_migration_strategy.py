#!/usr/bin/env python3
"""
Matricule Migration Strategy Implementation
Task 1: System Analysis and Migration Preparation (COMPLETED)
Task 2: Data Model Updates and Matricule Service Implementation
"""

import sqlite3
import json
from datetime import datetime
import re
from collections import defaultdict

class MatriculeMigrationService:
    """Service for managing matricule-based organizational system migration"""
    
    def __init__(self, db_path="siirh-backend/siirh.db"):
        self.db_path = db_path
        self.analysis_results = None
    
    def connect_db(self):
        """Create database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def generate_unique_matricule(self, employer_id, existing_matricules):
        """Generate a unique matricule for a worker"""
        # Format: E{employer_id:03d}{sequence:05d}
        # Example: E001AB001, E001AB002, etc.
        
        # Find existing matricules for this employer
        employer_matricules = [m for m in existing_matricules if m.startswith(f"E{employer_id:03d}")]
        
        # Extract sequence numbers
        sequences = []
        for matricule in employer_matricules:
            match = re.search(r'E\d{3}[A-Z]{2}(\d{3})$', matricule)
            if match:
                sequences.append(int(match.group(1)))
        
        # Find next available sequence
        next_seq = 1
        if sequences:
            next_seq = max(sequences) + 1
        
        # Generate random letters for uniqueness
        import random
        import string
        letters = ''.join(random.choices(string.ascii_uppercase, k=2))
        
        return f"E{employer_id:03d}{letters}{next_seq:03d}"
    
    def fix_matricule_issues(self):
        """Fix existing matricule issues (duplicates, too short, etc.)"""
        print("🔧 Correction des problèmes de matricules...")
        
        conn = self.connect_db()
        cursor = conn.cursor()
        
        try:
            # Get all current matricules
            cursor.execute("SELECT id, matricule, employer_id FROM workers WHERE matricule IS NOT NULL AND matricule != ''")
            workers_with_matricules = cursor.fetchall()
            
            existing_matricules = [w['matricule'] for w in workers_with_matricules]
            fixes_applied = []
            
            # Fix too short matricules
            for worker in workers_with_matricules:
                if len(worker['matricule']) < 5:  # Too short
                    old_matricule = worker['matricule']
                    new_matricule = self.generate_unique_matricule(worker['employer_id'], existing_matricules)
                    
                    cursor.execute(
                        "UPDATE workers SET matricule = ? WHERE id = ?",
                        (new_matricule, worker['id'])
                    )
                    
                    existing_matricules.append(new_matricule)
                    fixes_applied.append({
                        "worker_id": worker['id'],
                        "old_matricule": old_matricule,
                        "new_matricule": new_matricule,
                        "reason": "too_short"
                    })
                    
                    print(f"   ✅ Worker {worker['id']}: {old_matricule} → {new_matricule}")
            
            conn.commit()
            print(f"   Corrections appliquées: {len(fixes_applied)}")
            return fixes_applied
            
        except Exception as e:
            conn.rollback()
            print(f"   ❌ Erreur lors des corrections: {e}")
            return []
        finally:
            conn.close()
    
    def generate_missing_matricules(self):
        """Generate matricules for workers who don't have them"""
        print("🆔 Génération des matricules manquants...")
        
        conn = self.connect_db()
        cursor = conn.cursor()
        
        try:
            # Get workers without matricules
            cursor.execute("""
                SELECT id, employer_id, nom, prenom 
                FROM workers 
                WHERE matricule IS NULL OR matricule = '' OR TRIM(matricule) = ''
            """)
            workers_without_matricules = cursor.fetchall()
            
            # Get existing matricules
            cursor.execute("SELECT matricule FROM workers WHERE matricule IS NOT NULL AND matricule != ''")
            existing_matricules = [row['matricule'] for row in cursor.fetchall()]
            
            generated_matricules = []
            
            for worker in workers_without_matricules:
                new_matricule = self.generate_unique_matricule(worker['employer_id'], existing_matricules)
                
                cursor.execute(
                    "UPDATE workers SET matricule = ? WHERE id = ?",
                    (new_matricule, worker['id'])
                )
                
                existing_matricules.append(new_matricule)
                generated_matricules.append({
                    "worker_id": worker['id'],
                    "worker_name": f"{worker['nom']} {worker['prenom']}",
                    "new_matricule": new_matricule
                })
                
                print(f"   ✅ {worker['nom']} {worker['prenom']} (ID: {worker['id']}) → {new_matricule}")
            
            conn.commit()
            print(f"   Matricules générés: {len(generated_matricules)}")
            return generated_matricules
            
        except Exception as e:
            conn.rollback()
            print(f"   ❌ Erreur lors de la génération: {e}")
            return []
        finally:
            conn.close()
    
    def create_matricule_name_resolver_table(self):
        """Create the matricule-name resolver table for bidirectional lookup"""
        print("📋 Création de la table de résolution matricule-nom...")
        
        conn = self.connect_db()
        cursor = conn.cursor()
        
        try:
            # Create the resolver table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS matricule_name_resolver (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    worker_id INTEGER NOT NULL,
                    matricule VARCHAR(20) NOT NULL,
                    nom VARCHAR(100),
                    prenom VARCHAR(100),
                    full_name VARCHAR(200),
                    employer_id INTEGER NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (worker_id) REFERENCES workers(id),
                    FOREIGN KEY (employer_id) REFERENCES employers(id)
                )
            """)
            
            # Create indexes for fast lookup
            cursor.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS idx_resolver_matricule 
                ON matricule_name_resolver(matricule)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_resolver_name 
                ON matricule_name_resolver(full_name, employer_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_resolver_worker 
                ON matricule_name_resolver(worker_id)
            """)
            
            # Populate the resolver table
            cursor.execute("""
                INSERT OR REPLACE INTO matricule_name_resolver 
                (worker_id, matricule, nom, prenom, full_name, employer_id)
                SELECT 
                    id,
                    matricule,
                    nom,
                    prenom,
                    TRIM(COALESCE(nom, '') || ' ' || COALESCE(prenom, '')) as full_name,
                    employer_id
                FROM workers
                WHERE matricule IS NOT NULL AND matricule != ''
            """)
            
            conn.commit()
            
            # Verify creation
            cursor.execute("SELECT COUNT(*) FROM matricule_name_resolver")
            count = cursor.fetchone()[0]
            print(f"   ✅ Table créée avec {count} entrées")
            
            return True
            
        except Exception as e:
            conn.rollback()
            print(f"   ❌ Erreur lors de la création: {e}")
            return False
        finally:
            conn.close()
    
    def create_audit_trail_table(self):
        """Create audit trail table for tracking matricule changes"""
        print("📝 Création de la table d'audit des matricules...")
        
        conn = self.connect_db()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS matricule_audit_trail (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    worker_id INTEGER NOT NULL,
                    old_matricule VARCHAR(20),
                    new_matricule VARCHAR(20),
                    old_name VARCHAR(200),
                    new_name VARCHAR(200),
                    change_type VARCHAR(50) NOT NULL,
                    change_reason VARCHAR(200),
                    changed_by VARCHAR(100),
                    changed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (worker_id) REFERENCES workers(id)
                )
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_audit_worker 
                ON matricule_audit_trail(worker_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_audit_date 
                ON matricule_audit_trail(changed_at)
            """)
            
            conn.commit()
            print(f"   ✅ Table d'audit créée")
            return True
            
        except Exception as e:
            conn.rollback()
            print(f"   ❌ Erreur lors de la création: {e}")
            return False
        finally:
            conn.close()
    
    def validate_matricule_integrity(self):
        """Validate the integrity of the matricule system"""
        print("🔍 Validation de l'intégrité du système de matricules...")
        
        conn = self.connect_db()
        cursor = conn.cursor()
        
        try:
            issues = []
            
            # Check for duplicate matricules
            cursor.execute("""
                SELECT matricule, COUNT(*) as count
                FROM workers 
                WHERE matricule IS NOT NULL AND matricule != ''
                GROUP BY matricule
                HAVING COUNT(*) > 1
            """)
            
            duplicates = cursor.fetchall()
            for dup in duplicates:
                issues.append({
                    "type": "duplicate_matricule",
                    "matricule": dup['matricule'],
                    "count": dup['count']
                })
            
            # Check for missing matricules
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM workers 
                WHERE matricule IS NULL OR matricule = '' OR TRIM(matricule) = ''
            """)
            
            missing_count = cursor.fetchone()['count']
            if missing_count > 0:
                issues.append({
                    "type": "missing_matricules",
                    "count": missing_count
                })
            
            # Check resolver table consistency
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM workers w
                LEFT JOIN matricule_name_resolver r ON w.id = r.worker_id
                WHERE w.matricule IS NOT NULL AND w.matricule != '' AND r.id IS NULL
            """)
            
            resolver_missing = cursor.fetchone()['count']
            if resolver_missing > 0:
                issues.append({
                    "type": "resolver_inconsistency",
                    "count": resolver_missing
                })
            
            if issues:
                print(f"   ⚠️  Problèmes détectés: {len(issues)}")
                for issue in issues:
                    print(f"     - {issue['type']}: {issue.get('count', issue.get('matricule'))}")
            else:
                print(f"   ✅ Aucun problème d'intégrité détecté")
            
            return issues
            
        except Exception as e:
            print(f"   ❌ Erreur lors de la validation: {e}")
            return []
        finally:
            conn.close()
    
    def run_migration_preparation(self):
        """Run the complete migration preparation process"""
        print("🚀 DÉMARRAGE DE LA PRÉPARATION DE MIGRATION")
        print("=" * 60)
        
        migration_log = {
            "timestamp": datetime.now().isoformat(),
            "steps_completed": [],
            "issues_found": [],
            "fixes_applied": [],
            "next_steps": []
        }
        
        try:
            # Step 1: Fix existing matricule issues
            print("\n📋 ÉTAPE 1: Correction des problèmes de matricules")
            fixes = self.fix_matricule_issues()
            migration_log["fixes_applied"].extend(fixes)
            migration_log["steps_completed"].append("matricule_fixes")
            
            # Step 2: Generate missing matricules
            print("\n📋 ÉTAPE 2: Génération des matricules manquants")
            generated = self.generate_missing_matricules()
            migration_log["fixes_applied"].extend([{
                "type": "generated_matricule",
                **gen
            } for gen in generated])
            migration_log["steps_completed"].append("matricule_generation")
            
            # Step 3: Create resolver table
            print("\n📋 ÉTAPE 3: Création de la table de résolution")
            if self.create_matricule_name_resolver_table():
                migration_log["steps_completed"].append("resolver_table_created")
            
            # Step 4: Create audit trail
            print("\n📋 ÉTAPE 4: Création de la table d'audit")
            if self.create_audit_trail_table():
                migration_log["steps_completed"].append("audit_table_created")
            
            # Step 5: Validate integrity
            print("\n📋 ÉTAPE 5: Validation de l'intégrité")
            issues = self.validate_matricule_integrity()
            migration_log["issues_found"] = issues
            migration_log["steps_completed"].append("integrity_validation")
            
            # Determine next steps
            if not issues:
                migration_log["next_steps"] = [
                    "Créer le service de gestion des matricules",
                    "Implémenter les endpoints API pour les matricules",
                    "Migrer les références organisationnelles",
                    "Mettre à jour le frontend pour utiliser les matricules"
                ]
            else:
                migration_log["next_steps"] = [
                    "Résoudre les problèmes d'intégrité détectés",
                    "Re-valider l'intégrité du système"
                ]
            
            # Save migration log
            log_filename = f"migration_preparation_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(log_filename, 'w', encoding='utf-8') as f:
                json.dump(migration_log, f, indent=2, ensure_ascii=False)
            
            print(f"\n📊 RÉSUMÉ DE LA PRÉPARATION")
            print("=" * 60)
            print(f"✅ Étapes complétées: {len(migration_log['steps_completed'])}")
            print(f"🔧 Corrections appliquées: {len(migration_log['fixes_applied'])}")
            print(f"⚠️  Problèmes restants: {len(migration_log['issues_found'])}")
            print(f"💾 Log sauvegardé: {log_filename}")
            
            print(f"\n🎯 PROCHAINES ÉTAPES:")
            for i, step in enumerate(migration_log["next_steps"], 1):
                print(f"   {i}. {step}")
            
            return migration_log
            
        except Exception as e:
            print(f"❌ Erreur critique lors de la préparation: {e}")
            import traceback
            traceback.print_exc()
            return None

if __name__ == "__main__":
    service = MatriculeMigrationService()
    service.run_migration_preparation()