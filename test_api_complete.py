"""
Test complet de l'API hiérarchique organisationnelle
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_api():
    print("=" * 60)
    print("TEST COMPLET DE L'API HIÉRARCHIQUE")
    print("=" * 60)
    
    # Test 1: Health check
    print("\n1. Health Check")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ API accessible")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return
    
    # Test 2: Get employers
    print("\n2. Liste des employeurs")
    try:
        response = requests.get(f"{BASE_URL}/employers")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            employers = response.json()
            print(f"   ✅ {len(employers)} employeurs trouvés")
            if employers:
                employer_id = employers[0]['id']
                print(f"   Utilisation de l'employeur ID: {employer_id}")
            else:
                print("   ❌ Aucun employeur trouvé")
                return
        else:
            print(f"   ❌ Erreur: {response.text}")
            return
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return
    
    # Test 3: Get organizational tree
    print("\n3. Arbre organisationnel")
    try:
        response = requests.get(f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/tree")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            tree = response.json()
            print(f"   ✅ Arbre récupéré: {tree.get('total_count', 0)} nœuds")
            print(f"   Nœuds racine: {len(tree.get('nodes', []))}")
        else:
            print(f"   ❌ Erreur: {response.text}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Test 4: Get cascading options (établissements)
    print("\n4. Options en cascade - Établissements")
    try:
        response = requests.get(f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/cascading-options")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            options = response.json()
            print(f"   ✅ {len(options)} établissements trouvés")
            if options:
                etablissement_id = options[0]['id']
                print(f"   Premier établissement: {options[0]['name']} (ID: {etablissement_id})")
                
                # Test 5: Get cascading options (départements)
                print("\n5. Options en cascade - Départements")
                response = requests.get(
                    f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/cascading-options",
                    params={"parent_id": etablissement_id}
                )
                print(f"   Status: {response.status_code}")
                if response.status_code == 200:
                    dept_options = response.json()
                    print(f"   ✅ {len(dept_options)} départements trouvés")
                    if dept_options:
                        departement_id = dept_options[0]['id']
                        print(f"   Premier département: {dept_options[0]['name']} (ID: {departement_id})")
                        
                        # Test 6: Get cascading options (services)
                        print("\n6. Options en cascade - Services")
                        response = requests.get(
                            f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/cascading-options",
                            params={"parent_id": departement_id}
                        )
                        print(f"   Status: {response.status_code}")
                        if response.status_code == 200:
                            service_options = response.json()
                            print(f"   ✅ {len(service_options)} services trouvés")
                            if service_options:
                                service_id = service_options[0]['id']
                                print(f"   Premier service: {service_options[0]['name']} (ID: {service_id})")
                                
                                # Test 7: Validate path
                                print("\n7. Validation du chemin organisationnel")
                                response = requests.post(
                                    f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/validate-path",
                                    json={
                                        "etablissement_id": etablissement_id,
                                        "departement_id": departement_id,
                                        "service_id": service_id,
                                        "unite_id": None
                                    }
                                )
                                print(f"   Status: {response.status_code}")
                                if response.status_code == 200:
                                    validation = response.json()
                                    if validation['is_valid']:
                                        print(f"   ✅ Chemin valide")
                                    else:
                                        print(f"   ❌ Chemin invalide: {validation['errors']}")
                                else:
                                    print(f"   ❌ Erreur: {response.text}")
                        else:
                            print(f"   ❌ Erreur: {response.text}")
                else:
                    print(f"   ❌ Erreur: {response.text}")
        else:
            print(f"   ❌ Erreur: {response.text}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Test 8: Get nodes by level
    print("\n8. Récupération par niveau")
    for level in ['etablissement', 'departement', 'service', 'unite']:
        try:
            response = requests.get(f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/levels/{level}")
            print(f"   {level}: Status {response.status_code}", end="")
            if response.status_code == 200:
                nodes = response.json()
                print(f" - {len(nodes)} nœuds ✅")
            else:
                print(f" - Erreur ❌")
        except Exception as e:
            print(f"   {level}: Erreur - {e}")
    
    # Test 9: Search
    print("\n9. Recherche")
    try:
        response = requests.get(
            f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/search",
            params={"query": "a"}
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            results = response.json()
            print(f"   ✅ {len(results)} résultats trouvés")
        else:
            print(f"   ❌ Erreur: {response.text}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Test 10: Create node (test)
    print("\n10. Test de création de nœud")
    try:
        response = requests.post(
            f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/nodes",
            json={
                "parent_id": None,
                "level": "etablissement",
                "name": "Test Établissement API",
                "code": "TEST_API",
                "description": "Test de création via API",
                "sort_order": 999
            }
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            node = response.json()
            print(f"   ✅ Nœud créé: {node['name']} (ID: {node['id']})")
            
            # Test 11: Update node
            print("\n11. Test de mise à jour")
            response = requests.put(
                f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/nodes/{node['id']}",
                json={
                    "name": "Test Établissement API Modifié",
                    "description": "Description mise à jour"
                }
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                updated_node = response.json()
                print(f"   ✅ Nœud mis à jour: {updated_node['name']}")
            else:
                print(f"   ❌ Erreur: {response.text}")
            
            # Test 12: Delete node
            print("\n12. Test de suppression")
            response = requests.delete(
                f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/nodes/{node['id']}"
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   ✅ Nœud supprimé")
            else:
                print(f"   ❌ Erreur: {response.text}")
        else:
            print(f"   ❌ Erreur de création: {response.text}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    print("\n" + "=" * 60)
    print("TESTS TERMINÉS")
    print("=" * 60)

if __name__ == "__main__":
    test_api()
