#!/usr/bin/env python3
"""
Test de la synchronisation automatique lors des modifications de structures
"""

import requests
import json

def test_automatic_sync():
    print('🔄 Test de la synchronisation automatique')
    print('=' * 50)

    # 1. État initial
    print('1️⃣ État initial:')
    response = requests.get('http://localhost:8000/workers?employer_id=2')
    if response.status_code == 200:
        workers = response.json()
        for worker in workers:
            print(f'   {worker["prenom"]} {worker["nom"]}: département = "{worker.get("departement", "N/A")}"')
    
    print()

    # 2. Renommer SWEETY → FACEBOOK (pour tester le changement)
    print('2️⃣ Renommage SWEETY → FACEBOOK:')
    
    # Trouver l'ID de SWEETY
    response = requests.get('http://localhost:8000/organizational-structure/2/tree')
    if response.status_code == 200:
        tree = response.json()
        
        def find_unit_by_name(units, name):
            for unit in units:
                if unit['name'] == name:
                    return unit
                if 'children' in unit:
                    result = find_unit_by_name(unit['children'], name)
                    if result:
                        return result
            return None
        
        sweety_unit = find_unit_by_name(tree.get('tree', []), 'SWEETY')
        
        if sweety_unit:
            print(f'   Trouvé SWEETY (ID: {sweety_unit["id"]})')
            
            # Renommer avec synchronisation automatique
            update_data = {"name": "FACEBOOK"}
            response = requests.put(
                f'http://localhost:8000/organizational-structure/{sweety_unit["id"]}',
                json=update_data
            )
            
            if response.status_code == 200:
                print('   ✅ Renommage réussi avec sync automatique')
                
                # Vérifier les affectations
                response = requests.get('http://localhost:8000/workers?employer_id=2')
                if response.status_code == 200:
                    workers = response.json()
                    for worker in workers:
                        print(f'   Après sync: {worker["prenom"]} {worker["nom"]}: département = "{worker.get("departement", "N/A")}"')
            else:
                print(f'   ❌ Erreur: {response.status_code}')
        else:
            print('   ❌ SWEETY non trouvé')
    
    print()

    # 3. Test du filtrage avec le nouveau nom
    print('3️⃣ Test filtrage avec FACEBOOK:')
    params = {
        'employer_id': 2,
        'period': '2025-01',
        'departement': 'FACEBOOK'
    }
    response = requests.get('http://localhost:8000/payroll/bulk-preview', params=params)
    if response.status_code == 200:
        bulletins = response.json()
        print(f'   ✅ {len(bulletins)} bulletin(s) avec FACEBOOK')
    else:
        print(f'   ❌ Erreur: {response.status_code}')

    print()

    # 4. Renommer à nouveau FACEBOOK → SWEETY
    print('4️⃣ Renommage FACEBOOK → SWEETY:')
    
    response = requests.get('http://localhost:8000/organizational-structure/2/tree')
    if response.status_code == 200:
        tree = response.json()
        facebook_unit = find_unit_by_name(tree.get('tree', []), 'FACEBOOK')
        
        if facebook_unit:
            update_data = {"name": "SWEETY"}
            response = requests.put(
                f'http://localhost:8000/organizational-structure/{facebook_unit["id"]}',
                json=update_data
            )
            
            if response.status_code == 200:
                print('   ✅ Renommage réussi avec sync automatique')
                
                # Vérifier les affectations finales
                response = requests.get('http://localhost:8000/workers?employer_id=2')
                if response.status_code == 200:
                    workers = response.json()
                    for worker in workers:
                        print(f'   Final: {worker["prenom"]} {worker["nom"]}: département = "{worker.get("departement", "N/A")}"')
            else:
                print(f'   ❌ Erreur: {response.status_code}')

    print()

    # 5. Test final du filtrage
    print('5️⃣ Test final avec SWEETY:')
    params = {
        'employer_id': 2,
        'period': '2025-01',
        'departement': 'SWEETY'
    }
    response = requests.get('http://localhost:8000/payroll/bulk-preview', params=params)
    if response.status_code == 200:
        bulletins = response.json()
        print(f'   ✅ {len(bulletins)} bulletin(s) avec SWEETY')
        print('   🎉 Synchronisation automatique fonctionnelle!')
    else:
        print(f'   ❌ Erreur: {response.status_code}')

if __name__ == "__main__":
    test_automatic_sync()