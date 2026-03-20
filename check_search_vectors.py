#!/usr/bin/env python3
"""
Vérifier les search_vectors dans la base
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'siirh-backend'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Configuration PostgreSQL
DATABASE_URL = "postgresql+psycopg2://postgres:tantely123@127.0.0.1:5432/db_siirh_app"

def check_search_vectors():
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        print("🔍 SEARCH VECTORS DANS LA BASE")
        print("=" * 50)
        
        entries = db.execute(text("""
            SELECT matricule, full_name, search_vector 
            FROM matricule_name_resolver 
            WHERE is_active = 1
            ORDER BY matricule
        """)).fetchall()
        
        for entry in entries:
            print(f"Matricule: {entry.matricule}")
            print(f"Nom: {entry.full_name}")
            print(f"Search Vector: '{entry.search_vector}'")
            print("-" * 30)
        
        # Test de recherche directe
        print("\n🧪 TEST DE RECHERCHE DIRECTE")
        print("=" * 30)
        
        test_terms = ["jean", "rakoto", "souzzy"]
        for term in test_terms:
            pattern = f"%{term}%"
            results = db.execute(text("""
                SELECT matricule, full_name 
                FROM matricule_name_resolver 
                WHERE LOWER(full_name) LIKE :pattern AND is_active = 1
            """), {"pattern": pattern}).fetchall()
            
            print(f"Recherche '{term}': {len(results)} résultats")
            for result in results:
                print(f"   - {result.matricule}: {result.full_name}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_search_vectors()