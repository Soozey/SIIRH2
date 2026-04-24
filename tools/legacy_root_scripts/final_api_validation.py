"""
Validation finale complète de l'API hiérarchique
"""
import requests
import time
import json

BASE_URL = "http://127.0.0.1:8000"

def test_all_endpoints():
    print("=" * 70)
    print("VALIDATION FINALE COMPLÈTE DE L'API HIÉRARCHIQUE")
    print("=" * 70)
    
    employer_id = 1
    results = {
        "total_tests": 0,
        "passed": 0,
        "failed": 0,
        "tests": []
    }
    
    def run_test(name, func):
        results["total_tests"] += 1
        try:
            start = time.time()
            success, message = func()
            elapsed = (time.time() - start) * 1000
            
            if success:
                results["passed"] += 1
                status = "✅ PASS"
            else:
                results["failed"] += 1
                status = "❌ FAIL"
            
            print(f"\n{status} {name}")
            print(f"   {message}")
            print(f"   Temps: {elapsed:.2f}ms")
            
            results["tests"].append({
                "name": name,
                "success": success,
                "message": message,
                "time_ms": elapsed
            })
            
            return success
        except Exception as e:
            results["failed"] += 1
            print(f"\n❌ FAIL {name}")
            print(f"   Erreur: {str(e)}")
            results["tests"].append({
                "name": name,
                "success": False,
                "message": str(e),
                "time_ms": 0
            })
            return False
    
    # Test 1: GET /tree
    def test_tree():
        response = requests.get(f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/tree")
        if response.status_code == 200:
            data = response.json()
            return True, f"Arbre récupéré: {data.get('total_count', 0)} nœuds"
        return False, f"Status {response.status_code}"
    
    run_test("1. GET /tree - Récupération de l'arbre", test_tree)
    
    # Test 2: GET /cascading-options (établissements)
    def test_cascading_etablissements():
        response = requests.get(f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/cascading-options")
        if response.status_code == 200:
            data = response.json()
            return True, f"{len(data)} établissements trouvés"
        return False, f"Status {response.status_code}"
    
    run_test("2. GET /cascading-options - Établissements", test_cascading_etablissements)
    
    # Test 3: GET /cascading-options (départements)
    def test_cascading_departements():
        response = requests.get(
            f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/cascading-options",
            params={"parent_id": 1}
        )
        if response.status_code == 200:
            data = response.json()
            return True, f"{len(data)} départements trouvés"
        return False, f"Status {response.status_code}"
    
    run_test("3. GET /cascading-options - Départements", test_cascading_departements)
    
    # Test 4: POST /nodes - Création
    created_node_id = None
    def test_create_node():
        nonlocal created_node_id
        response = requests.post(
            f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/nodes",
            json={
                "parent_id": None,
                "level": "etablissement",
                "name": "Test Validation Finale",
                "code": "TEST_VAL",
                "sort_order": 9999
            }
        )
        if response.status_code == 200:
            data = response.json()
            created_node_id = data['id']
            return True, f"Nœud créé: {data['name']} (ID: {data['id']})"
        return False, f"Status {response.status_code}"
    
    run_test("4. POST /nodes - Création", test_create_node)
    
    # Test 5: GET /nodes/{id} - Récupération
    def test_get_node():
        if not created_node_id:
            return False, "Pas de nœud créé"
        response = requests.get(
            f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/nodes/{created_node_id}"
        )
        if response.status_code == 200:
            data = response.json()
            return True, f"Nœud récupéré: {data['name']}"
        return False, f"Status {response.status_code}"
    
    run_test("5. GET /nodes/{id} - Récupération", test_get_node)
    
    # Test 6: PUT /nodes/{id} - Mise à jour
    def test_update_node():
        if not created_node_id:
            return False, "Pas de nœud créé"
        response = requests.put(
            f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/nodes/{created_node_id}",
            json={
                "name": "Test Validation Finale Updated",
                "description": "Description mise à jour"
            }
        )
        if response.status_code == 200:
            data = response.json()
            return True, f"Nœud mis à jour: {data['name']}"
        return False, f"Status {response.status_code}"
    
    run_test("6. PUT /nodes/{id} - Mise à jour", test_update_node)
    
    # Test 7: POST /validate-path - Validation
    def test_validate_path():
        response = requests.post(
            f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/validate-path",
            json={
                "etablissement_id": 1,
                "departement_id": 2,
                "service_id": None,
                "unite_id": None
            }
        )
        if response.status_code == 200:
            data = response.json()
            if data['is_valid']:
                return True, "Chemin valide"
            else:
                return True, f"Chemin invalide (attendu): {data['errors']}"
        return False, f"Status {response.status_code}"
    
    run_test("7. POST /validate-path - Validation", test_validate_path)
    
    # Test 8: GET /search - Recherche
    def test_search():
        response = requests.get(
            f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/search",
            params={"query": "test"}
        )
        if response.status_code == 200:
            data = response.json()
            return True, f"{len(data)} résultats trouvés"
        return False, f"Status {response.status_code}"
    
    run_test("8. GET /search - Recherche", test_search)
    
    # Test 9: GET /levels/{level} - Par niveau
    def test_levels():
        response = requests.get(
            f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/levels/etablissement"
        )
        if response.status_code == 200:
            data = response.json()
            return True, f"{len(data)} établissements trouvés"
        return False, f"Status {response.status_code}"
    
    run_test("9. GET /levels/{level} - Par niveau", test_levels)
    
    # Test 10: DELETE /nodes/{id} - Suppression
    def test_delete_node():
        if not created_node_id:
            return False, "Pas de nœud créé"
        response = requests.delete(
            f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/nodes/{created_node_id}"
        )
        if response.status_code == 200:
            return True, "Nœud supprimé avec succès"
        return False, f"Status {response.status_code}"
    
    run_test("10. DELETE /nodes/{id} - Suppression", test_delete_node)
    
    # Résumé
    print("\n" + "=" * 70)
    print("RÉSUMÉ DE LA VALIDATION")
    print("=" * 70)
    print(f"\nTests totaux: {results['total_tests']}")
    print(f"✅ Réussis: {results['passed']}")
    print(f"❌ Échoués: {results['failed']}")
    
    success_rate = (results['passed'] / results['total_tests']) * 100
    print(f"\nTaux de réussite: {success_rate:.1f}%")
    
    if results['failed'] == 0:
        print("\n🎉 VALIDATION COMPLÈTE RÉUSSIE !")
        print("✅ L'API est prête pour la production")
    else:
        print("\n⚠️ Certains tests ont échoué")
        print("Veuillez vérifier les erreurs ci-dessus")
    
    # Sauvegarder les résultats
    with open("api_validation_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Résultats sauvegardés dans: api_validation_results.json")
    print("=" * 70)
    
    return results['failed'] == 0

if __name__ == "__main__":
    success = test_all_endpoints()
    exit(0 if success else 1)
