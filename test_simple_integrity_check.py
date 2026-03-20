#!/usr/bin/env python3
"""
Test simple du service d'intégrité - Vérification de base
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'siirh-backend'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def test_simple_integrity():
    """Test simple de la base de données"""
    
    # Configuration de la base de données
    DATABASE_URL = "postgresql://siirh_user:siirh_password@localhost:5432/siirh_db"
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    print("🔍 Test simple d'intégrité")
    print("=" * 40)
    
    with SessionLocal() as db:
        
        # Test 1: Compter les workers
        try:
            result = db.execute(text("SELECT COUNT(*) as count FROM workers"))
            count = result.fetchone().count
            print(f"✅ Total workers: {count}")
        except Exception as e:
            print(f"❌ Erreur count workers: {e}")
        
        # Test 2: Vérifier les matricules
        try:
            result = db.execute(text("""
                SELECT COUNT(*) as total,
                       COUNT(CASE WHEN matricule IS NOT NULL AND matricule != '' THEN 1 END) as with_matricule,
                       COUNT(CASE WHEN matricule IS NULL OR matricule = '' THEN 1 END) as without_matricule
                FROM workers
            """))
            stats = result.fetchone()
            print(f"✅ Matricules - Total: {stats.total}, Avec: {stats.with_matricule}, Sans: {stats.without_matricule}")
        except Exception as e:
            print(f"❌ Erreur stats matricules: {e}")
        
        # Test 3: Vérifier les tables
        try:
            tables = ['workers', 'matricule_name_resolver', 'worker_organizational_assignments', 'matricule_audit_trail']
            for table in tables:
                try:
                    result = db.execute(text(f"SELECT COUNT(*) as count FROM {table}"))
                    count = result.fetchone().count
                    print(f"✅ Table {table}: {count} entrées")
                except Exception as e:
                    print(f"⚠️  Table {table}: {e}")
        except Exception as e:
            print(f"❌ Erreur vérification tables: {e}")
        
        # Test 4: Vérifier l'encodage
        try:
            result = db.execute(text("SELECT id, matricule FROM workers LIMIT 5"))
            workers = result.fetchall()
            print(f"✅ Échantillon workers:")
            for w in workers:
                print(f"   ID: {w.id}, Matricule: {w.matricule}")
        except Exception as e:
            print(f"❌ Erreur échantillon: {e}")

if __name__ == "__main__":
    test_simple_integrity()