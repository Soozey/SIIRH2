#!/usr/bin/env python3
"""
Diagnostic approfondi du goulot d'étranglement de performance
Identifier la cause exacte du problème 2000ms
"""

import requests
import time
import json
from datetime import datetime
import threading

def test_basic_connectivity():
    """Tester la connectivité de base"""
    print("🔍 Test de Connectivité de Base")
    print("-" * 40)
    
    try:
        # Test simple de ping
        start_time = time.time()
        response = requests.get("http://localhost:8000/docs")
        response_time = time.time() - start_time
        
        print(f"✅ Docs endpoint: {response_time:.3f}s (Status: {response.status_code})")
        
        # Test health check simple
        start_time = time.time()
        response = requests.get("http://localhost:8000/api/matricules/health")
        response_time = time.time() - start_time
        
        print(f"⚠️  Health check: {response_time:.3f}s (Status: {response.status_code})")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Workers count: {data.get('workers_with_matricules', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Erreur connectivité: {e}")

def test_different_endpoints():
    """Tester différents endpoints pour identifier le problème"""
    print("\n🔍 Test de Différents Endpoints")
    print("-" * 40)
    
    endpoints = [
        ("Constants", "http://localhost:8000/constants/payroll"),
        ("Employers", "http://localhost:8000/api/employers"),
        ("Organization", "http://localhost:8000/api/organization/tree"),
        ("Matricules Health", "http://localhost:8000/api/matricules/health"),
        ("Matricules Search", "http://localhost:8000/api/matricules/search?query=M0001"),
    ]
    
    for name, url in endpoints:
        try:
            start_time = time.time()
            response = requests.get(url, timeout=10)
            response_time = time.time() - start_time
            
            status = "✅" if response_time < 0.5 else "⚠️" if response_time < 2.0 else "❌"
            print(f"{status} {name}: {response_time:.3f}s (Status: {response.status_code})")
            
        except requests.exceptions.Timeout:
            print(f"❌ {name}: TIMEOUT (>10s)")
        except Exception as e:
            print(f"❌ {name}: Erreur - {e}")

def test_concurrent_requests():
    """Tester les requêtes concurrentes"""
    print("\n🔍 Test de Requêtes Concurrentes")
    print("-" * 40)
    
    def make_request(request_id, results):
        try:
            start_time = time.time()
            response = requests.get("http://localhost:8000/api/matricules/health", timeout=5)
            response_time = time.time() - start_time
            results.append({
                "id": request_id,
                "time": response_time,
                "status": response.status_code,
                "success": True
            })
        except Exception as e:
            results.append({
                "id": request_id,
                "time": None,
                "status": None,
                "success": False,
                "error": str(e)
            })
    
    # Lancer 5 requêtes simultanées
    results = []
    threads = []
    
    for i in range(5):
        thread = threading.Thread(target=make_request, args=(i, results))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]
    
    if successful:
        avg_time = sum(r["time"] for r in successful) / len(successful)
        print(f"✅ Requêtes réussies: {len(successful)}/5")
        print(f"   Temps moyen: {avg_time:.3f}s")
    
    if failed:
        print(f"❌ Requêtes échouées: {len(failed)}")
        for f in failed:
            print(f"   ID {f['id']}: {f.get('error', 'Unknown error')}")

def test_database_direct():
    """Tester l'accès direct à la base de données"""
    print("\n🔍 Test d'Accès Direct à la Base de Données")
    print("-" * 40)
    
    try:
        import psycopg2
        
        # Connexion directe
        start_time = time.time()
        conn = psycopg2.connect(
            host='localhost',
            database='siirh_db',
            user='siirh_user',
            password='siirh_password',
            port=5432
        )
        connection_time = time.time() - start_time
        
        print(f"✅ Connexion DB: {connection_time:.3f}s")
        
        cur = conn.cursor()
        
        # Test requête simple
        start_time = time.time()
        cur.execute("SELECT COUNT(*) FROM workers")
        count = cur.fetchone()[0]
        query_time = time.time() - start_time
        
        print(f"✅ Requête COUNT: {query_time:.3f}s ({count} workers)")
        
        # Test requête avec WHERE
        start_time = time.time()
        cur.execute("SELECT id, matricule FROM workers WHERE matricule = %s", ('M0001',))
        result = cur.fetchone()
        query_time = time.time() - start_time
        
        print(f"✅ Requête WHERE: {query_time:.3f}s")
        
        cur.close()
        conn.close()
        
    except ImportError:
        print("⚠️  psycopg2 non disponible, test ignoré")
    except Exception as e:
        print(f"❌ Erreur DB directe: {e}")

def test_api_response_analysis():
    """Analyser en détail les réponses API"""
    print("\n🔍 Analyse Détaillée des Réponses API")
    print("-" * 40)
    
    try:
        # Test avec mesure détaillée
        url = "http://localhost:8000/api/matricules/search?query=M0001"
        
        # Mesurer différentes phases
        start_total = time.time()
        
        # Phase 1: Établissement de la connexion
        start_connect = time.time()
        response = requests.get(url, timeout=10)
        total_time = time.time() - start_total
        
        print(f"⚠️  Temps total: {total_time:.3f}s")
        print(f"   Status: {response.status_code}")
        print(f"   Content-Length: {len(response.content)} bytes")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   Résultats: {len(data)} items")
                if data:
                    print(f"   Premier résultat: {data[0].get('matricule', 'N/A')}")
            except:
                print("   Erreur parsing JSON")
        
        # Headers de réponse
        print(f"   Headers importants:")
        for header in ['content-type', 'content-length', 'server']:
            if header in response.headers:
                print(f"     {header}: {response.headers[header]}")
        
    except Exception as e:
        print(f"❌ Erreur analyse API: {e}")

def test_network_latency():
    """Tester la latence réseau"""
    print("\n🔍 Test de Latence Réseau")
    print("-" * 40)
    
    try:
        # Test ping simple
        import subprocess
        result = subprocess.run(['ping', '-n', '1', 'localhost'], 
                              capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            print("✅ Ping localhost: OK")
        else:
            print("⚠️  Ping localhost: Problème détecté")
            
    except Exception as e:
        print(f"⚠️  Test ping: {e}")
    
    # Test de latence HTTP simple
    try:
        times = []
        for i in range(5):
            start_time = time.time()
            response = requests.get("http://localhost:8000/docs", timeout=2)
            response_time = time.time() - start_time
            times.append(response_time)
        
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        print(f"✅ Latence HTTP docs:")
        print(f"   Moyenne: {avg_time:.3f}s")
        print(f"   Min/Max: {min_time:.3f}s / {max_time:.3f}s")
        
    except Exception as e:
        print(f"❌ Erreur latence HTTP: {e}")

def main():
    """Diagnostic complet"""
    print("🚨 DIAGNOSTIC APPROFONDI DU PROBLÈME DE PERFORMANCE")
    print("=" * 60)
    print("Objectif: Identifier la cause exacte du problème 2000ms")
    print()
    
    # Tests séquentiels
    test_basic_connectivity()
    test_different_endpoints()
    test_concurrent_requests()
    test_database_direct()
    test_api_response_analysis()
    test_network_latency()
    
    print("\n" + "=" * 60)
    print("🎯 CONCLUSIONS DU DIAGNOSTIC")
    print("=" * 60)
    
    print("\n📋 Hypothèses à vérifier:")
    print("1. Problème de configuration PostgreSQL")
    print("2. Problème d'encodage au niveau de la DB")
    print("3. Problème de réseau/latence locale")
    print("4. Problème de configuration FastAPI/Uvicorn")
    print("5. Problème de pool de connexions")
    
    print("\n🔧 Actions recommandées:")
    print("1. Vérifier les logs du serveur backend")
    print("2. Tester avec une base de données de test")
    print("3. Analyser la configuration PostgreSQL")
    print("4. Implémenter un cache temporaire")

if __name__ == "__main__":
    main()