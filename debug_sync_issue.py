#!/usr/bin/env python3
"""
Debug du problème de synchronisation qui vide les affectations des salariés
"""

import requests
import json

def debug_sync_issue():
    print('🔍 Debug du problème de synchronisation')
    print('=' * 60)

    # 1. Vérifier l'état actuel des salariés
    print('1️⃣ État actuel des salariés:')
    response = requests.get('http://localhost:8000/workers?employer_id=2')
    if response.status_code == 200:
        workers = response.json()
        for worker in workers:
            print(f'   {worker["prenom"]} {worker["nom"]}:')
            print(f'     ID: {worker["id"]}')
            print(f'     Établissement: {worker.get("etablissement", "N/A")}')
            print(f'     Département: {worker.get("departement", "N/A")}')
            print(f'     Service: {worker.get("service", "N/A")}')
            print(f'     Unité: {worker.get("unite", "N/A")}')
            print(f'     organizational_unit_id: {worker.get("organizational_unit_id", "N/A")}')
            print()
    else:
        print(f'   Erreur: {response.status_code}')

    print()

    # 2. Vérifier les structures hiérarchiques disponibles
    print('2️⃣ Structures hiérarchiques disponibles:')
    response = requests.get('http://localhost:8000/employers/2/organizational-data/hierarchical')
    if response.status_code == 200:
        data = response.json()
        for key, values in data.items():
            if values:
                print(f'   {key}: {values}')
    else:
        print(f'   Erreur: {response.status_code}')

    print()

    # 3. Vérifier la validation des affectations
    print('3️⃣ Validation des affectations:')
    response = requests.get('http://localhost:8000/organizational-structure/2/validate-assignments')
    if response.status_code == 200:
        validation = response.json()
        print(f'   Valide: {validation["is_valid"]}')
        print(f'   Erreurs: {validation["errors_count"]}')
        if validation['errors_count'] > 0:
            print('   Détails des erreurs:')
            for error in validation['errors']:
                print(f'     - {error["worker_name"]}: {error["structure_type"]} = "{error["current_value"]}"')
                print(f'       Valeurs disponibles: {error["available_values"]}')
    else:
        print(f'   Erreur: {response.status_code}')

    print()

    # 4. Simuler une synchronisation et voir ce qui se passe
    print('4️⃣ Simulation de synchronisation (ATTENTION: peut vider les données):')
    print('   Voulez-vous continuer? (y/N)')
    # Pour le debug, on va juste analyser sans exécuter
    print('   [Simulation désactivée pour éviter de vider les données]')

if __name__ == "__main__":
    debug_sync_issue()