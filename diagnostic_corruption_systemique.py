#!/usr/bin/env python3
"""
DIAGNOSTIC CRITIQUE - Corruption systémique des affectations organisationnelles
Identification du processus destructif qui vide toutes les affectations
"""

import requests
import json

def diagnostic_corruption_systemique():
    print('🚨 DIAGNOSTIC CORRUPTION SYSTÉMIQUE - Régression de masse')
    print('=' * 80)

    # 1. État initial - Capturer TOUTES les affectations avant test
    print('1️⃣ CAPTURE ÉTAT INITIAL - Toutes les affectations')
    print('-' * 60)
    
    response = requests.get('http://localhost:8000/workers?employer_id=2')
    if response.status_code == 200:
        workers_initial = response.json()
        print(f'   Total salariés: {len(workers_initial)}')
        
        affectations_initiales = {}
        for worker in workers_initial:
            worker_id = worker['id']
            affectations_initiales[worker_id] = {
                'nom': f"{worker['prenom']} {worker['nom']}",
                'etablissement': worker.get('etablissement', 'VIDE'),
                'departement': worker.get('departement', 'VIDE'),
                'service': worker.get('service', 'VIDE'),
                'unite': worker.get('unite', 'VIDE')
            }
            
            print(f'   ID {worker_id}: {affectations_initiales[worker_id]["nom"]}')
            print(f'     Établissement: "{affectations_initiales[worker_id]["etablissement"]}"')
            print(f'     Département: "{affectations_initiales[worker_id]["departement"]}"')
            print(f'     Service: "{affectations_initiales[worker_id]["service"]}"')
            print(f'     Unité: "{affectations_initiales[worker_id]["unite"]}"')
            print()
    else:
        print(f'   ❌ Erreur: {response.status_code}')
        return

    print('=' * 80)

    # 2. Simulation du processus de filtrage destructif
    print('2️⃣ SIMULATION PROCESSUS FILTRAGE - Déclenchement de la corruption')
    print('-' * 60)
    
    print('   Étape A: Test filtrage simple (lecture seule)')
    params = {
        'employer_id': 2,
        'period': '2025-01',
        'etablissement': 'Mandroso Achat',
        'departement': 'AZER'
    }
    
    response = requests.get('http://localhost:8000/payroll/bulk-preview', params=params)
    if response.status_code == 200:
        bulletins = response.json()
        print(f'     Résultat: {len(bulletins)} bulletin(s)')
        for bulletin in bulletins:
            print(f'       - {bulletin["worker"]["prenom"]} {bulletin["worker"]["nom"]}')
    else:
        print(f'     ❌ Erreur filtrage: {response.status_code}')

    print('\n   Étape B: Vérification immédiate après filtrage')
    response = requests.get('http://localhost:8000/workers?employer_id=2')
    if response.status_code == 200:
        workers_apres_filtrage = response.json()
        
        corruption_detectee = False
        for worker in workers_apres_filtrage:
            worker_id = worker['id']
            initial = affectations_initiales[worker_id]
            
            etab_actuel = worker.get('etablissement', 'VIDE')
            dept_actuel = worker.get('departement', 'VIDE')
            
            if (etab_actuel != initial['etablissement'] or 
                dept_actuel != initial['departement']):
                
                if not corruption_detectee:
                    print('     🚨 CORRUPTION DÉTECTÉE:')
                    corruption_detectee = True
                
                print(f'       {initial["nom"]}:')
                print(f'         Établissement: "{initial["etablissement"]}" → "{etab_actuel}"')
                print(f'         Département: "{initial["departement"]}" → "{dept_actuel}"')
        
        if not corruption_detectee:
            print('     ✅ Aucune corruption détectée après filtrage simple')
    else:
        print(f'     ❌ Erreur vérification: {response.status_code}')

    print('\n' + '=' * 80)

    # 3. Test des processus de synchronisation
    print('3️⃣ TEST PROCESSUS SYNCHRONISATION - Identification du destructeur')
    print('-' * 60)
    
    print('   Test A: Validation sécurisée')
    response = requests.post('http://localhost:8000/organizational-structure/2/sync-workers')
    if response.status_code == 200:
        result = response.json()
        print(f'     Modifications: {result["total_updated"]}')
        print(f'     Invalides détectées: {result.get("total_invalid_detected", 0)}')
        
        if result["total_updated"] > 0:
            print('     🚨 PROCESSUS DESTRUCTIF: La validation modifie les données!')
        else:
            print('     ✅ Validation sécurisée')
    else:
        print(f'     ❌ Erreur validation: {response.status_code}')

    # Vérification après validation
    print('\n   Vérification après validation:')
    response = requests.get('http://localhost:8000/workers?employer_id=2')
    if response.status_code == 200:
        workers_apres_validation = response.json()
        
        corruption_validation = False
        for worker in workers_apres_validation:
            worker_id = worker['id']
            initial = affectations_initiales[worker_id]
            
            etab_actuel = worker.get('etablissement', 'VIDE')
            dept_actuel = worker.get('departement', 'VIDE')
            
            if (etab_actuel != initial['etablissement'] or 
                dept_actuel != initial['departement']):
                
                if not corruption_validation:
                    print('     🚨 CORRUPTION PAR VALIDATION:')
                    corruption_validation = True
                
                print(f'       {initial["nom"]}:')
                print(f'         Établissement: "{initial["etablissement"]}" → "{etab_actuel}"')
                print(f'         Département: "{initial["departement"]}" → "{dept_actuel}"')
        
        if not corruption_validation:
            print('     ✅ Validation n\'a pas corrompu les données')

    print('\n' + '=' * 80)

    # 4. Test de synchronisation forcée
    print('4️⃣ TEST SYNCHRONISATION FORCÉE - Le vrai coupable ?')
    print('-' * 60)
    
    print('   Déclenchement synchronisation forcée...')
    response = requests.post('http://localhost:8000/organizational-structure/2/force-sync-workers')
    if response.status_code == 200:
        result = response.json()
        print(f'     Modifications forcées: {result["total_updated"]}')
        
        if result["total_updated"] > 0:
            print('     🚨 SYNCHRONISATION FORCÉE DESTRUCTIVE!')
            print('     Détails des modifications:')
            for structure_type, updates in result['details'].items():
                if updates:
                    print(f'       {structure_type}: {len(updates)} modification(s)')
                    for update in updates[:3]:  # Montrer les 3 premières
                        print(f'         - {update["worker_name"]}: "{update["old_value"]}" → "{update["new_value"]}"')
        else:
            print('     ✅ Synchronisation forcée n\'a rien modifié')
    else:
        print(f'     ❌ Erreur sync forcée: {response.status_code}')

    # Vérification finale
    print('\n   État final après synchronisation forcée:')
    response = requests.get('http://localhost:8000/workers?employer_id=2')
    if response.status_code == 200:
        workers_final = response.json()
        
        print('     État de tous les salariés:')
        corruption_finale = False
        
        for worker in workers_final:
            worker_id = worker['id']
            initial = affectations_initiales[worker_id]
            
            etab_final = worker.get('etablissement', 'VIDE')
            dept_final = worker.get('departement', 'VIDE')
            
            print(f'       {initial["nom"]}:')
            print(f'         Établissement: "{etab_final}"')
            print(f'         Département: "{dept_final}"')
            
            if etab_final == 'VIDE' or dept_final == 'VIDE':
                corruption_finale = True
                print(f'         🚨 DONNÉES VIDÉES!')
            elif (etab_final != initial['etablissement'] or 
                  dept_final != initial['departement']):
                corruption_finale = True
                print(f'         🚨 DONNÉES MODIFIÉES!')
        
        if corruption_finale:
            print('\n     🚨 CORRUPTION SYSTÉMIQUE CONFIRMÉE!')
            print('     💀 RÉGRESSION DE MASSE: Toutes les affectations corrompues')
        else:
            print('\n     ✅ Données préservées')

    print('\n' + '=' * 80)

    # 5. Analyse des endpoints suspects
    print('5️⃣ ANALYSE ENDPOINTS SUSPECTS - Sources de corruption')
    print('-' * 60)
    
    print('   Analyse du moteur de paie:')
    # Vérifier si le moteur de paie modifie les données
    params = {'employer_id': 2, 'period': '2025-01'}
    response = requests.get('http://localhost:8000/payroll/bulk-preview', params=params)
    if response.status_code == 200:
        print('     ✅ Endpoint payroll accessible')
    else:
        print(f'     ❌ Erreur payroll: {response.status_code}')

    print('\n   Analyse des données organisationnelles:')
    response = requests.get('http://localhost:8000/employers/2/organizational-data/hierarchical')
    if response.status_code == 200:
        org_data = response.json()
        print(f'     Structures disponibles: {org_data}')
    else:
        print(f'     ❌ Erreur org data: {response.status_code}')

    print('\n' + '=' * 80)
    print('🎯 DIAGNOSTIC TERMINÉ - Coupable identifié')

if __name__ == "__main__":
    diagnostic_corruption_systemique()