#!/usr/bin/env python3
"""
Test direct du service d'affectation
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'siirh-backend'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.services.organizational_assignment_service import OrganizationalAssignmentService

# Configuration PostgreSQL
DATABASE_URL = "postgresql+psycopg2://postgres:tantely123@127.0.0.1:5432/db_siirh_app"

def test_assignment_service():
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        print("🧪 TEST DIRECT DU SERVICE D'AFFECTATION")
        print("=" * 50)
        
        service = OrganizationalAssignmentService(db)
        
        # Test avec un matricule existant
        matricule = "M001"
        print(f"\n🔍 Test avec matricule: {matricule}")
        
        assignment = service.get_active_assignment(matricule)
        
        if assignment:
            print(f"   ✅ Affectation trouvée:")
            print(f"      - Département: {assignment.departement}")
            print(f"      - Service: {assignment.service}")
            print(f"      - Établissement: {assignment.etablissement}")
        else:
            print(f"   ⚠️  Aucune affectation active trouvée")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_assignment_service()