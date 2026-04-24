#!/usr/bin/env python3
"""
DIAGNOSTIC TRACE CORRUPTION COMPLÈTE
====================================
Trace exactement le processus utilisateur pour identifier la source de corruption
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
EMPLOYER_ID = 2  # Mandroso Services (correct ID)

def log_step(step, description):
    """Log une étape avec timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"\n[{timestamp}] 🔍 ÉTAPE {step}: {description}")
    print("=" * 80)

def get_worker_assignments():
    """Récupère l'état actuel des affectations"""
    try:
        response = requests.get(f"{BASE_URL}/workers")
        if response.status_code == 200:
            workers = response.json()
            assignments = {}
            for worker in workers:
                if worker.get('employer_id') == EMPLOYER_ID:
                    assignments[worker['id']] = {
                        'name': f"{worker.get('prenom', '')} {worker.get('nom', '')}",
                        'etablissement': worker.get('etablissement', ''),
                        'departement': worker.get('departement', ''),
                        'service': worker.get('service', ''),
                        'unite': worker.get('unite', '')
                    }
            return assignments
        else:
            print(f"❌ Erreur récupération workers: {response.status_code}")
            return {}
    except Exception as e:
        print(f"❌ Exception récupération workers: {e}")
        return {}

def display_assignments(assignments, title):
    """Affiche les affectations de manière lisible"""
    print(f"\n📋 {title}")
    print("-" * 60)
    for worker_id, data in assignments.items():
        print(f"   ID {worker_id}: {data['name']}")
        print(f"     Établissement: '{data['etablissement']}'")
        print(f"     Département: '{data['departement']}'")
        print(f"     Service: '{data['service']}'")
        print(f"     Unité: '{data['unite']}'")
        print()

def compare_assignments(before, after, step_name):
    """Compare les affectations avant/après et détecte les changements"""
    print(f"\n🔍 COMPARAISON APRÈS {step_name}")
    print("-" * 60)
    
    changes_detected = False
    
    for worker_id in before.keys():
        if worker_id not in after:
            print(f"❌ SALARIÉ SUPPRIMÉ: {before[worker_id]['name']}")
            changes_detected = True
            continue
            
        before_data = before[worker_id]
        after_data = after[worker_id]
        
        for field in ['etablissement', 'departement', 'service', 'unite']:
            before_val = before_data.get(field, '')
            after_val = after_data.get(field, '')
            
            if before_val != after_val:
                print(f"🚨 CHANGEMENT DÉTECTÉ - {before_data['name']}:")
                print(f"   {field}: '{before_val}' → '{after_val}'")
                changes_detected = True
    
    if not changes_detected:
        print("✅ Aucun changement détecté")
    
    return changes_detected

def test_organizational_data_endpoints():
    """Test les endpoints de données organisationnelles"""
    log_step("A", "Test des endpoints de données organisationnelles")
    
    endpoints = [
        f"/employers/{EMPLOYER_ID}/organizational-data/hierarchical",
        f"/employers/{EMPLOYER_ID}/organizational-data/workers",
        f"/employers/{EMPLOYER_ID}/organizational-data/hierarchical-filtered?etablissement=Mandroso Formation"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            print(f"   {endpoint}: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"     Établissements: {data.get('etablissements', [])}")
                print(f"     Départements: {data.get('departements', [])}")
        except Exception as e:
            print(f"   {endpoint}: ERREUR - {e}")

def test_sync_validation():
    """Test la validation de synchronisation"""
    log_step("B", "Test validation synchronisation")
    
    try:
        response = requests.post(f"{BASE_URL}/organizational-structure/{EMPLOYER_ID}/sync-workers")
        print(f"   Validation sync: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"     Succès: {result.get('success')}")
            print(f"     Invalides détectées: {result.get('total_invalid_detected', 0)}")
            print(f"     Message: {result.get('message', 'N/A')}")
        else:
            print(f"     Erreur: {response.text}")
    except Exception as e:
        print(f"   Validation sync: ERREUR - {e}")

def test_sync_force():
    """Test la synchronisation forcée"""
    log_step("C", "Test synchronisation forcée")
    
    try:
        response = requests.post(f"{BASE_URL}/organizational-structure/{EMPLOYER_ID}/force-sync-workers")
        print(f"   Sync forcée: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"     Succès: {result.get('success')}")
            print(f"     Mises à jour: {result.get('total_updated', 0)}")
            print(f"     Message: {result.get('message', 'N/A')}")
        else:
            print(f"     Erreur: {response.text}")
    except Exception as e:
        print(f"   Sync forcée: ERREUR - {e}")

def test_payroll_filtering():
    """Test le filtrage de paie qui pourrait causer la corruption"""
    log_step("D", "Test filtrage de paie (source potentielle de corruption)")
    
    # Test sans filtres
    try:
        response = requests.get(f"{BASE_URL}/payroll/bulk-preview", params={
            'employer_id': EMPLOYER_ID,
            'period': '2024-12'
        })
        print(f"   Bulk preview sans filtres: {response.status_code}")
        if response.status_code == 200:
            results = response.json()
            print(f"     Bulletins générés: {len(results)}")
        else:
            print(f"     Erreur: {response.text}")
    except Exception as e:
        print(f"   Bulk preview sans filtres: ERREUR - {e}")
    
    # Test avec filtres
    try:
        response = requests.get(f"{BASE_URL}/payroll/bulk-preview", params={
            'employer_id': EMPLOYER_ID,
            'period': '2024-12',
            'etablissement': 'Mandroso Formation',
            'departement': 'AZER'
        })
        print(f"   Bulk preview avec filtres: {response.status_code}")
        if response.status_code == 200:
            results = response.json()
            print(f"     Bulletins filtrés: {len(results)}")
        else:
            print(f"     Erreur: {response.text}")
    except Exception as e:
        print(f"   Bulk preview avec filtres: ERREUR - {e}")

def main():
    """Processus principal de diagnostic"""
    print("🚨 DIAGNOSTIC TRACE CORRUPTION COMPLÈTE")
    print("================================================================================")
    print("Simulation du workflow utilisateur pour identifier la source de corruption")
    print("================================================================================")
    
    # ÉTAPE 1: Capture état initial
    log_step("1", "CAPTURE ÉTAT INITIAL")
    initial_assignments = get_worker_assignments()
    display_assignments(initial_assignments, "ÉTAT INITIAL DES AFFECTATIONS")
    
    # ÉTAPE 2: Test des endpoints organisationnels
    test_organizational_data_endpoints()
    after_org_data = get_worker_assignments()
    compare_assignments(initial_assignments, after_org_data, "TEST ENDPOINTS ORGANISATIONNELS")
    
    # ÉTAPE 3: Test validation synchronisation
    test_sync_validation()
    after_sync_validation = get_worker_assignments()
    compare_assignments(after_org_data, after_sync_validation, "VALIDATION SYNCHRONISATION")
    
    # ÉTAPE 4: Test synchronisation forcée
    test_sync_force()
    after_sync_force = get_worker_assignments()
    compare_assignments(after_sync_validation, after_sync_force, "SYNCHRONISATION FORCÉE")
    
    # ÉTAPE 5: Test filtrage de paie (suspect principal)
    test_payroll_filtering()
    after_payroll_filtering = get_worker_assignments()
    corruption_detected = compare_assignments(after_sync_force, after_payroll_filtering, "FILTRAGE DE PAIE")
    
    # ÉTAPE 6: Résumé final
    log_step("FINAL", "RÉSUMÉ DU DIAGNOSTIC")
    
    if corruption_detected:
        print("🚨 CORRUPTION DÉTECTÉE LORS DU FILTRAGE DE PAIE!")
        print("   Le processus de génération des bulletins avec filtres modifie les affectations")
        print("   Ceci explique pourquoi les salariés perdent leurs affectations après filtrage")
    else:
        print("✅ Aucune corruption détectée dans les processus testés")
        print("   La corruption pourrait venir d'un autre processus non testé")
    
    print("\n📊 ÉTAT FINAL DES AFFECTATIONS:")
    display_assignments(after_payroll_filtering, "ÉTAT FINAL")
    
    print("\n🎯 RECOMMANDATIONS:")
    if corruption_detected:
        print("   1. Examiner le code de bulk-preview dans payroll.py")
        print("   2. Vérifier si des modifications de base de données sont effectuées")
        print("   3. Implémenter des transactions read-only pour les opérations de lecture")
    else:
        print("   1. Tester d'autres processus (import Excel, modifications manuelles)")
        print("   2. Vérifier les logs du serveur pendant l'utilisation réelle")
        print("   3. Implémenter un monitoring en temps réel des modifications")

if __name__ == "__main__":
    main()