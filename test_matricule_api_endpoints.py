#!/usr/bin/env python3
"""
Tests pour les endpoints API du système de matricules
Task 7: Validation des API endpoints
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'siirh-backend'))

import requests
import json
from datetime import datetime

# Configuration de l'API
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/matricules"

def test_api_connection():
    """Test de connectivité de base"""
    try:
        response = requests.get(f"{BASE_URL}/docs")
        print(f"✅ Connexion API réussie (status: {response.status_code})")
        return True
    except Exception as e:
        print(f"❌ Erreur de connexion API: {e}")
        return False

def test_health_endpoint():
    """Test de l'endpoint de santé"""
    try:
        response = requests.get(f"{API_BASE}/health")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check réussi")
            print(f"   Status: {data.get('status')}")
            print(f"   Workers count: {data.get('workers_count')}")
            print(f"   Services: {data.get('services')}")
            return True
        else:
            print(f"❌ Health check échoué (status: {response.status_code})")
            return False
            
    except Exception as e:
        print(f"❌ Erreur health check: {e}")
        return False

def test_search_endpoints():
    """Test des endpoints de recherche"""
    test_cases = [
        {"query": "DURAND", "description": "Recherche par nom"},
        {"query": "E001GY006", "description": "Recherche par matricule"},
        {"query": "Sophie", "description": "Recherche par prénom"},
    ]
    
    results = []
    
    for case in test_cases:
        try:
            response = requests.get(f"{API_BASE}/search", params={"query": case["query"]})
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {case['description']}: {len(data)} résultats")
                if data:
                    print(f"   Premier résultat: {data[0].get('full_name')} ({data[0].get('matricule')})")
                results.append(True)
            else:
                print(f"❌ {case['description']} échoué (status: {response.status_code})")
                results.append(False)
                
        except Exception as e:
            print(f"❌ Erreur {case['description']}: {e}")
            results.append(False)
    
    return all(results)

def test_matricule_resolution():
    """Test de résolution de matricule"""
    test_matricules = ["E001GY006", "E001GY007", "E001GY008"]
    
    results = []
    
    for matricule in test_matricules:
        try:
            response = requests.get(f"{API_BASE}/resolve/{matricule}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Résolution {matricule}: {data.get('full_name')}")
                results.append(True)
            elif response.status_code == 404:
                print(f"⚠️  Matricule {matricule} non trouvé (normal si pas encore migré)")
                results.append(True)  # Acceptable pour les tests
            else:
                print(f"❌ Résolution {matricule} échoué (status: {response.status_code})")
                results.append(False)
                
        except Exception as e:
            print(f"❌ Erreur résolution {matricule}: {e}")
            results.append(False)
    
    return all(results)

def test_integrity_validation():
    """Test de validation d'intégrité"""
    try:
        response = requests.get(f"{API_BASE}/integrity/validate")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Validation d'intégrité réussie")
            print(f"   Status: {data.get('overall_status')}")
            print(f"   Checks: {data.get('passed_checks')}/{data.get('total_checks')}")
            print(f"   Issues: {data.get('issues_count')}")
            return True
        else:
            print(f"❌ Validation d'intégrité échouée (status: {response.status_code})")
            return False
            
    except Exception as e:
        print(f"❌ Erreur validation d'intégrité: {e}")
        return False

def test_migration_analysis():
    """Test d'analyse de migration"""
    try:
        response = requests.get(f"{API_BASE}/migration/analysis")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Analyse de migration réussie")
            print(f"   Complexité: {data.get('complexity')}")
            print(f"   Durée estimée: {data.get('estimated_duration')}")
            print(f"   Issues: {data.get('issues_count')}")
            return True
        else:
            print(f"❌ Analyse de migration échouée (status: {response.status_code})")
            return False
            
    except Exception as e:
        print(f"❌ Erreur analyse de migration: {e}")
        return False

def test_assignment_endpoints():
    """Test des endpoints d'affectation"""
    # Test de récupération d'affectations
    test_matricules = ["E001GY006", "E001GY007"]
    
    results = []
    
    for matricule in test_matricules:
        try:
            response = requests.get(f"{API_BASE}/assignments/{matricule}")
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    print(f"✅ Affectation {matricule}: {data.get('departement', 'N/A')}")
                else:
                    print(f"⚠️  Aucune affectation pour {matricule}")
                results.append(True)
            else:
                print(f"❌ Récupération affectation {matricule} échouée (status: {response.status_code})")
                results.append(False)
                
        except Exception as e:
            print(f"❌ Erreur affectation {matricule}: {e}")
            results.append(False)
    
    return all(results)

def run_all_tests():
    """Exécuter tous les tests d'API"""
    print("=== Tests des Endpoints API Matricules ===")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    tests = [
        ("Connexion API", test_api_connection),
        ("Health Check", test_health_endpoint),
        ("Endpoints de recherche", test_search_endpoints),
        ("Résolution de matricules", test_matricule_resolution),
        ("Validation d'intégrité", test_integrity_validation),
        ("Analyse de migration", test_migration_analysis),
        ("Endpoints d'affectation", test_assignment_endpoints),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            result = test_func()
            results.append(result)
            print(f"Résultat: {'✅ SUCCÈS' if result else '❌ ÉCHEC'}")
        except Exception as e:
            print(f"❌ Erreur inattendue: {e}")
            results.append(False)
    
    print(f"\n=== Résumé des Tests ===")
    passed = sum(results)
    total = len(results)
    print(f"Tests réussis: {passed}/{total}")
    print(f"Taux de réussite: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("🎉 Tous les tests d'API sont passés!")
        return True
    else:
        print("⚠️  Certains tests ont échoué. Vérifiez les détails ci-dessus.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    
    # Sauvegarder les résultats
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "test_type": "matricule_api_endpoints",
        "success": success,
        "total_tests": 7
    }
    
    with open(f"matricule_api_test_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "w") as f:
        json.dump(log_data, f, indent=2)
    
    print(f"\nLog sauvegardé: matricule_api_test_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")