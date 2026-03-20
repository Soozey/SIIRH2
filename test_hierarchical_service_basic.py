#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'siirh-backend'))

from app.config.config import SessionLocal
from app.services.hierarchical_organizational_service import HierarchicalOrganizationalService
from app.models import OrganizationalNode, Employer

def test_basic_hierarchical_service():
    """Test basique du service hiérarchique"""
    
    db = SessionLocal()
    
    try:
        # Créer le service
        service = HierarchicalOrganizationalService(db)
        print("✅ Service hiérarchique créé")
        
        # Vérifier qu'on a au moins un employeur
        employer = db.query(Employer).first()
        if not employer:
            print("❌ Aucun employeur trouvé dans la base")
            return False
        
        print(f"✅ Employeur trouvé: {employer.raison_sociale} (ID: {employer.id})")
        
        # Tester la récupération de l'arbre (vide pour l'instant)
        tree = service.get_organizational_tree(employer.id)
        print(f"✅ Arbre récupéré: {len(tree)} nœuds")
        
        # Tester les options en cascade (vide pour l'instant)
        options = service.get_cascading_options(employer.id)
        print(f"✅ Options cascade récupérées: {len(options)} options")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        db.close()

if __name__ == "__main__":
    success = test_basic_hierarchical_service()
    print(f"\n{'✅ Test réussi' if success else '❌ Test échoué'}")
    sys.exit(0 if success else 1)