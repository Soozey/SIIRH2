"""
Test rapide de l'intégration API hiérarchique
"""
import requests
import json

BASE_URL = "http://localhost:8000"
EMPLOYER_ID = 1

def test_api_endpoints():
    """Test rapide des endpoints principaux"""
    
    print("🧪 Test de l'API Hiérarchique Organisationnelle\n")
    print("=" * 60)
    
    # Test 1: Health check
    print("\n1️⃣ Test Health Check")
    try:
        response = requests.get(f"{BASE_URL}/employers/{EMPLOYER_ID}/hierarchical-organization/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check OK")
            print(f"   Status: {data.get('status')}")
            print(f"   Nodes: {data.get('total_nodes')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    # Test 2: Arbre hiérarchique
    print("\n2️⃣ Test Arbre Hiérarchique")
    try:
        response = requests.get(f"{BASE_URL}/employers/{EMPLOYER_ID}/hierarchical-organization/tree")
        if response.status_code == 200:
            data = response.json()
            nodes = data.get('nodes', [])
            print(f"✅ Arbre récupéré")
            print(f"   Nœuds racines: {len(nodes)}")
            if nodes:
                print(f"   Premier nœud: {nodes[0].get('name')}")
        else:
            print(f"❌ Erreur: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    # Test 3: Options en cascade - Établissements
    print("\n3️⃣ Test Options Cascade - Établissements")
    try:
        response = requests.get(
            f"{BASE_URL}/employers/{EMPLOYER_ID}/hierarchical-organization/cascading-options"
        )
        if response.status_code == 200:
            options = response.json()
            print(f"✅ Établissements récupérés: {len(options)}")
            for opt in options[:3]:
                print(f"   • {opt.get('name')} (ID: {opt.get('id')})")
        else:
            print(f"❌ Erreur: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    # Test 4: Options en cascade - Départements
    print("\n4️⃣ Test Options Cascade - Départements (parent_id=7)")
    try:
        response = requests.get(
            f"{BASE_URL}/employers/{EMPLOYER_ID}/hierarchical-organization/cascading-options",
            params={"parent_id": 7}
        )
        if response.status_code == 200:
            options = response.json()
            print(f"✅ Départements récupérés: {len(options)}")
            for opt in options:
                print(f"   • {opt.get('name')} (ID: {opt.get('id')})")
        else:
            print(f"❌ Erreur: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    # Test 5: Recherche
    print("\n5️⃣ Test Recherche (query='Informatique')")
    try:
        response = requests.get(
            f"{BASE_URL}/employers/{EMPLOYER_ID}/hierarchical-organization/tree",
            params={"search_query": "Informatique"}
        )
        if response.status_code == 200:
            data = response.json()
            nodes = data.get('nodes', [])
            print(f"✅ Résultats trouvés: {len(nodes)} nœuds")
        else:
            print(f"❌ Erreur: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Tests terminés\n")

if __name__ == "__main__":
    test_api_endpoints()
