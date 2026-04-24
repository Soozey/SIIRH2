"""
Test d'intégration complète Frontend + Backend
"""
import requests
import time

def test_integration():
    print("=" * 70)
    print("TEST D'INTÉGRATION COMPLÈTE")
    print("=" * 70)
    
    # 1. Vérifier le frontend
    print("\n1. Vérification du Frontend")
    frontend_ports = [5173, 5174, 5175]
    frontend_url = None
    
    for port in frontend_ports:
        try:
            url = f"http://localhost:{port}"
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                frontend_url = url
                print(f"   ✅ Frontend accessible: {url}")
                break
        except:
            pass
    
    if not frontend_url:
        print("   ❌ Frontend non accessible")
        return False
    
    # 2. Vérifier le backend
    print("\n2. Vérification du Backend")
    backend_urls = ["http://127.0.0.1:8000", "http://localhost:8000"]
    backend_url = None
    
    for url in backend_urls:
        try:
            response = requests.get(f"{url}/employers", timeout=2)
            if response.status_code == 200:
                backend_url = url
                print(f"   ✅ Backend accessible: {url}")
                print(f"   Temps de réponse: {response.elapsed.total_seconds() * 1000:.2f}ms")
                break
        except:
            pass
    
    if not backend_url:
        print("   ❌ Backend non accessible")
        return False
    
    # 3. Tester l'API hiérarchique
    print("\n3. Test de l'API Hiérarchique")
    employer_id = 1
    
    tests = [
        ("GET /tree", f"{backend_url}/employers/{employer_id}/hierarchical-organization/tree"),
        ("GET /cascading-options", f"{backend_url}/employers/{employer_id}/hierarchical-organization/cascading-options"),
    ]
    
    all_passed = True
    for name, url in tests:
        try:
            start = time.time()
            response = requests.get(url, timeout=5)
            elapsed = (time.time() - start) * 1000
            
            if response.status_code == 200:
                print(f"   ✅ {name}: {elapsed:.2f}ms")
            else:
                print(f"   ❌ {name}: Status {response.status_code}")
                all_passed = False
        except Exception as e:
            print(f"   ❌ {name}: {e}")
            all_passed = False
    
    # 4. Vérifier la configuration
    print("\n4. Vérification de la Configuration")
    
    # Vérifier que le .env existe
    import os
    env_exists = os.path.exists("siirh-frontend/.env")
    print(f"   {'✅' if env_exists else '❌'} Fichier .env existe")
    
    # Vérifier que api.ts existe
    api_ts_exists = os.path.exists("siirh-frontend/src/config/api.ts")
    print(f"   {'✅' if api_ts_exists else '❌'} Fichier api.ts existe")
    
    # 5. Résumé
    print("\n" + "=" * 70)
    print("RÉSUMÉ")
    print("=" * 70)
    
    if all_passed and frontend_url and backend_url:
        print("\n🎉 INTÉGRATION COMPLÈTE RÉUSSIE !")
        print(f"\n✅ Frontend: {frontend_url}")
        print(f"✅ Backend: {backend_url}")
        print(f"✅ API Hiérarchique: Fonctionnelle")
        print(f"\n💡 Vous pouvez maintenant utiliser l'application !")
        return True
    else:
        print("\n⚠️ Certains tests ont échoué")
        return False

if __name__ == "__main__":
    success = test_integration()
    exit(0 if success else 1)
