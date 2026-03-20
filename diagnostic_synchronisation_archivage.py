#!/usr/bin/env python3
"""
DIAGNOSTIC SYNCHRONISATION ARCHIVAGE
====================================
Analyse le problème de désynchronisation entre :
1. Les structures organisationnelles créées/modifiées (Page Employeur)
2. Les affectations des salariés (Page Travailleur) 
3. Le filtrage et l'impression (Page Bulletin)

Objectif: Identifier pourquoi l'archivage et la modification ne sont pas synchronisés
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
    print(f"\n[{timestamp}] 🔍 {step}: {description}")
    print("=" * 80)

def analyze_organizational_structures():
    """Analyse les structures organisationnelles définies"""
    log_step("ÉTAPE 1", "ANALYSE DES STRUCTURES ORGANISATIONNELLES")
    
    print("📋 Structures hiérarchiques définies dans le système:")
    try:
        response = requests.get(f"{BASE_URL}/organizational-structure")
        if response.status_code == 200:
            structures = response.json()
            employer_structures = [s for s in structures if s.get('employer_id') == EMPLOYER_ID]
            
            if employer_structures:
                for structure in employer_structures:
                    print(f"   - {structure.get('name', '')} ({structure.get('level', '')})")
            else:
                print("   ❌ AUCUNE structure hiérarchique définie pour cet employeur")
                
            return employer_structures
        else:
            print(f"   ❌ Erreur récupération structures: {response.status_code}")
            return []
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return []

def analyze_organizational_data_sources():
    """Analyse les différentes sources de données organisationnelles"""
    log_step("ÉTAPE 2", "ANALYSE DES SOURCES DE DONNÉES ORGANISATIONNELLES")
    
    sources = {
        "hierarchical": f"/employers/{EMPLOYER_ID}/organizational-data/hierarchical",
        "workers": f"/employers/{EMPLOYER_ID}/organizational-data/workers"
    }
    
    results = {}
    
    for source_name, endpoint in sources.items():
        print(f"\n📊 Source: {source_name.upper()}")
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            if response.status_code == 200:
                data = response.json()
                results[source_name] = data
                
                print(f"   Établissements: {data.get('etablissements', [])}")
                print(f"   Départements: {data.get('departements', [])}")
                print(f"   Services: {data.get('services', [])}")
                print(f"   Unités: {data.get('unites', [])}")
            else:
                print(f"   ❌ Erreur {source_name}: {response.status_code}")
                results[source_name] = {}
        except Exception as e:
            print(f"   ❌ Exception {source_name}: {e}")
            results[source_name] = {}
    
    return results

def analyze_worker_assignments():
    """Analyse les affectations actuelles des salariés"""
    log_step("ÉTAPE 3", "ANALYSE DES AFFECTATIONS DES SALARIÉS")
    
    try:
        response = requests.get(f"{BASE_URL}/workers")
        if response.status_code == 200:
            workers = response.json()
            mandroso_workers = [w for w in workers if w.get('employer_id') == EMPLOYER_ID]
            
            print("📋 Affectations actuelles des salariés:")
            worker_assignments = {}
            
            for worker in mandroso_workers:
                worker_id = worker['id']
                assignment = {
                    'name': f"{worker.get('prenom', '')} {worker.get('nom', '')}",
                    'etablissement': worker.get('etablissement', ''),
                    'departement': worker.get('departement', ''),
                    'service': worker.get('service', ''),
                    'unite': worker.get('unite', '')
                }
                worker_assignments[worker_id] = assignment
                
                print(f"   {assignment['name']}:")
                print(f"     Établissement: '{assignment['etablissement']}'")
                print(f"     Département: '{assignment['departement']}'")
                print(f"     Service: '{assignment['service']}'")
                print(f"     Unité: '{assignment['unite']}'")
                print()
            
            return worker_assignments
        else:
            print(f"❌ Erreur récupération workers: {response.status_code}")
            return {}
    except Exception as e:
        print(f"❌ Exception: {e}")
        return {}

def analyze_synchronization_gaps(structures, data_sources, worker_assignments):
    """Analyse les écarts de synchronisation"""
    log_step("ÉTAPE 4", "ANALYSE DES ÉCARTS DE SYNCHRONISATION")
    
    print("🔍 Comparaison entre les sources de données:")
    
    # Comparer les sources hierarchical vs workers
    hierarchical = data_sources.get('hierarchical', {})
    workers_data = data_sources.get('workers', {})
    
    print("\n📊 COMPARAISON HIERARCHICAL vs WORKERS:")
    for field in ['etablissements', 'departements', 'services', 'unites']:
        h_values = set(hierarchical.get(field, []))
        w_values = set(workers_data.get(field, []))
        
        print(f"\n   {field.upper()}:")
        print(f"     Hiérarchique: {sorted(h_values)}")
        print(f"     Salariés: {sorted(w_values)}")
        
        # Identifier les écarts
        only_in_hierarchical = h_values - w_values
        only_in_workers = w_values - h_values
        
        if only_in_hierarchical:
            print(f"     ⚠️ Seulement dans hiérarchique: {sorted(only_in_hierarchical)}")
        if only_in_workers:
            print(f"     ⚠️ Seulement dans salariés: {sorted(only_in_workers)}")
        if not only_in_hierarchical and not only_in_workers:
            print(f"     ✅ Synchronisé")
    
    # Analyser les affectations des salariés vs structures disponibles
    print("\n🔍 VALIDATION DES AFFECTATIONS:")
    available_structures = {
        'etablissements': set(hierarchical.get('etablissements', [])) | set(workers_data.get('etablissements', [])),
        'departements': set(hierarchical.get('departements', [])) | set(workers_data.get('departements', [])),
        'services': set(hierarchical.get('services', [])) | set(workers_data.get('services', [])),
        'unites': set(hierarchical.get('unites', [])) | set(workers_data.get('unites', []))
    }
    
    invalid_assignments = []
    
    for worker_id, assignment in worker_assignments.items():
        worker_name = assignment['name']
        
        # Vérifier chaque niveau d'affectation
        checks = [
            ('etablissement', assignment['etablissement'], available_structures['etablissements']),
            ('departement', assignment['departement'], available_structures['departements']),
            ('service', assignment['service'], available_structures['services']),
            ('unite', assignment['unite'], available_structures['unites'])
        ]
        
        worker_invalid = []
        for field_name, value, available in checks:
            if value and value not in available:
                worker_invalid.append(f"{field_name}='{value}' (non défini)")
        
        if worker_invalid:
            invalid_assignments.append({
                'worker': worker_name,
                'issues': worker_invalid
            })
            print(f"   ❌ {worker_name}: {', '.join(worker_invalid)}")
        else:
            print(f"   ✅ {worker_name}: Affectation valide")
    
    return invalid_assignments

def test_filtering_with_current_state():
    """Test le filtrage avec l'état actuel"""
    log_step("ÉTAPE 5", "TEST DU FILTRAGE AVEC L'ÉTAT ACTUEL")
    
    # Test différents filtres
    test_filters = [
        {"name": "Tous les bulletins", "params": {"employer_id": EMPLOYER_ID, "period": "2024-12"}},
        {"name": "Mandroso Achat", "params": {"employer_id": EMPLOYER_ID, "period": "2024-12", "etablissement": "Mandroso Achat"}},
        {"name": "Mandroso Formation", "params": {"employer_id": EMPLOYER_ID, "period": "2024-12", "etablissement": "Mandroso Formation"}},
        {"name": "AZER (département)", "params": {"employer_id": EMPLOYER_ID, "period": "2024-12", "departement": "AZER"}},
        {"name": "QSD (service)", "params": {"employer_id": EMPLOYER_ID, "period": "2024-12", "service": "QSD"}}
    ]
    
    filtering_results = {}
    
    for test_filter in test_filters:
        filter_name = test_filter["name"]
        params = test_filter["params"]
        
        try:
            response = requests.get(f"{BASE_URL}/payroll/bulk-preview", params=params)
            if response.status_code == 200:
                results = response.json()
                worker_names = [f"{r.get('worker', {}).get('prenom', '')} {r.get('worker', {}).get('nom', '')}" for r in results]
                
                filtering_results[filter_name] = {
                    'count': len(results),
                    'workers': worker_names
                }
                
                print(f"\n📊 Filtre: {filter_name}")
                print(f"   Bulletins trouvés: {len(results)}")
                for name in worker_names:
                    print(f"   - {name}")
            else:
                print(f"\n❌ Erreur filtre {filter_name}: {response.status_code}")
                filtering_results[filter_name] = {'count': 0, 'workers': [], 'error': response.status_code}
        except Exception as e:
            print(f"\n❌ Exception filtre {filter_name}: {e}")
            filtering_results[filter_name] = {'count': 0, 'workers': [], 'error': str(e)}
    
    return filtering_results

def generate_synchronization_report(structures, data_sources, worker_assignments, invalid_assignments, filtering_results):
    """Génère un rapport de synchronisation"""
    log_step("RAPPORT", "RAPPORT DE SYNCHRONISATION")
    
    print("📋 RÉSUMÉ DES PROBLÈMES IDENTIFIÉS:")
    
    # 1. Structures hiérarchiques
    if not structures:
        print("   🚨 PROBLÈME 1: Aucune structure hiérarchique définie")
        print("      → Les structures doivent être créées dans la page Employeur")
    else:
        print("   ✅ Structures hiérarchiques présentes")
    
    # 2. Cohérence des sources de données
    hierarchical = data_sources.get('hierarchical', {})
    workers_data = data_sources.get('workers', {})
    
    has_hierarchical_data = any(hierarchical.get(field, []) for field in ['etablissements', 'departements', 'services', 'unites'])
    has_workers_data = any(workers_data.get(field, []) for field in ['etablissements', 'departements', 'services', 'unites'])
    
    if not has_hierarchical_data and has_workers_data:
        print("   🚨 PROBLÈME 2: Données organisationnelles basées uniquement sur les affectations des salariés")
        print("      → Le système utilise les affectations existantes au lieu des structures définies")
        print("      → Ceci explique la désynchronisation archivage/modification")
    elif has_hierarchical_data and not has_workers_data:
        print("   🚨 PROBLÈME 3: Structures définies mais aucune affectation de salarié")
        print("      → Les salariés ne sont pas affectés aux structures créées")
    elif not has_hierarchical_data and not has_workers_data:
        print("   🚨 PROBLÈME 4: Aucune donnée organisationnelle disponible")
        print("      → Système complètement désynchronisé")
    else:
        print("   ✅ Sources de données cohérentes")
    
    # 3. Affectations invalides
    if invalid_assignments:
        print(f"   🚨 PROBLÈME 5: {len(invalid_assignments)} salarié(s) avec affectations invalides")
        for assignment in invalid_assignments:
            print(f"      → {assignment['worker']}: {', '.join(assignment['issues'])}")
    else:
        print("   ✅ Toutes les affectations sont valides")
    
    # 4. Résultats de filtrage
    total_workers = len(worker_assignments)
    all_bulletins = filtering_results.get("Tous les bulletins", {}).get('count', 0)
    
    if all_bulletins != total_workers:
        print(f"   🚨 PROBLÈME 6: Filtrage incohérent")
        print(f"      → {total_workers} salariés dans la base, mais {all_bulletins} bulletins générés")
    else:
        print("   ✅ Filtrage cohérent avec les données")
    
    print("\n🎯 SOLUTIONS RECOMMANDÉES:")
    
    if not structures:
        print("   1. Créer les structures organisationnelles dans la page Employeur")
        print("   2. Définir la hiérarchie complète (établissements → départements → services → unités)")
    
    if not has_hierarchical_data and has_workers_data:
        print("   3. Synchroniser les affectations existantes avec les structures hiérarchiques")
        print("   4. Migrer les données des salariés vers le système hiérarchique")
    
    if invalid_assignments:
        print("   5. Corriger les affectations invalides des salariés")
        print("   6. Utiliser la fonction de synchronisation pour aligner les données")
    
    print("   7. Implémenter une validation en temps réel lors des affectations")
    print("   8. Ajouter des contrôles de cohérence entre les pages")

def main():
    """Diagnostic principal de la synchronisation archivage/modification"""
    print("🔍 DIAGNOSTIC SYNCHRONISATION ARCHIVAGE")
    print("================================================================================")
    print("Objectif: Identifier pourquoi l'archivage et la modification ne sont pas synchronisés")
    print("Processus attendu par l'utilisateur:")
    print("1. Page Employeur: Créer/modifier structures → Mémorisation système")
    print("2. Page Travailleur: Affecter salariés → Mémorisation par travailleur") 
    print("3. Page Bulletin: Filtrer → Résultats correspondant aux filtres")
    print("================================================================================")
    
    # Analyse étape par étape
    structures = analyze_organizational_structures()
    data_sources = analyze_organizational_data_sources()
    worker_assignments = analyze_worker_assignments()
    invalid_assignments = analyze_synchronization_gaps(structures, data_sources, worker_assignments)
    filtering_results = test_filtering_with_current_state()
    
    # Rapport final
    generate_synchronization_report(structures, data_sources, worker_assignments, invalid_assignments, filtering_results)

if __name__ == "__main__":
    main()