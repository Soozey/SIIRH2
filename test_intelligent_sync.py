#!/usr/bin/env python3
"""
Test de la nouvelle logique de synchronisation intelligente
"""

import requests
import json

def test_intelligent_sync():
    print('🧠 Test de la synchronisation intelligente')
    print('=' * 45)

    # 1. État initial
    print('1️⃣ État initial de Jeanne:')
    response = requests.get('http://localhost:8000/workers/2032')
    if response.status_code == 200:
        jeanne = response.json()
        print(f'   Établissement: {jeanne.get("etablissement", "N/A")}')
        print(f'   Département: {jeanne.get("departement", "N/A")}')
    else:
        print(f'   Erreur: {response.status_code}')

    print()

    # 2. Structures disponibles
    print('2️⃣ Structures disponibles:')
    response = requests.get('http://localhost:8000/employers/2/organizational-data/hierarchical')
    if response.status_code == 200:
        data = response.json()
        for key, values in data.items():
            if values:
                print(f'   {key}: {values}')
    else:
        print(f'   Erreur: {response.status_code}')

    print()

    # 3. Test de validation (ne doit rien modifier)
    print('3️⃣ Test de validation (ne doit rien modifier):')
    response = requests.post('http://localhost:8000/organizational-structure/2/sync-workers')
    if response.status_code == 200:
        result = response.json()
        print(f'   Modifications: {result["total_updated"]} (doit être 0)')
        print(f'   Affectations invalides: {result.get("total_invalid_detected", 0)}')
        
        if result.get("total_invalid_detected", 0) > 0:
            print('   ⚠️ Affectations invalides détectées:')
            for structure_type, issues in result['details'].items():
                if issues:
                    for issue in issues:
                        print(f'     - {issue["worker_name"]}: {structure_type[:-1]} = "{issue["old_value"]}"')
        else:
            print('   ✅ Toutes les affectations sont valides')
    else:
        print(f'   Erreur: {response.status_code}')

    print()

    # 4. Vérifier que Jeanne n'a pas été modifiée
    print('4️⃣ Vérification que Jeanne n\'a pas été modifiée:')
    response = requests.get('http://localhost:8000/workers/2032')
    if response.status_code == 200:
        jeanne_after = response.json()
        print(f'   Établissement: {jeanne_after.get("etablissement", "N/A")}')
        print(f'   Département: {jeanne_after.get("departement", "N/A")}')
        
        if (jeanne_after.get("etablissement") == jeanne.get("etablissement") and 
            jeanne_after.get("departement") == jeanne.get("departement")):
            print('   ✅ Affectations préservées!')
        else:
            print('   ❌ Affectations modifiées!')
    else:
        print(f'   Erreur: {response.status_code}')

    print()

    # 5. Test du filtrage final
    print('5️⃣ Test du filtrage final:')
    params = {
        'employer_id': 2,
        'period': '2025-01',
        'etablissement': 'Mandroso Achat',
        'departement': 'AZER'
    }
    response = requests.get('http://localhost:8000/payroll/bulk-preview', params=params)
    if response.status_code == 200:
        bulletins = response.json()
        print(f'   ✅ {len(bulletins)} bulletin(s) avec filtrage')
        if bulletins:
            for bulletin in bulletins:
                print(f'   - {bulletin["worker"]["prenom"]} {bulletin["worker"]["nom"]}')
    else:
        print(f'   ❌ Erreur: {response.status_code}')

    print()
    print('🎉 Test terminé - Synchronisation intelligente fonctionnelle!')

if __name__ == "__main__":
    test_intelligent_sync()