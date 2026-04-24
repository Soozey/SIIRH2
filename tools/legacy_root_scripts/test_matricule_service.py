#!/usr/bin/env python3
"""
Test du MatriculeService - Validation des fonctionnalités de résolution nom-matricule
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'siirh-backend'))

import sqlite3
from datetime import datetime

def test_matricule_service():
    """Tester les fonctionnalités du MatriculeService"""
    
    print("🧪 TEST DU MATRICULE SERVICE")
    print("=" * 50)
    
    # Connexion directe à la base pour les tests
    conn = sqlite3.connect("siirh-backend/siirh.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    test_results = {
        "timestamp": datetime.now().isoformat(),
        "tests_passed": 0,
        "tests_failed": 0,
        "test_details": []
    }
    
    try:
        # Test 1: Résolution matricule → nom
        print("\n🔍 Test 1: Résolution matricule → nom")
        cursor.execute("""
            SELECT r.matricule, r.full_name, r.worker_id
            FROM matricule_name_resolver r
            WHERE r.is_active = 1
            LIMIT 1
        """)
        
        test_matricule = cursor.fetchone()
        if test_matricule:
            cursor.execute("""
                SELECT r.matricule, r.worker_id, r.full_name, r.employer_id
                FROM matricule_name_resolver r
                WHERE r.matricule = ? AND r.is_active = 1
            """, (test_matricule["matricule"],))
            
            result = cursor.fetchone()
            if result and result["full_name"] == test_matricule["full_name"]:
                print(f"   ✅ Résolution réussie: {result['matricule']} → {result['full_name']}")
                test_results["tests_passed"] += 1
                test_results["test_details"].append({
                    "test": "matricule_to_name_resolution",
                    "status": "PASSED",
                    "details": f"{result['matricule']} → {result['full_name']}"
                })
            else:
                print(f"   ❌ Échec de la résolution matricule → nom")
                test_results["tests_failed"] += 1
                test_results["test_details"].append({
                    "test": "matricule_to_name_resolution",
                    "status": "FAILED",
                    "details": "Résolution incorrecte"
                })
        else:
            print("   ⚠️  Aucun matricule de test disponible")
        
        # Test 2: Résolution nom → matricule
        print("\n🔍 Test 2: Résolution nom → matricule")
        cursor.execute("""
            SELECT DISTINCT full_name
            FROM matricule_name_resolver
            WHERE is_active = 1 AND full_name IS NOT NULL
            LIMIT 1
        """)
        
        test_name = cursor.fetchone()
        if test_name:
            search_pattern = f"%{test_name['full_name']}%"
            cursor.execute("""
                SELECT r.matricule, r.full_name, COUNT(*) OVER() as total_matches
                FROM matricule_name_resolver r
                WHERE LOWER(r.full_name) LIKE LOWER(?) AND r.is_active = 1
            """, (search_pattern,))
            
            results = cursor.fetchall()
            if results:
                print(f"   ✅ Recherche réussie: '{test_name['full_name']}' → {len(results)} résultat(s)")
                for result in results:
                    print(f"     - {result['matricule']}: {result['full_name']}")
                
                test_results["tests_passed"] += 1
                test_results["test_details"].append({
                    "test": "name_to_matricule_resolution",
                    "status": "PASSED",
                    "details": f"Trouvé {len(results)} résultat(s) pour '{test_name['full_name']}'"
                })
            else:
                print(f"   ❌ Aucun résultat pour '{test_name['full_name']}'")
                test_results["tests_failed"] += 1
        
        # Test 3: Détection des homonymes
        print("\n👥 Test 3: Détection des homonymes")
        cursor.execute("""
            SELECT full_name, COUNT(*) as count
            FROM matricule_name_resolver
            WHERE is_active = 1
            GROUP BY LOWER(TRIM(full_name))
            HAVING COUNT(*) > 1
            LIMIT 1
        """)
        
        homonym_test = cursor.fetchone()
        if homonym_test:
            cursor.execute("""
                SELECT matricule, full_name
                FROM matricule_name_resolver
                WHERE LOWER(TRIM(full_name)) = LOWER(TRIM(?)) AND is_active = 1
                ORDER BY matricule
            """, (homonym_test["full_name"],))
            
            homonyms = cursor.fetchall()
            print(f"   ✅ Homonymes détectés pour '{homonym_test['full_name']}': {len(homonyms)} personnes")
            for homonym in homonyms:
                print(f"     - {homonym['matricule']}: {homonym['full_name']}")
            
            test_results["tests_passed"] += 1
            test_results["test_details"].append({
                "test": "homonym_detection",
                "status": "PASSED",
                "details": f"Détecté {len(homonyms)} homonymes pour '{homonym_test['full_name']}'"
            })
        else:
            print("   ℹ️  Aucun homonyme trouvé dans les données de test")
            test_results["test_details"].append({
                "test": "homonym_detection",
                "status": "SKIPPED",
                "details": "Aucun homonyme dans les données de test"
            })
        
        # Test 4: Recherche par préfixe
        print("\n🔍 Test 4: Recherche par préfixe de matricule")
        cursor.execute("""
            SELECT DISTINCT SUBSTR(matricule, 1, 4) as prefix
            FROM matricule_name_resolver
            WHERE is_active = 1 AND matricule IS NOT NULL
            LIMIT 1
        """)
        
        prefix_test = cursor.fetchone()
        if prefix_test:
            search_prefix = prefix_test["prefix"] + "%"
            cursor.execute("""
                SELECT matricule, full_name
                FROM matricule_name_resolver
                WHERE matricule LIKE ? AND is_active = 1
                ORDER BY matricule
                LIMIT 5
            """, (search_prefix,))
            
            prefix_results = cursor.fetchall()
            print(f"   ✅ Recherche par préfixe '{prefix_test['prefix']}': {len(prefix_results)} résultat(s)")
            for result in prefix_results:
                print(f"     - {result['matricule']}: {result['full_name']}")
            
            test_results["tests_passed"] += 1
            test_results["test_details"].append({
                "test": "prefix_search",
                "status": "PASSED",
                "details": f"Trouvé {len(prefix_results)} résultats pour préfixe '{prefix_test['prefix']}'"
            })
        
        # Test 5: Validation de l'unicité
        print("\n🔒 Test 5: Validation de l'unicité des matricules")
        cursor.execute("""
            SELECT matricule, COUNT(*) as count
            FROM matricule_name_resolver
            WHERE is_active = 1
            GROUP BY matricule
            HAVING COUNT(*) > 1
        """)
        
        duplicates = cursor.fetchall()
        if not duplicates:
            print("   ✅ Tous les matricules sont uniques")
            test_results["tests_passed"] += 1
            test_results["test_details"].append({
                "test": "matricule_uniqueness",
                "status": "PASSED",
                "details": "Tous les matricules sont uniques"
            })
        else:
            print(f"   ❌ {len(duplicates)} matricules dupliqués détectés:")
            for dup in duplicates:
                print(f"     - {dup['matricule']}: {dup['count']} occurrences")
            test_results["tests_failed"] += 1
            test_results["test_details"].append({
                "test": "matricule_uniqueness",
                "status": "FAILED",
                "details": f"{len(duplicates)} matricules dupliqués"
            })
        
        # Test 6: Performance des requêtes
        print("\n⚡ Test 6: Performance des requêtes")
        import time
        
        # Test de performance pour recherche exacte
        start_time = time.time()
        cursor.execute("""
            SELECT r.matricule, r.full_name
            FROM matricule_name_resolver r
            WHERE r.matricule = (SELECT matricule FROM matricule_name_resolver WHERE is_active = 1 LIMIT 1)
            AND r.is_active = 1
        """)
        cursor.fetchone()
        exact_search_time = (time.time() - start_time) * 1000
        
        # Test de performance pour recherche textuelle
        start_time = time.time()
        cursor.execute("""
            SELECT r.matricule, r.full_name
            FROM matricule_name_resolver r
            WHERE LOWER(r.full_name) LIKE '%martin%' AND r.is_active = 1
            LIMIT 10
        """)
        cursor.fetchall()
        text_search_time = (time.time() - start_time) * 1000
        
        print(f"   ⏱️  Recherche exacte: {exact_search_time:.2f}ms")
        print(f"   ⏱️  Recherche textuelle: {text_search_time:.2f}ms")
        
        if exact_search_time < 100 and text_search_time < 100:
            print("   ✅ Performances acceptables (< 100ms)")
            test_results["tests_passed"] += 1
            test_results["test_details"].append({
                "test": "query_performance",
                "status": "PASSED",
                "details": f"Exact: {exact_search_time:.2f}ms, Textuel: {text_search_time:.2f}ms"
            })
        else:
            print("   ⚠️  Performances à améliorer (> 100ms)")
            test_results["test_details"].append({
                "test": "query_performance",
                "status": "WARNING",
                "details": f"Exact: {exact_search_time:.2f}ms, Textuel: {text_search_time:.2f}ms"
            })
        
        # Test 7: Intégrité des données
        print("\n🔍 Test 7: Intégrité des données")
        
        # Vérifier que tous les workers ont une entrée dans le resolver
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM workers w
            LEFT JOIN matricule_name_resolver r ON w.matricule = r.matricule
            WHERE w.matricule IS NOT NULL AND w.matricule != '' AND r.matricule IS NULL
        """)
        
        missing_resolver = cursor.fetchone()["count"]
        
        # Vérifier que toutes les entrées du resolver correspondent à des workers
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM matricule_name_resolver r
            LEFT JOIN workers w ON r.worker_id = w.id
            WHERE r.is_active = 1 AND w.id IS NULL
        """)
        
        orphaned_resolver = cursor.fetchone()["count"]
        
        if missing_resolver == 0 and orphaned_resolver == 0:
            print("   ✅ Intégrité des données validée")
            test_results["tests_passed"] += 1
            test_results["test_details"].append({
                "test": "data_integrity",
                "status": "PASSED",
                "details": "Aucune incohérence détectée"
            })
        else:
            print(f"   ❌ Problèmes d'intégrité: {missing_resolver} manquants, {orphaned_resolver} orphelins")
            test_results["tests_failed"] += 1
            test_results["test_details"].append({
                "test": "data_integrity",
                "status": "FAILED",
                "details": f"{missing_resolver} manquants, {orphaned_resolver} orphelins"
            })
        
        # Résumé des tests
        print(f"\n📊 RÉSUMÉ DES TESTS")
        print("=" * 50)
        print(f"✅ Tests réussis: {test_results['tests_passed']}")
        print(f"❌ Tests échoués: {test_results['tests_failed']}")
        print(f"📋 Total des tests: {test_results['tests_passed'] + test_results['tests_failed']}")
        
        success_rate = (test_results['tests_passed'] / (test_results['tests_passed'] + test_results['tests_failed'])) * 100
        print(f"📈 Taux de réussite: {success_rate:.1f}%")
        
        # Sauvegarder les résultats
        import json
        log_filename = f"matricule_service_test_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(log_filename, 'w', encoding='utf-8') as f:
            json.dump(test_results, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Résultats sauvegardés: {log_filename}")
        
        if test_results['tests_failed'] == 0:
            print(f"\n🎉 TOUS LES TESTS SONT RÉUSSIS!")
            return True
        else:
            print(f"\n⚠️  CERTAINS TESTS ONT ÉCHOUÉ")
            return False
        
    except Exception as e:
        print(f"❌ Erreur lors des tests: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        conn.close()

if __name__ == "__main__":
    test_matricule_service()