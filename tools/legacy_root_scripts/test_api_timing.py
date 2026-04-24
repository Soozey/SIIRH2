"""
Test de timing détaillé de l'API
"""
import requests
import time

BASE_URL = "http://localhost:8000"

def test_timing():
    print("=" * 60)
    print("TEST DE TIMING DÉTAILLÉ")
    print("=" * 60)
    
    # Test simple
    print("\n1. Test simple GET /employers")
    start = time.time()
    response = requests.get(f"{BASE_URL}/employers")
    elapsed = (time.time() - start) * 1000
    print(f"   Status: {response.status_code}")
    print(f"   Temps: {elapsed:.2f}ms")
    
    # Test hiérarchique
    print("\n2. Test GET /hierarchical-organization/tree")
    start = time.time()
    response = requests.get(f"{BASE_URL}/employers/1/hierarchical-organization/tree")
    elapsed = (time.time() - start) * 1000
    print(f"   Status: {response.status_code}")
    print(f"   Temps: {elapsed:.2f}ms")
    
    # Test avec timeout court
    print("\n3. Test avec timeout de 5 secondes")
    try:
        start = time.time()
        response = requests.get(
            f"{BASE_URL}/employers/1/hierarchical-organization/tree",
            timeout=5
        )
        elapsed = (time.time() - start) * 1000
        print(f"   Status: {response.status_code}")
        print(f"   Temps: {elapsed:.2f}ms")
    except requests.Timeout:
        print(f"   ❌ Timeout après 5 secondes")
    
    # Test de connexion
    print("\n4. Test de connexion simple")
    start = time.time()
    try:
        response = requests.get(f"{BASE_URL}/", timeout=1)
        elapsed = (time.time() - start) * 1000
        print(f"   Status: {response.status_code}")
        print(f"   Temps: {elapsed:.2f}ms")
    except Exception as e:
        elapsed = (time.time() - start) * 1000
        print(f"   Erreur: {e}")
        print(f"   Temps: {elapsed:.2f}ms")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_timing()
