#!/usr/bin/env python3
"""
Test de Performance Post-Optimisation
Validation que le problème 2000ms est résolu
"""

import requests
import time
import statistics
from datetime import datetime

def test_optimized_performance():
    """Tester les performances après optimisation"""
    
    print("⚡ Test de Performance Post-Optimisation")
    print("=" * 50)
    
    base_url = "http://localhost:8000/api/matricules"
    target_time = 0.1  # 100ms
    
    test_cases = [
        ("Health Check", "GET", "/health", {}),
        ("Search M0001", "GET", "/search", {"query": "M0001"}),
        ("Search Jean", "GET", "/search", {"query": "Jean"}),
        ("Resolve M0001", "GET", "/resolve/M0001", {}),
        ("Search with limit", "GET", "/search", {"query": "a", "limit": 5}),
    ]
    
    results = []
    
    for test_name, method, endpoint, params in test_cases:
        times = []
        
        # 10 tests par cas
        for i in range(10):
            start_time = time.time()
            try:
                if method == "GET":
                    response = requests.get(f"{base_url}{endpoint}", params=params)
                response_time = time.time() - start_time
                times.append(response_time)
            except Exception as e:
                print(f"❌ Erreur {test_name}: {e}")
                continue
        
        if times:
            avg_time = statistics.mean(times)
            min_time = min(times)
            max_time = max(times)
            
            performance_ok = avg_time < target_time
            status = "✅" if performance_ok else "⚠️"
            
            print(f"{status} {test_name}:")
            print(f"   Temps moyen: {avg_time:.3f}s")
            print(f"   Min/Max: {min_time:.3f}s / {max_time:.3f}s")
            print(f"   Objectif atteint: {'Oui' if performance_ok else 'Non'}")
            
            results.append({
                "test": test_name,
                "avg_time": avg_time,
                "performance_ok": performance_ok
            })
    
    # Résumé
    if results:
        total_tests = len(results)
        passed_tests = len([r for r in results if r["performance_ok"]])
        success_rate = (passed_tests / total_tests) * 100
        avg_response_time = sum(r["avg_time"] for r in results) / total_tests
        
        print(f"\n📊 Résumé:")
        print(f"   Tests réussis: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        print(f"   Temps moyen global: {avg_response_time:.3f}s")
        
        if success_rate >= 80:
            print("   🎉 OPTIMISATION RÉUSSIE!")
            print("   ✅ Problème de performance résolu")
            print("   🚀 Système prêt pour la Tâche 8")
        else:
            print("   ⚠️  Optimisations supplémentaires nécessaires")

if __name__ == "__main__":
    test_optimized_performance()
