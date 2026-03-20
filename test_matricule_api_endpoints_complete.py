#!/usr/bin/env python3
"""
Test complet des endpoints API matricule
Task 7: Validation complète des API endpoints
"""

import requests
import json
from datetime import datetime

def test_matricule_api_endpoints():
    """Test complet des endpoints API matricule"""
    
    BASE_URL = "http://localhost:8000/api/matricules"
    
    print("🔍 Test Complet des Endpoints API Matricule")
    print("=" * 60)
    
    # Test 1: Health Check
    print("\n1️⃣ Test Health Check")
    print("-" * 40)
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health Check: {data['status']}")
            print(f"   Workers count: {data.get('workers_count', 'N/A')}")
            print(f"   Services: {data.get('services', {})}")
        else:
            print(f"❌ Health Check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health Check error: {e}")
    
    # Test 2: Recherche par matricule
    print("\n2️⃣ Test Recherche par Matricule")
    print("-" * 40)
    
    test_matricules = ["E001001", "E001002", "INVALID"]
    
    for matricule in test_matricules:
        try:
            response = requests.get(f"{BASE_URL}/search", params={"query": matricule})
            if response.status_code == 200:
                results = response.json()
                print(f"✅ Recherche '{matricule}': {len(results)} résultats")
                for result in results[:2]:  # Afficher max 2 résultats
                    print(f"   - {result['matricule']}: {result['full_name']}")
            else:
                print(f"⚠️  Recherche '{matricule}': {response.status_code}")
        except Exception as e:
            print(f"❌ Erreur recherche '{matricule}': {e}")
    
    # Test 3: Recherche par nom
    print("\n3️⃣ Test Recherche par Nom")
    print("-" * 40)
    
    test_names = ["Jean", "Marie", "TestName"]
    
    for name in test_names:
        try:
            response = requests.get(f"{BASE_URL}/search", params={"query": name, "limit": 3})
            if response.status_code == 200:
                results = response.json()
                print(f"✅ Recherche '{name}': {len(results)} résultats")
                for result in results[:2]:
                    print(f"   - {result['matricule']}: {result['full_name']}")
            else:
                print(f"⚠️  Recherche '{name}': {response.status_code}")
        except Exception as e:
            print(f"❌ Erreur recherche '{name}': {e}")
    
    # Test 4: Résolution de matricule
    print("\n4️⃣ Test Résolution de Matricule")
    print("-" * 40)
    
    try:
        response = requests.get(f"{BASE_URL}/resolve/E001001")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Résolution E001001:")
            print(f"   Nom: {data.get('full_name', 'N/A')}")
            print(f"   Worker ID: {data.get('worker_id', 'N/A')}")
        elif response.status_code == 404:
            print("⚠️  Matricule E001001 non trouvé")
        else:
            print(f"❌ Erreur résolution: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur résolution: {e}")
    
    # Test 5: Analyse de migration
    print("\n5️⃣ Test Analyse de Migration")
    print("-" * 40)
    
    try:
        response = requests.get(f"{BASE_URL}/migration/analysis")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Analyse migration:")
            print(f"   Complexité: {data.get('complexity', 'N/A')}")
            print(f"   Durée estimée: {data.get('estimated_duration', 'N/A')}")
            print(f"   Problèmes: {data.get('issues_count', 0)}")
        else:
            print(f"⚠️  Analyse migration: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur analyse: {e}")
    
    # Test 6: Validation d'intégrité
    print("\n6️⃣ Test Validation d'Intégrité")
    print("-" * 40)
    
    try:
        response = requests.get(f"{BASE_URL}/integrity/validate")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Validation intégrité:")
            print(f"   Status: {data.get('overall_status', 'N/A')}")
            print(f"   Checks: {data.get('passed_checks', 0)}/{data.get('total_checks', 0)}")
            print(f"   Problèmes critiques: {data.get('critical_issues', 0)}")
        else:
            print(f"⚠️  Validation intégrité: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur validation: {e}")
    
    # Test 7: Test d'erreur avec gestion par matricule
    print("\n7️⃣ Test Gestion d'Erreurs")
    print("-" * 40)
    
    try:
        # Tenter une résolution avec matricule invalide
        response = requests.get(f"{BASE_URL}/resolve/INVALID_MATRICULE")
        if response.status_code == 404:
            data = response.json()
            print(f"✅ Gestion d'erreur 404:")
            print(f"   Error ID: {data.get('error_id', 'N/A')}")
            print(f"   Message: {data.get('message', 'N/A')}")
            print(f"   Matricules impliqués: {len(data.get('matricules_involved', {}).get('invalid_matricules', []))}")
            
            guidance = data.get('user_guidance', {})
            if guidance.get('suggestions'):
                print(f"   Suggestions: {guidance['suggestions'][0]}")
        else:
            print(f"⚠️  Test erreur: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur test erreur: {e}")
    
    # Test 8: Création d'affectation organisationnelle
    print("\n8️⃣ Test Affectation Organisationnelle")
    print("-" * 40)
    
    try:
        assignment_data = {
            "worker_matricule": "E001TEST999",
            "employer_id": 1,
            "etablissement": "Siège",
            "departement": "IT",
            "service": "Développement"
        }
        
        response = requests.post(f"{BASE_URL}/assignments", json=assignment_data)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Affectation créée:")
            print(f"   ID: {data.get('id', 'N/A')}")
            print(f"   Matricule: {data.get('worker_matricule', 'N/A')}")
        else:
            print(f"⚠️  Création affectation: {response.status_code}")
            if response.status_code == 400:
                error_data = response.json()
                print(f"   Erreur: {error_data.get('message', 'N/A')}")
    except Exception as e:
        print(f"❌ Erreur affectation: {e}")
    
    # Test 9: Récupération des affectations
    print("\n9️⃣ Test Récupération Affectations")
    print("-" * 40)
    
    try:
        response = requests.get(f"{BASE_URL}/assignments/E001001")
        if response.status_code == 200:
            data = response.json()
            if data:
                print(f"✅ Affectation trouvée:")
                print(f"   Matricule: {data.get('worker_matricule', 'N/A')}")
                print(f"   Établissement: {data.get('etablissement', 'N/A')}")
            else:
                print("⚠️  Aucune affectation trouvée")
        else:
            print(f"⚠️  Récupération affectations: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur récupération: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Test complet des endpoints API terminé")

if __name__ == "__main__":
    test_matricule_api_endpoints()