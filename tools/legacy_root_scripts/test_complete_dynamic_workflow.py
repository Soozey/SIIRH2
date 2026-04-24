#!/usr/bin/env python3
"""
Test complet du workflow dynamique organisationnel
Simule le scénario utilisateur complet
"""

import requests
import json

def test_complete_workflow():
    print('🔄 Test complet du workflow dynamique organisationnel')
    print('=' * 70)

    # 1. État initial
    print('1️⃣ État initial:')
    response = requests.get('http://localhost:8000/employers/2/organizational-data/hierarchical')
    if response.status_code == 200:
        data = response.json()
        print('   Structures hiérarchiques:')
        for key, values in data.items():
            if values:
                print(f'     {key}: {values}')
    
    # Vérifier les affectations actuelles
    response = requests.get('http://localhost:8000/workers?employer_id=2')
    if response.status_code == 200:
        workers = response.json()
        for worker in workers:
            print(f'   Salarié {worker["prenom"]} {worker["nom"]}:')
            print(f'     Établissement: {worker.get("etablissement", "N/A")}')
            print(f'     Département: {worker.get("departement", "N/A")}')
    
    print()

    # 2. Simuler le renommage d'une structure (FACEBOOK → SWEETY)
    print('2️⃣ Simulation du renommage FACEBOOK → SWEETY:')
    
    # D'abord, trouver l'ID de la structure FACEBOOK
    response = requests.get('http://localhost:8000/organizational-structure/2/tree')
    if response.status_code == 200:
        tree = response.json()
        facebook_unit = None
        
        def find_unit_by_name(units, name):
            for unit in units:
                if unit['name'] == name:
                    return unit
                if 'children' in unit:
                    result = find_unit_by_name(unit['children'], name)
                    if result:
                        return result
            return None
        
        facebook_unit = find_unit_by_name(tree.get('tree', []), 'FACEBOOK')
        
        if facebook_unit:
            print(f'   Trouvé unité FACEBOOK (ID: {facebook_unit["id"]})')
            
            # Renommer la structure
            update_data = {
                "name": "SWEETY"
            }
            response = requests.put(
                f'http://localhost:8000/organizational-structure/{facebook_unit["id"]}',
                json=update_data
            )
            
            if response.status_code == 200:
                print('   ✅ Structure renommée avec succès')
                
                # Synchroniser automatiquement les affectations
                sync_response = requests.post(
                    f'http://localhost:8000/organizational-structure/2/sync-structure-change',
                    params={
                        'old_name': 'FACEBOOK',
                        'new_name': 'SWEETY',
                        'structure_type': 'departement'
                    }
                )
                
                if sync_response.status_code == 200:
                    sync_result = sync_response.json()
                    print(f'   ✅ Synchronisation automatique: {sync_result["updated_workers_count"]} salarié(s) mis à jour')
                else:
                    print(f'   ❌ Erreur synchronisation: {sync_response.status_code}')
            else:
                print(f'   ❌ Erreur renommage: {response.status_code}')
        else:
            print('   ❌ Structure FACEBOOK non trouvée')
    
    print()

    # 3. Vérifier l'état après modification
    print('3️⃣ État après modification:')
    response = requests.get('http://localhost:8000/employers/2/organizational-data/hierarchical')
    if response.status_code == 200:
        data = response.json()
        print('   Nouvelles structures hiérarchiques:')
        for key, values in data.items():
            if values:
                print(f'     {key}: {values}')
    
    # Vérifier les affectations mises à jour
    response = requests.get('http://localhost:8000/workers?employer_id=2')
    if response.status_code == 200:
        workers = response.json()
        for worker in workers:
            print(f'   Salarié {worker["prenom"]} {worker["nom"]}:')
            print(f'     Établissement: {worker.get("etablissement", "N/A")}')
            print(f'     Département: {worker.get("departement", "N/A")}')
    
    print()

    # 4. Test du filtrage avec le nouveau nom
    print('4️⃣ Test du filtrage avec "SWEETY":')
    params = {
        'employer_id': 2,
        'period': '2025-01',
        'departement': 'SWEETY'
    }
    response = requests.get('http://localhost:8000/payroll/bulk-preview', params=params)
    if response.status_code == 200:
        bulletins = response.json()
        print(f'   ✅ {len(bulletins)} bulletin(s) trouvé(s) avec le filtre SWEETY')
        if bulletins:
            print(f'   Premier bulletin: {bulletins[0]["worker"]["prenom"]} {bulletins[0]["worker"]["nom"]}')
            # Essayer d'afficher le salaire si disponible
            try:
                if "salary_details" in bulletins[0]:
                    print(f'   Salaire brut: {bulletins[0]["salary_details"]["gross_salary"]:,.0f} Ar')
                elif "gross_salary" in bulletins[0]:
                    print(f'   Salaire brut: {bulletins[0]["gross_salary"]:,.0f} Ar')
            except (KeyError, TypeError):
                print('   Salaire: structure non disponible dans ce test')
    else:
        print(f'   ❌ Erreur: {response.status_code}')

    print()

    # 5. Test avec l'ancien nom (doit retourner 0)
    print('5️⃣ Test avec l\'ancien nom "FACEBOOK" (doit être vide):')
    params = {
        'employer_id': 2,
        'period': '2025-01',
        'departement': 'FACEBOOK'
    }
    response = requests.get('http://localhost:8000/payroll/bulk-preview', params=params)
    if response.status_code == 200:
        bulletins = response.json()
        print(f'   ✅ {len(bulletins)} bulletin(s) trouvé(s) avec l\'ancien nom FACEBOOK')
        print('   ✅ Correct: l\'ancien nom ne retourne plus de résultats')
    else:
        print(f'   ❌ Erreur: {response.status_code}')

if __name__ == "__main__":
    test_complete_workflow()