"""
Test d'intégration frontend-backend pour l'API hiérarchique
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_frontend_integration():
    print("=" * 60)
    print("TEST D'INTÉGRATION FRONTEND-BACKEND")
    print("=" * 60)
    
    # Simuler les appels du frontend
    employer_id = 1
    
    # 1. Récupérer l'arbre complet (pour HierarchicalOrganizationTree)
    print("\n1. GET /employers/{employer_id}/hierarchical-organization/tree")
    response = requests.get(f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/tree")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Arbre récupéré: {data.get('total_count', 0)} nœuds")
        print(f"   Structure: {json.dumps(data, indent=2)[:500]}...")
    else:
        print(f"   ❌ Erreur: {response.text}")
    
    # 2. Récupérer les établissements (pour CascadingOrganizationalSelect)
    print("\n2. GET /employers/{employer_id}/hierarchical-organization/cascading-options")
    response = requests.get(f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/cascading-options")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        etablissements = response.json()
        print(f"   ✅ {len(etablissements)} établissements")
        if etablissements:
            print(f"   Premier: {etablissements[0]}")
            etablissement_id = etablissements[0]['id']
            
            # 3. Récupérer les départements
            print("\n3. GET cascading-options?parent_id={etablissement_id}")
            response = requests.get(
                f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/cascading-options",
                params={"parent_id": etablissement_id}
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                departements = response.json()
                print(f"   ✅ {len(departements)} départements")
                if departements:
                    print(f"   Premier: {departements[0]}")
    else:
        print(f"   ❌ Erreur: {response.text}")
    
    # 4. Test de création (pour HierarchyManagerModal)
    print("\n4. POST /employers/{employer_id}/hierarchical-organization/nodes")
    new_node = {
        "parent_id": None,
        "level": "etablissement",
        "name": "Test Frontend Integration",
        "code": "TEST_FE",
        "description": "Test d'intégration frontend",
        "sort_order": 999
    }
    response = requests.post(
        f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/nodes",
        json=new_node
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        created = response.json()
        print(f"   ✅ Nœud créé: {created['name']} (ID: {created['id']})")
        node_id = created['id']
        
        # 5. Test de mise à jour
        print("\n5. PUT /employers/{employer_id}/hierarchical-organization/nodes/{node_id}")
        update_data = {
            "name": "Test Frontend Integration Updated",
            "description": "Description mise à jour"
        }
        response = requests.put(
            f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/nodes/{node_id}",
            json=update_data
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            updated = response.json()
            print(f"   ✅ Nœud mis à jour: {updated['name']}")
        else:
            print(f"   ❌ Erreur: {response.text}")
        
        # 6. Test de suppression
        print("\n6. DELETE /employers/{employer_id}/hierarchical-organization/nodes/{node_id}")
        response = requests.delete(
            f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/nodes/{node_id}"
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ Nœud supprimé")
        else:
            print(f"   ❌ Erreur: {response.text}")
    else:
        print(f"   ❌ Erreur de création: {response.text}")
    
    # 7. Test de validation de chemin
    print("\n7. POST /employers/{employer_id}/hierarchical-organization/validate-path")
    validation_data = {
        "etablissement_id": 1,
        "departement_id": 2,
        "service_id": None,
        "unite_id": None
    }
    response = requests.post(
        f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/validate-path",
        json=validation_data
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        if result['is_valid']:
            print(f"   ✅ Chemin valide")
        else:
            print(f"   ⚠️ Chemin invalide: {result['errors']}")
    else:
        print(f"   ❌ Erreur: {response.text}")
    
    # 8. Test de recherche
    print("\n8. GET /employers/{employer_id}/hierarchical-organization/search?query=test")
    response = requests.get(
        f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/search",
        params={"query": "test"}
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        results = response.json()
        print(f"   ✅ {len(results)} résultats trouvés")
    else:
        print(f"   ❌ Erreur: {response.text}")
    
    # 9. Test de récupération par niveau
    print("\n9. GET /employers/{employer_id}/hierarchical-organization/levels/etablissement")
    response = requests.get(
        f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/levels/etablissement"
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        nodes = response.json()
        print(f"   ✅ {len(nodes)} établissements trouvés")
    else:
        print(f"   ❌ Erreur: {response.text}")
    
    print("\n" + "=" * 60)
    print("TESTS D'INTÉGRATION TERMINÉS")
    print("=" * 60)

if __name__ == "__main__":
    test_frontend_integration()
