"""
Script de diagnostic pour identifier l'erreur 500
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_endpoints():
    """Tester les endpoints principaux pour identifier l'erreur 500"""
    print("=" * 80)
    print("DIAGNOSTIC DES ERREURS 500")
    print("=" * 80)
    
    endpoints = [
        # Endpoints de base
        ("/employers", "GET", None),
        ("/workers", "GET", None),
        
        # Endpoints hiérarchiques
        ("/employers/1/hierarchical-organization/tree", "GET", None),
        ("/employers/1/hierarchical-organization/cascading-options", "GET", {"parent_id": None}),
        
        # Endpoints organisationnels (anciens)
        ("/employers/1/organizational-data/hierarchical", "GET", None),
        ("/employers/1/organizational-data/workers", "GET", None),
    ]
    
    errors = []
    
    for endpoint, method, params in endpoints:
        try:
            print(f"\n🔍 Test: {method} {endpoint}")
            if params:
                print(f"   Params: {params}")
            
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}", params=params, timeout=5)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 500:
                print(f"   ❌ ERREUR 500 DÉTECTÉE!")
                print(f"   Réponse: {response.text[:500]}")
                errors.append({
                    "endpoint": endpoint,
                    "method": method,
                    "params": params,
                    "response": response.text
                })
            elif response.status_code == 200:
                print(f"   ✓ OK")
                try:
                    data = response.json()
                    if isinstance(data, list):
                        print(f"   Données: {len(data)} élément(s)")
                    elif isinstance(data, dict):
                        print(f"   Clés: {list(data.keys())}")
                except:
                    pass
            else:
                print(f"   ⚠️  Status: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            errors.append({
                "endpoint": endpoint,
                "method": method,
                "params": params,
                "error": str(e)
            })
    
    print("\n" + "=" * 80)
    print("RÉSUMÉ")
    print("=" * 80)
    
    if errors:
        print(f"\n❌ {len(errors)} erreur(s) détectée(s):\n")
        for i, error in enumerate(errors, 1):
            print(f"{i}. {error['method']} {error['endpoint']}")
            if 'response' in error:
                print(f"   Réponse: {error['response'][:200]}")
            if 'error' in error:
                print(f"   Erreur: {error['error']}")
            print()
    else:
        print("\n✅ Aucune erreur 500 détectée!")
    
    return errors

if __name__ == "__main__":
    errors = test_endpoints()
    exit(1 if errors else 0)
