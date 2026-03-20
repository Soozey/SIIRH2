#!/usr/bin/env python3
"""
Ajouter les colonnes manquantes à la table worker_organizational_assignments
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'siirh-backend'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Configuration PostgreSQL
DATABASE_URL = "postgresql+psycopg2://postgres:tantely123@127.0.0.1:5432/db_siirh_app"

def fix_assignment_table():
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        print("🔧 AJOUT DES COLONNES MANQUANTES")
        print("=" * 40)
        
        # Ajouter les colonnes manquantes
        columns_to_add = [
            ("assignment_type", "VARCHAR(50) DEFAULT 'MATRICULE'"),
            ("effective_date", "DATE DEFAULT CURRENT_DATE"),
            ("end_date", "DATE")
        ]
        
        for column_name, column_def in columns_to_add:
            try:
                db.execute(text(f"""
                    ALTER TABLE worker_organizational_assignments 
                    ADD COLUMN IF NOT EXISTS {column_name} {column_def}
                """))
                print(f"   ✅ Colonne {column_name} ajoutée")
            except Exception as e:
                if "already exists" in str(e).lower():
                    print(f"   ℹ️  Colonne {column_name} existe déjà")
                else:
                    print(f"   ❌ Erreur pour {column_name}: {e}")
        
        db.commit()
        print("\n✅ Colonnes ajoutées avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_assignment_table()