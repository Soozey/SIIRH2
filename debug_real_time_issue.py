#!/usr/bin/env python3
"""
Debug en temps réel du problème utilisateur persistant
"""

import requests
import json

def debug_real_time_issue():
    print('🔍 DEBUG EN TEMPS RÉEL - Problème persistant')
    print('=' * 60)

    # 1. Vérifier l'état EXACT actuel de tous les salariés
    print('1️⃣ État EXACT de tous les salariés de Mandroso Services:')
    response = requests.get('http://localhost:8000/workers?employer_id=2')
    if response.status_code == 200:
        workers = response.json()
        print(f'   Nombre total de salariés: {len(workers)}')
        for worker in workers:
            print(f'   ID {worker["id"]}: {worker["prenom"]} {worker["nom"]}')
            print(f'     Établissement: "{worker.get("etablissement", "VIDE")}"')
            print(f'     Département: "{worker.get("departement", "VIDE")}"')
            print(f'     Service: "{worker.get("service", "VIDE")}"')
            print(f'     Unité: "{worker.get("unite", "VIDE")}"')
            print()
    else:
        print(f'   ❌ Erreur: {response.status_code}')

    print()

    # 2. Vérifier les structures hiérarchiques EXACTES
    print('2️⃣ Structures hiérarchiques EXACTES disponibles:')
    response = requests.get('http://localhost:8000/employers/2/organizational-data/hierarchical')
    if response.status_code == 200:
        data = response.json()
        for key, values in data.items():
            print(f'   {key}: {values}')
    else:
        print(f'   ❌ Erreur: {response.status_code}')

    print()

    # 3. Test de TOUS les filtres possibles
    print('3️⃣ Test de TOUS les filtres possibles:')
    
    # Test sans filtre
    print('   Test SANS FILTRE:')
    params = {'employer_id': 2, 'period': '2025-01'}
    response = requests.get('http://localhost:8000/payroll/bulk-preview', params=params)
    if response.status_code == 200:
        bulletins = response.json()
        print(f'     ✅ {len(bulletins)} bulletin(s) sans filtre')
        for bulletin in bulletins:
            print(f'       - {bulletin["worker"]["prenom"]} {bulletin["worker"]["nom"]}')
    else:
        print(f'     ❌ Erreur: {response.status_code}')

    print()

    # Test avec chaque établissement
    print('   Test avec CHAQUE ÉTABLISSEMENT:')
    etablissements = ['Mandroso Achat', 'Mandroso Formation']
    for etab in etablissements:
        params = {'employer_id': 2, 'period': '2025-01', 'etablissement': etab}
        response = requests.get('http://localhost:8000/payroll/bulk-preview', params=params)
        if response.status_code == 200:
            bulletins = response.json()
            print(f'     "{etab}": {len(bulletins)} bulletin(s)')
            for bulletin in bulletins:
                print(f'       - {bulletin["worker"]["prenom"]} {bulletin["worker"]["nom"]}')
        else:
            print(f'     "{etab}": Erreur {response.status_code}')

    print()

    # Test avec chaque département
    print('   Test avec CHAQUE DÉPARTEMENT:')
    departements = ['AZER']
    for dept in departements:
        params = {'employer_id': 2, 'period': '2025-01', 'departement': dept}
        response = requests.get('http://localhost:8000/payroll/bulk-preview', params=params)
        if response.status_code == 200:
            bulletins = response.json()
            print(f'     "{dept}": {len(bulletins)} bulletin(s)')
            for bulletin in bulletins:
                print(f'       - {bulletin["worker"]["prenom"]} {bulletin["worker"]["nom"]}')
        else:
            print(f'     "{dept}": Erreur {response.status_code}')

    print()

    # 4. Test de la combinaison EXACTE que vous utilisez
    print('4️⃣ Test de la combinaison EXACTE utilisée dans l\'interface:')
    params = {
        'employer_id': 2,
        'period': '2025-01',
        'etablissement': 'Mandroso Achat',
        'departement': 'AZER'
    }
    print(f'   Paramètres: {params}')
    response = requests.get('http://localhost:8000/payroll/bulk-preview', params=params)
    if response.status_code == 200:
        bulletins = response.json()
        print(f'   ✅ {len(bulletins)} bulletin(s) avec cette combinaison')
        if bulletins:
            for bulletin in bulletins:
                print(f'     - {bulletin["worker"]["prenom"]} {bulletin["worker"]["nom"]}')
                print(f'       Salaire brut: {bulletin.get("gross_salary", "N/A")}')
        else:
            print('   ⚠️ AUCUN BULLETIN - C\'est le problème!')
    else:
        print(f'   ❌ Erreur: {response.status_code}')
        print(f'   Détails: {response.text}')

    print()

    # 5. Vérifier si les salariés ont des données de paie
    print('5️⃣ Vérification des données de paie:')
    response = requests.get('http://localhost:8000/workers?employer_id=2')
    if response.status_code == 200:
        workers = response.json()
        for worker in workers:
            print(f'   {worker["prenom"]} {worker["nom"]}:')
            print(f'     Salaire de base: {worker.get("salaire_base", "N/A")}')
            print(f'     Date embauche: {worker.get("date_embauche", "N/A")}')
            print(f'     Actif: {worker.get("date_debauche") is None}')

    print()
    print('🎯 DIAGNOSTIC TERMINÉ - Analysez les résultats ci-dessus')

if __name__ == "__main__":
    debug_real_time_issue()