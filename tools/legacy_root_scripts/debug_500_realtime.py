#!/usr/bin/env python3
"""
Diagnostic en temps réel de l'erreur 500 après Ctrl+F5
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_all_endpoints():
    """Test tous les endpoints susceptibles de causer l'erreur 500"""
    
    print("🔍 Diagnostic en temps réel de l'erreur 500")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().strftime('%H:%M:%S')}")
    
    # Liste des endpoints à tester
    endpoints_to_test = [
        # Endpoints de base
        "/",
        "/docs",
        "/employers",
        
        # Endpoints organisationnels avec différents IDs
        "/organizational-structure/1/tree",
        "/organizational-structure/null/tree",
        "/organizational-structure/undefined/tree",
        "/organizational-structure/0/tree",
        
        # Endpoints avec employeurs existants
        "/organizational-structure/1/validate",
        "/organizational-structure/1/children",
        
        # Endpoints workers
        "/workers",
        "/workers/1",
        
        # Autres endpoints
        "/constants",
        "/document_templates",
        "/custom_contracts"
    ]
    
    errors_500 = []
    
    for endpoint in endpoints_to_test:
        try:
            print(f"\n🧪 Test: {endpoint}")
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            
            if response.status_code == 500:
                print(f"❌ ERREUR 500 TROUVÉE: {endpoint}")
                errors_500.append({
                    'endpoint': endpoint,
                    'response': response.text[:500],
                    'headers': dict(response.headers)
                })
            elif response.status_code >= 400:
                print(f"⚠️  {response.status_code}: {endpoint}")
            else:
                print(f"✅ {response.status_code}: {endpoint}")
                
        except requests.exceptions.Timeout:
            print(f"⏱️  TIMEOUT: {endpoint}")
        except requests.exceptions.ConnectionError:
            print(f"🔌 CONNECTION ERROR: {endpoint}")
        except Exception as e:
            print(f"❌ EXCEPTION: {endpoint} - {e}")
    
    # Rapport des erreurs 500
    if errors_500:
        print(f"\n🚨 {len(errors_500)} ERREUR(S) 500 DÉTECTÉE(S):")
        print("=" * 50)
        
        for i, error in enumerate(errors_500, 1):
            print(f"\n{i}. ENDPOINT: {error['endpoint']}")
            print(f"   RESPONSE: {error['response']}")
            print(f"   HEADERS: {error['headers']}")
    else:
        print(f"\n✅ Aucune erreur 500 détectée dans les endpoints testés")
    
    return errors_500

def test_frontend_specific_calls():
    """Test les appels spécifiques que fait le frontend"""
    
    print(f"\n🎯 Test des appels spécifiques du frontend")
    print("-" * 40)
    
    # Simuler les appels que fait le frontend au chargement
    frontend_calls = [
        # Appel initial pour récupérer les employeurs
        "/employers",
        
        # Appels organisationnels avec le premier employeur
        "/organizational-structure/1/tree",
        
        # Appels avec des IDs potentiellement problématiques
        "/organizational-structure/null/tree",
        "/organizational-structure/undefined/tree",
        
        # Appels de validation
        "/organizational-structure/1/validate",
    ]
    
    for call in frontend_calls:
        try:
            print(f"Frontend call: {call}")
            response = requests.get(f"{BASE_URL}{call}")
            
            if response.status_code == 500:
                print(f"❌ ERREUR 500 - C'est probablement ça!")
                print(f"Response: {response.text}")
                return call
            else:
                print(f"✅ {response.status_code}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    return None

def check_backend_logs():
    """Vérifier les logs du backend"""
    
    print(f"\n📋 Vérification des logs backend")
    print("-" * 30)
    
    try:
        # Test simple pour voir si le backend répond
        response = requests.get(f"{BASE_URL}/")
        print(f"Backend status: {response.status_code}")
        
        # Test avec un endpoint qui devrait fonctionner
        response = requests.get(f"{BASE_URL}/employers")
        print(f"Employers endpoint: {response.status_code}")
        
        if response.status_code == 200:
            employers = response.json()
            print(f"Nombre d'employeurs: {len(employers)}")
            
            if employers:
                first_employer_id = employers[0]['id']
                print(f"Premier employeur ID: {first_employer_id}")
                
                # Test avec cet employeur
                response = requests.get(f"{BASE_URL}/organizational-structure/{first_employer_id}/tree")
                print(f"Tree pour employeur {first_employer_id}: {response.status_code}")
                
                if response.status_code == 500:
                    print("❌ ERREUR 500 TROUVÉE ICI!")
                    print(f"Response: {response.text}")
                    return f"/organizational-structure/{first_employer_id}/tree"
        
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")
    
    return None

if __name__ == "__main__":
    print("🚨 DIAGNOSTIC D'URGENCE - ERREUR 500 APRÈS CTRL+F5")
    print("=" * 60)
    
    # 1. Test général des endpoints
    errors_500 = test_all_endpoints()
    
    # 2. Test spécifique frontend
    problematic_call = test_frontend_specific_calls()
    
    # 3. Vérification des logs
    log_issue = check_backend_logs()
    
    # Résumé
    print(f"\n📊 RÉSUMÉ DU DIAGNOSTIC")
    print("=" * 30)
    
    if errors_500 or problematic_call or log_issue:
        print("❌ PROBLÈMES DÉTECTÉS:")
        if errors_500:
            print(f"   - {len(errors_500)} erreurs 500 dans les endpoints")
        if problematic_call:
            print(f"   - Appel frontend problématique: {problematic_call}")
        if log_issue:
            print(f"   - Problème dans les logs: {log_issue}")
    else:
        print("✅ Aucun problème détecté - l'erreur 500 pourrait être intermittente")
    
    print(f"\n💡 PROCHAINES ÉTAPES:")
    print("1. Vérifiez la console F12 > Network pour voir l'URL exacte")
    print("2. Reproduisez l'action qui cause l'erreur")
    print("3. Notez l'URL complète de la requête qui échoue")
    print("4. Relancez ce script pendant que vous reproduisez l'erreur")