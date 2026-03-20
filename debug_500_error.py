#!/usr/bin/env python3
"""
Script pour identifier la source des erreurs 500 (Internal Server Error).
"""

import requests
import json
import time

def test_common_endpoints():
    """Test les endpoints couramment utilisés pour identifier celui qui cause l'erreur 500"""
    
    base_url = "http://localhost:8000"
    
    endpoints_to_test = [
        # Endpoints de base
        ("/workers", "GET", None),
        ("/employers", "GET", None),
        ("/type_regimes", "GET", None),
        
        # Endpoints organisationnels
        ("/organizational-structure/1/tree", "GET", None),
        ("/organizational-structure/1/choices?level=etablissement", "GET", None),
        ("/organizational-structure/2/tree", "GET", None),
        ("/organizational-structure/2/choices?level=etablissement", "GET", None),
        
        # Endpoints workers spécifiques
        ("/workers/2022", "GET", None),
        ("/workers/2007", "GET", None),
        
        # Endpoints avec paramètres
        ("/workers?q=", "GET", None),
        ("/workers?employer_id=1", "GET", None),
        
        # Endpoints organisationnels avec données employeur
        ("/employers/1/organizational-data/workers", "GET", None),
        ("/employers/2/organizational-data/workers", "GET", None),
    ]
    
    print("🔍 Test des endpoints pour identifier les erreurs 500...")
    print("=" * 60)
    
    errors_found = []
    
    for endpoint, method, data in endpoints_to_test:
        try:
            url = f"{base_url}{endpoint}"
            
            if method == "GET":
                response = requests.get(url, timeout=10)
            elif method == "POST":
                response = requests.post(url, json=data, timeout=10)
            
            status_icon = "✅" if response.status_code == 200 else "❌" if response.status_code == 500 else "⚠️"
            print(f"{status_icon} {method} {endpoint}: {response.status_code}")
            
            if response.status_code == 500:
                errors_found.append({
                    'endpoint': endpoint,
                    'method': method,
                    'status': response.status_code,
                    'response': response.text[:200] if response.text else "No response body"
                })
                
        except requests.exceptions.RequestException as e:
            print(f"❌ {method} {endpoint}: Erreur de connexion - {e}")
            errors_found.append({
                'endpoint': endpoint,
                'method': method,
                'error': str(e)
            })
    
    return errors_found

def test_organizational_endpoints_detailed():
    """Test détaillé des endpoints organisationnels"""
    
    print("\n🏢 Test détaillé des endpoints organisationnels...")
    print("-" * 50)
    
    base_url = "http://localhost:8000"
    
    # Test pour chaque employeur
    for employer_id in [1, 2]:
        print(f"\n📊 Employeur {employer_id}:")
        
        # Test tree
        try:
            response = requests.get(f"{base_url}/organizational-structure/{employer_id}/tree")
            print(f"  Tree: {response.status_code}")
            if response.status_code == 500:
                print(f"    Erreur: {response.text[:100]}")
        except Exception as e:
            print(f"  Tree: Erreur - {e}")
        
        # Test choices pour chaque niveau
        levels = ['etablissement', 'departement', 'service', 'unite']
        for level in levels:
            try:
                response = requests.get(f"{base_url}/organizational-structure/{employer_id}/choices", 
                                      params={'level': level})
                print(f"  Choices {level}: {response.status_code}")
                if response.status_code == 500:
                    print(f"    Erreur: {response.text[:100]}")
            except Exception as e:
                print(f"  Choices {level}: Erreur - {e}")

def main():
    print("🚨 Diagnostic des erreurs 500 (Internal Server Error)")
    print("=" * 60)
    
    # Test des endpoints communs
    errors = test_common_endpoints()
    
    # Test détaillé des endpoints organisationnels
    test_organizational_endpoints_detailed()
    
    # Résumé des erreurs
    if errors:
        print(f"\n❌ {len(errors)} erreur(s) 500 détectée(s):")
        for i, error in enumerate(errors, 1):
            print(f"\n{i}. {error['method']} {error['endpoint']}")
            if 'response' in error:
                print(f"   Status: {error['status']}")
                print(f"   Response: {error['response']}")
            if 'error' in error:
                print(f"   Error: {error['error']}")
        
        print("\n🔧 Actions recommandées:")
        print("  1. Vérifier les logs du backend pour plus de détails")
        print("  2. Redémarrer le serveur backend si nécessaire")
        print("  3. Vérifier la base de données")
        print("  4. Examiner le code des endpoints qui échouent")
        
    else:
        print("\n✅ Aucune erreur 500 détectée dans les tests!")
        print("\n💡 Si vous voyez encore des erreurs 500:")
        print("  1. L'erreur peut se produire lors d'actions spécifiques")
        print("  2. Vérifiez la console F12 pour voir l'URL exacte qui échoue")
        print("  3. Testez les actions qui causent l'erreur (création, modification, etc.)")

if __name__ == "__main__":
    main()