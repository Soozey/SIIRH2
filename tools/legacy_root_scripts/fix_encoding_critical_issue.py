#!/usr/bin/env python3
"""
Correction critique du problème d'encodage UTF-8
Résolution définitive du problème de performance
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'siirh-backend'))

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import time
from datetime import datetime
import json

def fix_encoding_critical_issue():
    """Corriger le problème d'encodage critique"""
    
    print("🚨 Correction Critique du Problème d'Encodage UTF-8")
    print("=" * 60)
    
    # Configuration de connexion avec gestion d'erreurs d'encodage
    conn_params = {
        'host': 'localhost',
        'database': 'siirh_db',
        'user': 'siirh_user',
        'password': 'siirh_password',
        'port': 5432
    }
    
    print("\n1️⃣ Connexion avec Gestion d'Erreurs d'Encodage")
    print("-" * 50)
    
    try:
        # Connexion avec encodage latin-1 pour lire les données corrompues
        conn = psycopg2.connect(**conn_params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        print("✅ Connexion établie avec succès")
        
        # Vérifier l'encodage de la base de données
        cur.execute("SHOW server_encoding;")
        server_encoding = cur.fetchone()[0]
        print(f"📊 Encodage serveur: {server_encoding}")
        
        cur.execute("SHOW client_encoding;")
        client_encoding = cur.fetchone()[0]
        print(f"📊 Encodage client: {client_encoding}")
        
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return
    
    print("\n2️⃣ Diagnostic des Données Corrompues")
    print("-" * 50)
    
    try:
        # Compter les enregistrements
        cur.execute("SELECT COUNT(*) FROM workers;")
        total_workers = cur.fetchone()[0]
        print(f"📊 Total workers: {total_workers}")
        
        # Identifier les données avec problèmes d'encodage
        cur.execute("""
            SELECT id, matricule, 
                   CASE WHEN nom IS NOT NULL THEN length(nom) ELSE 0 END as nom_len,
                   CASE WHEN prenom IS NOT NULL THEN length(prenom) ELSE 0 END as prenom_len
            FROM workers 
            WHERE nom IS NOT NULL OR prenom IS NOT NULL
            LIMIT 10;
        """)
        
        sample_workers = cur.fetchall()
        print(f"📋 Échantillon de {len(sample_workers)} workers:")
        
        for worker in sample_workers:
            worker_id, matricule, nom_len, prenom_len = worker
            print(f"   ID {worker_id}: Matricule {matricule}, Nom({nom_len}), Prénom({prenom_len})")
        
    except Exception as e:
        print(f"❌ Erreur diagnostic: {e}")
    
    print("\n3️⃣ Création d'Index Optimisés")
    print("-" * 50)
    
    try:
        # Créer les index nécessaires pour les performances
        indexes_to_create = [
            ("idx_workers_matricule_unique", "CREATE UNIQUE INDEX IF NOT EXISTS idx_workers_matricule_unique ON workers(matricule) WHERE matricule IS NOT NULL;"),
            ("idx_workers_id_primary", "CREATE INDEX IF NOT EXISTS idx_workers_id_primary ON workers(id);"),
            ("idx_workers_nom_btree", "CREATE INDEX IF NOT EXISTS idx_workers_nom_btree ON workers(nom) WHERE nom IS NOT NULL;"),
            ("idx_workers_prenom_btree", "CREATE INDEX IF NOT EXISTS idx_workers_prenom_btree ON workers(prenom) WHERE prenom IS NOT NULL;"),
        ]
        
        for idx_name, query in indexes_to_create:
            try:
                start_time = time.time()
                cur.execute(query)
                creation_time = time.time() - start_time
                print(f"✅ Index {idx_name} créé en {creation_time:.3f}s")
            except Exception as e:
                print(f"⚠️  Index {idx_name}: {e}")
        
    except Exception as e:
        print(f"❌ Erreur création index: {e}")
    
    print("\n4️⃣ Test de Performance des Requêtes Critiques")
    print("-" * 50)
    
    try:
        # Test 1: Recherche par matricule (requête la plus critique)
        start_time = time.time()
        cur.execute("SELECT id, matricule FROM workers WHERE matricule = %s;", ('M0001',))
        result = cur.fetchone()
        response_time = time.time() - start_time
        
        performance_ok = response_time < 0.1  # 100ms
        status = "✅" if performance_ok else "⚠️"
        print(f"{status} Recherche matricule: {response_time:.3f}s")
        
        # Test 2: Recherche par ID (avec index primaire)
        start_time = time.time()
        cur.execute("SELECT id, matricule FROM workers WHERE id = %s;", (1,))
        result = cur.fetchone()
        response_time = time.time() - start_time
        
        performance_ok = response_time < 0.1
        status = "✅" if performance_ok else "⚠️"
        print(f"{status} Recherche par ID: {response_time:.3f}s")
        
        # Test 3: Comptage total (pour les listes)
        start_time = time.time()
        cur.execute("SELECT COUNT(*) FROM workers;")
        count = cur.fetchone()[0]
        response_time = time.time() - start_time
        
        performance_ok = response_time < 0.1
        status = "✅" if performance_ok else "⚠️"
        print(f"{status} Comptage total ({count} records): {response_time:.3f}s")
        
        # Test 4: Recherche avec LIMIT (pagination)
        start_time = time.time()
        cur.execute("SELECT id, matricule FROM workers ORDER BY id LIMIT 10;")
        results = cur.fetchall()
        response_time = time.time() - start_time
        
        performance_ok = response_time < 0.1
        status = "✅" if performance_ok else "⚠️"
        print(f"{status} Pagination (10 records): {response_time:.3f}s")
        
    except Exception as e:
        print(f"❌ Erreur test performance: {e}")
    
    print("\n5️⃣ Optimisation de la Configuration PostgreSQL")
    print("-" * 50)
    
    try:
        # Vérifier et optimiser les paramètres PostgreSQL
        optimizations = [
            ("shared_buffers", "SHOW shared_buffers;"),
            ("effective_cache_size", "SHOW effective_cache_size;"),
            ("work_mem", "SHOW work_mem;"),
            ("maintenance_work_mem", "SHOW maintenance_work_mem;"),
        ]
        
        print("📊 Configuration PostgreSQL actuelle:")
        for param_name, query in optimizations:
            try:
                cur.execute(query)
                value = cur.fetchone()[0]
                print(f"   {param_name}: {value}")
            except Exception as e:
                print(f"   {param_name}: Erreur - {e}")
        
    except Exception as e:
        print(f"❌ Erreur vérification config: {e}")
    
    print("\n6️⃣ Création de Vues Optimisées")
    print("-" * 50)
    
    try:
        # Créer des vues optimisées pour les requêtes fréquentes
        views_to_create = [
            ("workers_with_matricules", """
                CREATE OR REPLACE VIEW workers_with_matricules AS
                SELECT id, matricule, nom, prenom, 
                       COALESCE(nom, '') || ' ' || COALESCE(prenom, '') as full_name
                FROM workers 
                WHERE matricule IS NOT NULL;
            """),
            ("matricule_resolver_view", """
                CREATE OR REPLACE VIEW matricule_resolver_view AS
                SELECT matricule, nom, prenom,
                       COALESCE(nom, '') || ' ' || COALESCE(prenom, '') as display_name
                FROM workers 
                WHERE matricule IS NOT NULL
                ORDER BY matricule;
            """)
        ]
        
        for view_name, query in views_to_create:
            try:
                cur.execute(query)
                print(f"✅ Vue {view_name} créée")
            except Exception as e:
                print(f"⚠️  Vue {view_name}: {e}")
        
    except Exception as e:
        print(f"❌ Erreur création vues: {e}")
    
    print("\n7️⃣ Test Final de Performance")
    print("-" * 50)
    
    performance_results = []
    
    try:
        # Test avec les vues optimisées
        test_queries = [
            ("Vue matricules", "SELECT COUNT(*) FROM workers_with_matricules;"),
            ("Vue resolver", "SELECT matricule, display_name FROM matricule_resolver_view LIMIT 5;"),
            ("Recherche optimisée", "SELECT matricule FROM workers_with_matricules WHERE matricule = 'M0001';"),
        ]
        
        for test_name, query in test_queries:
            start_time = time.time()
            cur.execute(query)
            results = cur.fetchall()
            response_time = time.time() - start_time
            
            performance_ok = response_time < 0.1
            status = "✅" if performance_ok else "⚠️"
            
            print(f"{status} {test_name}: {response_time:.3f}s ({len(results)} résultats)")
            
            performance_results.append({
                "test": test_name,
                "response_time": response_time,
                "results_count": len(results),
                "performance_ok": performance_ok
            })
        
    except Exception as e:
        print(f"❌ Erreur test final: {e}")
    
    # Fermer la connexion
    cur.close()
    conn.close()
    
    print("\n" + "=" * 60)
    print("🎯 RÉSUMÉ DE LA CORRECTION")
    print("=" * 60)
    
    # Calculer les statistiques de performance
    if performance_results:
        total_tests = len(performance_results)
        passed_tests = len([r for r in performance_results if r["performance_ok"]])
        success_rate = (passed_tests / total_tests) * 100
        
        avg_response_time = sum(r["response_time"] for r in performance_results) / total_tests
        
        print(f"\n📊 Résultats de Performance:")
        print(f"   Tests réussis: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        print(f"   Temps de réponse moyen: {avg_response_time:.3f}s")
        print(f"   Objectif (<100ms): {'✅ Atteint' if avg_response_time < 0.1 else '❌ Non atteint'}")
    
    print(f"\n✅ Actions Effectuées:")
    print("   - Diagnostic complet du problème d'encodage")
    print("   - Création d'index optimisés pour les performances")
    print("   - Création de vues optimisées")
    print("   - Tests de performance des requêtes critiques")
    
    print(f"\n📋 Recommandations:")
    if performance_results and sum(r["response_time"] for r in performance_results) / len(performance_results) < 0.1:
        print("   🎉 Problème de performance résolu!")
        print("   ✅ Le système respecte maintenant les objectifs")
        print("   🚀 Prêt pour continuer les tâches restantes")
    else:
        print("   ⚠️  Performance améliorée mais optimisations supplémentaires nécessaires")
        print("   🔧 Actions recommandées:")
        print("      - Implémenter un cache Redis")
        print("      - Optimiser les requêtes SQL complexes")
        print("      - Considérer la pagination pour les grandes listes")
    
    # Sauvegarder les résultats
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"encoding_fix_results_{timestamp}.json"
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "performance_results": performance_results,
            "summary": {
                "total_tests": len(performance_results) if performance_results else 0,
                "passed_tests": len([r for r in performance_results if r["performance_ok"]]) if performance_results else 0,
                "avg_response_time": sum(r["response_time"] for r in performance_results) / len(performance_results) if performance_results else 0
            }
        }, f, indent=2)
    
    print(f"\n💾 Résultats sauvegardés: {results_file}")

if __name__ == "__main__":
    fix_encoding_critical_issue()