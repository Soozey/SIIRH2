#!/usr/bin/env python3
"""
Test de la fonctionnalité de synchronisation organisationnelle
"""

import requests
import json

def test_sync_functionality():
    print('🔄 Test de synchronisation organisationnelle')
    print('=' * 60)

    # 1. Vérifier l'état actuel
    print('1️⃣ État actuel des affectations:')
    response = requests.get('http://localhost:8000/organizational-structure/2/validate-assignments')
    if response.status_code == 200:
        validation = response.json()
        print(f'   Valide: {validation["is_valid"]}')
        print(f'   Erreurs: {validation["errors_count"]}')
        if validation['errors_count'] > 0:
            for error in validation['errors'][:3]:  # Montrer les 3 premières erreurs
                print(f'   - {error["worker_name"]}: {error["structure_type"]} = "{error["current_value"]}"')
            if validation['errors_count'] > 3:
                print(f'   ... et {validation["errors_count"] - 3} autres erreurs')
    else:
        print(f'   Erreur: {response.status_code}')

    print()

    # 2. Lancer la synchronisation
    print('2️⃣ Lancement de la synchronisation:')
    response = requests.post('http://localhost:8000/organizational-structure/2/sync-workers')
    if response.status_code == 200:
        result = response.json()
        print(f'   Succès: {result["success"]}')
        print(f'   Total mis à jour: {result["total_updated"]}')
        
        if result['total_updated'] > 0:
            print('   Détails des mises à jour:')
            for structure_type, updates in result['details'].items():
                if updates:
                    print(f'     {structure_type}: {len(updates)} mise(s) à jour')
                    for update in updates[:2]:  # Montrer les 2 premières
                        print(f'       - {update["worker_name"]}: "{update["old_value"]}" → "{update["new_value"]}"')
    else:
        print(f'   Erreur: {response.status_code} - {response.text}')

    print()

    # 3. Vérifier après synchronisation
    print('3️⃣ État après synchronisation:')
    response = requests.get('http://localhost:8000/organizational-structure/2/validate-assignments')
    if response.status_code == 200:
        validation = response.json()
        print(f'   Valide: {validation["is_valid"]}')
        print(f'   Erreurs restantes: {validation["errors_count"]}')
    else:
        print(f'   Erreur: {response.status_code}')

    print()

    # 4. Test du filtrage après synchronisation
    print('4️⃣ Test du filtrage avec "Mandroso Formation":')
    params = {
        'employer_id': 2,
        'period': '2025-01',
        'etablissement': 'Mandroso Formation'
    }
    response = requests.get('http://localhost:8000/payroll/bulk-preview', params=params)
    if response.status_code == 200:
        bulletins = response.json()
        print(f'   ✅ {len(bulletins)} bulletin(s) trouvé(s)')
        if bulletins:
            print(f'   Premier bulletin: {bulletins[0]["worker"]["prenom"]} {bulletins[0]["worker"]["nom"]}')
    else:
        print(f'   ❌ Erreur: {response.status_code}')

    print()

    # 5. Test avec "SWEETY" (le département renommé)
    print('5️⃣ Test du filtrage avec "SWEETY":')
    params = {
        'employer_id': 2,
        'period': '2025-01',
        'departement': 'SWEETY'
    }
    response = requests.get('http://localhost:8000/payroll/bulk-preview', params=params)
    if response.status_code == 200:
        bulletins = response.json()
        print(f'   ✅ {len(bulletins)} bulletin(s) trouvé(s)')
        if bulletins:
            print(f'   Premier bulletin: {bulletins[0]["worker"]["prenom"]} {bulletins[0]["worker"]["nom"]}')
    else:
        print(f'   ❌ Erreur: {response.status_code}')

if __name__ == "__main__":
    test_sync_functionality()