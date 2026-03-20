#!/usr/bin/env python3
import sys
sys.path.append('siirh-backend')

from app.config.config import get_db
from app.models import Employer, TypeRegime
from sqlalchemy.orm import Session

def test_db_connection():
    print("Testing database connection...")
    
    try:
        # Get database session
        db_gen = get_db()
        db: Session = next(db_gen)
        
        print("✅ Database connection successful")
        
        # Test query
        employers = db.query(Employer).limit(5).all()
        print(f"✅ Found {len(employers)} employers in database")
        
        # Test type regimes
        type_regimes = db.query(TypeRegime).all()
        print(f"✅ Found {len(type_regimes)} type regimes")
        for tr in type_regimes:
            print(f"   - {tr.id}: {tr.label} (VHM: {tr.vhm})")
        
        # Test creating a simple employer object (without saving)
        test_data = {
            'raison_sociale': 'Test',
            'type_etab': 'general',
            'taux_pat_cnaps': 13.0,
            'etablissements': '[]',
            'departements': '[]',
            'services': '[]',
            'unites': '[]'
        }
        
        test_employer = Employer(**test_data)
        print("✅ Employer object created successfully")
        print(f"   - Raison sociale: {test_employer.raison_sociale}")
        print(f"   - Type etab: {test_employer.type_etab}")
        print(f"   - Taux CNaPS: {test_employer.taux_pat_cnaps}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_db_connection()