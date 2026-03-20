#!/usr/bin/env python3
"""
Debug du scénario utilisateur exact basé sur les captures d'écran
"""

import requests
import json

def debug_user_scenario():
    print('🔍 Debug du scénario utilisateur exact')
    print('=' * 50)

    # 1. Vérifier l'état actuel de Jeanne
    print('1️⃣ État actuel de Jeanne RAFARAVAVY:')
    response = requests.get('http://localhost:8000/workers?employer_id=2')
    if response.status_code == 200:
        workers = response.json()
        jeanne = None
        for worker in workers:
            if worker['prenom'] == 'Jeanne' and worker['nom'] == 'RAFARAVAVY':
                jeanne = worker
                break
        
        if jeanne:
            print(f'   ID: {jeanne["id"]}')
            print(f'   Établissement: {jeanne.get("etablissement", "N/A")}')
            print(f'   Département: {jeanne.get("departement", "N/A")}')
            print(f'   Service: {jeanne.get("service", "N/A")}')
            print(f'   Unité: {jeanne.get("unite", "N/A")}')
        else:
            print('   ❌ Jeanne non trouvée')
    else:
        print(f'   Erreur: {response.status_code}')

    print()

    # 2. Vérifier les structures disponibles
    print('2️⃣ Structures organisationnelles disponibles:')
    response = requests.get('http://localhost:8000/employers/2/organizational-data/hierarchical')
    if response.status_code == 200:
        data = response.json()
        for key, values in data.items():
            if values:
                print(f'   {key}: {values}')
    else:
        print(f'   Erreur: {response.status_code}')

    print()

    # 3. Restaurer l'affectation correcte de Jeanne
    print('3️⃣ Restauration de l\'affectation correcte:')
    if jeanne:
        # Remettre Jeanne sur "Mandroso Achat" comme dans la Photo 1
        update_data = {
            "etablissement": "Mandroso Achat",
            "departement": "AZER"
        }
        
        response = requests.put(f'http://localhost:8000/workers/{jeanne["id"]}', json=update_data)
        if response.status_code == 200:
            print('   ✅ Affectation restaurée: Mandroso Achat / AZER')
        else:
            print(f'   ❌ Erreur restauration: {response.status_code}')
            print(f'   Détails: {response.text}')

    print()

    # 4. Test du filtrage avec les bonnes valeurs
    print('4️⃣ Test du filtrage avec "Mandroso Achat" + "AZER":')
    params = {
        'employer_id': 2,
        'period': '2025-01',
        'etablissement': 'Mandroso Achat',
        'departement': 'AZER'
    }
    response = requests.get('http://localhost:8000/payroll/bulk-preview', params=params)
    if response.status_code == 200:
        bulletins = response.json()
        print(f'   ✅ {len(bulletins)} bulletin(s) trouvé(s)')
        if bulletins:
            for bulletin in bulletins:
                print(f'   - {bulletin["worker"]["prenom"]} {bulletin["worker"]["nom"]}')
    else:
        print(f'   ❌ Erreur: {response.status_code}')

    print()

    # 5. Vérifier l'état final
    print('5️⃣ Vérification finale de Jeanne:')
    response = requests.get('http://localhost:8000/workers?employer_id=2')
    if response.status_code == 200:
        workers = response.json()
        for worker in workers:
            if worker['prenom'] == 'Jeanne' and worker['nom'] == 'RAFARAVAVY':
                print(f'   Établissement: {worker.get("etablissement", "N/A")}')
                print(f'   Département: {worker.get("departement", "N/A")}')
                print('   ✅ Affectation préservée!')
                break
    else:
        print(f'   Erreur: {response.status_code}')

if __name__ == "__main__":
    debug_user_scenario()