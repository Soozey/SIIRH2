#!/usr/bin/env python3
"""
Trouve le bon employeur avec des salariés pour le diagnostic
"""

import requests

def main():
    # Récupérer les employeurs
    response = requests.get('http://localhost:8000/employers')
    employers = response.json()
    print('EMPLOYEURS DISPONIBLES:')
    for emp in employers:
        print(f'  ID {emp["id"]}: {emp["raison_sociale"]}')

    # Récupérer les salariés
    print('\nSALARIES PAR EMPLOYEUR:')
    response = requests.get('http://localhost:8000/workers')
    workers = response.json()
    
    from collections import defaultdict
    by_employer = defaultdict(list)
    for worker in workers:
        by_employer[worker['employer_id']].append({
            'name': f'{worker["prenom"]} {worker["nom"]}',
            'etablissement': worker.get('etablissement', ''),
            'departement': worker.get('departement', ''),
            'id': worker['id']
        })

    for emp_id, worker_list in by_employer.items():
        emp_name = next((e['raison_sociale'] for e in employers if e['id'] == emp_id), 'Inconnu')
        print(f'\n  Employeur {emp_id} ({emp_name}): {len(worker_list)} salarié(s)')
        for worker in worker_list:
            print(f'    - ID {worker["id"]}: {worker["name"]} | Étab: "{worker["etablissement"]}" | Dép: "{worker["departement"]}"')

if __name__ == "__main__":
    main()