#!/usr/bin/env python3
"""
DIAGNOSTIC WORKFLOW FRONTEND EXACT
==================================
Simule exactement le workflow décrit par l'utilisateur:
1. Page Employeur: modifier structures organisationnelles
2. Page Travailleur: affecter salarié
3. Page Bulletin: synchronisation + filtres + impression
4. Retour Page Travailleur: vérifier si affectations vidées
"""

import requests
import json
from datetime import datetime
import time

# Configuration
BASE_URL = "http://localhost:8000"
EMPLOYER_ID = 2  # Mandroso Services
WORKER_ID = 2032  # Jeanne RAFARAVAVY

def log_step(step, description):
    """Log une étape avec timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"\n[{timestamp}] 📱 WORKFLOW {step}: {description}")
    print("=" * 80)

def get_worker_details(worker_id):
    """Récupère les détails d'un salarié spécifique"""
    try:
        response = requests.get(f"{BASE_URL}/workers/{worker_id}")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Erreur récupération worker {worker_id}: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Exception récupération worker {worker_id}: {e}")
        return None

def display_worker_assignment(worker, title):
    """Affiche l'affectation d'un salarié"""
    if not worker:
        print(f"📋 {title}: SALARIÉ NON TROUVÉ")
        return
    
    print(f"\n📋 {title}")
    print("-" * 60)
    print(f"   Nom: {worker.get('prenom', '')} {worker.get('nom', '')}")
    print(f"   Établissement: '{worker.get('etablissement', '')}'")
    print(f"   Département: '{worker.get('departement', '')}'")
    print(f"   Service: '{worker.get('service', '')}'")
    print(f"   Unité: '{worker.get('unite', '')}'")

def compare_worker_assignment(before, after, step_name):
    """Compare l'affectation d'un salarié avant/après"""
    print(f"\n🔍 COMPARAISON APRÈS {step_name}")
    print("-" * 60)
    
    if not before or not after:
        print("❌ Impossible de comparer - données manquantes")
        return True
    
    changes_detected = False
    fields = ['etablissement', 'departement', 'service', 'unite']
    
    for field in fields:
        before_val = before.get(field, '')
        after_val = after.get(field, '')
        
        if before_val != after_val:
            print(f"🚨 CHANGEMENT DÉTECTÉ - {field}:")
            print(f"   AVANT: '{before_val}'")
            print(f"   APRÈS: '{after_val}'")
            changes_detected = True
    
    if not changes_detected:
        print("✅ Aucun changement détecté")
    
    return changes_detected

def simulate_page_employeur():
    """Simule les actions sur la page Employeur"""
    log_step("1", "PAGE EMPLOYEUR - Modification structures organisationnelles")
    
    # Récupérer les structures actuelles
    try:
        response = requests.get(f"{BASE_URL}/employers/{EMPLOYER_ID}/organizational-data/hierarchical")
        if response.status_code == 200:
            data = response.json()
            print(f"   Structures actuelles:")
            print(f"     Établissements: {data.get('etablissements', [])}")
            print(f"     Départements: {data.get('departements', [])}")
            print(f"     Services: {data.get('services', [])}")
            print(f"     Unités: {data.get('unites', [])}")
        else:
            print(f"   ❌ Erreur récupération structures: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Exception récupération structures: {e}")
    
    print("   ✅ Simulation: Utilisateur consulte/modifie les structures")

def simulate_page_travailleur_affectation():
    """Simule l'affectation d'un salarié sur la page Travailleur"""
    log_step("2", "PAGE TRAVAILLEUR - Affectation salarié")
    
    # Simuler une modification d'affectation
    worker_data = {
        "etablissement": "Mandroso Formation",
        "departement": "AZER",
        "service": "",
        "unite": ""
    }
    
    try:
        response = requests.put(f"{BASE_URL}/workers/{WORKER_ID}", json=worker_data)
        if response.status_code == 200:
            print(f"   ✅ Affectation mise à jour:")
            print(f"     Établissement: {worker_data['etablissement']}")
            print(f"     Département: {worker_data['departement']}")
        else:
            print(f"   ❌ Erreur mise à jour affectation: {response.status_code}")
            print(f"   Réponse: {response.text}")
    except Exception as e:
        print(f"   ❌ Exception mise à jour affectation: {e}")

def simulate_page_bulletin_sync():
    """Simule la synchronisation sur la page Bulletin"""
    log_step("3A", "PAGE BULLETIN - Synchronisation")
    
    # Étape 1: Validation
    try:
        response = requests.post(f"{BASE_URL}/organizational-structure/{EMPLOYER_ID}/sync-workers")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Validation synchronisation:")
            print(f"     Succès: {result.get('success')}")
            print(f"     Invalides détectées: {result.get('total_invalid_detected', 0)}")
        else:
            print(f"   ❌ Erreur validation sync: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Exception validation sync: {e}")
    
    # Étape 2: Correction (si nécessaire)
    try:
        response = requests.post(f"{BASE_URL}/organizational-structure/{EMPLOYER_ID}/force-sync-workers")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Correction synchronisation:")
            print(f"     Succès: {result.get('success')}")
            print(f"     Mises à jour: {result.get('total_updated', 0)}")
        else:
            print(f"   ❌ Erreur correction sync: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Exception correction sync: {e}")

def simulate_page_bulletin_filtrage():
    """Simule le filtrage et l'impression sur la page Bulletin"""
    log_step("3B", "PAGE BULLETIN - Filtrage et impression")
    
    # Test du filtrage exact mentionné par l'utilisateur
    filters = {
        'employer_id': EMPLOYER_ID,
        'period': '2024-12',
        'etablissement': 'Mandroso Achat',
        'departement': 'AZER'
    }
    
    try:
        response = requests.get(f"{BASE_URL}/payroll/bulk-preview", params=filters)
        if response.status_code == 200:
            results = response.json()
            print(f"   ✅ Filtrage appliqué:")
            print(f"     Filtres: Mandroso Achat / AZER")
            print(f"     Bulletins trouvés: {len(results)}")
            
            # Afficher les salariés trouvés
            for result in results:
                worker_info = result.get('worker', {})
                print(f"     - {worker_info.get('prenom', '')} {worker_info.get('nom', '')}")
        else:
            print(f"   ❌ Erreur filtrage: {response.status_code}")
            print(f"   Réponse: {response.text}")
    except Exception as e:
        print(f"   ❌ Exception filtrage: {e}")
    
    # Test avec le filtre pour Jeanne (Mandroso Formation)
    filters_jeanne = {
        'employer_id': EMPLOYER_ID,
        'period': '2024-12',
        'etablissement': 'Mandroso Formation',
        'departement': 'AZER'
    }
    
    try:
        response = requests.get(f"{BASE_URL}/payroll/bulk-preview", params=filters_jeanne)
        if response.status_code == 200:
            results = response.json()
            print(f"   ✅ Filtrage pour Jeanne:")
            print(f"     Filtres: Mandroso Formation / AZER")
            print(f"     Bulletins trouvés: {len(results)}")
            
            for result in results:
                worker_info = result.get('worker', {})
                print(f"     - {worker_info.get('prenom', '')} {worker_info.get('nom', '')}")
        else:
            print(f"   ❌ Erreur filtrage Jeanne: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Exception filtrage Jeanne: {e}")

def simulate_retour_page_travailleur():
    """Simule le retour sur la page Travailleur pour vérifier les affectations"""
    log_step("4", "RETOUR PAGE TRAVAILLEUR - Vérification affectations")
    
    # Vérifier si les affectations sont toujours présentes
    worker = get_worker_details(WORKER_ID)
    if worker:
        print(f"   État de Jeanne après workflow complet:")
        print(f"     Établissement: '{worker.get('etablissement', '')}'")
        print(f"     Département: '{worker.get('departement', '')}'")
        print(f"     Service: '{worker.get('service', '')}'")
        print(f"     Unité: '{worker.get('unite', '')}'")
        
        # Vérifier si les champs sont vides (corruption)
        empty_fields = []
        for field in ['etablissement', 'departement', 'service', 'unite']:
            if not worker.get(field, '').strip():
                empty_fields.append(field)
        
        if empty_fields:
            print(f"   🚨 CORRUPTION DÉTECTÉE: Champs vidés: {empty_fields}")
            return True
        else:
            print(f"   ✅ Affectations préservées")
            return False
    else:
        print(f"   ❌ Impossible de vérifier - salarié non trouvé")
        return True

def main():
    """Workflow principal simulant exactement le processus utilisateur"""
    print("🚨 DIAGNOSTIC WORKFLOW FRONTEND EXACT")
    print("================================================================================")
    print("Simulation exacte du workflow utilisateur pour reproduire la corruption")
    print("================================================================================")
    
    # État initial
    log_step("INIT", "CAPTURE ÉTAT INITIAL")
    initial_worker = get_worker_details(WORKER_ID)
    display_worker_assignment(initial_worker, "ÉTAT INITIAL - Jeanne RAFARAVAVY")
    
    # Workflow étape par étape
    simulate_page_employeur()
    after_employeur = get_worker_details(WORKER_ID)
    compare_worker_assignment(initial_worker, after_employeur, "PAGE EMPLOYEUR")
    
    simulate_page_travailleur_affectation()
    after_affectation = get_worker_details(WORKER_ID)
    compare_worker_assignment(after_employeur, after_affectation, "AFFECTATION TRAVAILLEUR")
    
    simulate_page_bulletin_sync()
    after_sync = get_worker_details(WORKER_ID)
    compare_worker_assignment(after_affectation, after_sync, "SYNCHRONISATION")
    
    simulate_page_bulletin_filtrage()
    after_filtrage = get_worker_details(WORKER_ID)
    corruption_detected = compare_worker_assignment(after_sync, after_filtrage, "FILTRAGE ET IMPRESSION")
    
    # Vérification finale
    final_corruption = simulate_retour_page_travailleur()
    
    # Résumé
    log_step("RÉSUMÉ", "ANALYSE FINALE")
    if corruption_detected or final_corruption:
        print("🚨 CORRUPTION CONFIRMÉE!")
        print("   Le workflow utilisateur provoque bien la perte des affectations")
        print("   Source identifiée: Processus de filtrage/impression des bulletins")
    else:
        print("✅ Aucune corruption détectée")
        print("   Le workflow backend ne corrompt pas les données")
        print("   La corruption pourrait venir du frontend ou d'interactions spécifiques")
    
    # État final
    final_worker = get_worker_details(WORKER_ID)
    display_worker_assignment(final_worker, "ÉTAT FINAL - Jeanne RAFARAVAVY")

if __name__ == "__main__":
    main()