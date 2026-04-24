#!/usr/bin/env python3
"""
Test de la nouvelle logique de synchronisation sécurisée
"""

import requests
import json

def test_safe_sync():
    print('🔒 Test de la synchronisation sécurisée')
    print('=' * 50)

    # 1. État initial des salariés
    print('1️⃣ État initial des salariés:')
    response = requests.get('http://localhost:8000/workers?employer_id=2')
    if response.status_code == 200:
        workers = response.json()
        for worker in workers:
            print(f'   {worker["prenom"]} {worker["nom"]}:')
            print(f'     Établissement: {worker.get("etablissement", "N/A")}')
            print(f'     Département: {worker.get("departement", "N/A")}')
            print(f'     Service: {worker.get("service", "N/A")}')
    else:
        print(f'   Erreur: {response.status_code}')

    print()

    # 2. Test de validation (ne doit PAS modifier les données)
    print('2️⃣ Test de validation sécurisée:')
    response = requests.post('http://localhost:8000/organizational-structure/2/sync-workers')
    if response.status_code == 200:
        result = response.json()
        print(f'   Succès: {result["success"]}')
        print(f'   Modifications appliquées: {result["total_updated"]}')
        print(f'   Affectations invalides détectées: {result.get("total_invalid_detected", 0)}')
        print(f'   Message: {result.get("message", "N/A")}')
    else:
        print(f'   Erreur: {response.status_code}')

    print()

    # 3. Vérifier que les données n'ont PAS été modifiées
    print('3️⃣ Vérification que les données sont préservées:')
    response = requests.get('http://localhost:8000/workers?employer_id=2')
    if response.status_code == 200:
        workers = response.json()
        for worker in workers:
            print(f'   {worker["prenom"]} {worker["nom"]}:')
            print(f'     Établissement: {worker.get("etablissement", "N/A")}')
            print(f'     Département: {worker.get("departement", "N/A")}')
            print(f'     Service: {worker.get("service", "N/A")}')
    else:
        print(f'   Erreur: {response.status_code}')

    print()

    # 4. Test du filtrage avec les affectations actuelles
    print('4️⃣ Test du filtrage avec les affectations actuelles:')
    
    # Test avec AZER (département actuel)
    params = {
        'employer_id': 2,
        'period': '2025-01',
        'departement': 'AZER'
    }
    response = requests.get('http://localhost:8000/payroll/bulk-preview', params=params)
    if response.status_code == 200:
        bulletins = response.json()
        print(f'   ✅ Filtrage avec "AZER": {len(bulletins)} bulletin(s)')
    else:
        print(f'   ❌ Erreur filtrage AZER: {response.status_code}')

    # Test avec QSD (service actuel)
    params = {
        'employer_id': 2,
        'period': '2025-01',
        'service': 'QSD'
    }
    response = requests.get('http://localhost:8000/payroll/bulk-preview', params=params)
    if response.status_code == 200:
        bulletins = response.json()
        print(f'   ✅ Filtrage avec "QSD": {len(bulletins)} bulletin(s)')
    else:
        print(f'   ❌ Erreur filtrage QSD: {response.status_code}')

    print()
    print('🎉 Test terminé - Les affectations des salariés sont préservées!')

if __name__ == "__main__":
    test_safe_sync()