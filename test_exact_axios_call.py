#!/usr/bin/env python3
"""
Test exact de l'appel axios comme l'interface
"""

import requests
import json

BACKEND_URL = "http://localhost:8000"

def test_exact_axios_behavior():
    """Teste exactement le comportement d'axios"""
    print("🔍 Test exact du comportement axios")
    print("=" * 70)
    
    employer_id = 2
    period = "2025-01"
    
    # Simuler exactement ce que fait axios avec les paramètres
    params = {
        'employer_id': employer_id,
        'period': period,
        'etablissement': 'Mandroso Formation'
    }
    
    print(f"📋 Paramètres envoyés:")
    for key, value in params.items():
        print(f"   {key}: '{value}' (type: {type(value).__name__})")
    
    print()
    
    # 1. Test avec requests (comme mes tests précédents)
    print("1️⃣ TEST AVEC REQUESTS (mes tests précédents):")
    print("-" * 50)
    
    try:
        response = requests.get(f"{BACKEND_URL}/payroll/bulk-preview", params=params)
        
        print(f"Status: {response.status_code}")
        print(f"URL: {response.url}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Type de réponse: {type(data)}")
            print(f"Longueur: {len(data) if isinstance(data, list) else 'N/A'}")
            
            if isinstance(data, list) and len(data) > 0:
                bulletin = data[0]
                totaux = bulletin.get('totaux', {})
                brut = totaux.get('brut', 0)
                print(f"✅ {len(data)} bulletin(s), Brut: {brut} Ar")
            elif isinstance(data, list):
                print("⚠️ Liste vide retournée")
            else:
                print(f"⚠️ Type de réponse inattendu: {type(data)}")
                print(f"Contenu: {data}")
        else:
            print(f"❌ Erreur: {response.status_code}")
            print(f"Réponse: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    print()
    
    # 2. Test avec différents types de paramètres
    print("2️⃣ TEST AVEC DIFFÉRENTS TYPES DE PARAMÈTRES:")
    print("-" * 50)
    
    test_params_variations = [
        {
            "name": "Paramètres string",
            "params": {
                'employer_id': str(employer_id),
                'period': str(period),
                'etablissement': 'Mandroso Formation'
            }
        },
        {
            "name": "Paramètres avec None pour les filtres vides",
            "params": {
                'employer_id': employer_id,
                'period': period,
                'etablissement': 'Mandroso Formation',
                'departement': None,
                'service': None,
                'unite': None
            }
        },
        {
            "name": "Paramètres avec chaînes vides",
            "params": {
                'employer_id': employer_id,
                'period': period,
                'etablissement': 'Mandroso Formation',
                'departement': '',
                'service': '',
                'unite': ''
            }
        }
    ]
    
    for i, test_case in enumerate(test_params_variations, 1):
        print(f"\n{i}. {test_case['name']}:")
        
        # Nettoyer les paramètres None comme le ferait JavaScript
        clean_params = {k: v for k, v in test_case['params'].items() if v is not None and v != ''}
        
        print(f"   Paramètres nettoyés: {clean_params}")
        
        try:
            response = requests.get(f"{BACKEND_URL}/payroll/bulk-preview", params=clean_params)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    print(f"   ✅ {len(data)} bulletin(s)")
                    if len(data) == 0:
                        print(f"   ⚠️ LISTE VIDE - C'est le problème!")
                else:
                    print(f"   ⚠️ Type inattendu: {type(data)}")
            else:
                print(f"   ❌ Erreur: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    print()
    
    # 3. Test de debug avec headers
    print("3️⃣ TEST AVEC HEADERS COMME AXIOS:")
    print("-" * 40)
    
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json',
        'User-Agent': 'axios/1.6.0'
    }
    
    try:
        response = requests.get(
            f"{BACKEND_URL}/payroll/bulk-preview", 
            params=params,
            headers=headers
        )
        
        print(f"Status: {response.status_code}")
        print(f"Headers envoyés: {headers}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {len(data)} bulletin(s) avec headers axios")
        else:
            print(f"❌ Erreur avec headers: {response.status_code}")
    except Exception as e:
        print(f"❌ Exception: {e}")

def test_backend_logs():
    """Suggère comment capturer les logs backend"""
    print("\n4️⃣ CAPTURE DES LOGS BACKEND:")
    print("-" * 35)
    
    print("🔧 Pour identifier le problème exact:")
    print("1. Dans le terminal où tourne le backend, regardez les logs")
    print("2. Faites l'action dans l'interface qui ne fonctionne pas")
    print("3. Vérifiez si vous voyez une requête vers /payroll/bulk-preview")
    print("4. Regardez les paramètres reçus par le backend")
    print()
    print("💡 Ou ajoutez temporairement des logs dans le backend:")
    print("   Dans siirh-backend/app/routers/payroll.py, ligne ~45:")
    print("   print(f'DEBUG: employer_id={employer_id}, period={period}')")
    print("   print(f'DEBUG: etablissement={etablissement}, departement={departement}')")

def test_worker_data_consistency():
    """Vérifie la cohérence des données du salarié"""
    print("\n5️⃣ VÉRIFICATION COHÉRENCE DONNÉES:")
    print("-" * 40)
    
    try:
        # Récupérer le salarié directement
        response = requests.get(f"{BACKEND_URL}/workers/2032")
        if response.status_code == 200:
            worker = response.json()
            
            print(f"👤 Données actuelles de Jeanne (ID: 2032):")
            print(f"   Employeur ID: {worker.get('employer_id')}")
            print(f"   Établissement: '{worker.get('etablissement')}'")
            print(f"   Département: '{worker.get('departement')}'")
            
            # Vérifier si elle appartient bien à l'employeur 2
            if worker.get('employer_id') != 2:
                print(f"   ❌ PROBLÈME: Le salarié n'appartient pas à l'employeur 2!")
                print(f"      Employeur actuel: {worker.get('employer_id')}")
                return False
            
            # Tester avec ses vraies valeurs
            real_params = {
                'employer_id': 2,
                'period': '2025-01',
                'etablissement': worker.get('etablissement')
            }
            
            print(f"\n🧪 Test avec ses vraies valeurs:")
            print(f"   Paramètres: {real_params}")
            
            response = requests.get(f"{BACKEND_URL}/payroll/bulk-preview", params=real_params)
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ {len(data)} bulletin(s) avec vraies valeurs")
                
                if len(data) == 0:
                    print(f"   ❌ TOUJOURS VIDE! Le problème est ailleurs")
                    
                    # Test sans filtres pour comparaison
                    no_filter_params = {
                        'employer_id': 2,
                        'period': '2025-01'
                    }
                    
                    response2 = requests.get(f"{BACKEND_URL}/payroll/bulk-preview", params=no_filter_params)
                    if response2.status_code == 200:
                        data2 = response2.json()
                        print(f"   📊 Sans filtres: {len(data2)} bulletin(s)")
                        
                        if len(data2) > 0:
                            print(f"   🔍 Le problème est dans le filtrage!")
                        else:
                            print(f"   🔍 Le problème est dans le calcul de base!")
                else:
                    print(f"   ✅ Ça fonctionne avec les vraies valeurs!")
            else:
                print(f"   ❌ Erreur: {response.status_code}")
        else:
            print(f"❌ Impossible de récupérer le salarié: {response.status_code}")
    except Exception as e:
        print(f"❌ Exception: {e}")

def main():
    """Fonction principale"""
    test_exact_axios_behavior()
    test_backend_logs()
    test_worker_data_consistency()

if __name__ == "__main__":
    main()