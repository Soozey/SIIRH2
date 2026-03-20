#!/usr/bin/env python3
"""
Task 2.3: Création des index optimisés pour les performances
Index sur matricules pour les requêtes rapides, recherche textuelle et jointures
"""

import sqlite3
import json
from datetime import datetime
import time

class PerformanceIndexManager:
    """Gestionnaire des index de performance pour le système matricule"""
    
    def __init__(self, db_path="siirh-backend/siirh.db"):
        self.db_path = db_path
        self.index_log = {
            "timestamp": datetime.now().isoformat(),
            "indexes_created": [],
            "performance_tests": [],
            "errors": []
        }
    
    def connect_db(self):
        """Créer une connexion à la base de données"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def create_matricule_search_indexes(self):
        """Créer les index pour les recherches rapides par matricule"""
        print("🔍 Création des index de recherche matricule...")
        
        conn = self.connect_db()
        cursor = conn.cursor()
        
        try:
            indexes_to_create = [
                # Index principal pour recherche exacte par matricule
                {
                    "name": "idx_fast_matricule_lookup",
                    "table": "matricule_name_resolver",
                    "sql": """
                        CREATE INDEX IF NOT EXISTS idx_fast_matricule_lookup 
                        ON matricule_name_resolver(matricule, is_active)
                    """,
                    "purpose": "Recherche exacte par matricule"
                },
                
                # Index pour recherche par préfixe matricule
                {
                    "name": "idx_matricule_prefix_search",
                    "table": "matricule_name_resolver", 
                    "sql": """
                        CREATE INDEX IF NOT EXISTS idx_matricule_prefix_search 
                        ON matricule_name_resolver(matricule COLLATE NOCASE)
                    """,
                    "purpose": "Recherche par préfixe matricule (insensible à la casse)"
                },
                
                # Index composite pour recherche par employeur + matricule
                {
                    "name": "idx_employer_matricule_lookup",
                    "table": "matricule_name_resolver",
                    "sql": """
                        CREATE INDEX IF NOT EXISTS idx_employer_matricule_lookup 
                        ON matricule_name_resolver(employer_id, matricule, is_active)
                    """,
                    "purpose": "Recherche matricule par employeur"
                },
                
                # Index pour recherche textuelle sur noms
                {
                    "name": "idx_name_text_search",
                    "table": "matricule_name_resolver",
                    "sql": """
                        CREATE INDEX IF NOT EXISTS idx_name_text_search 
                        ON matricule_name_resolver(full_name COLLATE NOCASE)
                    """,
                    "purpose": "Recherche textuelle sur noms complets"
                }
            ]
            
            for index_info in indexes_to_create:
                print(f"   📇 Création de {index_info['name']}...")
                cursor.execute(index_info["sql"])
                
                self.index_log["indexes_created"].append({
                    "name": index_info["name"],
                    "table": index_info["table"],
                    "purpose": index_info["purpose"]
                })
                
                print(f"     ✅ {index_info['purpose']}")
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            error_msg = f"Erreur lors de la création des index matricule: {e}"
            print(f"   ❌ {error_msg}")
            self.index_log["errors"].append(error_msg)
            return False
        finally:
            conn.close()
    
    def create_organizational_indexes(self):
        """Créer les index pour les requêtes organisationnelles"""
        print("🏢 Création des index organisationnels...")
        
        conn = self.connect_db()
        cursor = conn.cursor()
        
        try:
            indexes_to_create = [
                # Index pour recherche d'affectations par matricule
                {
                    "name": "idx_org_assignment_matricule_active",
                    "table": "worker_organizational_assignments",
                    "sql": """
                        CREATE INDEX IF NOT EXISTS idx_org_assignment_matricule_active 
                        ON worker_organizational_assignments(worker_matricule, is_active, effective_date)
                    """,
                    "purpose": "Affectations actives par matricule"
                },
                
                # Index pour recherche par unité organisationnelle
                {
                    "name": "idx_org_assignment_unit_active",
                    "table": "worker_organizational_assignments",
                    "sql": """
                        CREATE INDEX IF NOT EXISTS idx_org_assignment_unit_active 
                        ON worker_organizational_assignments(organizational_unit_id, is_active)
                    """,
                    "purpose": "Workers par unité organisationnelle"
                },
                
                # Index pour recherche par établissement (legacy)
                {
                    "name": "idx_org_assignment_etablissement",
                    "table": "worker_organizational_assignments",
                    "sql": """
                        CREATE INDEX IF NOT EXISTS idx_org_assignment_etablissement 
                        ON worker_organizational_assignments(etablissement, is_active)
                        WHERE etablissement IS NOT NULL
                    """,
                    "purpose": "Recherche par établissement (legacy)"
                },
                
                # Index pour audit trail des affectations
                {
                    "name": "idx_org_assignment_audit",
                    "table": "worker_organizational_assignments",
                    "sql": """
                        CREATE INDEX IF NOT EXISTS idx_org_assignment_audit 
                        ON worker_organizational_assignments(created_at, updated_at)
                    """,
                    "purpose": "Audit trail des affectations"
                }
            ]
            
            for index_info in indexes_to_create:
                print(f"   📇 Création de {index_info['name']}...")
                cursor.execute(index_info["sql"])
                
                self.index_log["indexes_created"].append({
                    "name": index_info["name"],
                    "table": index_info["table"],
                    "purpose": index_info["purpose"]
                })
                
                print(f"     ✅ {index_info['purpose']}")
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            error_msg = f"Erreur lors de la création des index organisationnels: {e}"
            print(f"   ❌ {error_msg}")
            self.index_log["errors"].append(error_msg)
            return False
        finally:
            conn.close()
    
    def create_composite_indexes(self):
        """Créer les index composites pour les jointures complexes"""
        print("🔗 Création des index composites pour jointures...")
        
        conn = self.connect_db()
        cursor = conn.cursor()
        
        try:
            indexes_to_create = [
                # Index pour jointure workers <-> resolver
                {
                    "name": "idx_workers_resolver_join",
                    "table": "workers",
                    "sql": """
                        CREATE INDEX IF NOT EXISTS idx_workers_resolver_join 
                        ON workers(matricule, employer_id)
                        WHERE matricule IS NOT NULL
                    """,
                    "purpose": "Jointure workers-resolver optimisée"
                },
                
                # Index pour jointure resolver <-> assignments
                {
                    "name": "idx_resolver_assignment_join",
                    "table": "matricule_name_resolver",
                    "sql": """
                        CREATE INDEX IF NOT EXISTS idx_resolver_assignment_join 
                        ON matricule_name_resolver(matricule, employer_id, is_active)
                    """,
                    "purpose": "Jointure resolver-assignments optimisée"
                },
                
                # Index pour audit trail par matricule
                {
                    "name": "idx_audit_matricule_chronological",
                    "table": "matricule_audit_trail",
                    "sql": """
                        CREATE INDEX IF NOT EXISTS idx_audit_matricule_chronological 
                        ON matricule_audit_trail(worker_id, changed_at DESC)
                    """,
                    "purpose": "Historique chronologique par worker"
                },
                
                # Index pour recherche d'audit par matricule
                {
                    "name": "idx_audit_matricule_search",
                    "table": "matricule_audit_trail",
                    "sql": """
                        CREATE INDEX IF NOT EXISTS idx_audit_matricule_search 
                        ON matricule_audit_trail(new_matricule, old_matricule)
                    """,
                    "purpose": "Recherche dans l'audit par matricule"
                }
            ]
            
            for index_info in indexes_to_create:
                print(f"   📇 Création de {index_info['name']}...")
                cursor.execute(index_info["sql"])
                
                self.index_log["indexes_created"].append({
                    "name": index_info["name"],
                    "table": index_info["table"],
                    "purpose": index_info["purpose"]
                })
                
                print(f"     ✅ {index_info['purpose']}")
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            error_msg = f"Erreur lors de la création des index composites: {e}"
            print(f"   ❌ {error_msg}")
            self.index_log["errors"].append(error_msg)
            return False
        finally:
            conn.close()
    
    def test_index_performance(self):
        """Tester les performances des index créés"""
        print("⚡ Test des performances des index...")
        
        conn = self.connect_db()
        cursor = conn.cursor()
        
        try:
            performance_tests = []
            
            # Test 1: Recherche par matricule exact
            print("   🔍 Test recherche par matricule exact...")
            start_time = time.time()
            cursor.execute("""
                SELECT r.*, w.nom, w.prenom 
                FROM matricule_name_resolver r
                JOIN workers w ON r.worker_id = w.id
                WHERE r.matricule = 'E001AB001' AND r.is_active = 1
            """)
            result = cursor.fetchone()
            end_time = time.time()
            
            performance_tests.append({
                "test": "matricule_exact_search",
                "duration_ms": round((end_time - start_time) * 1000, 2),
                "result_found": result is not None
            })
            print(f"     ⏱️  Durée: {performance_tests[-1]['duration_ms']}ms")
            
            # Test 2: Recherche par nom (avec LIKE)
            print("   🔍 Test recherche par nom...")
            start_time = time.time()
            cursor.execute("""
                SELECT matricule, full_name 
                FROM matricule_name_resolver 
                WHERE full_name LIKE '%MARTIN%' AND is_active = 1
            """)
            results = cursor.fetchall()
            end_time = time.time()
            
            performance_tests.append({
                "test": "name_like_search",
                "duration_ms": round((end_time - start_time) * 1000, 2),
                "results_count": len(results)
            })
            print(f"     ⏱️  Durée: {performance_tests[-1]['duration_ms']}ms ({len(results)} résultats)")
            
            # Test 3: Jointure complexe avec affectations
            print("   🔍 Test jointure complexe...")
            start_time = time.time()
            cursor.execute("""
                SELECT r.matricule, r.full_name, oa.etablissement, oa.departement
                FROM matricule_name_resolver r
                JOIN worker_organizational_assignments oa ON r.matricule = oa.worker_matricule
                WHERE r.employer_id = 1 AND oa.is_active = 1
                ORDER BY r.full_name
            """)
            results = cursor.fetchall()
            end_time = time.time()
            
            performance_tests.append({
                "test": "complex_join_query",
                "duration_ms": round((end_time - start_time) * 1000, 2),
                "results_count": len(results)
            })
            print(f"     ⏱️  Durée: {performance_tests[-1]['duration_ms']}ms ({len(results)} résultats)")
            
            # Test 4: Recherche par préfixe matricule
            print("   🔍 Test recherche par préfixe...")
            start_time = time.time()
            cursor.execute("""
                SELECT matricule, full_name 
                FROM matricule_name_resolver 
                WHERE matricule LIKE 'E001%' AND is_active = 1
            """)
            results = cursor.fetchall()
            end_time = time.time()
            
            performance_tests.append({
                "test": "matricule_prefix_search",
                "duration_ms": round((end_time - start_time) * 1000, 2),
                "results_count": len(results)
            })
            print(f"     ⏱️  Durée: {performance_tests[-1]['duration_ms']}ms ({len(results)} résultats)")
            
            self.index_log["performance_tests"] = performance_tests
            
            # Vérifier que toutes les requêtes sont rapides (< 100ms)
            slow_queries = [test for test in performance_tests if test["duration_ms"] > 100]
            
            if not slow_queries:
                print("   ✅ Toutes les requêtes sont rapides (< 100ms)")
                return True
            else:
                print(f"   ⚠️  {len(slow_queries)} requêtes lentes détectées")
                for query in slow_queries:
                    print(f"     - {query['test']}: {query['duration_ms']}ms")
                return False
            
        except Exception as e:
            error_msg = f"Erreur lors des tests de performance: {e}"
            print(f"   ❌ {error_msg}")
            self.index_log["errors"].append(error_msg)
            return False
        finally:
            conn.close()
    
    def analyze_index_usage(self):
        """Analyser l'utilisation des index créés"""
        print("📊 Analyse de l'utilisation des index...")
        
        conn = self.connect_db()
        cursor = conn.cursor()
        
        try:
            # Obtenir la liste de tous les index créés
            cursor.execute("""
                SELECT name, tbl_name, sql 
                FROM sqlite_master 
                WHERE type = 'index' 
                AND name LIKE 'idx_%'
                ORDER BY tbl_name, name
            """)
            
            indexes = cursor.fetchall()
            
            print(f"   📇 Index trouvés: {len(indexes)}")
            
            index_analysis = []
            for index in indexes:
                analysis = {
                    "name": index["name"],
                    "table": index["tbl_name"],
                    "sql": index["sql"]
                }
                index_analysis.append(analysis)
                print(f"     - {index['name']} sur {index['tbl_name']}")
            
            self.index_log["index_analysis"] = index_analysis
            return True
            
        except Exception as e:
            error_msg = f"Erreur lors de l'analyse des index: {e}"
            print(f"   ❌ {error_msg}")
            self.index_log["errors"].append(error_msg)
            return False
        finally:
            conn.close()
    
    def run_performance_optimization(self):
        """Exécuter l'optimisation complète des performances"""
        print("🚀 DÉMARRAGE DE L'OPTIMISATION DES PERFORMANCES")
        print("=" * 70)
        
        success_count = 0
        total_steps = 5
        
        try:
            # Étape 1: Index de recherche matricule
            print(f"\n📋 ÉTAPE 1/{total_steps}: Index de recherche matricule")
            if self.create_matricule_search_indexes():
                success_count += 1
            
            # Étape 2: Index organisationnels
            print(f"\n📋 ÉTAPE 2/{total_steps}: Index organisationnels")
            if self.create_organizational_indexes():
                success_count += 1
            
            # Étape 3: Index composites
            print(f"\n📋 ÉTAPE 3/{total_steps}: Index composites")
            if self.create_composite_indexes():
                success_count += 1
            
            # Étape 4: Tests de performance
            print(f"\n📋 ÉTAPE 4/{total_steps}: Tests de performance")
            if self.test_index_performance():
                success_count += 1
            
            # Étape 5: Analyse des index
            print(f"\n📋 ÉTAPE 5/{total_steps}: Analyse des index")
            if self.analyze_index_usage():
                success_count += 1
            
            # Sauvegarder le log
            log_filename = f"performance_indexes_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(log_filename, 'w', encoding='utf-8') as f:
                json.dump(self.index_log, f, indent=2, ensure_ascii=False)
            
            print(f"\n📊 RÉSUMÉ DE L'OPTIMISATION")
            print("=" * 70)
            print(f"✅ Étapes réussies: {success_count}/{total_steps}")
            print(f"📇 Index créés: {len(self.index_log['indexes_created'])}")
            print(f"⚡ Tests de performance: {len(self.index_log['performance_tests'])}")
            print(f"❌ Erreurs: {len(self.index_log['errors'])}")
            print(f"💾 Log sauvegardé: {log_filename}")
            
            if success_count == total_steps:
                print(f"\n🎉 OPTIMISATION DES PERFORMANCES TERMINÉE AVEC SUCCÈS!")
                
                # Afficher un résumé des performances
                if self.index_log["performance_tests"]:
                    print(f"\n⚡ RÉSUMÉ DES PERFORMANCES:")
                    for test in self.index_log["performance_tests"]:
                        status = "✅" if test["duration_ms"] < 100 else "⚠️"
                        print(f"   {status} {test['test']}: {test['duration_ms']}ms")
                
                return True
            else:
                print(f"\n⚠️  OPTIMISATION PARTIELLEMENT RÉUSSIE")
                return False
                
        except Exception as e:
            print(f"❌ Erreur critique lors de l'optimisation: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    manager = PerformanceIndexManager()
    manager.run_performance_optimization()