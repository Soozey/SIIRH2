#!/usr/bin/env python3
"""
Création des tables matricules dans PostgreSQL
Task 7: Finalisation de l'intégration API
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'siirh-backend'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json

# Configuration PostgreSQL
DATABASE_URL = "postgresql+psycopg2://postgres:tantely123@127.0.0.1:5432/db_siirh_app"

def create_matricule_tables():
    """Créer les tables matricules dans PostgreSQL"""
    
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        print("🚀 CRÉATION DES TABLES MATRICULES DANS POSTGRESQL")
        print("=" * 60)
        
        # 1. Créer la table matricule_name_resolver
        print("\n📋 ÉTAPE 1: Création de matricule_name_resolver")
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS matricule_name_resolver (
                id SERIAL PRIMARY KEY,
                matricule VARCHAR(20) UNIQUE NOT NULL,
                worker_id INTEGER NOT NULL,
                full_name VARCHAR(200) NOT NULL,
                employer_id INTEGER NOT NULL,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                search_vector TEXT,
                FOREIGN KEY (worker_id) REFERENCES workers(id),
                FOREIGN KEY (employer_id) REFERENCES employers(id)
            )
        """))
        print("   ✅ Table matricule_name_resolver créée")
        
        # 2. Créer la table worker_organizational_assignments
        print("\n📋 ÉTAPE 2: Création de worker_organizational_assignments")
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS worker_organizational_assignments (
                id SERIAL PRIMARY KEY,
                worker_matricule VARCHAR(20) NOT NULL,
                employer_id INTEGER NOT NULL,
                organizational_unit_id INTEGER,
                etablissement VARCHAR(100),
                departement VARCHAR(100),
                service VARCHAR(100),
                unite VARCHAR(100),
                assignment_type VARCHAR(50) DEFAULT 'MATRICULE',
                is_active INTEGER DEFAULT 1,
                effective_date DATE DEFAULT CURRENT_DATE,
                end_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                deactivated_at TIMESTAMP,
                FOREIGN KEY (employer_id) REFERENCES employers(id)
            )
        """))
        print("   ✅ Table worker_organizational_assignments créée")
        
        # 3. Créer la table matricule_audit_trail
        print("\n📋 ÉTAPE 3: Création de matricule_audit_trail")
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS matricule_audit_trail (
                id SERIAL PRIMARY KEY,
                worker_id INTEGER NOT NULL,
                old_matricule VARCHAR(20),
                new_matricule VARCHAR(20),
                change_type VARCHAR(50) NOT NULL,
                change_reason TEXT,
                changed_by VARCHAR(100),
                changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT,
                FOREIGN KEY (worker_id) REFERENCES workers(id)
            )
        """))
        print("   ✅ Table matricule_audit_trail créée")
        
        # 4. Créer la table matricule_validation_rules
        print("\n📋 ÉTAPE 4: Création de matricule_validation_rules")
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS matricule_validation_rules (
                id SERIAL PRIMARY KEY,
                rule_name VARCHAR(100) NOT NULL,
                rule_pattern VARCHAR(200),
                min_length INTEGER DEFAULT 6,
                max_length INTEGER DEFAULT 20,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        print("   ✅ Table matricule_validation_rules créée")
        
        # 5. Peupler matricule_name_resolver avec les données existantes
        print("\n📋 ÉTAPE 5: Population de matricule_name_resolver")
        
        # Récupérer les workers avec matricules
        workers = db.execute(text("""
            SELECT id, matricule, nom, prenom, employer_id 
            FROM workers 
            WHERE matricule IS NOT NULL AND matricule != ''
        """)).fetchall()
        
        inserted_count = 0
        for worker in workers:
            full_name = f"{worker.nom} {worker.prenom}".strip()
            
            # Vérifier si l'entrée existe déjà
            existing = db.execute(text("""
                SELECT id FROM matricule_name_resolver 
                WHERE matricule = :matricule
            """), {"matricule": worker.matricule}).fetchone()
            
            if not existing:
                db.execute(text("""
                    INSERT INTO matricule_name_resolver 
                    (matricule, worker_id, full_name, employer_id, search_vector)
                    VALUES (:matricule, :worker_id, :full_name, :employer_id, :search_vector)
                """), {
                    "matricule": worker.matricule,
                    "worker_id": worker.id,
                    "full_name": full_name,
                    "employer_id": worker.employer_id,
                    "search_vector": f"{worker.matricule} {full_name}".lower()
                })
                inserted_count += 1
        
        print(f"   ✅ {inserted_count} entrées ajoutées à matricule_name_resolver")
        
        # 6. Peupler worker_organizational_assignments
        print("\n📋 ÉTAPE 6: Population de worker_organizational_assignments")
        
        # Migrer les affectations existantes depuis workers
        assignments = db.execute(text("""
            SELECT w.matricule, w.employer_id, w.etablissement, w.departement, w.service, w.unite
            FROM workers w
            WHERE w.matricule IS NOT NULL 
            AND (w.etablissement IS NOT NULL OR w.departement IS NOT NULL 
                 OR w.service IS NOT NULL OR w.unite IS NOT NULL)
        """)).fetchall()
        
        assignment_count = 0
        for assignment in assignments:
            # Vérifier si l'affectation existe déjà
            existing = db.execute(text("""
                SELECT id FROM worker_organizational_assignments 
                WHERE worker_matricule = :matricule AND is_active = 1
            """), {"matricule": assignment.matricule}).fetchone()
            
            if not existing:
                db.execute(text("""
                    INSERT INTO worker_organizational_assignments 
                    (worker_matricule, employer_id, etablissement, departement, service, unite)
                    VALUES (:matricule, :employer_id, :etablissement, :departement, :service, :unite)
                """), {
                    "matricule": assignment.matricule,
                    "employer_id": assignment.employer_id,
                    "etablissement": assignment.etablissement,
                    "departement": assignment.departement,
                    "service": assignment.service,
                    "unite": assignment.unite
                })
                assignment_count += 1
        
        print(f"   ✅ {assignment_count} affectations organisationnelles créées")
        
        # 7. Créer les index pour les performances
        print("\n📋 ÉTAPE 7: Création des index")
        
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_matricule_resolver_matricule ON matricule_name_resolver(matricule)",
            "CREATE INDEX IF NOT EXISTS idx_matricule_resolver_worker ON matricule_name_resolver(worker_id)",
            "CREATE INDEX IF NOT EXISTS idx_matricule_resolver_search ON matricule_name_resolver(search_vector)",
            "CREATE INDEX IF NOT EXISTS idx_assignments_matricule ON worker_organizational_assignments(worker_matricule)",
            "CREATE INDEX IF NOT EXISTS idx_assignments_active ON worker_organizational_assignments(is_active)",
            "CREATE INDEX IF NOT EXISTS idx_audit_worker ON matricule_audit_trail(worker_id)",
            "CREATE INDEX IF NOT EXISTS idx_audit_date ON matricule_audit_trail(changed_at)"
        ]
        
        for index_sql in indexes:
            db.execute(text(index_sql))
        
        print(f"   ✅ {len(indexes)} index créés")
        
        # 8. Validation finale
        print("\n📋 ÉTAPE 8: Validation finale")
        
        # Compter les enregistrements
        resolver_count = db.execute(text("SELECT COUNT(*) FROM matricule_name_resolver")).scalar()
        assignments_count = db.execute(text("SELECT COUNT(*) FROM worker_organizational_assignments")).scalar()
        workers_count = db.execute(text("SELECT COUNT(*) FROM workers WHERE matricule IS NOT NULL")).scalar()
        
        print(f"   📊 Matricule resolver: {resolver_count} entrées")
        print(f"   📊 Affectations organisationnelles: {assignments_count} entrées")
        print(f"   📊 Workers avec matricules: {workers_count} entrées")
        
        # Commit toutes les modifications
        db.commit()
        
        print("\n🎉 CRÉATION DES TABLES MATRICULES TERMINÉE!")
        print("✅ Toutes les tables sont créées et peuplées")
        print("✅ Les index sont en place pour les performances")
        print("✅ Le système est prêt pour les API matricules")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la création des tables: {e}")
        db.rollback()
        return False
        
    finally:
        db.close()

if __name__ == "__main__":
    success = create_matricule_tables()
    
    # Sauvegarder le résultat
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "operation": "create_matricule_tables_postgresql",
        "success": success,
        "database": "postgresql"
    }
    
    with open(f"matricule_tables_creation_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "w") as f:
        json.dump(log_data, f, indent=2)
    
    if success:
        print(f"\n💾 Log sauvegardé: matricule_tables_creation_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        print("\n🚀 PRÊT POUR LES TESTS API!")
    else:
        print("\n❌ Échec de la création des tables. Vérifiez les logs.")