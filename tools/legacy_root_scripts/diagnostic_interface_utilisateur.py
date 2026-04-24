#!/usr/bin/env python3
"""
Diagnostic des couches d'interface utilisateur et des processus automatiques
Identification des sources de désynchronisation
"""

import requests
import json

def diagnostic_interface_utilisateur():
    print('🔍 DIAGNOSTIC INTERFACE UTILISATEUR - Sources de désynchronisation')
    print('=' * 80)

    # 1. Analyser les endpoints utilisés par l'interface
    print('1️⃣ ANALYSE DES ENDPOINTS - Sources de données pour l\'interface')
    print('-' * 60)
    
    # Endpoint pour les données organisationnelles hiérarchiques
    print('   A. Endpoint données hiérarchiques:')
    response = requests.get('http://localhost:8000/employers/2/organizational-data/hierarchical')
    if response.status_code == 200:
        hierarchical_data = response.json()
        print(f'     Établissements disponibles: {hierarchical_data.get("etablissements", [])}')
        print(f'     Départements disponibles: {hierarchical_data.get("departements", [])}')
    else:
        print(f'     ❌ Erreur: {response.status_code}')

    # Endpoint pour les données des salariés (source réelle)
    print('\n   B. Endpoint données salariés (source réelle):')
    response = requests.get('http://localhost:8000/workers?employer_id=2')
    if response.status_code == 200:
        workers = response.json()
        etablissements_reels = set()
        departements_reels = set()
        
        for worker in workers:
            if worker.get("etablissement"):
                etablissements_reels.add(worker["etablissement"])
            if worker.get("departement"):
                departements_reels.add(worker["departement"])
        
        print(f'     Établissements réels des salariés: {list(etablissements_reels)}')
        print(f'     Départements réels des salariés: {list(departements_reels)}')
    else:
        print(f'     ❌ Erreur: {response.status_code}')

    # Endpoint pour les données filtrées
    print('\n   C. Endpoint données filtrées (utilisé par l\'interface):')
    response = requests.get('http://localhost:8000/employers/2/organizational-data/hierarchical-filtered')
    if response.status_code == 200:
        filtered_data = response.json()
        print(f'     Données filtrées: {filtered_data}')
    else:
        print(f'     ❌ Erreur: {response.status_code}')

    print('\n' + '=' * 80)

    # 2. Tester les différents scénarios de filtrage
    print('2️⃣ TEST SCÉNARIOS FILTRAGE - Comportement selon les sources')
    print('-' * 60)
    
    # Scénario A: Filtrage avec données hiérarchiques
    print('   Scénario A: Filtrage avec "Mandroso Formation" (hiérarchique):')
    params = {'employer_id': 2, 'period': '2025-01', 'etablissement': 'Mandroso Formation'}
    response = requests.get('http://localhost:8000/payroll/bulk-preview', params=params)
    if response.status_code == 200:
        bulletins = response.json()
        print(f'     Résultat: {len(bulletins)} bulletin(s)')
    else:
        print(f'     ❌ Erreur: {response.status_code}')

    # Scénario B: Filtrage avec données réelles des salariés
    print('\n   Scénario B: Filtrage avec "Mandroso Achat" (réel salarié):')
    params = {'employer_id': 2, 'period': '2025-01', 'etablissement': 'Mandroso Achat'}
    response = requests.get('http://localhost:8000/payroll/bulk-preview', params=params)
    if response.status_code == 200:
        bulletins = response.json()
        print(f'     Résultat: {len(bulletins)} bulletin(s)')
    else:
        print(f'     ❌ Erreur: {response.status_code}')

    print('\n' + '=' * 80)

    # 3. Analyser les processus de synchronisation automatique
    print('3️⃣ ANALYSE SYNCHRONISATION AUTOMATIQUE - Processus destructifs')
    print('-' * 60)
    
    # Vérifier l'état avant synchronisation
    print('   État avant synchronisation:')
    response = requests.get('http://localhost:8000/workers/2032')
    if response.status_code == 200:
        jeanne_avant = response.json()
        print(f'     Jeanne - Établissement: "{jeanne_avant.get("etablissement", "VIDE")}"')
    
    # Déclencher une validation (ne doit pas modifier)
    print('\n   Déclenchement validation sécurisée:')
    response = requests.post('http://localhost:8000/organizational-structure/2/sync-workers')
    if response.status_code == 200:
        result = response.json()
        print(f'     Modifications: {result["total_updated"]}')
        print(f'     Invalides détectées: {result.get("total_invalid_detected", 0)}')
    else:
        print(f'     ❌ Erreur: {response.status_code}')
    
    # Vérifier l'état après synchronisation
    print('\n   État après synchronisation:')
    response = requests.get('http://localhost:8000/workers/2032')
    if response.status_code == 200:
        jeanne_apres = response.json()
        print(f'     Jeanne - Établissement: "{jeanne_apres.get("etablissement", "VIDE")}"')
        
        if jeanne_avant.get("etablissement") == jeanne_apres.get("etablissement"):
            print('     ✅ Synchronisation sécurisée - Données préservées')
        else:
            print('     ❌ Synchronisation destructive - Données modifiées')
    else:
        print(f'     ❌ Erreur: {response.status_code}')

    print('\n' + '=' * 80)

    # 4. Identifier les sources de confusion dans l'interface
    print('4️⃣ SOURCES DE CONFUSION - Analyse des incohérences interface')
    print('-' * 60)
    
    # Comparer ce que l'interface affiche vs la réalité
    print('   Comparaison Interface vs Réalité:')
    
    # Ce que l'interface propose (structures hiérarchiques)
    response = requests.get('http://localhost:8000/employers/2/organizational-data/hierarchical')
    if response.status_code == 200:
        interface_data = response.json()
        print(f'     Interface propose: {interface_data.get("etablissements", [])}')
    
    # Ce que les salariés ont réellement
    response = requests.get('http://localhost:8000/workers?employer_id=2')
    if response.status_code == 200:
        workers = response.json()
        real_etablissements = set()
        for worker in workers:
            if worker.get("etablissement"):
                real_etablissements.add(worker["etablissement"])
        print(f'     Salariés ont réellement: {list(real_etablissements)}')
        
        # Identifier les incohérences
        interface_etabs = set(interface_data.get("etablissements", []))
        real_etabs = real_etablissements
        
        if interface_etabs != real_etabs:
            print('     ❌ INCOHÉRENCE DÉTECTÉE:')
            print(f'       - Interface propose: {interface_etabs}')
            print(f'       - Salariés utilisent: {real_etabs}')
            print(f'       - Manquant dans interface: {real_etabs - interface_etabs}')
            print(f'       - Inutile dans interface: {interface_etabs - real_etabs}')
        else:
            print('     ✅ Cohérence Interface-Réalité')

    print('\n' + '=' * 80)

    # 5. Test de workflow utilisateur complet
    print('5️⃣ SIMULATION WORKFLOW UTILISATEUR - Reproduction du problème')
    print('-' * 60)
    
    print('   Étape 1: Utilisateur affecte salarié à "Mandroso Achat"')
    # (Déjà fait dans les tests précédents)
    
    print('   Étape 2: Utilisateur ouvre interface filtrage')
    response = requests.get('http://localhost:8000/employers/2/organizational-data/hierarchical')
    if response.status_code == 200:
        interface_options = response.json()
        print(f'     Interface propose: {interface_options.get("etablissements", [])}')
        
        if "Mandroso Achat" in interface_options.get("etablissements", []):
            print('     ✅ "Mandroso Achat" disponible dans interface')
        else:
            print('     ❌ "Mandroso Achat" MANQUANT dans interface')
            print('     🚨 CAUSE IDENTIFIÉE: Interface ne propose pas l\'option choisie par l\'utilisateur')
    
    print('\n   Étape 3: Utilisateur sélectionne filtres et lance traitement')
    params = {'employer_id': 2, 'period': '2025-01', 'etablissement': 'Mandroso Achat'}
    response = requests.get('http://localhost:8000/payroll/bulk-preview', params=params)
    if response.status_code == 200:
        bulletins = response.json()
        print(f'     Résultat: {len(bulletins)} bulletin(s)')
        if len(bulletins) == 0:
            print('     ❌ PROBLÈME CONFIRMÉ: Aucun bulletin malgré affectation correcte')
        else:
            print('     ✅ Filtrage fonctionne')
    else:
        print(f'     ❌ Erreur: {response.status_code}')

    print('\n' + '=' * 80)
    print('🎯 DIAGNOSTIC TERMINÉ - Sources de désynchronisation identifiées')

if __name__ == "__main__":
    diagnostic_interface_utilisateur()