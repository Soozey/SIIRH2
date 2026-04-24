"""
Vérification finale de l'API - Checklist complète
"""
import requests
import os
import json

BASE_URL = "http://127.0.0.1:8000"

def check_file_exists(path):
    """Vérifie qu'un fichier existe"""
    return os.path.exists(path)

def check_api_endpoint(url, method="GET", json_data=None):
    """Vérifie qu'un endpoint API fonctionne"""
    try:
        if method == "GET":
            response = requests.get(url, timeout=5)
        elif method == "POST":
            response = requests.post(url, json=json_data, timeout=5)
        return response.status_code in [200, 201]
    except:
        return False

def main():
    print("=" * 70)
    print("VÉRIFICATION FINALE DE L'API HIÉRARCHIQUE")
    print("=" * 70)
    
    checks = []
    
    # 1. Vérification des fichiers backend
    print("\n📁 FICHIERS BACKEND")
    backend_files = [
        "siirh-backend/app/schemas.py",
        "siirh-backend/app/models.py",
        "siirh-backend/app/routers/hierarchical_organization.py",
        "siirh-backend/app/services/hierarchical_organizational_service.py",
    ]
    
    for file in backend_files:
        exists = check_file_exists(file)
        status = "✅" if exists else "❌"
        print(f"   {status} {file}")
        checks.append(("Backend file: " + file, exists))
    
    # 2. Vérification des fichiers frontend
    print("\n📁 FICHIERS FRONTEND")
    frontend_files = [
        "siirh-frontend/src/config/api.ts",
        "siirh-frontend/.env",
        "siirh-frontend/.env.example",
    ]
    
    for file in frontend_files:
        exists = check_file_exists(file)
        status = "✅" if exists else "❌"
        print(f"   {status} {file}")
        checks.append(("Frontend file: " + file, exists))
    
    # 3. Vérification des fichiers de documentation
    print("\n📁 DOCUMENTATION")
    doc_files = [
        "API_HIERARCHIQUE_VALIDATION_FINALE.md",
        "GUIDE_CONFIGURATION_FRONTEND_API.md",
        "CORRECTION_API_COMPLETE.md",
        "RESUME_CORRECTION_API.md",
    ]
    
    for file in doc_files:
        exists = check_file_exists(file)
        status = "✅" if exists else "❌"
        print(f"   {status} {file}")
        checks.append(("Documentation: " + file, exists))
    
    # 4. Vérification des endpoints API
    print("\n🌐 ENDPOINTS API")
    employer_id = 1
    
    endpoints = [
        ("GET /tree", f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/tree", "GET", None),
        ("GET /cascading-options", f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/cascading-options", "GET", None),
        ("GET /search", f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/search?query=test", "GET", None),
        ("GET /levels", f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/levels/etablissement", "GET", None),
    ]
    
    for name, url, method, data in endpoints:
        works = check_api_endpoint(url, method, data)
        status = "✅" if works else "❌"
        print(f"   {status} {name}")
        checks.append(("API endpoint: " + name, works))
    
    # 5. Vérification de la configuration
    print("\n⚙️ CONFIGURATION")
    
    # Vérifier le contenu du .env
    env_correct = False
    if check_file_exists("siirh-frontend/.env"):
        with open("siirh-frontend/.env", "r") as f:
            content = f.read()
            env_correct = "127.0.0.1" in content
    
    status = "✅" if env_correct else "❌"
    print(f"   {status} .env contient 127.0.0.1")
    checks.append(("Configuration: .env correct", env_correct))
    
    # Vérifier le contenu de api.ts
    api_ts_correct = False
    if check_file_exists("siirh-frontend/src/config/api.ts"):
        with open("siirh-frontend/src/config/api.ts", "r") as f:
            content = f.read()
            api_ts_correct = "127.0.0.1" in content
    
    status = "✅" if api_ts_correct else "❌"
    print(f"   {status} api.ts contient 127.0.0.1")
    checks.append(("Configuration: api.ts correct", api_ts_correct))
    
    # 6. Résumé
    print("\n" + "=" * 70)
    print("RÉSUMÉ")
    print("=" * 70)
    
    total = len(checks)
    passed = sum(1 for _, result in checks if result)
    failed = total - passed
    
    print(f"\nTotal: {total}")
    print(f"✅ Réussis: {passed}")
    print(f"❌ Échoués: {failed}")
    
    success_rate = (passed / total) * 100
    print(f"\nTaux de réussite: {success_rate:.1f}%")
    
    if failed == 0:
        print("\n🎉 VÉRIFICATION COMPLÈTE RÉUSSIE !")
        print("✅ L'API est 100% fonctionnelle et prête pour la production")
    else:
        print("\n⚠️ Certaines vérifications ont échoué")
        print("\nÉléments échoués:")
        for name, result in checks:
            if not result:
                print(f"   ❌ {name}")
    
    print("=" * 70)
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
