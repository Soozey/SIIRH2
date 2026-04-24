#!/usr/bin/env python3
"""
Test de validation des performances des requêtes par matricule
Task 12.3: Valider les performances des requêtes par matricule
"""

import requests
import time
import statistics
import json
from datetime import datetime
from typing import List, Dict, Any

class MatriculePerformanceValidator:
    """Validateur de performance pour les requêtes matricule"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000/api/matricules"
        self.performance_results = []
        self.target_response_time = 0.1  # 100ms selon l'exigence 9.2
    
    def run_performance_validation(self):
        """Exécuter la validation complète des performances"""
        
        print("⚡ Validation des Performances - Requêtes Matricule")
        print("=" * 60)
        
        # Test 1: Performance de recherche par matricule
        self.test_matricule_search_performance()
        
        # Test 2: Performance de résolution de matricule
        self.test_matricule_resolution_performance()
        
        # Test 3: Performance avec index optimisés
        self.test_optimized_index_performance()
        
        # Test 4: Test de scalabilité
        self.test_scalability_performance()
        
        # Test 5: Performance sous charge
        self.test_load_performance()
        
        # Résumé des performances
        self.print_performance_summary()
    
    def test_matricule_search_performance(self):
        """Test de performance pour la recherche par matricule"""
        
        print("\n1️⃣ Test Performance Recherche par Matricule")
        print("-" * 50)
        
        test_matricules = ["M0001", "M0002", "E001001", "INVALID"]
        response_times = []
        
        for matricule in test_matricules:
            times = []
            
            # Effectuer 10 requêtes pour chaque matricule
            for i in range(10):
                start_time = time.time()
                try:
                    response = requests.get(f"{self.base_url}/search", 
                                          params={"query": matricule})
                    response_time = time.time() - start_time
                    times.append(response_time)
                    
                except Exception as e:
                    print(f"❌ Erreur requête {matricule}: {e}")
                    continue
            
            if times:
                avg_time = statistics.mean(times)
                min_time = min(times)
                max_time = max(times)
                
                performance_ok = avg_time < self.target_response_time
                status_icon = "✅" if performance_ok else "⚠️"
                
                print(f"{status_icon} Matricule {matricule}:")
                print(f"   Temps moyen: {avg_time:.3f}s")
                print(f"   Min/Max: {min_time:.3f}s / {max_time:.3f}s")
                print(f"   Objectif atteint: {'Oui' if performance_ok else 'Non'}")
                
                response_times.extend(times)
                
                self.performance_results.append({
                    "test": "matricule_search",
                    "matricule": matricule,
                    "avg_response_time": avg_time,
                    "min_response_time": min_time,
                    "max_response_time": max_time,
                    "target_met": performance_ok,
                    "iterations": len(times)
                })
        
        if response_times:
            overall_avg = statistics.mean(response_times)
            overall_target_met = overall_avg < self.target_response_time
            
            print(f"\n📊 Performance globale recherche:")
            print(f"   Temps moyen global: {overall_avg:.3f}s")
            print(f"   Objectif global: {'✅ Atteint' if overall_target_met else '❌ Non atteint'}")
    
    def test_matricule_resolution_performance(self):
        """Test de performance pour la résolution de matricule"""
        
        print("\n2️⃣ Test Performance Résolution de Matricule")
        print("-" * 50)
        
        # D'abord obtenir des matricules valides
        try:
            search_response = requests.get(f"{self.base_url}/search", 
                                         params={"query": "a", "limit": 5})
            if search_response.status_code == 200:
                results = search_response.json()
                test_matricules = [r["matricule"] for r in results[:3]]
            else:
                test_matricules = ["M0001", "M0002"]
        except:
            test_matricules = ["M0001", "M0002"]
        
        response_times = []
        
        for matricule in test_matricules:
            times = []
            
            # Effectuer 10 requêtes pour chaque matricule
            for i in range(10):
                start_time = time.time()
                try:
                    response = requests.get(f"{self.base_url}/resolve/{matricule}")
                    response_time = time.time() - start_time
                    times.append(response_time)
                    
                except Exception as e:
                    continue
            
            if times:
                avg_time = statistics.mean(times)
                performance_ok = avg_time < self.target_response_time
                status_icon = "✅" if performance_ok else "⚠️"
                
                print(f"{status_icon} Résolution {matricule}: {avg_time:.3f}s")
                response_times.extend(times)
                
                self.performance_results.append({
                    "test": "matricule_resolution",
                    "matricule": matricule,
                    "avg_response_time": avg_time,
                    "target_met": performance_ok,
                    "iterations": len(times)
                })
        
        if response_times:
            overall_avg = statistics.mean(response_times)
            overall_target_met = overall_avg < self.target_response_time
            
            print(f"\n📊 Performance globale résolution:")
            print(f"   Temps moyen: {overall_avg:.3f}s")
            print(f"   Objectif: {'✅ Atteint' if overall_target_met else '❌ Non atteint'}")
    
    def test_optimized_index_performance(self):
        """Test de performance avec index optimisés"""
        
        print("\n3️⃣ Test Performance Index Optimisés")
        print("-" * 50)
        
        # Test de recherche avec différentes tailles de résultats
        limits = [1, 10, 50, 100]
        
        for limit in limits:
            times = []
            
            # Effectuer 5 requêtes pour chaque limite
            for i in range(5):
                start_time = time.time()
                try:
                    response = requests.get(f"{self.base_url}/search", 
                                          params={"query": "a", "limit": limit})
                    response_time = time.time() - start_time
                    times.append(response_time)
                    
                except Exception as e:
                    continue
            
            if times:
                avg_time = statistics.mean(times)
                performance_ok = avg_time < self.target_response_time
                status_icon = "✅" if performance_ok else "⚠️"
                
                print(f"{status_icon} Limite {limit}: {avg_time:.3f}s")
                
                self.performance_results.append({
                    "test": "optimized_index",
                    "limit": limit,
                    "avg_response_time": avg_time,
                    "target_met": performance_ok,
                    "iterations": len(times)
                })
    
    def test_scalability_performance(self):
        """Test de scalabilité avec grandes quantités de données"""
        
        print("\n4️⃣ Test Scalabilité")
        print("-" * 50)
        
        # Test avec différents patterns de recherche
        search_patterns = ["a", "jean", "marie", "test", "xyz"]
        
        for pattern in search_patterns:
            start_time = time.time()
            try:
                response = requests.get(f"{self.base_url}/search", 
                                      params={"query": pattern, "limit": 100})
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    results = response.json()
                    results_count = len(results)
                    
                    performance_ok = response_time < self.target_response_time
                    status_icon = "✅" if performance_ok else "⚠️"
                    
                    print(f"{status_icon} Pattern '{pattern}': {results_count} résultats en {response_time:.3f}s")
                    
                    self.performance_results.append({
                        "test": "scalability",
                        "pattern": pattern,
                        "results_count": results_count,
                        "response_time": response_time,
                        "target_met": performance_ok
                    })
                    
            except Exception as e:
                print(f"❌ Erreur pattern '{pattern}': {e}")
    
    def test_load_performance(self):
        """Test de performance sous charge"""
        
        print("\n5️⃣ Test Performance sous Charge")
        print("-" * 50)
        
        # Simuler une charge avec requêtes simultanées
        import threading
        import queue
        
        results_queue = queue.Queue()
        
        def make_request(request_id):
            start_time = time.time()
            try:
                response = requests.get(f"{self.base_url}/search", 
                                      params={"query": "jean", "limit": 10})
                response_time = time.time() - start_time
                results_queue.put({
                    "request_id": request_id,
                    "response_time": response_time,
                    "success": response.status_code == 200
                })
            except Exception as e:
                results_queue.put({
                    "request_id": request_id,
                    "response_time": None,
                    "success": False,
                    "error": str(e)
                })
        
        # Lancer 20 requêtes simultanées
        threads = []
        for i in range(20):
            thread = threading.Thread(target=make_request, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Attendre que tous les threads se terminent
        for thread in threads:
            thread.join()
        
        # Collecter les résultats
        load_results = []
        while not results_queue.empty():
            load_results.append(results_queue.get())
        
        successful_requests = [r for r in load_results if r["success"]]
        failed_requests = [r for r in load_results if not r["success"]]
        
        if successful_requests:
            response_times = [r["response_time"] for r in successful_requests]
            avg_time = statistics.mean(response_times)
            max_time = max(response_times)
            
            performance_ok = avg_time < self.target_response_time
            status_icon = "✅" if performance_ok else "⚠️"
            
            print(f"{status_icon} Charge simultanée (20 requêtes):")
            print(f"   Requêtes réussies: {len(successful_requests)}/20")
            print(f"   Temps moyen: {avg_time:.3f}s")
            print(f"   Temps maximum: {max_time:.3f}s")
            print(f"   Objectif atteint: {'Oui' if performance_ok else 'Non'}")
            
            self.performance_results.append({
                "test": "load_performance",
                "concurrent_requests": 20,
                "successful_requests": len(successful_requests),
                "failed_requests": len(failed_requests),
                "avg_response_time": avg_time,
                "max_response_time": max_time,
                "target_met": performance_ok
            })
        
        if failed_requests:
            print(f"   ❌ Requêtes échouées: {len(failed_requests)}")
    
    def print_performance_summary(self):
        """Afficher le résumé des performances"""
        
        print("\n" + "=" * 60)
        print("📊 RÉSUMÉ DE VALIDATION DES PERFORMANCES")
        print("=" * 60)
        
        # Statistiques globales
        total_tests = len(self.performance_results)
        target_met_tests = len([r for r in self.performance_results if r.get("target_met", False)])
        
        print(f"\n📈 Statistiques Globales:")
        print(f"   Total tests: {total_tests}")
        print(f"   ✅ Objectifs atteints: {target_met_tests}")
        print(f"   ❌ Objectifs non atteints: {total_tests - target_met_tests}")
        print(f"   📊 Taux de réussite: {(target_met_tests/total_tests)*100:.1f}%")
        
        # Analyse par type de test
        test_types = {}
        for result in self.performance_results:
            test_type = result["test"]
            if test_type not in test_types:
                test_types[test_type] = {"total": 0, "passed": 0, "times": []}
            
            test_types[test_type]["total"] += 1
            if result.get("target_met", False):
                test_types[test_type]["passed"] += 1
            
            if "avg_response_time" in result:
                test_types[test_type]["times"].append(result["avg_response_time"])
            elif "response_time" in result:
                test_types[test_type]["times"].append(result["response_time"])
        
        print(f"\n📋 Analyse par Type de Test:")
        for test_type, stats in test_types.items():
            success_rate = (stats["passed"] / stats["total"]) * 100
            avg_time = statistics.mean(stats["times"]) if stats["times"] else 0
            
            status_icon = "✅" if success_rate >= 80 else "⚠️" if success_rate >= 50 else "❌"
            print(f"   {status_icon} {test_type}:")
            print(f"      Réussite: {stats['passed']}/{stats['total']} ({success_rate:.1f}%)")
            print(f"      Temps moyen: {avg_time:.3f}s")
        
        # Recommandations
        print(f"\n🎯 Recommandations:")
        
        overall_success_rate = (target_met_tests / total_tests) * 100
        
        if overall_success_rate >= 90:
            print("   🎉 Excellentes performances!")
            print("   ✅ Le système respecte les objectifs de performance")
            print("   🚀 Prêt pour la production")
        elif overall_success_rate >= 70:
            print("   ⚠️  Performances correctes mais améliorables")
            print("   🔧 Optimisations recommandées:")
            print("      - Vérifier les index de base de données")
            print("      - Optimiser les requêtes SQL")
            print("      - Considérer la mise en cache")
        else:
            print("   🚨 Performances insuffisantes")
            print("   🛠️  Actions critiques requises:")
            print("      - Revoir l'architecture des requêtes")
            print("      - Optimiser les index de base de données")
            print("      - Implémenter un système de cache")
            print("      - Considérer la pagination pour les grandes listes")
        
        # Sauvegarde des résultats
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"matricule_performance_results_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "target_response_time": self.target_response_time,
                "summary": {
                    "total_tests": total_tests,
                    "target_met_tests": target_met_tests,
                    "success_rate": overall_success_rate
                },
                "detailed_results": self.performance_results
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Résultats sauvegardés: {filename}")

def main():
    """Fonction principale"""
    validator = MatriculePerformanceValidator()
    validator.run_performance_validation()

if __name__ == "__main__":
    main()