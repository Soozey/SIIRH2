#!/usr/bin/env python3
"""
Task 2.1: Mise à jour du modèle de données pour les matricules
Création des nouvelles tables et contraintes pour le système basé sur les matricules
"""

import sqlite3
import json
from datetime import datetime

class DataModelUpdater:
    """Service pour mettre à jour le modèle de données avec les nouvelles structures matricules"""
    
    def __init__(self, db_path="siirh-backend/siirh.db"):
        self.db_path = db_path
        self.updates_log = {
            "timestamp": datetime.now().isoformat(),
            "updates_applied": [],
            "constraints_added": [],
            "indexes_created": [],
            "errors": []
        }
    
    def connect_db(self):
        """Créer une connexion à la base de données"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def create_worker_organizational_assignments_table(self):
        """Créer la table des affectations organisationnelles par matricule"""
        print("📋 Création de la table worker_organizational_assignments...")
        
        conn = self.connect_db()
        cursor = conn.cursor()
        
        try:
            # Créer la table des affectations organisationnelles
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS worker_organizational_assignments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    worker_matricule VARCHAR(20) NOT NULL,
                    employer_id INTEGER NOT NULL,
                    organizational_unit_id INTEGER,
                    
                    -- Champs organisationnels pour compatibilité
                    etablissement VARCHAR(100),
                    departement VARCHAR(100),
                    service VARCHAR(100),
                    unite VARCHAR(100),
                    
                    -- Métadonnées
                    assignment_type VARCHAR(20) DEFAULT 'MATRICULE', -- 'MATRICULE' ou 'LEGACY'
                    is_active BOOLEAN DEFAULT 1,
                    effective_date DATE DEFAULT CURRENT_DATE,
                    end_date DATE NULL,
                    
                    -- Audit
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    created_by VARCHAR(100),
                    
                    -- Contraintes
                    FOREIGN KEY (employer_id) REFERENCES employers(id),
                    FOREIGN KEY (organizational_unit_id) REFERENCES organizational_units(id),
                    FOREIGN KEY (worker_matricule) REFERENCES matricule_name_resolver(matricule)
                )
            """)
            
            # Index pour les performances
            cursor.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS idx_worker_org_assignment_unique 
                ON worker_organizational_assignments(worker_matricule, employer_id, effective_date)
                WHERE is_active = 1
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_worker_org_assignment_matricule 
                ON worker_organizational_assignments(worker_matricule)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_worker_org_assignment_employer 
                ON worker_organizational_assignments(employer_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_worker_org_assignment_unit 
                ON worker_organizational_assignments(organizational_unit_id)
            """)
            
            conn.commit()
            
            self.updates_log["updates_applied"].append("worker_organizational_assignments_table_created")
            self.updates_log["indexes_created"].extend([
                "idx_worker_org_assignment_unique",
                "idx_worker_org_assignment_matricule", 
                "idx_worker_org_assignment_employer",
                "idx_worker_org_assignment_unit"
            ])
            
            print("   ✅ Table worker_organizational_assignments créée avec succès")
            return True
            
        except Exception as e:
            conn.rollback()
            error_msg = f"Erreur lors de la création de worker_organizational_assignments: {e}"
            print(f"   ❌ {error_msg}")
            self.updates_log["errors"].append(error_msg)
            return False
        finally:
            conn.close()
    
    def add_matricule_constraints_to_workers(self):
        """Ajouter les contraintes d'unicité sur les matricules dans la table workers"""
        print("🔒 Ajout des contraintes d'unicité sur les matricules...")
        
        conn = self.connect_db()
        cursor = conn.cursor()
        
        try:
            # Vérifier si la contrainte existe déjà
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='index' AND name='idx_workers_matricule_unique'
            """)
            
            if not cursor.fetchone():
                # Créer l'index unique sur matricule (si pas déjà existant)
                cursor.execute("""
                    CREATE UNIQUE INDEX idx_workers_matricule_unique 
                    ON workers(matricule) 
                    WHERE matricule IS NOT NULL AND matricule != ''
                """)
                
                self.updates_log["constraints_added"].append("workers_matricule_unique_constraint")
                print("   ✅ Contrainte d'unicité sur matricule ajoutée")
            else:
                print("   ℹ️  Contrainte d'unicité sur matricule déjà existante")
            
            # Ajouter un index composite pour les requêtes par employeur
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_workers_employer_matricule 
                ON workers(employer_id, matricule)
            """)
            
            self.updates_log["indexes_created"].append("idx_workers_employer_matricule")
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            error_msg = f"Erreur lors de l'ajout des contraintes matricule: {e}"
            print(f"   ❌ {error_msg}")
            self.updates_log["errors"].append(error_msg)
            return False
        finally:
            conn.close()
    
    def enhance_matricule_name_resolver(self):
        """Améliorer la table matricule_name_resolver avec des index supplémentaires"""
        print("🔍 Amélioration de la table matricule_name_resolver...")
        
        conn = self.connect_db()
        cursor = conn.cursor()
        
        try:
            # Ajouter des colonnes supplémentaires si nécessaire
            cursor.execute("PRAGMA table_info(matricule_name_resolver)")
            columns = [col[1] for col in cursor.fetchall()]
            
            # Ajouter la colonne search_vector pour la recherche textuelle si elle n'existe pas
            if 'search_vector' not in columns:
                cursor.execute("""
                    ALTER TABLE matricule_name_resolver 
                    ADD COLUMN search_vector TEXT
                """)
                
                # Remplir le search_vector avec les données existantes
                cursor.execute("""
                    UPDATE matricule_name_resolver 
                    SET search_vector = LOWER(
                        COALESCE(matricule, '') || ' ' || 
                        COALESCE(nom, '') || ' ' || 
                        COALESCE(prenom, '') || ' ' || 
                        COALESCE(full_name, '')
                    )
                """)
                
                self.updates_log["updates_applied"].append("search_vector_column_added")
                print("   ✅ Colonne search_vector ajoutée")
            
            # Créer des index pour la recherche textuelle
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_resolver_search_vector 
                ON matricule_name_resolver(search_vector)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_resolver_employer_active 
                ON matricule_name_resolver(employer_id, is_active)
            """)
            
            self.updates_log["indexes_created"].extend([
                "idx_resolver_search_vector",
                "idx_resolver_employer_active"
            ])
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            error_msg = f"Erreur lors de l'amélioration du resolver: {e}"
            print(f"   ❌ {error_msg}")
            self.updates_log["errors"].append(error_msg)
            return False
        finally:
            conn.close()
    
    def create_matricule_validation_rules_table(self):
        """Créer une table pour les règles de validation des matricules"""
        print("📏 Création de la table matricule_validation_rules...")
        
        conn = self.connect_db()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS matricule_validation_rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employer_id INTEGER NOT NULL,
                    
                    -- Règles de format
                    format_pattern VARCHAR(100) NOT NULL DEFAULT 'E{employer_id:03d}[A-Z]{2}[0-9]{3}',
                    min_length INTEGER DEFAULT 9,
                    max_length INTEGER DEFAULT 20,
                    
                    -- Règles métier
                    allow_duplicates BOOLEAN DEFAULT 0,
                    require_employer_prefix BOOLEAN DEFAULT 1,
                    case_sensitive BOOLEAN DEFAULT 1,
                    
                    -- Métadonnées
                    is_active BOOLEAN DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    
                    FOREIGN KEY (employer_id) REFERENCES employers(id),
                    UNIQUE(employer_id)
                )
            """)
            
            # Insérer une règle par défaut pour l'employeur existant
            cursor.execute("""
                INSERT OR IGNORE INTO matricule_validation_rules 
                (employer_id, format_pattern, min_length, max_length)
                SELECT DISTINCT employer_id, 'E{employer_id:03d}[A-Z]{2}[0-9]{3}', 9, 20
                FROM workers
                WHERE employer_id IS NOT NULL
            """)
            
            conn.commit()
            
            self.updates_log["updates_applied"].append("matricule_validation_rules_table_created")
            print("   ✅ Table matricule_validation_rules créée avec règles par défaut")
            return True
            
        except Exception as e:
            conn.rollback()
            error_msg = f"Erreur lors de la création des règles de validation: {e}"
            print(f"   ❌ {error_msg}")
            self.updates_log["errors"].append(error_msg)
            return False
        finally:
            conn.close()
    
    def populate_organizational_assignments(self):
        """Peupler la table des affectations avec les données existantes"""
        print("📊 Population de la table des affectations organisationnelles...")
        
        conn = self.connect_db()
        cursor = conn.cursor()
        
        try:
            # Migrer les affectations existantes depuis la table workers
            cursor.execute("""
                INSERT OR IGNORE INTO worker_organizational_assignments 
                (worker_matricule, employer_id, organizational_unit_id, 
                 etablissement, departement, service, unite, 
                 assignment_type, created_by)
                SELECT 
                    w.matricule,
                    w.employer_id,
                    w.organizational_unit_id,
                    w.etablissement,
                    w.departement,
                    w.service,
                    w.unite,
                    CASE 
                        WHEN w.organizational_unit_id IS NOT NULL THEN 'MATRICULE'
                        ELSE 'LEGACY'
                    END,
                    'MIGRATION_SCRIPT'
                FROM workers w
                WHERE w.matricule IS NOT NULL AND w.matricule != ''
            """)
            
            migrated_count = cursor.rowcount
            
            conn.commit()
            
            self.updates_log["updates_applied"].append(f"organizational_assignments_migrated_{migrated_count}")
            print(f"   ✅ {migrated_count} affectations organisationnelles migrées")
            return True
            
        except Exception as e:
            conn.rollback()
            error_msg = f"Erreur lors de la population des affectations: {e}"
            print(f"   ❌ {error_msg}")
            self.updates_log["errors"].append(error_msg)
            return False
        finally:
            conn.close()
    
    def validate_data_model_integrity(self):
        """Valider l'intégrité du nouveau modèle de données"""
        print("🔍 Validation de l'intégrité du modèle de données...")
        
        conn = self.connect_db()
        cursor = conn.cursor()
        
        try:
            validation_results = {}
            
            # 1. Vérifier que tous les workers ont des matricules
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM workers 
                WHERE matricule IS NULL OR matricule = '' OR TRIM(matricule) = ''
            """)
            validation_results["workers_without_matricule"] = cursor.fetchone()["count"]
            
            # 2. Vérifier l'unicité des matricules
            cursor.execute("""
                SELECT matricule, COUNT(*) as count
                FROM workers 
                WHERE matricule IS NOT NULL AND matricule != ''
                GROUP BY matricule
                HAVING COUNT(*) > 1
            """)
            validation_results["duplicate_matricules"] = cursor.fetchall()
            
            # 3. Vérifier la cohérence du resolver
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM workers w
                LEFT JOIN matricule_name_resolver r ON w.matricule = r.matricule
                WHERE w.matricule IS NOT NULL AND w.matricule != '' AND r.matricule IS NULL
            """)
            validation_results["resolver_missing_entries"] = cursor.fetchone()["count"]
            
            # 4. Vérifier les affectations organisationnelles
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM worker_organizational_assignments
            """)
            validation_results["organizational_assignments_count"] = cursor.fetchone()["count"]
            
            # 5. Vérifier les contraintes de clés étrangères
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM worker_organizational_assignments woa
                LEFT JOIN matricule_name_resolver r ON woa.worker_matricule = r.matricule
                WHERE r.matricule IS NULL
            """)
            validation_results["invalid_foreign_keys"] = cursor.fetchone()["count"]
            
            # Afficher les résultats
            print(f"   📊 Résultats de validation:")
            print(f"     - Workers sans matricule: {validation_results['workers_without_matricule']}")
            print(f"     - Matricules dupliqués: {len(validation_results['duplicate_matricules'])}")
            print(f"     - Entrées resolver manquantes: {validation_results['resolver_missing_entries']}")
            print(f"     - Affectations organisationnelles: {validation_results['organizational_assignments_count']}")
            print(f"     - Clés étrangères invalides: {validation_results['invalid_foreign_keys']}")
            
            # Déterminer si la validation est réussie
            is_valid = (
                validation_results["workers_without_matricule"] == 0 and
                len(validation_results["duplicate_matricules"]) == 0 and
                validation_results["resolver_missing_entries"] == 0 and
                validation_results["invalid_foreign_keys"] == 0
            )
            
            if is_valid:
                print("   ✅ Validation d'intégrité réussie")
            else:
                print("   ⚠️  Problèmes d'intégrité détectés")
            
            self.updates_log["validation_results"] = validation_results
            return is_valid
            
        except Exception as e:
            error_msg = f"Erreur lors de la validation: {e}"
            print(f"   ❌ {error_msg}")
            self.updates_log["errors"].append(error_msg)
            return False
        finally:
            conn.close()
    
    def run_data_model_update(self):
        """Exécuter toutes les mises à jour du modèle de données"""
        print("🚀 DÉMARRAGE DE LA MISE À JOUR DU MODÈLE DE DONNÉES")
        print("=" * 70)
        
        success_count = 0
        total_steps = 6
        
        try:
            # Étape 1: Créer la table des affectations organisationnelles
            print(f"\n📋 ÉTAPE 1/{total_steps}: Création de la table des affectations")
            if self.create_worker_organizational_assignments_table():
                success_count += 1
            
            # Étape 2: Ajouter les contraintes sur les matricules
            print(f"\n📋 ÉTAPE 2/{total_steps}: Ajout des contraintes matricules")
            if self.add_matricule_constraints_to_workers():
                success_count += 1
            
            # Étape 3: Améliorer le resolver
            print(f"\n📋 ÉTAPE 3/{total_steps}: Amélioration du resolver")
            if self.enhance_matricule_name_resolver():
                success_count += 1
            
            # Étape 4: Créer les règles de validation
            print(f"\n📋 ÉTAPE 4/{total_steps}: Création des règles de validation")
            if self.create_matricule_validation_rules_table():
                success_count += 1
            
            # Étape 5: Peupler les affectations
            print(f"\n📋 ÉTAPE 5/{total_steps}: Population des affectations")
            if self.populate_organizational_assignments():
                success_count += 1
            
            # Étape 6: Validation finale
            print(f"\n📋 ÉTAPE 6/{total_steps}: Validation d'intégrité")
            if self.validate_data_model_integrity():
                success_count += 1
            
            # Sauvegarder le log
            log_filename = f"data_model_update_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(log_filename, 'w', encoding='utf-8') as f:
                json.dump(self.updates_log, f, indent=2, ensure_ascii=False)
            
            print(f"\n📊 RÉSUMÉ DE LA MISE À JOUR")
            print("=" * 70)
            print(f"✅ Étapes réussies: {success_count}/{total_steps}")
            print(f"🔧 Mises à jour appliquées: {len(self.updates_log['updates_applied'])}")
            print(f"🔒 Contraintes ajoutées: {len(self.updates_log['constraints_added'])}")
            print(f"📇 Index créés: {len(self.updates_log['indexes_created'])}")
            print(f"❌ Erreurs: {len(self.updates_log['errors'])}")
            print(f"💾 Log sauvegardé: {log_filename}")
            
            if success_count == total_steps:
                print(f"\n🎉 MISE À JOUR DU MODÈLE DE DONNÉES TERMINÉE AVEC SUCCÈS!")
                return True
            else:
                print(f"\n⚠️  MISE À JOUR PARTIELLEMENT RÉUSSIE")
                return False
                
        except Exception as e:
            print(f"❌ Erreur critique lors de la mise à jour: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    updater = DataModelUpdater()
    updater.run_data_model_update()