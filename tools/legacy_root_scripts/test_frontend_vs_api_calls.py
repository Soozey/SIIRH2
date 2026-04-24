#!/usr/bin/env python3
"""
Test pour comparer les appels API directs vs ce que fait le frontend
"""

import requests
import json

BACKEND_URL = "http://localhost:8000"

def test_exact_frontend_calls():
    """Teste exactement les mêmes appels que fait le frontend"""
    print("🔍 Test des appels API exacts du frontend")
    print("=" * 70)
    
    worker_id = 2032  # Jeanne RAFARAVAVY
    employer_id = 2   # Mandroso Services
    period = "2025-01"
    
    # 1. Simuler l'appel exact du frontend pour bulletin individuel
    print("1️⃣ SIMULATION APPEL FRONTEND - BULLETIN INDIVIDUEL:")
    print("-" * 55)
    
    try:
        # Headers que le frontend pourrait envoyer
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        response = requests.get(
            f"{BACKEND_URL}/payroll/preview",
            params={
                'worker_id': worker_id,
                'period': period
            },
            headers=headers
        )
        
        print(f"Status: {response.status_code}")
        print(f"Headers envoyés: {headers}")
        print(f"URL complète: {response.url}")
        
        if response.status_code == 200:
            bulletin = response.json()
            
            # Afficher la structure complète du bulletin
            print(f"\n📄 Structure complète du bulletin:")
            print(f"   Keys: {list(bulletin.keys())}")
            
            if 'totaux' in bulletin:
                totaux = bulletin['totaux']
                print(f"   Totaux keys: {list(totaux.keys())}")
                for key, value in totaux.items():
                    print(f"      {key}: {value}")
            
            if 'lines' in bulletin:
                lines = bulletin['lines']
                print(f"\n   📋 {len(lines)} ligne(s) de calcul:")
                for i, line in enumerate(lines[:3]):  # Afficher les 3 premières
                    print(f"      {i+1}. {line.get('label', 'N/A')}: {line.get('montant_sal', 0)} Ar")
            
            # Vérifier les données du worker dans la réponse
            if 'worker' in bulletin:
                worker = bulletin['worker']
                print(f"\n   👤 Données worker dans la réponse:")
                print(f"      Salaire base: {worker.get('salaire_base', 'N/A')}")
                print(f"      VHM: {worker.get('vhm', 'N/A')}")
                print(f"      Type régime: {worker.get('type_regime_id', 'N/A')}")
        else:
            print(f"❌ Erreur: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    print()
    
    # 2. Vérifier les données brutes du worker
    print("2️⃣ VÉRIFICATION DONNÉES BRUTES DU WORKER:")
    print("-" * 45)
    
    try:
        response = requests.get(f"{BACKEND_URL}/workers/{worker_id}")
        if response.status_code == 200:
            worker = response.json()
            
            print(f"👤 Données brutes de Jeanne:")
            print(f"   ID: {worker.get('id')}")
            print(f"   Nom: {worker.get('prenom')} {worker.get('nom')}")
            print(f"   Salaire base: {worker.get('salaire_base')} (type: {type(worker.get('salaire_base'))})")
            print(f"   VHM: {worker.get('vhm')} (type: {type(worker.get('vhm'))})")
            print(f"   Salaire horaire: {worker.get('salaire_horaire')} (type: {type(worker.get('salaire_horaire'))})")
            print(f"   Type régime: {worker.get('type_regime_id')} (type: {type(worker.get('type_regime_id'))})")
            print(f"   Employeur ID: {worker.get('employer_id')} (type: {type(worker.get('employer_id'))})")
            
            # Vérifier si les valeurs sont None ou 0
            salaire_base = worker.get('salaire_base')
            if salaire_base is None:
                print("   ⚠️ PROBLÈME: salaire_base est None")
            elif salaire_base == 0:
                print("   ⚠️ PROBLÈME: salaire_base est 0")
            elif isinstance(salaire_base, str):
                print("   ⚠️ PROBLÈME: salaire_base est une string")
            else:
                print(f"   ✅ salaire_base semble correct: {salaire_base}")
        else:
            print(f"❌ Erreur récupération worker: {response.status_code}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    print()
    
    # 3. Test avec différents formats de paramètres
    print("3️⃣ TEST DIFFÉRENTS FORMATS DE PARAMÈTRES:")
    print("-" * 45)
    
    test_params = [
        {'worker_id': worker_id, 'period': period},
        {'worker_id': str(worker_id), 'period': period},
        {'worker_id': worker_id, 'period': str(period)},
    ]
    
    for i, params in enumerate(test_params, 1):
        print(f"\n{i}. Test avec params: {params}")
        print(f"   Types: worker_id={type(params['worker_id'])}, period={type(params['period'])}")
        
        try:
            response = requests.get(f"{BACKEND_URL}/payroll/preview", params=params)
            
            if response.status_code == 200:
                bulletin = response.json()
                totaux = bulletin.get('totaux', {})
                brut = totaux.get('brut_total', 0)
                print(f"   ✅ Status 200, Brut: {brut} Ar")
                
                if brut > 0:
                    print(f"   🎉 SUCCÈS! Ce format fonctionne")
                    return True
            else:
                print(f"   ❌ Status: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    return False

def test_payvar_creation():
    """Teste la création d'un PayVar pour forcer le calcul"""
    print("\n4️⃣ TEST CRÉATION PAYVAR:")
    print("-" * 30)
    
    worker_id = 2032
    period = "2025-01"
    
    # Créer un PayVar minimal pour cette période
    payvar_data = {
        "worker_id": worker_id,
        "period": period,
        "prime_fixe": 0.0,
        "prime_variable": 0.0,
        "abs_non_remu_j": 0,
        "abs_maladie_j": 0
    }
    
    try:
        # Vérifier si PayVar existe déjà
        print("🔍 Vérification PayVar existant...")
        
        # Créer ou mettre à jour PayVar
        print("🔄 Création/mise à jour PayVar...")
        
        # Note: Il faudrait l'endpoint POST /payvar, mais testons d'abord sans
        
        # Test bulletin après
        response = requests.get(f"{BACKEND_URL}/payroll/preview", params={
            'worker_id': worker_id,
            'period': period
        })
        
        if response.status_code == 200:
            bulletin = response.json()
            totaux = bulletin.get('totaux', {})
            brut = totaux.get('brut_total', 0)
            print(f"✅ Bulletin après PayVar: Brut {brut} Ar")
        else:
            print(f"❌ Erreur après PayVar: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Exception PayVar: {e}")

def main():
    """Fonction principale"""
    print("🚀 Diagnostic Frontend vs API")
    print("=" * 70)
    
    success = test_exact_frontend_calls()
    
    if not success:
        test_payvar_creation()
        
        print(f"\n🎯 CONCLUSION:")
        print(f"Le problème semble être dans le calcul de paie lui-même.")
        print(f"Tous les appels API retournent Brut: 0 Ar")
        print(f"\n💡 SUGGESTIONS:")
        print(f"1. Vérifiez dans l'interface si le bulletin affiché a vraiment des valeurs > 0")
        print(f"2. Ouvrez les outils de développement (F12) et regardez les appels réseau")
        print(f"3. Vérifiez si l'interface fait des appels différents ou avec d'autres paramètres")

if __name__ == "__main__":
    main()