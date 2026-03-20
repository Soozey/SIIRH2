"""
Test de résolution localhost
"""
import requests
import time
import socket

def test_resolution():
    print("=" * 60)
    print("TEST DE RÉSOLUTION LOCALHOST")
    print("=" * 60)
    
    # Test 1: Résolution DNS
    print("\n1. Résolution DNS de 'localhost'")
    start = time.time()
    try:
        ip = socket.gethostbyname('localhost')
        elapsed = (time.time() - start) * 1000
        print(f"   IP: {ip}")
        print(f"   Temps: {elapsed:.2f}ms")
    except Exception as e:
        print(f"   Erreur: {e}")
    
    # Test 2: Test avec 127.0.0.1
    print("\n2. Test avec 127.0.0.1")
    start = time.time()
    try:
        response = requests.get("http://127.0.0.1:8000/employers", timeout=5)
        elapsed = (time.time() - start) * 1000
        print(f"   Status: {response.status_code}")
        print(f"   Temps: {elapsed:.2f}ms")
    except Exception as e:
        elapsed = (time.time() - start) * 1000
        print(f"   Erreur: {e}")
        print(f"   Temps: {elapsed:.2f}ms")
    
    # Test 3: Test avec localhost
    print("\n3. Test avec localhost")
    start = time.time()
    try:
        response = requests.get("http://localhost:8000/employers", timeout=5)
        elapsed = (time.time() - start) * 1000
        print(f"   Status: {response.status_code}")
        print(f"   Temps: {elapsed:.2f}ms")
    except Exception as e:
        elapsed = (time.time() - start) * 1000
        print(f"   Erreur: {e}")
        print(f"   Temps: {elapsed:.2f}ms")
    
    # Test 4: Test avec IPv6
    print("\n4. Test avec ::1 (IPv6)")
    start = time.time()
    try:
        response = requests.get("http://[::1]:8000/employers", timeout=5)
        elapsed = (time.time() - start) * 1000
        print(f"   Status: {response.status_code}")
        print(f"   Temps: {elapsed:.2f}ms")
    except Exception as e:
        elapsed = (time.time() - start) * 1000
        print(f"   Erreur: {e}")
        print(f"   Temps: {elapsed:.2f}ms")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_resolution()
