"""
Test de performance de l'API hiérarchique
"""
import requests
import time
import statistics

BASE_URL = "http://localhost:8000"

def measure_endpoint(name, url, method="GET", json_data=None, params=None, iterations=10):
    """Mesure le temps de réponse d'un endpoint"""
    times = []
    
    for i in range(iterations):
        start = time.time()
        
        if method == "GET":
            response = requests.get(url, params=params)
        elif method == "POST":
            response = requests.post(url, json=json_data)
        elif method == "PUT":
            response = requests.put(url, json=json_data)
        elif method == "DELETE":
            response = requests.delete(url)
        
        elapsed = (time.time() - start) * 1000  # en ms
        times.append(elapsed)
        
        if response.status_code not in [200, 201]:
            print(f"   ⚠️ Erreur {response.status_code} à l'itération {i+1}")
    
    avg = statistics.mean(times)
    median = statistics.median(times)
    min_time = min(times)
    max_time = max(times)
    
    print(f"\n{name}:")
    print(f"   Moyenne: {avg:.2f}ms")
    print(f"   Médiane: {median:.2f}ms")
    print(f"   Min: {min_time:.2f}ms")
    print(f"   Max: {max_time:.2f}ms")
    
    # Évaluation
    if avg < 50:
        print(f"   ✅ Excellent")
    elif avg < 100:
        print(f"   ✅ Bon")
    elif avg < 200:
        print(f"   ⚠️ Acceptable")
    else:
        print(f"   ❌ Lent")
    
    return avg

def test_performance():
    print("=" * 60)
    print("TEST DE PERFORMANCE DE L'API HIÉRARCHIQUE")
    print("=" * 60)
    
    employer_id = 1
    
    # Test 1: Récupération de l'arbre complet
    measure_endpoint(
        "1. GET /tree (arbre complet)",
        f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/tree"
    )
    
    # Test 2: Récupération des options en cascade (établissements)
    measure_endpoint(
        "2. GET /cascading-options (établissements)",
        f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/cascading-options"
    )
    
    # Test 3: Récupération des options en cascade (départements)
    measure_endpoint(
        "3. GET /cascading-options (départements)",
        f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/cascading-options",
        params={"parent_id": 1}
    )
    
    # Test 4: Récupération par niveau
    measure_endpoint(
        "4. GET /levels/etablissement",
        f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/levels/etablissement"
    )
    
    # Test 5: Recherche
    measure_endpoint(
        "5. GET /search",
        f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/search",
        params={"query": "test"}
    )
    
    # Test 6: Validation de chemin
    measure_endpoint(
        "6. POST /validate-path",
        f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/validate-path",
        method="POST",
        json_data={
            "etablissement_id": 1,
            "departement_id": 2,
            "service_id": None,
            "unite_id": None
        }
    )
    
    # Test 7: Création de nœud
    print("\n7. POST /nodes (création)")
    create_times = []
    created_ids = []
    
    for i in range(5):
        start = time.time()
        response = requests.post(
            f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/nodes",
            json={
                "parent_id": None,
                "level": "etablissement",
                "name": f"Test Perf {i}",
                "code": f"PERF{i}",
                "sort_order": 1000 + i
            }
        )
        elapsed = (time.time() - start) * 1000
        create_times.append(elapsed)
        
        if response.status_code == 200:
            created_ids.append(response.json()['id'])
    
    avg_create = statistics.mean(create_times)
    print(f"   Moyenne: {avg_create:.2f}ms")
    if avg_create < 100:
        print(f"   ✅ Bon")
    else:
        print(f"   ⚠️ Acceptable")
    
    # Test 8: Mise à jour de nœud
    if created_ids:
        print("\n8. PUT /nodes/{id} (mise à jour)")
        update_times = []
        
        for node_id in created_ids:
            start = time.time()
            response = requests.put(
                f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/nodes/{node_id}",
                json={"description": "Updated"}
            )
            elapsed = (time.time() - start) * 1000
            update_times.append(elapsed)
        
        avg_update = statistics.mean(update_times)
        print(f"   Moyenne: {avg_update:.2f}ms")
        if avg_update < 100:
            print(f"   ✅ Bon")
        else:
            print(f"   ⚠️ Acceptable")
    
    # Test 9: Suppression de nœud
    if created_ids:
        print("\n9. DELETE /nodes/{id} (suppression)")
        delete_times = []
        
        for node_id in created_ids:
            start = time.time()
            response = requests.delete(
                f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/nodes/{node_id}"
            )
            elapsed = (time.time() - start) * 1000
            delete_times.append(elapsed)
        
        avg_delete = statistics.mean(delete_times)
        print(f"   Moyenne: {avg_delete:.2f}ms")
        if avg_delete < 100:
            print(f"   ✅ Bon")
        else:
            print(f"   ⚠️ Acceptable")
    
    print("\n" + "=" * 60)
    print("TESTS DE PERFORMANCE TERMINÉS")
    print("=" * 60)

if __name__ == "__main__":
    test_performance()
