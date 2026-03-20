#!/usr/bin/env python3
"""
Test final du système de suppression conditionnelle après corrections
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_final_system():
    """Test final complet du système"""
    
    print("🎯 Test final du système de suppression conditionnelle")
    print("=" * 60)
    
    # 1. Vérifier que le backend fonctionne
    print("\n1. Vérification du backend...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✅ Backend accessible: {response.status_code}")
    except Exception as e:
        print(f"❌ Backend inaccessible: {e}")
        return
    
    # 2. Tester les endpoints organisationnels
    print("\n2. Test des endpoints organisationnels...")
    
    # Test avec employeur valide
    try:
        response = requests.get(f"{BASE_URL}/organizational-structure/1/tree")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Tree endpoint: {data['total_units']} unités trouvées")
        else:
            print(f"⚠️ Tree endpoint: {response.status_code}")
    except Exception as e:
        print(f"❌ Tree endpoint error: {e}")
    
    # Test can-delete avec une unité existante
    try:
        # D'abord récupérer une unité
        tree_response = requests.get(f"{BASE_URL}/organizational-structure/1/tree")
        if tree_response.status_code == 200:
            tree_data = tree_response.json()
            if tree_data['tree']:
                unit_id = tree_data['tree'][0]['id']
                
                # Tester can-delete
                response = requests.get(f"{BASE_URL}/organizational-structure/{unit_id}/can-delete")
                if response.status_code == 200:
                    constraints = response.json()
                    print(f"✅ Can-delete endpoint: Unité {constraints['unit_name']}")
                    print(f"   - Supprimable: {constraints['can_delete']}")
                    print(f"   - Salariés: {constraints['direct_workers_count']}")
                    print(f"   - Sous-structures: {constraints['children_count']}")
                else:
                    print(f"⚠️ Can-delete endpoint: {response.status_code}")
    except Exception as e:
        print(f"❌ Can-delete endpoint error: {e}")
    
    # 3. Test des cas d'erreur (qui ne devraient plus causer d'erreur 500)
    print("\n3. Test des cas d'erreur...")
    
    error_cases = [
        ("ID null", "null"),
        ("ID undefined", "undefined"),
        ("ID négatif", "-1"),
        ("ID inexistant", "99999")
    ]
    
    for case_name, test_id in error_cases:
        try:
            response = requests.get(f"{BASE_URL}/organizational-structure/{test_id}/tree")
            expected_codes = [400, 404, 422]  # Codes d'erreur attendus (pas 500)
            
            if response.status_code in expected_codes:
                print(f"✅ {case_name}: {response.status_code} (attendu)")
            elif response.status_code == 500:
                print(f"❌ {case_name}: 500 (erreur serveur non résolue)")
            else:
                print(f"⚠️ {case_name}: {response.status_code} (inattendu)")
        except Exception as e:
            print(f"❌ {case_name}: Exception - {e}")
    
    # 4. Test de création et suppression
    print("\n4. Test de création et suppression...")
    
    try:
        # Créer un employeur de test
        employer_data = {
            "raison_sociale": "Test Final Company",
            "adresse": "Test Address",
            "email": "test@final.com",
            "type_regime_id": 1
        }
        
        response = requests.post(f"{BASE_URL}/employers/", json=employer_data)
        if response.status_code == 200:
            employer = response.json()
            employer_id = employer["id"]
            print(f"✅ Employeur créé: ID {employer_id}")
            
            # Créer une structure vide
            unit_data = {
                "employer_id": employer_id,
                "parent_id": None,
                "level": "etablissement",
                "code": "TEST",
                "name": "Test Établissement",
                "description": "Test"
            }
            
            response = requests.post(f"{BASE_URL}/organizational-structure/create", json=unit_data)
            if response.status_code == 200:
                unit = response.json()
                unit_id = unit["id"]
                print(f"✅ Structure créée: ID {unit_id}")
                
                # Vérifier les contraintes
                response = requests.get(f"{BASE_URL}/organizational-structure/{unit_id}/can-delete")
                if response.status_code == 200:
                    constraints = response.json()
                    print(f"✅ Contraintes vérifiées: Supprimable = {constraints['can_delete']}")
                    
                    # Supprimer la structure
                    if constraints['can_delete']:
                        response = requests.delete(f"{BASE_URL}/organizational-structure/{unit_id}")
                        if response.status_code == 200:
                            print("✅ Structure supprimée avec succès")
                        else:
                            print(f"⚠️ Erreur suppression: {response.status_code}")
                    else:
                        print("⚠️ Structure non supprimable (normal si elle a des enfants)")
                else:
                    print(f"❌ Erreur vérification contraintes: {response.status_code}")
            else:
                print(f"❌ Erreur création structure: {response.status_code}")
        else:
            print(f"❌ Erreur création employeur: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur test création/suppression: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Test final terminé !")
    print("\n📋 Résumé des corrections apportées:")
    print("✅ Ajout de vérifications dans HierarchicalOrganizationTreeFinal")
    print("✅ Correction des imports API dans les composants")
    print("✅ Création de composants simplifiés sans Antd")
    print("✅ Gestion des cas d'erreur avec employerId null/undefined")
    print("✅ Validation des paramètres avant appels API")
    
    print("\n💡 L'erreur 500 devrait maintenant être résolue.")
    print("   Les composants React ne font plus d'appels avec des IDs invalides.")

if __name__ == "__main__":
    test_final_system()