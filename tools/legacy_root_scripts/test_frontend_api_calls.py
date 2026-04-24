#!/usr/bin/env python3
"""
Test des appels API du frontend pour vérifier qu'il n'y a plus d'erreurs 500
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_organizational_endpoints():
    """Test des endpoints organisationnels"""
    
    print("🧪 Test des endpoints organisationnels")
    print("=" * 50)
    
    # 1. Test avec un employeur valide
    print("\n1. Test avec employeur valide (ID: 1)...")
    try:
        response = requests.get(f"{BASE_URL}/organizational-structure/1/tree")
        print(f"✅ Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   - Employeur ID: {data['employer_id']}")
            print(f"   - Nombre d'unités: {data['total_units']}")
            print(f"   - Niveaux présents: {data['levels_present']}")
        else:
            print(f"❌ Erreur: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # 2. Test avec employeur inexistant
    print("\n2. Test avec employeur inexistant (ID: 999)...")
    try:
        response = requests.get(f"{BASE_URL}/organizational-structure/999/tree")
        print(f"✅ Status: {response.status_code} (404 attendu)")
        if response.status_code == 404:
            print("   - Gestion d'erreur correcte")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # 3. Test des contraintes de suppression
    print("\n3. Test des contraintes de suppression...")
    try:
        # Chercher une unité existante
        tree_response = requests.get(f"{BASE_URL}/organizational-structure/1/tree")
        if tree_response.status_code == 200:
            tree_data = tree_response.json()
            if tree_data['tree']:
                # Prendre la première unité
                first_unit = tree_data['tree'][0]
                unit_id = first_unit['id']
                
                print(f"   Test avec unité ID: {unit_id} ({first_unit['name']})")
                
                # Test can-delete
                response = requests.get(f"{BASE_URL}/organizational-structure/{unit_id}/can-delete")
                print(f"   ✅ can-delete Status: {response.status_code}")
                
                if response.status_code == 200:
                    constraints = response.json()
                    print(f"   - Peut être supprimé: {constraints['can_delete']}")
                    print(f"   - Salariés directs: {constraints['direct_workers_count']}")
                    print(f"   - Sous-structures: {constraints['children_count']}")
            else:
                print("   - Aucune unité trouvée pour tester")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # 4. Test des endpoints de base
    print("\n4. Test des endpoints de base...")
    
    endpoints_to_test = [
        "/employers",
        "/organizational-structure/1/validate",
        "/organizational-structure/1/children"
    ]
    
    for endpoint in endpoints_to_test:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            status_icon = "✅" if response.status_code < 400 else "❌"
            print(f"   {status_icon} {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"   ❌ {endpoint}: Exception - {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Test des endpoints terminé !")
    print("\n💡 Si tous les tests passent, l'erreur 500 devrait être résolue.")
    print("   Les composants React ne devraient plus faire d'appels avec des IDs invalides.")

if __name__ == "__main__":
    test_organizational_endpoints()