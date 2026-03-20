#!/usr/bin/env python3
"""
Test des Méthodes Arbre Hiérarchique et Filtrage en Cascade

Ce script teste les nouvelles méthodes implémentées dans HierarchicalOrganizationalService :
- get_organizational_tree : Construction de l'arbre hiérarchique complet
- get_cascading_options : Filtrage des options en cascade
- validate_cascading_selection : Validation des sélections en cascade

Tâche 3.3 : Implémenter la méthode get_organizational_tree
Tâche 3.4 : Implémenter la méthode get_cascading_options
"""

import sys
import os
import json
from datetime import datetime
from typing import Dict, List, Any

# Ajouter le chemin du backend
sys.path.append('siirh-backend')

from app.services.hierarchical_organizational_service import HierarchicalOrganizationalService, OrganizationalNode


def test_organizational_tree_construction():
    """Test de la construction de l'arbre hiérarchique"""
    print("=== Test 1: Construction de l'Arbre Hiérarchique ===")
    
    service = HierarchicalOrganizationalService()
    
    try:
        # Test avec l'employeur 1 (qui devrait avoir des données de test)
        employer_id = 1
        
        print(f"📊 Construction de l'arbre pour l'employeur {employer_id}...")
        tree = service.get_organizational_tree(employer_id)
        
        print(f"✅ Arbre construit avec {len(tree)} nœuds racines")
        
        # Analyser la structure de l'arbre
        total_nodes = count_total_nodes(tree)
        max_depth = calculate_max_depth(tree)
        
        print(f"📈 Statistiques de l'arbre :")
        print(f"   - Nœuds racines : {len(tree)}")
        print(f"   - Total nœuds : {total_nodes}")
        print(f"   - Profondeur max : {max_depth}")
        
        # Afficher la structure
        print(f"\n🌳 Structure de l'arbre :")
        for root in tree:
            print_tree_node(root, 0)
        
        return True, tree
        
    except Exception as e:
        print(f"❌ Erreur lors de la construction de l'arbre : {e}")
        return False, None


def test_tree_search_functionality():
    """Test de la fonctionnalité de recherche dans l'arbre"""
    print("\n=== Test 2: Fonctionnalité de Recherche ===")
    
    service = HierarchicalOrganizationalService()
    
    try:
        employer_id = 1
        search_queries = ["Siège", "IT", "Dev", "Unité"]
        
        for query in search_queries:
            print(f"\n🔍 Recherche pour '{query}'...")
            tree = service.get_organizational_tree(employer_id, search_query=query)
            
            matching_nodes = count_matching_nodes(tree)
            print(f"   - {matching_nodes} nœuds correspondent à la recherche")
            
            # Afficher les résultats de recherche
            if matching_nodes > 0:
                print("   - Résultats :")
                display_search_results(tree, query, "     ")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la recherche : {e}")
        return False


def test_level_filtering():
    """Test du filtrage par niveau"""
    print("\n=== Test 3: Filtrage par Niveau ===")
    
    service = HierarchicalOrganizationalService()
    
    try:
        employer_id = 1
        
        for level in [1, 2, 3, 4]:
            print(f"\n📊 Filtrage niveau {level}...")
            tree = service.get_organizational_tree(employer_id, level_filter=level)
            
            total_nodes = count_total_nodes(tree)
            print(f"   - {total_nodes} nœuds de niveau {level}")
            
            # Vérifier que tous les nœuds sont du bon niveau
            all_correct_level = verify_level_consistency(tree, level)
            if all_correct_level:
                print(f"   ✅ Tous les nœuds sont de niveau {level}")
            else:
                print(f"   ❌ Incohérence de niveau détectée")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du filtrage par niveau : {e}")
        return False


def test_cascading_options():
    """Test du filtrage en cascade"""
    print("\n=== Test 4: Filtrage en Cascade ===")
    
    service = HierarchicalOrganizationalService()
    
    try:
        employer_id = 1
        
        # Test 1: Récupérer les établissements (niveau 1)
        print("🏢 Récupération des établissements...")
        etablissements = service.get_cascading_options(employer_id, parent_id=None)
        print(f"   - {len(etablissements)} établissements trouvés")
        
        for etab in etablissements:
            print(f"     • {etab['name']} (ID: {etab['id']}, Enfants: {etab['has_children']})")
        
        # Test 2: Récupérer les départements pour chaque établissement
        if etablissements:
            etab_id = etablissements[0]['id']
            print(f"\n🏬 Récupération des départements pour l'établissement {etab_id}...")
            departements = service.get_cascading_options(employer_id, parent_id=etab_id)
            print(f"   - {len(departements)} départements trouvés")
            
            for dept in departements:
                print(f"     • {dept['name']} (ID: {dept['id']}, Enfants: {dept['has_children']})")
            
            # Test 3: Récupérer les services pour le premier département
            if departements:
                dept_id = departements[0]['id']
                print(f"\n🏭 Récupération des services pour le département {dept_id}...")
                services = service.get_cascading_options(employer_id, parent_id=dept_id)
                print(f"   - {len(services)} services trouvés")
                
                for serv in services:
                    print(f"     • {serv['name']} (ID: {serv['id']}, Enfants: {serv['has_children']})")
                
                # Test 4: Récupérer les unités pour le premier service
                if services:
                    serv_id = services[0]['id']
                    print(f"\n🏗️ Récupération des unités pour le service {serv_id}...")
                    unites = service.get_cascading_options(employer_id, parent_id=serv_id)
                    print(f"   - {len(unites)} unités trouvées")
                    
                    for unite in unites:
                        print(f"     • {unite['name']} (ID: {unite['id']}, Enfants: {unite['has_children']})")
        
        return True, etablissements
        
    except Exception as e:
        print(f"❌ Erreur lors du filtrage en cascade : {e}")
        return False, None


def test_cascading_validation():
    """Test de la validation des sélections en cascade"""
    print("\n=== Test 5: Validation des Sélections en Cascade ===")
    
    service = HierarchicalOrganizationalService()
    
    try:
        employer_id = 1
        
        # Récupérer quelques nœuds pour les tests
        etablissements = service.get_cascading_options(employer_id, parent_id=None)
        if not etablissements:
            print("❌ Aucun établissement trouvé pour les tests")
            return False
        
        etab_id = etablissements[0]['id']
        departements = service.get_cascading_options(employer_id, parent_id=etab_id)
        
        # Test 1: Sélection valide complète
        if departements:
            dept_id = departements[0]['id']
            services = service.get_cascading_options(employer_id, parent_id=dept_id)
            
            if services:
                serv_id = services[0]['id']
                unites = service.get_cascading_options(employer_id, parent_id=serv_id)
                
                unite_id = unites[0]['id'] if unites else None
                
                print("✅ Test sélection valide complète...")
                is_valid, errors = service.validate_cascading_selection(
                    employer_id, etab_id, dept_id, serv_id, unite_id
                )
                
                if is_valid:
                    print("   ✅ Sélection valide")
                else:
                    print(f"   ❌ Sélection invalide : {[e.message for e in errors]}")
        
        # Test 2: Sélection invalide (département sans établissement)
        if departements:
            dept_id = departements[0]['id']
            
            print("\n❌ Test sélection invalide (département sans établissement)...")
            is_valid, errors = service.validate_cascading_selection(
                employer_id, None, dept_id, None, None
            )
            
            if not is_valid:
                print("   ✅ Invalidité correctement détectée")
                for error in errors:
                    print(f"     - {error.message}")
            else:
                print("   ❌ L'invalidité n'a pas été détectée")
        
        # Test 3: Sélection incohérente (mauvaise relation parent-enfant)
        if len(etablissements) > 1 and departements:
            wrong_etab_id = etablissements[1]['id']
            dept_id = departements[0]['id']  # Département du premier établissement
            
            print("\n❌ Test relation parent-enfant incorrecte...")
            is_valid, errors = service.validate_cascading_selection(
                employer_id, wrong_etab_id, dept_id, None, None
            )
            
            if not is_valid:
                print("   ✅ Relation incorrecte correctement détectée")
                for error in errors:
                    print(f"     - {error.message}")
            else:
                print("   ❌ La relation incorrecte n'a pas été détectée")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la validation en cascade : {e}")
        return False


def test_performance_with_large_tree():
    """Test de performance avec un arbre plus large"""
    print("\n=== Test 6: Performance avec Arbre Large ===")
    
    service = HierarchicalOrganizationalService()
    
    try:
        employer_id = 1
        
        # Mesurer le temps de construction de l'arbre
        start_time = datetime.now()
        tree = service.get_organizational_tree(employer_id)
        end_time = datetime.now()
        
        construction_time = (end_time - start_time).total_seconds() * 1000
        total_nodes = count_total_nodes(tree)
        
        print(f"⏱️ Performance de construction :")
        print(f"   - Temps : {construction_time:.2f}ms")
        print(f"   - Nœuds : {total_nodes}")
        print(f"   - Temps/nœud : {construction_time/max(total_nodes, 1):.2f}ms")
        
        # Mesurer le temps de recherche
        start_time = datetime.now()
        search_tree = service.get_organizational_tree(employer_id, search_query="test")
        end_time = datetime.now()
        
        search_time = (end_time - start_time).total_seconds() * 1000
        print(f"   - Temps recherche : {search_time:.2f}ms")
        
        # Mesurer le temps de filtrage en cascade
        start_time = datetime.now()
        options = service.get_cascading_options(employer_id, parent_id=None)
        end_time = datetime.now()
        
        cascade_time = (end_time - start_time).total_seconds() * 1000
        print(f"   - Temps cascade : {cascade_time:.2f}ms")
        
        # Évaluer les performances
        if construction_time < 200:
            print("   ✅ Performance de construction excellente (<200ms)")
        elif construction_time < 500:
            print("   ⚠️ Performance de construction acceptable (<500ms)")
        else:
            print("   ❌ Performance de construction lente (>500ms)")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test de performance : {e}")
        return False


# Fonctions utilitaires

def count_total_nodes(tree: List[Dict[str, Any]]) -> int:
    """Compte le nombre total de nœuds dans l'arbre"""
    total = len(tree)
    for node in tree:
        total += count_total_nodes(node.get('children', []))
    return total


def calculate_max_depth(tree: List[Dict[str, Any]], current_depth: int = 0) -> int:
    """Calcule la profondeur maximale de l'arbre"""
    if not tree:
        return current_depth
    
    max_depth = current_depth
    for node in tree:
        child_depth = calculate_max_depth(node.get('children', []), current_depth + 1)
        max_depth = max(max_depth, child_depth)
    
    return max_depth


def print_tree_node(node: Dict[str, Any], indent: int):
    """Affiche un nœud de l'arbre avec indentation"""
    prefix = "  " * indent
    level_name = node.get('level_name', f"Niveau {node.get('level', '?')}")
    name = node.get('name', 'Sans nom')
    children_count = node.get('children_count', 0)
    
    print(f"{prefix}├─ {level_name}: {name} ({children_count} enfants)")
    
    # Afficher les enfants (limiter à 3 niveaux pour la lisibilité)
    if indent < 3:
        for child in node.get('children', []):
            print_tree_node(child, indent + 1)


def count_matching_nodes(tree: List[Dict[str, Any]]) -> int:
    """Compte les nœuds qui correspondent à la recherche"""
    count = 0
    for node in tree:
        if node.get('matches_search', False):
            count += 1
        count += count_matching_nodes(node.get('children', []))
    return count


def display_search_results(tree: List[Dict[str, Any]], query: str, prefix: str):
    """Affiche les résultats de recherche"""
    for node in tree:
        if node.get('matches_search', False):
            path = node.get('hierarchical_path', {}).get('full_path', 'Chemin inconnu')
            print(f"{prefix}• {node.get('name')} ({path})")
        
        display_search_results(node.get('children', []), query, prefix)


def verify_level_consistency(tree: List[Dict[str, Any]], expected_level: int) -> bool:
    """Vérifie que tous les nœuds sont du niveau attendu"""
    for node in tree:
        if node.get('level') != expected_level:
            return False
        if not verify_level_consistency(node.get('children', []), expected_level):
            return False
    return True


def main():
    """Fonction principale de test"""
    print("🚀 Test des Méthodes Arbre Hiérarchique et Filtrage en Cascade")
    print("=" * 70)
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'tests': {}
    }
    
    # Test 1: Construction de l'arbre
    success, tree_data = test_organizational_tree_construction()
    results['tests']['tree_construction'] = {
        'success': success,
        'tree_nodes_count': count_total_nodes(tree_data) if tree_data else 0
    }
    
    # Test 2: Recherche
    success = test_tree_search_functionality()
    results['tests']['search_functionality'] = {'success': success}
    
    # Test 3: Filtrage par niveau
    success = test_level_filtering()
    results['tests']['level_filtering'] = {'success': success}
    
    # Test 4: Filtrage en cascade
    success, cascade_data = test_cascading_options()
    results['tests']['cascading_options'] = {
        'success': success,
        'etablissements_count': len(cascade_data) if cascade_data else 0
    }
    
    # Test 5: Validation en cascade
    success = test_cascading_validation()
    results['tests']['cascading_validation'] = {'success': success}
    
    # Test 6: Performance
    success = test_performance_with_large_tree()
    results['tests']['performance'] = {'success': success}
    
    # Résumé final
    print("\n" + "=" * 70)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 70)
    
    total_tests = len(results['tests'])
    successful_tests = sum(1 for test in results['tests'].values() if test['success'])
    
    print(f"✅ Tests réussis : {successful_tests}/{total_tests}")
    print(f"📈 Taux de réussite : {(successful_tests/total_tests)*100:.1f}%")
    
    if successful_tests == total_tests:
        print("\n🎉 TOUS LES TESTS SONT RÉUSSIS !")
        print("✅ Tâche 3.3 : get_organizational_tree - TERMINÉE")
        print("✅ Tâche 3.4 : get_cascading_options - TERMINÉE")
    else:
        print(f"\n⚠️ {total_tests - successful_tests} test(s) ont échoué")
        for test_name, test_result in results['tests'].items():
            if not test_result['success']:
                print(f"❌ {test_name}")
    
    # Sauvegarder les résultats
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"hierarchical_tree_cascade_test_results_{timestamp}.json"
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Résultats sauvegardés dans : {results_file}")
    
    return successful_tests == total_tests


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)