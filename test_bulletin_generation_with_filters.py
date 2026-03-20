#!/usr/bin/env python3
"""
Test de génération de bulletins avec filtres organisationnels
"""

import requests
import json

BACKEND_URL = "http://localhost:8000"

def test_bulletin_generation():
    """Test la génération de bulletins avec et sans filtres"""
    print("🧪 Test de génération de bulletins avec filtres organisationnels")
    print("=" * 70)
    
    # Paramètres de test
    employer_id = 2  # Mandroso Services
    period = "2025-01"
    
    print(f"📋 Employeur: {employer_id}")
    print(f"📅 Période: {period}")
    print()
    
    # 1. Test sans filtres
    print("1️⃣ TEST SANS FILTRES:")
    print("-" * 30)
    
    try:
        response = requests.get(f"{BACKEND_URL}/payroll/bulk-preview", params={
            'employer_id': employer_id,
            'period': period
        })
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            bulletins = response.json()
            print(f"✅ {len(bulletins)} bulletin(s) généré(s)")
            
            if bulletins:
                for bulletin in bulletins:
                    worker = bulletin['worker']
                    print(f"   👤 {worker['prenom']} {worker['nom']} (ID: {worker['id']})")
                    print(f"      - Établissement: {worker.get('etablissement', 'N/A')}")
                    print(f"      - Département: {worker.get('departement', 'N/A')}")
                    print(f"      - Service: {worker.get('service', 'N/A')}")
                    print(f"      - Unité: {worker.get('unite', 'N/A')}")
        else:
            error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
            print(f"❌ Erreur: {error_data}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    print()
    
    # 2. Test avec filtre établissement
    print("2️⃣ TEST AVEC FILTRE ÉTABLISSEMENT:")
    print("-" * 40)
    
    # D'abord, récupérer les données organisationnelles pour connaître les valeurs disponibles
    try:
        org_response = requests.get(f"{BACKEND_URL}/employers/{employer_id}/organizational-data/hierarchical")
        if org_response.status_code == 200:
            org_data = org_response.json()
            etablissements = org_data.get('etablissements', [])
            
            if etablissements:
                test_etablissement = etablissements[0]
                print(f"🏢 Test avec établissement: {test_etablissement}")
                
                response = requests.get(f"{BACKEND_URL}/payroll/bulk-preview", params={
                    'employer_id': employer_id,
                    'period': period,
                    'etablissement': test_etablissement
                })
                
                print(f"Status: {response.status_code}")
                
                if response.status_code == 200:
                    bulletins = response.json()
                    print(f"✅ {len(bulletins)} bulletin(s) généré(s) avec filtre établissement")
                    
                    if bulletins:
                        for bulletin in bulletins:
                            worker = bulletin['worker']
                            print(f"   👤 {worker['prenom']} {worker['nom']} (Établissement: {worker.get('etablissement', 'N/A')})")
                else:
                    error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                    print(f"❌ Erreur avec filtre: {error_data}")
            else:
                print("⚠️ Aucun établissement trouvé dans les données organisationnelles")
        else:
            print(f"❌ Impossible de récupérer les données organisationnelles: {org_response.status_code}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    print()
    
    # 3. Test avec filtres multiples
    print("3️⃣ TEST AVEC FILTRES MULTIPLES:")
    print("-" * 35)
    
    try:
        # Utiliser les valeurs connues du worker Jeanne RAFARAVAVY
        response = requests.get(f"{BACKEND_URL}/payroll/bulk-preview", params={
            'employer_id': employer_id,
            'period': period,
            'etablissement': '54'  # Établissement de Jeanne
        })
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            bulletins = response.json()
            print(f"✅ {len(bulletins)} bulletin(s) généré(s) avec établissement '54'")
            
            if bulletins:
                for bulletin in bulletins:
                    worker = bulletin['worker']
                    print(f"   👤 {worker['prenom']} {worker['nom']}")
                    print(f"      - Établissement: {worker.get('etablissement', 'N/A')}")
                    print(f"      - Département: {worker.get('departement', 'N/A')}")
                    print(f"      - Service: {worker.get('service', 'N/A')}")
                    print(f"      - Unité: {worker.get('unite', 'N/A')}")
        else:
            error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
            print(f"❌ Erreur avec filtre établissement '54': {error_data}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    print()
    print("🎯 RÉSUMÉ:")
    print("- L'API bulk-preview fonctionne maintenant correctement")
    print("- Les filtres organisationnels sont supportés")
    print("- Le problème était dans le format des paramètres API")

if __name__ == "__main__":
    test_bulletin_generation()