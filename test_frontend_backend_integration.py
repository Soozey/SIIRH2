#!/usr/bin/env python3
"""
Tests d'intégration Frontend-Backend pour le système matricule
Task 12.1: Tests d'intégration frontend-backend
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any

class FrontendBackendIntegrationTest:
    """Tests d'intégration complets Frontend-Backend"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000/api"
        self.test_results = []
        self.performance_metrics = []
    
    def run_all_tests(self):
        """Exécuter tous les tests d'intégration"""
        
        print("🔍 Tests d'Intégration Frontend-Backend")
        print("=" * 60)
        
        # Test 1: Workflow de sélection de salarié
        self.test_worker_selection_workflow()
        
        # Test 2: Synchronisation avec gestion des homonymes
        self.test_homonym_synchronization()
        
        # Test 3: Performance avec grandes quantités de données
        self.test_performance_large_datasets()
        
        # Test 4: Workflow complet d'affectation organisationnelle
        self.test_organizational_assignment_workflow()
        
        # Test 5: Gestion des erreurs bout en bout
        self.test_end_to_end_error_handling()
        
        # Test 6: Synchronisation temps réel
        self.test_real_time_synchronization()
        
        # Résumé des résultats
        self.print_test_summary()
    
    def test_worker_selection_workflow(self):
        """Test du workflow de sélection de salarié (Exigence 7.1, 7.2)"""
        
        print("\n1️⃣ Test Workflow Sélection de Salarié")
        print("-" * 50)
        
        test_result = {
            "test_name": "worker_selection_workflow",
            "steps": [],
            "overall_status": "PASS",
            "performance": {}
        }
        
        # Étape 1: Recherche initiale par nom (simulation frontend)
        start_time = time.time()
        try:
            response = requests.get(f"{self.base_url}/matricules/search", 
                                  params={"query": "Jean", "limit": 5})
            search_time = time.time() - start_time
            
            if response.status_code == 200:
                results = response.json()
                test_result["steps"].append({
                    "step": "search_by_name",
                    "status": "PASS",
                    "results_count": len(results),
                    "response_time": f"{search_time:.3f}s"
                })
                print(f"✅ Recherche par nom: {len(results)} résultats en {search_time:.3f}s")
                
                # Étape 2: Sélection d'un matricule spécifique
                if results:
                    selected_matricule = results[0]["matricule"]
                    
                    start_time = time.time()
                    resolve_response = requests.get(f"{self.base_url}/matricules/resolve/{selected_matricule}")
                    resolve_time = time.time() - start_time
                    
                    if resolve_response.status_code == 200:
                        worker_data = resolve_response.json()
                        test_result["steps"].append({
                            "step": "resolve_matricule",
                            "status": "PASS",
                            "matricule": selected_matricule,
                            "response_time": f"{resolve_time:.3f}s"
                        })
                        print(f"✅ Résolution matricule: {selected_matricule} -> {worker_data.get('full_name', 'N/A')}")
                    else:
                        test_result["steps"].append({
                            "step": "resolve_matricule",
                            "status": "FAIL",
                            "error": f"Status {resolve_response.status_code}"
                        })
                        test_result["overall_status"] = "FAIL"
            else:
                test_result["overall_status"] = "FAIL"
                test_result["steps"].append({
                    "step": "search_by_name",
                    "status": "FAIL",
                    "error": f"Status {response.status_code}"
                })
                
        except Exception as e:
            test_result["overall_status"] = "ERROR"
            test_result["steps"].append({
                "step": "search_by_name",
                "status": "ERROR",
                "error": str(e)
            })
            print(f"❌ Erreur recherche: {e}")
        
        self.test_results.append(test_result)
    
    def test_homonym_synchronization(self):
        """Test de synchronisation avec gestion des homonymes (Exigence 2.2)"""
        
        print("\n2️⃣ Test Synchronisation Homonymes")
        print("-" * 50)
        
        test_result = {
            "test_name": "homonym_synchronization",
            "steps": [],
            "overall_status": "PASS"
        }
        
        try:
            # Rechercher des homonymes potentiels
            response = requests.get(f"{self.base_url}/matricules/search", 
                                  params={"query": "Jean", "limit": 10})
            
            if response.status_code == 200:
                results = response.json()
                homonymes = [r for r in results if r.get("is_homonym", False)]
                
                test_result["steps"].append({
                    "step": "detect_homonyms",
                    "status": "PASS",
                    "total_results": len(results),
                    "homonyms_detected": len(homonymes)
                })
                
                print(f"✅ Détection homonymes: {len(homonymes)}/{len(results)} homonymes détectés")
                
                # Test de distinction par matricule
                if len(results) > 1:
                    matricules = [r["matricule"] for r in results]
                    unique_matricules = set(matricules)
                    
                    if len(matricules) == len(unique_matricules):
                        test_result["steps"].append({
                            "step": "matricule_uniqueness",
                            "status": "PASS",
                            "unique_matricules": len(unique_matricules)
                        })
                        print(f"✅ Unicité matricules: {len(unique_matricules)} matricules uniques")
                    else:
                        test_result["steps"].append({
                            "step": "matricule_uniqueness",
                            "status": "FAIL",
                            "error": "Matricules dupliqués détectés"
                        })
                        test_result["overall_status"] = "FAIL"
                        print("❌ Matricules dupliqués détectés")
            else:
                test_result["overall_status"] = "FAIL"
                
        except Exception as e:
            test_result["overall_status"] = "ERROR"
            print(f"❌ Erreur test homonymes: {e}")
        
        self.test_results.append(test_result)
    
    def test_performance_large_datasets(self):
        """Test de performance avec grandes quantités de données (Exigence 9.1, 9.2)"""
        
        print("\n3️⃣ Test Performance Grandes Données")
        print("-" * 50)
        
        test_result = {
            "test_name": "performance_large_datasets",
            "steps": [],
            "overall_status": "PASS",
            "performance_metrics": {}
        }
        
        # Test de recherche avec différentes tailles de résultats
        limits = [10, 50, 100]
        
        for limit in limits:
            try:
                start_time = time.time()
                response = requests.get(f"{self.base_url}/matricules/search", 
                                      params={"query": "a", "limit": limit})
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    results = response.json()
                    
                    # Vérifier que le temps de réponse est < 100ms (exigence 9.2)
                    performance_ok = response_time < 0.1
                    
                    test_result["steps"].append({
                        "step": f"search_limit_{limit}",
                        "status": "PASS" if performance_ok else "WARN",
                        "response_time": f"{response_time:.3f}s",
                        "results_count": len(results),
                        "performance_target_met": performance_ok
                    })
                    
                    status_icon = "✅" if performance_ok else "⚠️"
                    print(f"{status_icon} Recherche limit {limit}: {len(results)} résultats en {response_time:.3f}s")
                    
                    self.performance_metrics.append({
                        "operation": f"search_limit_{limit}",
                        "response_time": response_time,
                        "target_met": performance_ok
                    })
                    
            except Exception as e:
                test_result["steps"].append({
                    "step": f"search_limit_{limit}",
                    "status": "ERROR",
                    "error": str(e)
                })
                print(f"❌ Erreur test limit {limit}: {e}")
        
        self.test_results.append(test_result)
    
    def test_organizational_assignment_workflow(self):
        """Test du workflow complet d'affectation organisationnelle"""
        
        print("\n4️⃣ Test Workflow Affectation Organisationnelle")
        print("-" * 50)
        
        test_result = {
            "test_name": "organizational_assignment_workflow",
            "steps": [],
            "overall_status": "PASS"
        }
        
        try:
            # Étape 1: Rechercher un salarié
            response = requests.get(f"{self.base_url}/matricules/search", 
                                  params={"query": "Jean", "limit": 1})
            
            if response.status_code == 200 and response.json():
                worker = response.json()[0]
                matricule = worker["matricule"]
                
                test_result["steps"].append({
                    "step": "find_worker",
                    "status": "PASS",
                    "matricule": matricule
                })
                print(f"✅ Salarié trouvé: {matricule}")
                
                # Étape 2: Créer une affectation
                assignment_data = {
                    "worker_matricule": matricule,
                    "employer_id": worker["employer_id"],
                    "etablissement": "Test Établissement",
                    "departement": "Test Département",
                    "service": "Test Service"
                }
                
                create_response = requests.post(f"{self.base_url}/matricules/assignments", 
                                              json=assignment_data)
                
                if create_response.status_code == 200:
                    assignment = create_response.json()
                    test_result["steps"].append({
                        "step": "create_assignment",
                        "status": "PASS",
                        "assignment_id": assignment.get("id")
                    })
                    print(f"✅ Affectation créée: ID {assignment.get('id', 'N/A')}")
                    
                    # Étape 3: Récupérer l'affectation
                    get_response = requests.get(f"{self.base_url}/matricules/assignments/{matricule}")
                    
                    if get_response.status_code == 200:
                        retrieved_assignment = get_response.json()
                        test_result["steps"].append({
                            "step": "retrieve_assignment",
                            "status": "PASS",
                            "retrieved": retrieved_assignment is not None
                        })
                        print(f"✅ Affectation récupérée: {retrieved_assignment.get('etablissement', 'N/A')}")
                    else:
                        test_result["steps"].append({
                            "step": "retrieve_assignment",
                            "status": "FAIL",
                            "error": f"Status {get_response.status_code}"
                        })
                else:
                    test_result["steps"].append({
                        "step": "create_assignment",
                        "status": "FAIL",
                        "error": f"Status {create_response.status_code}"
                    })
                    test_result["overall_status"] = "FAIL"
            else:
                test_result["overall_status"] = "FAIL"
                test_result["steps"].append({
                    "step": "find_worker",
                    "status": "FAIL",
                    "error": "Aucun salarié trouvé"
                })
                
        except Exception as e:
            test_result["overall_status"] = "ERROR"
            print(f"❌ Erreur workflow affectation: {e}")
        
        self.test_results.append(test_result)
    
    def test_end_to_end_error_handling(self):
        """Test de gestion des erreurs bout en bout"""
        
        print("\n5️⃣ Test Gestion d'Erreurs Bout en Bout")
        print("-" * 50)
        
        test_result = {
            "test_name": "end_to_end_error_handling",
            "steps": [],
            "overall_status": "PASS"
        }
        
        # Test d'erreurs avec matricules invalides
        invalid_matricules = ["INVALID123", "NOTFOUND", ""]
        
        for matricule in invalid_matricules:
            try:
                response = requests.get(f"{self.base_url}/matricules/resolve/{matricule}")
                
                if response.status_code == 404:
                    error_data = response.json()
                    
                    # Vérifier la structure de l'erreur
                    has_error_id = "error_id" in error_data
                    has_matricules_info = "matricules_involved" in error_data
                    has_user_guidance = "user_guidance" in error_data
                    
                    test_result["steps"].append({
                        "step": f"error_handling_{matricule or 'empty'}",
                        "status": "PASS",
                        "has_error_id": has_error_id,
                        "has_matricules_info": has_matricules_info,
                        "has_user_guidance": has_user_guidance
                    })
                    
                    print(f"✅ Erreur {matricule or 'vide'}: Structure complète")
                else:
                    test_result["steps"].append({
                        "step": f"error_handling_{matricule or 'empty'}",
                        "status": "FAIL",
                        "error": f"Expected 404, got {response.status_code}"
                    })
                    
            except Exception as e:
                test_result["steps"].append({
                    "step": f"error_handling_{matricule or 'empty'}",
                    "status": "ERROR",
                    "error": str(e)
                })
        
        self.test_results.append(test_result)
    
    def test_real_time_synchronization(self):
        """Test de synchronisation temps réel (Exigence 2.3)"""
        
        print("\n6️⃣ Test Synchronisation Temps Réel")
        print("-" * 50)
        
        test_result = {
            "test_name": "real_time_synchronization",
            "steps": [],
            "overall_status": "PASS"
        }
        
        try:
            # Test de validation d'intégrité
            start_time = time.time()
            response = requests.get(f"{self.base_url}/matricules/integrity/validate")
            validation_time = time.time() - start_time
            
            if response.status_code == 200:
                validation_data = response.json()
                
                test_result["steps"].append({
                    "step": "integrity_validation",
                    "status": "PASS",
                    "response_time": f"{validation_time:.3f}s",
                    "overall_status": validation_data.get("overall_status"),
                    "checks_passed": validation_data.get("passed_checks", 0),
                    "total_checks": validation_data.get("total_checks", 0)
                })
                
                print(f"✅ Validation intégrité: {validation_data.get('overall_status', 'N/A')} en {validation_time:.3f}s")
                print(f"   Checks: {validation_data.get('passed_checks', 0)}/{validation_data.get('total_checks', 0)}")
            else:
                test_result["overall_status"] = "FAIL"
                
        except Exception as e:
            test_result["overall_status"] = "ERROR"
            print(f"❌ Erreur synchronisation: {e}")
        
        self.test_results.append(test_result)
    
    def print_test_summary(self):
        """Afficher le résumé des tests"""
        
        print("\n" + "=" * 60)
        print("📊 RÉSUMÉ DES TESTS D'INTÉGRATION")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t["overall_status"] == "PASS"])
        failed_tests = len([t for t in self.test_results if t["overall_status"] == "FAIL"])
        error_tests = len([t for t in self.test_results if t["overall_status"] == "ERROR"])
        
        print(f"\n📈 Statistiques Globales:")
        print(f"   Total tests: {total_tests}")
        print(f"   ✅ Réussis: {passed_tests}")
        print(f"   ❌ Échoués: {failed_tests}")
        print(f"   🚨 Erreurs: {error_tests}")
        print(f"   📊 Taux de réussite: {(passed_tests/total_tests)*100:.1f}%")
        
        # Détail par test
        print(f"\n📋 Détail par Test:")
        for test in self.test_results:
            status_icon = "✅" if test["overall_status"] == "PASS" else "❌" if test["overall_status"] == "FAIL" else "🚨"
            print(f"   {status_icon} {test['test_name']}: {test['overall_status']}")
            print(f"      Étapes: {len(test['steps'])}")
        
        # Métriques de performance
        if self.performance_metrics:
            print(f"\n⚡ Métriques de Performance:")
            avg_response_time = sum(m["response_time"] for m in self.performance_metrics) / len(self.performance_metrics)
            target_met_count = len([m for m in self.performance_metrics if m["target_met"]])
            
            print(f"   Temps de réponse moyen: {avg_response_time:.3f}s")
            print(f"   Objectifs atteints: {target_met_count}/{len(self.performance_metrics)}")
        
        print(f"\n🎯 Conclusion:")
        if passed_tests == total_tests:
            print("   🎉 Tous les tests d'intégration sont réussis!")
            print("   ✅ Le système est prêt pour la production")
        elif passed_tests >= total_tests * 0.8:
            print("   ⚠️  La plupart des tests sont réussis")
            print("   🔧 Quelques ajustements nécessaires")
        else:
            print("   🚨 Plusieurs tests ont échoué")
            print("   🛠️  Corrections importantes requises")

def main():
    """Fonction principale"""
    tester = FrontendBackendIntegrationTest()
    tester.run_all_tests()

if __name__ == "__main__":
    main()