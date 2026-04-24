#!/usr/bin/env python3
"""
DIAGNOSTIC API CALLS FRONTEND
=============================
Examine les appels API spécifiques du frontend pour identifier la corruption
Focus sur les endpoints qui pourraient modifier les données des salariés
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
EMPLOYER_ID = 2  # Mandroso Services

def log_step(step, description):
    """Log une étape avec timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"\n[{timestamp}] 🔍 API {step}: {description}")
    print("=" * 80)

def get_all_workers():
    """Récupère tous les salariés avec leurs affectations"""
    try:
        response = requests.get(f"{BASE_URL}/workers")
        if response.status_code == 200:
            workers = response.json()
            return {w['id']: w for w in workers if w.get('employer_id') == EMPLOYER_ID}
        else:
            print(f"❌ Erreur récupération workers: {response.status_code}")
            return {}
    except Exception as e:
        print(f"❌ Exception récupération workers: {e}")
        return {}

def display_all_assignments(workers, title):
    """Affiche toutes les affectations"""
    print(f"\n📋 {title}")
    print("-" * 80)
    for worker_id, worker in workers.items():
        print(f"   ID {worker_id}: {worker.get('prenom', '')} {worker.get('nom', '')}")
        print(f"     Établissement: '{worker.get('etablissement', '')}'")
        print(f"     Département: '{worker.get('departement', '')}'")
        print(f"     Service: '{worker.get('service', '')}'")
        print(f"     Unité: '{worker.get('unite', '')}'")
        print()

def compare_all_assignments(before, after, step_name):
    """Compare toutes les affectations avant/après"""
    print(f"\n🔍 COMPARAISON APRÈS {step_name}")
    print("-" * 80)
    
    changes_detected = False
    
    for worker_id in before.keys():
        if worker_id not in after:
            print(f"❌ SALARIÉ SUPPRIMÉ: {before[worker_id].get('prenom', '')} {before[worker_id].get('nom', '')}")
            changes_detected = True
            continue
            
        before_data = before[worker_id]
        after_data = after[worker_id]
        
        worker_changes = []
        for field in ['etablissement', 'departement', 'service', 'unite']:
            before_val = before_data.get(field, '')
            after_val = after_data.get(field, '')
            
            if before_val != after_val:
                worker_changes.append(f"{field}: '{before_val}' → '{after_val}'")
        
        if worker_changes:
            print(f"🚨 CHANGEMENTS - {before_data.get('prenom', '')} {before_data.get('nom', '')}:")
            for change in worker_changes:
                print(f"   {change}")
            changes_detected = True
    
    if not changes_detected:
        print("✅ Aucun changement détecté")
    
    return changes_detected

def test_organizational_data_endpoints():
    """Test tous les endpoints de données organisationnelles"""
    log_step("1", "Test endpoints données organisationnelles")
    
    endpoints = [
        f"/employers/{EMPLOYER_ID}/organizational-data/hierarchical",
        f"/employers/{EMPLOYER_ID}/organizational-data/workers",
        f"/employers/{EMPLOYER_ID}/organizational-data/hierarchical-filtered?etablissement=Mandroso%20Formation",
        f"/employers/{EMPLOYER_ID}/organizational-data/filtered?etablissement=Mandroso%20Formation"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            print(f"   {endpoint}: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"     Établissements: {len(data.get('etablissements', []))}")
                print(f"     Départements: {len(data.get('departements', []))}")
            else:
                print(f"     Erreur: {response.text[:100]}")
        except Exception as e:
            print(f"   {endpoint}: ERREUR - {e}")

def test_worker_update_endpoint():
    """Test l'endpoint de mise à jour des salariés"""
    log_step("2", "Test endpoint mise à jour salarié")
    
    # Récupérer d'abord un salarié existant
    worker_id = 2032  # Jeanne
    try:
        response = requests.get(f"{BASE_URL}/workers/{worker_id}")
        if response.status_code == 200:
            worker = response.json()
            print(f"   Salarié récupéré: {worker.get('prenom', '')} {worker.get('nom', '')}")
            
            # Tenter une mise à jour avec les données complètes
            update_data = {
                "employer_id": worker.get('employer_id'),
                "matricule": worker.get('matricule'),
                "nom": worker.get('nom'),
                "prenom": worker.get('prenom'),
                "salaire_base": worker.get('salaire_base'),
                "salaire_horaire": worker.get('salaire_horaire'),
                "vhm": worker.get('vhm'),
                "horaire_hebdo": worker.get('horaire_hebdo'),
                "etablissement": "Mandroso Formation",  # Modification
                "departement": "AZER",
                "service": "TEST SERVICE",  # Ajout pour test
                "unite": "TEST UNITE"  # Ajout pour test
            }
            
            response = requests.put(f"{BASE_URL}/workers/{worker_id}", json=update_data)
            if response.status_code == 200:
                print(f"   ✅ Mise à jour réussie")
                updated_worker = response.json()
                print(f"     Établissement: '{updated_worker.get('etablissement', '')}'")
                print(f"     Service: '{updated_worker.get('service', '')}'")
                print(f"     Unité: '{updated_worker.get('unite', '')}'")
            else:
                print(f"   ❌ Erreur mise à jour: {response.status_code}")
                print(f"   Détails: {response.text}")
        else:
            print(f"   ❌ Erreur récupération salarié: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")

def test_bulk_operations():
    """Test les opérations en lot qui pourraient causer la corruption"""
    log_step("3", "Test opérations en lot")
    
    # Test import/export
    try:
        response = requests.get(f"{BASE_URL}/workers/export")
        print(f"   Export workers: {response.status_code}")
    except Exception as e:
        print(f"   Export workers: ERREUR - {e}")
    
    # Test synchronisation
    try:
        response = requests.post(f"{BASE_URL}/organizational-structure/{EMPLOYER_ID}/sync-workers")
        print(f"   Sync validation: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"     Invalides: {result.get('total_invalid_detected', 0)}")
    except Exception as e:
        print(f"   Sync validation: ERREUR - {e}")

def test_payroll_operations():
    """Test les opérations de paie qui pourraient modifier les données"""
    log_step("4", "Test opérations de paie")
    
    # Test création payroll run
    try:
        response = requests.post(f"{BASE_URL}/payroll/get-or-create-run", params={
            'employer_id': EMPLOYER_ID,
            'period': '2024-12'
        })
        print(f"   Create payroll run: {response.status_code}")
        if response.status_code == 200:
            run_data = response.json()
            print(f"     Run ID: {run_data.get('id')}")
    except Exception as e:
        print(f"   Create payroll run: ERREUR - {e}")
    
    # Test bulk preview (suspect principal)
    try:
        response = requests.get(f"{BASE_URL}/payroll/bulk-preview", params={
            'employer_id': EMPLOYER_ID,
            'period': '2024-12'
        })
        print(f"   Bulk preview: {response.status_code}")
        if response.status_code == 200:
            results = response.json()
            print(f"     Bulletins: {len(results)}")
    except Exception as e:
        print(f"   Bulk preview: ERREUR - {e}")

def test_frontend_specific_calls():
    """Test les appels spécifiques du frontend qui pourraient causer la corruption"""
    log_step("5", "Test appels spécifiques frontend")
    
    # Simuler les appels exacts du frontend OrganizationalFilterModal
    
    # 1. Chargement des employeurs
    try:
        response = requests.get(f"{BASE_URL}/employers")
        print(f"   Load employers: {response.status_code}")
    except Exception as e:
        print(f"   Load employers: ERREUR - {e}")
    
    # 2. Chargement données organisationnelles (hiérarchiques)
    try:
        response = requests.get(f"{BASE_URL}/employers/{EMPLOYER_ID}/organizational-data/hierarchical")
        print(f"   Load org data hierarchical: {response.status_code}")
    except Exception as e:
        print(f"   Load org data hierarchical: ERREUR - {e}")
    
    # 3. Chargement données organisationnelles (workers fallback)
    try:
        response = requests.get(f"{BASE_URL}/employers/{EMPLOYER_ID}/organizational-data/workers")
        print(f"   Load org data workers: {response.status_code}")
    except Exception as e:
        print(f"   Load org data workers: ERREUR - {e}")
    
    # 4. Filtrage en cascade
    try:
        response = requests.get(f"{BASE_URL}/employers/{EMPLOYER_ID}/organizational-data/hierarchical-filtered", params={
            'etablissement': 'Mandroso Formation'
        })
        print(f"   Cascade filtering: {response.status_code}")
    except Exception as e:
        print(f"   Cascade filtering: ERREUR - {e}")

def main():
    """Diagnostic principal des appels API frontend"""
    print("🚨 DIAGNOSTIC API CALLS FRONTEND")
    print("================================================================================")
    print("Identification des appels API qui corrompent les données des salariés")
    print("================================================================================")
    
    # État initial
    log_step("INIT", "CAPTURE ÉTAT INITIAL")
    initial_workers = get_all_workers()
    display_all_assignments(initial_workers, "ÉTAT INITIAL - TOUS LES SALARIÉS")
    
    # Test 1: Endpoints organisationnels
    test_organizational_data_endpoints()
    after_org_endpoints = get_all_workers()
    compare_all_assignments(initial_workers, after_org_endpoints, "ENDPOINTS ORGANISATIONNELS")
    
    # Test 2: Mise à jour salarié
    test_worker_update_endpoint()
    after_worker_update = get_all_workers()
    compare_all_assignments(after_org_endpoints, after_worker_update, "MISE À JOUR SALARIÉ")
    
    # Test 3: Opérations en lot
    test_bulk_operations()
    after_bulk_ops = get_all_workers()
    compare_all_assignments(after_worker_update, after_bulk_ops, "OPÉRATIONS EN LOT")
    
    # Test 4: Opérations de paie
    test_payroll_operations()
    after_payroll_ops = get_all_workers()
    compare_all_assignments(after_bulk_ops, after_payroll_ops, "OPÉRATIONS DE PAIE")
    
    # Test 5: Appels spécifiques frontend
    test_frontend_specific_calls()
    after_frontend_calls = get_all_workers()
    corruption_detected = compare_all_assignments(after_payroll_ops, after_frontend_calls, "APPELS FRONTEND SPÉCIFIQUES")
    
    # Résumé final
    log_step("RÉSUMÉ", "ANALYSE FINALE")
    
    final_workers = get_all_workers()
    total_corruption = compare_all_assignments(initial_workers, final_workers, "WORKFLOW COMPLET")
    
    if total_corruption:
        print("🚨 CORRUPTION DÉTECTÉE!")
        print("   Des modifications non désirées ont été appliquées aux affectations")
        print("   Examiner les logs ci-dessus pour identifier l'étape responsable")
    else:
        print("✅ Aucune corruption détectée")
        print("   Les appels API backend ne corrompent pas les données")
        print("   La corruption pourrait venir d'interactions frontend spécifiques")
    
    print("\n📊 ÉTAT FINAL:")
    display_all_assignments(final_workers, "ÉTAT FINAL - TOUS LES SALARIÉS")

if __name__ == "__main__":
    main()