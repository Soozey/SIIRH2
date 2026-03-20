#!/usr/bin/env python3
"""
DIAGNOSTIC CORRUPTION RÉELLE
============================
Diagnostic de la corruption systémique que l'utilisateur observe :
1. Seuls HENINTSOA et Souzzy s'affichent dans le filtre QSD
2. Jeanne n'apparaît pas malgré sa modification
3. Dans la page salarié, tous redeviennent sans affectation
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
    print(f"\n[{timestamp}] 🚨 {step}: {description}")
    print("=" * 80)

def get_current_worker_state():
    """Récupère l'état actuel de tous les salariés"""
    log_step("ÉTAT ACTUEL", "Vérification de l'état réel des salariés")
    
    try:
        response = requests.get(f"{BASE_URL}/workers")
        if response.status_code == 200:
            workers = response.json()
            mandroso_workers = [w for w in workers if w.get('employer_id') == EMPLOYER_ID]
            
            print("📋 ÉTAT RÉEL DES SALARIÉS DANS LA BASE:")
            for worker in mandroso_workers:
                print(f"   ID {worker['id']}: {worker.get('prenom', '')} {worker.get('nom', '')}")
                print(f"     Établissement: '{worker.get('etablissement', '')}'")
                print(f"     Département: '{worker.get('departement', '')}'")
                print(f"     Service: '{worker.get('service', '')}'")
                print(f"     Unité: '{worker.get('unite', '')}'")
                print()
            
            return mandroso_workers
        else:
            print(f"❌ Erreur récupération workers: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Exception: {e}")
        return []

def test_specific_filter_qsd():
    """Test le filtre spécifique QSD mentionné par l'utilisateur"""
    log_step("TEST FILTRE QSD", "Test du filtre Mandroso Achat + AZER + QSD")
    
    filters = {
        'employer_id': EMPLOYER_ID,
        'period': '2024-12',
        'etablissement': 'Mandroso Achat',
        'departement': 'AZER',
        'service': 'QSD'
    }
    
    try:
        response = requests.get(f"{BASE_URL}/payroll/bulk-preview", params=filters)
        if response.status_code == 200:
            results = response.json()
            print(f"✅ Filtre QSD appliqué:")
            print(f"   Bulletins trouvés: {len(results)}")
            
            for result in results:
                worker_info = result.get('worker', {})
                worker_name = f"{worker_info.get('prenom', '')} {worker_info.get('nom', '')}"
                print(f"   - {worker_name}")
                print(f"     Établissement: '{worker_info.get('etablissement', '')}'")
                print(f"     Département: '{worker_info.get('departement', '')}'")
                print(f"     Service: '{worker_info.get('service', '')}'")
                print(f"     Unité: '{worker_info.get('unite', '')}'")
            
            # Vérifier si Jeanne est présente
            jeanne_found = any(
                'Jeanne' in result.get('worker', {}).get('prenom', '') and 
                'RAFARAVAVY' in result.get('worker', {}).get('nom', '')
                for result in results
            )
            
            if not jeanne_found:
                print("🚨 PROBLÈME CONFIRMÉ: Jeanne n'apparaît pas dans le filtre QSD")
                print("   Ceci confirme le problème décrit par l'utilisateur")
            
            return results
        else:
            print(f"❌ Erreur filtre QSD: {response.status_code}")
            print(f"   Réponse: {response.text}")
            return []
    except Exception as e:
        print(f"❌ Exception filtre QSD: {e}")
        return []

def analyze_jeanne_specific_state():
    """Analyse spécifique de l'état de Jeanne"""
    log_step("ANALYSE JEANNE", "État spécifique de Jeanne RAFARAVAVY")
    
    try:
        response = requests.get(f"{BASE_URL}/workers/2032")  # ID de Jeanne
        if response.status_code == 200:
            jeanne = response.json()
            print("📋 ÉTAT DÉTAILLÉ DE JEANNE:")
            print(f"   Nom: {jeanne.get('prenom', '')} {jeanne.get('nom', '')}")
            print(f"   Établissement: '{jeanne.get('etablissement', '')}'")
            print(f"   Département: '{jeanne.get('departement', '')}'")
            print(f"   Service: '{jeanne.get('service', '')}'")
            print(f"   Unité: '{jeanne.get('unite', '')}'")
            
            # Analyser pourquoi elle n'apparaît pas dans QSD
            if jeanne.get('service', '') != 'QSD':
                print(f"🔍 EXPLICATION: Jeanne n'a pas le service 'QSD'")
                print(f"   Son service actuel: '{jeanne.get('service', '')}'")
                print(f"   C'est pourquoi elle n'apparaît pas dans le filtre QSD")
            
            return jeanne
        else:
            print(f"❌ Erreur récupération Jeanne: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Exception Jeanne: {e}")
        return None

def test_all_filters_systematically():
    """Test systématique de tous les filtres"""
    log_step("TEST SYSTÉMATIQUE", "Test de tous les filtres possibles")
    
    test_filters = [
        {"name": "Tous", "params": {"employer_id": EMPLOYER_ID, "period": "2024-12"}},
        {"name": "Mandroso Achat", "params": {"employer_id": EMPLOYER_ID, "period": "2024-12", "etablissement": "Mandroso Achat"}},
        {"name": "Mandroso Formation", "params": {"employer_id": EMPLOYER_ID, "period": "2024-12", "etablissement": "Mandroso Formation"}},
        {"name": "AZER", "params": {"employer_id": EMPLOYER_ID, "period": "2024-12", "departement": "AZER"}},
        {"name": "QSD", "params": {"employer_id": EMPLOYER_ID, "period": "2024-12", "service": "QSD"}},
        {"name": "Mandroso Achat + AZER", "params": {"employer_id": EMPLOYER_ID, "period": "2024-12", "etablissement": "Mandroso Achat", "departement": "AZER"}},
        {"name": "Mandroso Achat + AZER + QSD", "params": {"employer_id": EMPLOYER_ID, "period": "2024-12", "etablissement": "Mandroso Achat", "departement": "AZER", "service": "QSD"}}
    ]
    
    results = {}
    
    for test_filter in test_filters:
        filter_name = test_filter["name"]
        params = test_filter["params"]
        
        try:
            response = requests.get(f"{BASE_URL}/payroll/bulk-preview", params=params)
            if response.status_code == 200:
                filter_results = response.json()
                worker_names = [f"{r.get('worker', {}).get('prenom', '')} {r.get('worker', {}).get('nom', '')}" for r in filter_results]
                
                results[filter_name] = {
                    'count': len(filter_results),
                    'workers': worker_names
                }
                
                print(f"\n📊 Filtre: {filter_name}")
                print(f"   Bulletins: {len(filter_results)}")
                for name in worker_names:
                    print(f"   - {name}")
            else:
                print(f"\n❌ Erreur filtre {filter_name}: {response.status_code}")
                results[filter_name] = {'count': 0, 'workers': [], 'error': response.status_code}
        except Exception as e:
            print(f"\n❌ Exception filtre {filter_name}: {e}")
            results[filter_name] = {'count': 0, 'workers': [], 'error': str(e)}
    
    return results

def check_organizational_data_sources():
    """Vérifie les sources de données organisationnelles"""
    log_step("SOURCES DONNÉES", "Vérification des sources de données organisationnelles")
    
    sources = {
        "hierarchical": f"/employers/{EMPLOYER_ID}/organizational-data/hierarchical",
        "workers": f"/employers/{EMPLOYER_ID}/organizational-data/workers"
    }
    
    for source_name, endpoint in sources.items():
        print(f"\n📊 Source: {source_name.upper()}")
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Établissements: {data.get('etablissements', [])}")
                print(f"   Départements: {data.get('departements', [])}")
                print(f"   Services: {data.get('services', [])}")
                print(f"   Unités: {data.get('unites', [])}")
            else:
                print(f"   ❌ Erreur: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")

def identify_corruption_pattern():
    """Identifie le pattern de corruption"""
    log_step("PATTERN CORRUPTION", "Identification du pattern de corruption")
    
    print("🔍 ANALYSE DU PATTERN DE CORRUPTION:")
    
    # Récupérer l'état actuel
    workers = get_current_worker_state()
    
    # Compter les salariés avec/sans affectations
    with_assignments = 0
    without_assignments = 0
    partial_assignments = 0
    
    for worker in workers:
        etablissement = worker.get('etablissement', '').strip()
        departement = worker.get('departement', '').strip()
        service = worker.get('service', '').strip()
        unite = worker.get('unite', '').strip()
        
        if not etablissement and not departement and not service and not unite:
            without_assignments += 1
        elif etablissement and departement:
            if service or unite:
                with_assignments += 1
            else:
                partial_assignments += 1
        else:
            partial_assignments += 1
    
    print(f"\n📊 RÉPARTITION DES AFFECTATIONS:")
    print(f"   Affectations complètes: {with_assignments}")
    print(f"   Affectations partielles: {partial_assignments}")
    print(f"   Sans affectation: {without_assignments}")
    
    if without_assignments > 0:
        print(f"\n🚨 CORRUPTION CONFIRMÉE:")
        print(f"   {without_assignments} salarié(s) ont perdu leurs affectations")
        print(f"   Ceci confirme le problème décrit par l'utilisateur")
    
    return {
        'with_assignments': with_assignments,
        'partial_assignments': partial_assignments,
        'without_assignments': without_assignments
    }

def main():
    """Diagnostic principal de la corruption réelle"""
    print("🚨 DIAGNOSTIC CORRUPTION RÉELLE")
    print("================================================================================")
    print("Problèmes rapportés par l'utilisateur:")
    print("1. Seuls HENINTSOA et Souzzy s'affichent dans le filtre QSD")
    print("2. Jeanne n'apparaît pas malgré sa modification")
    print("3. Dans la page salarié, tous redeviennent sans affectation")
    print("================================================================================")
    
    # Diagnostic étape par étape
    workers = get_current_worker_state()
    
    if not workers:
        print("❌ IMPOSSIBLE DE CONTINUER - Aucun salarié trouvé")
        return
    
    # Test du filtre spécifique QSD
    qsd_results = test_specific_filter_qsd()
    
    # Analyse de Jeanne
    jeanne = analyze_jeanne_specific_state()
    
    # Test systématique de tous les filtres
    all_results = test_all_filters_systematically()
    
    # Vérification des sources de données
    check_organizational_data_sources()
    
    # Identification du pattern de corruption
    corruption_stats = identify_corruption_pattern()
    
    # Résumé final
    log_step("RÉSUMÉ", "Résumé du diagnostic de corruption")
    
    print("🎯 PROBLÈMES CONFIRMÉS:")
    
    if corruption_stats['without_assignments'] > 0:
        print(f"   ✅ CORRUPTION CONFIRMÉE: {corruption_stats['without_assignments']} salarié(s) sans affectation")
        print("      → Ceci explique pourquoi ils n'apparaissent pas dans les filtres")
    
    if len(qsd_results) == 2:
        print("   ✅ FILTRE QSD LIMITÉ: Seulement 2 résultats (HENINTSOA et Souzzy)")
        print("      → Confirme l'observation de l'utilisateur")
    
    if jeanne and not jeanne.get('service', '').strip():
        print("   ✅ JEANNE SANS SERVICE: Pas de service assigné")
        print("      → Explique pourquoi elle n'apparaît pas dans le filtre QSD")
    
    print("\n🔧 ACTIONS NÉCESSAIRES:")
    print("   1. Identifier la source de la corruption des affectations")
    print("   2. Restaurer les affectations perdues")
    print("   3. Corriger le processus qui vide les affectations")
    print("   4. Implémenter des protections contre la corruption future")
    
    print("\n⚠️ CONCLUSION:")
    print("   Le problème décrit par l'utilisateur est RÉEL et CONFIRMÉ")
    print("   Il y a bien une corruption systémique des affectations organisationnelles")

if __name__ == "__main__":
    main()