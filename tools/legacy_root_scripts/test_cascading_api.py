"""
Tester l'API cascading-options pour comprendre pourquoi les structures ne sont pas accessibles
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_api():
    print("=" * 80)
    print("TEST DE L'API CASCADING-OPTIONS")
    print("=" * 80)
    
    employer_id = 2  # Mandroso Services
    
    # Test 1: Récupérer les établissements (parent_id=null)
    print("\n1. TEST: Récupérer les établissements")
    print("-" * 80)
    
    url = f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/cascading-options"
    params = {"parent_id": "null"}
    
    print(f"URL: {url}")
    print(f"Params: {params}")
    
    try:
        response = requests.get(url, params=params)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Réponse reçue: {len(data)} établissement(s)")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(f"❌ Erreur: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 2: Récupérer les départements (parent_id=12)
    print("\n2. TEST: Récupérer les départements sous l'établissement 12")
    print("-" * 80)
    
    params = {"parent_id": 12}
    
    try:
        response = requests.get(url, params=params)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Réponse reçue: {len(data)} département(s)")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(f"❌ Erreur: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 3: Récupérer les services (parent_id=13)
    print("\n3. TEST: Récupérer les services sous le département 13")
    print("-" * 80)
    
    params = {"parent_id": 13}
    
    try:
        response = requests.get(url, params=params)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Réponse reçue: {len(data)} service(s)")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(f"❌ Erreur: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    test_api()
