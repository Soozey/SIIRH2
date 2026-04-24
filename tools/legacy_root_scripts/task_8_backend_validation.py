#!/usr/bin/env python3
"""
Task 8: Checkpoint - Validation du Backend
Validation complète du système backend matricules
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'siirh-backend'))

import requests
import json
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Configuration
DATABASE_URL = "postgresql+psycopg2://postgres:tantely123@127.0.0.1:5432/db_siirh_app"
API_BASE = "http://localhost:8000/api/matricules"

class BackendValidator:
    """Validateur complet du backend matricules"""
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "validation_type": "backend_checkpoint",
            "tests": {},
            "overall_status": "UNKNOWN",
            "issues": [],
            "recommendations": []
        }
        
        # Configuration base de données
        self.engine = create_engine(DATABASE_URL)
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def validate_database_schema(self) -> bool:
        """Valider le schéma de base de données"""
        print("\n📋 VALIDATION DU SCHÉMA DE BASE DE DONNÉES")
        print("-" * 50)
        
        db = self.SessionLocal()
        try:
            required_tables = [
                "workers",
                "matricule_name_resolver", 
                "worker_organizational_assignments",
                "matricule_audit_trail",
                "matricule_validation_rules"
            ]
            
            existing_tables = []
            missing_tables = []
            
            for table in required_tables:
                try:
                    result = db.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
                    existing_tables.append(table)
                    print(f"   ✅ Table {table}: {result} enregistrements")
                except Exception as e:
                    missing_tables.append(table)
                    print(f"   ❌ Table {table}: MANQUANTE ({e})")
            
            # Vérifier les colonnes critiques
            critical_columns = [
                ("workers", "matricule"),
                ("matricule_name_resolver", "search_vector"),
                ("worker_organizational_assignments", "assignment_type"),
                ("worker_organizational_assignments", "effective_date")
            ]
            
            column_issues = []
            for table, column in critical_columns:
                try:
                    db.execute(text(f"SELECT {column} FROM {table} LIMIT 1"))
                    print(f"   ✅ Colonne {table}.{column}: OK")
                except Exception as e:
                    column_issues.append(f"{table}.{column}")
                    print(f"   ❌ Colonne {table}.{column}: MANQUANTE")
            
            schema_valid = len(missing_tables) == 0 and len(column_issues) == 0
            
            self.results["tests"]["database_schema"] = {
                "status": "PASS" if schema_valid else "FAIL",
                "existing_tables": existing_tables,
                "missing_tables": missing_tables,
                "column_issues": column_issues
            }
            
            if not schema_valid:
                self.results["issues"].extend([
                    f"Tables manquantes: {missing_tables}",
                    f"Colonnes manquantes: {column_issues}"
                ])
            
            return schema_valid
            
        finally:
            db.close()
    
    def validate_data_integrity(self) -> bool:
        """Valider l'intégrité des données"""
        print("\n🔍 VALIDATION DE L'INTÉGRITÉ DES DONNÉES")
        print("-" * 50)
        
        db = self.SessionLocal()
        try:
            integrity_checks = []
            
            # 1. Vérifier la cohérence matricule_name_resolver <-> workers
            resolver_workers = db.execute(text("""
                SELECT COUNT(*) FROM matricule_name_resolver r
                LEFT JOIN workers w ON w.id = r.worker_id
                WHERE w.id IS NULL
            """)).scalar()
            
            if resolver_workers == 0:
                print("   ✅ Cohérence resolver-workers: OK")
                integrity_checks.append(True)
            else:
                print(f"   ❌ {resolver_workers} entrées resolver orphelines")
                integrity_checks.append(False)
            
            # 2. Vérifier la cohérence assignments <-> workers
            assignment_workers = db.execute(text("""
                SELECT COUNT(*) FROM worker_organizational_assignments woa
                LEFT JOIN workers w ON w.matricule = woa.worker_matricule
                WHERE w.id IS NULL
            """)).scalar()
            
            if assignment_workers == 0:
                print("   ✅ Cohérence assignments-workers: OK")
                integrity_checks.append(True)
            else:
                print(f"   ❌ {assignment_workers} affectations avec matricules invalides")
                integrity_checks.append(False)
            
            # 3. Vérifier l'unicité des matricules
            duplicate_matricules = db.execute(text("""
                SELECT matricule, COUNT(*) as count
                FROM workers 
                WHERE matricule IS NOT NULL AND matricule != ''
                GROUP BY matricule
                HAVING COUNT(*) > 1
            """)).fetchall()
            
            if len(duplicate_matricules) == 0:
                print("   ✅ Unicité des matricules: OK")
                integrity_checks.append(True)
            else:
                print(f"   ❌ {len(duplicate_matricules)} matricules dupliqués")
                integrity_checks.append(False)
            
            # 4. Vérifier la synchronisation resolver
            sync_issues = db.execute(text("""
                SELECT COUNT(*) FROM workers w
                LEFT JOIN matricule_name_resolver r ON r.worker_id = w.id AND r.is_active = 1
                WHERE w.matricule IS NOT NULL AND w.matricule != '' AND r.id IS NULL
            """)).scalar()
            
            if sync_issues == 0:
                print("   ✅ Synchronisation resolver: OK")
                integrity_checks.append(True)
            else:
                print(f"   ❌ {sync_issues} workers non synchronisés dans resolver")
                integrity_checks.append(False)
            
            integrity_valid = all(integrity_checks)
            
            self.results["tests"]["data_integrity"] = {
                "status": "PASS" if integrity_valid else "FAIL",
                "resolver_orphans": resolver_workers,
                "assignment_orphans": assignment_workers,
                "duplicate_matricules": len(duplicate_matricules),
                "sync_issues": sync_issues
            }
            
            return integrity_valid
            
        finally:
            db.close()
    
    def validate_services(self) -> bool:
        """Valider les services backend"""
        print("\n🔧 VALIDATION DES SERVICES BACKEND")
        print("-" * 50)
        
        db = self.SessionLocal()
        try:
            from app.services.matricule_service import MatriculeService
            from app.services.organizational_assignment_service import OrganizationalAssignmentService
            from app.services.matricule_migration_service import MatriculeMigrationService
            from app.services.matricule_integrity_service import MatriculeIntegrityService
            
            service_tests = []
            
            # Test MatriculeService
            try:
                matricule_service = MatriculeService(db)
                # Test résolution
                test_matricule = db.execute(text("SELECT matricule FROM workers WHERE matricule IS NOT NULL LIMIT 1")).scalar()
                if test_matricule:
                    resolution = matricule_service.resolve_matricule_to_name(test_matricule)
                    if resolution:
                        print(f"   ✅ MatriculeService: Résolution OK ({test_matricule})")
                        service_tests.append(True)
                    else:
                        print(f"   ❌ MatriculeService: Résolution échouée")
                        service_tests.append(False)
                else:
                    print("   ⚠️  MatriculeService: Aucun matricule pour test")
                    service_tests.append(True)
            except Exception as e:
                print(f"   ❌ MatriculeService: Erreur ({e})")
                service_tests.append(False)
            
            # Test OrganizationalAssignmentService
            try:
                assignment_service = OrganizationalAssignmentService(db)
                test_matricule = db.execute(text("SELECT worker_matricule FROM worker_organizational_assignments LIMIT 1")).scalar()
                if test_matricule:
                    assignment = assignment_service.get_active_assignment(test_matricule)
                    print(f"   ✅ OrganizationalAssignmentService: OK")
                    service_tests.append(True)
                else:
                    print("   ⚠️  OrganizationalAssignmentService: Aucune affectation pour test")
                    service_tests.append(True)
            except Exception as e:
                print(f"   ❌ OrganizationalAssignmentService: Erreur ({e})")
                service_tests.append(False)
            
            # Test MatriculeMigrationService
            try:
                migration_service = MatriculeMigrationService(db)
                analysis = migration_service.analyze_migration_requirements()
                print(f"   ✅ MatriculeMigrationService: Analyse OK")
                service_tests.append(True)
            except Exception as e:
                print(f"   ❌ MatriculeMigrationService: Erreur ({e})")
                service_tests.append(False)
            
            # Test MatriculeIntegrityService
            try:
                integrity_service = MatriculeIntegrityService(db)
                report = integrity_service.validate_complete_integrity()
                print(f"   ✅ MatriculeIntegrityService: Validation OK")
                service_tests.append(True)
            except Exception as e:
                print(f"   ❌ MatriculeIntegrityService: Erreur ({e})")
                service_tests.append(False)
            
            services_valid = all(service_tests)
            
            self.results["tests"]["backend_services"] = {
                "status": "PASS" if services_valid else "FAIL",
                "matricule_service": service_tests[0] if len(service_tests) > 0 else False,
                "assignment_service": service_tests[1] if len(service_tests) > 1 else False,
                "migration_service": service_tests[2] if len(service_tests) > 2 else False,
                "integrity_service": service_tests[3] if len(service_tests) > 3 else False
            }
            
            return services_valid
            
        finally:
            db.close()
    
    def validate_api_endpoints(self) -> bool:
        """Valider les endpoints API"""
        print("\n🌐 VALIDATION DES ENDPOINTS API")
        print("-" * 50)
        
        api_tests = []
        
        # Test health check
        try:
            response = requests.get(f"{API_BASE}/health", timeout=5)
            if response.status_code == 200:
                print("   ✅ Health endpoint: OK")
                api_tests.append(True)
            else:
                print(f"   ❌ Health endpoint: {response.status_code}")
                api_tests.append(False)
        except Exception as e:
            print(f"   ❌ Health endpoint: Erreur ({e})")
            api_tests.append(False)
        
        # Test search endpoint
        try:
            response = requests.get(f"{API_BASE}/search?query=test", timeout=5)
            if response.status_code == 200:
                print("   ✅ Search endpoint: OK")
                api_tests.append(True)
            else:
                print(f"   ❌ Search endpoint: {response.status_code}")
                api_tests.append(False)
        except Exception as e:
            print(f"   ❌ Search endpoint: Erreur ({e})")
            api_tests.append(False)
        
        # Test integrity endpoint
        try:
            response = requests.get(f"{API_BASE}/integrity/validate", timeout=10)
            if response.status_code == 200:
                print("   ✅ Integrity endpoint: OK")
                api_tests.append(True)
            else:
                print(f"   ❌ Integrity endpoint: {response.status_code}")
                api_tests.append(False)
        except Exception as e:
            print(f"   ❌ Integrity endpoint: Erreur ({e})")
            api_tests.append(False)
        
        # Test migration analysis endpoint
        try:
            response = requests.get(f"{API_BASE}/migration/analysis", timeout=10)
            if response.status_code == 200:
                print("   ✅ Migration analysis endpoint: OK")
                api_tests.append(True)
            else:
                print(f"   ❌ Migration analysis endpoint: {response.status_code}")
                api_tests.append(False)
        except Exception as e:
            print(f"   ❌ Migration analysis endpoint: Erreur ({e})")
            api_tests.append(False)
        
        api_valid = all(api_tests)
        
        self.results["tests"]["api_endpoints"] = {
            "status": "PASS" if api_valid else "FAIL",
            "health_check": api_tests[0] if len(api_tests) > 0 else False,
            "search_endpoint": api_tests[1] if len(api_tests) > 1 else False,
            "integrity_endpoint": api_tests[2] if len(api_tests) > 2 else False,
            "migration_endpoint": api_tests[3] if len(api_tests) > 3 else False
        }
        
        return api_valid
    
    def validate_performance(self) -> bool:
        """Valider les performances"""
        print("\n⚡ VALIDATION DES PERFORMANCES")
        print("-" * 50)
        
        db = self.SessionLocal()
        try:
            performance_tests = []
            
            # Test performance requêtes de base
            import time
            
            # Test résolution matricule
            start_time = time.time()
            test_matricule = db.execute(text("SELECT matricule FROM workers WHERE matricule IS NOT NULL LIMIT 1")).scalar()
            if test_matricule:
                db.execute(text("SELECT * FROM matricule_name_resolver WHERE matricule = :matricule"), 
                          {"matricule": test_matricule})
            resolution_time = (time.time() - start_time) * 1000
            
            if resolution_time < 100:
                print(f"   ✅ Résolution matricule: {resolution_time:.1f}ms")
                performance_tests.append(True)
            else:
                print(f"   ⚠️  Résolution matricule: {resolution_time:.1f}ms (> 100ms)")
                performance_tests.append(False)
            
            # Test recherche par nom
            start_time = time.time()
            db.execute(text("SELECT * FROM matricule_name_resolver WHERE LOWER(full_name) LIKE '%jean%' LIMIT 10"))
            search_time = (time.time() - start_time) * 1000
            
            if search_time < 150:
                print(f"   ✅ Recherche par nom: {search_time:.1f}ms")
                performance_tests.append(True)
            else:
                print(f"   ⚠️  Recherche par nom: {search_time:.1f}ms (> 150ms)")
                performance_tests.append(False)
            
            # Test requête affectations
            start_time = time.time()
            db.execute(text("SELECT * FROM worker_organizational_assignments WHERE is_active = 1 LIMIT 10"))
            assignment_time = (time.time() - start_time) * 1000
            
            if assignment_time < 100:
                print(f"   ✅ Requête affectations: {assignment_time:.1f}ms")
                performance_tests.append(True)
            else:
                print(f"   ⚠️  Requête affectations: {assignment_time:.1f}ms (> 100ms)")
                performance_tests.append(False)
            
            performance_valid = all(performance_tests)
            
            self.results["tests"]["performance"] = {
                "status": "PASS" if performance_valid else "WARN",
                "matricule_resolution_ms": resolution_time,
                "name_search_ms": search_time,
                "assignment_query_ms": assignment_time
            }
            
            return performance_valid
            
        finally:
            db.close()
    
    def run_validation(self) -> bool:
        """Exécuter la validation complète"""
        print("🚀 VALIDATION COMPLÈTE DU BACKEND MATRICULES")
        print("=" * 60)
        print(f"Timestamp: {self.results['timestamp']}")
        
        # Exécuter tous les tests
        schema_valid = self.validate_database_schema()
        integrity_valid = self.validate_data_integrity()
        services_valid = self.validate_services()
        api_valid = self.validate_api_endpoints()
        performance_valid = self.validate_performance()
        
        # Calculer le statut global
        all_tests = [schema_valid, integrity_valid, services_valid, api_valid]
        critical_passed = all(all_tests)
        
        if critical_passed and performance_valid:
            self.results["overall_status"] = "EXCELLENT"
        elif critical_passed:
            self.results["overall_status"] = "GOOD"
        else:
            self.results["overall_status"] = "ISSUES"
        
        # Générer les recommandations
        if not schema_valid:
            self.results["recommendations"].append("Corriger le schéma de base de données")
        if not integrity_valid:
            self.results["recommendations"].append("Résoudre les problèmes d'intégrité des données")
        if not services_valid:
            self.results["recommendations"].append("Corriger les services backend défaillants")
        if not api_valid:
            self.results["recommendations"].append("Corriger les endpoints API défaillants")
        if not performance_valid:
            self.results["recommendations"].append("Optimiser les performances des requêtes")
        
        # Afficher le résumé
        print(f"\n📊 RÉSUMÉ DE LA VALIDATION")
        print("=" * 40)
        print(f"Statut global: {self.results['overall_status']}")
        print(f"Schéma DB: {'✅' if schema_valid else '❌'}")
        print(f"Intégrité: {'✅' if integrity_valid else '❌'}")
        print(f"Services: {'✅' if services_valid else '❌'}")
        print(f"API: {'✅' if api_valid else '❌'}")
        print(f"Performance: {'✅' if performance_valid else '⚠️'}")
        
        if self.results["recommendations"]:
            print(f"\n📋 Recommandations:")
            for rec in self.results["recommendations"]:
                print(f"   - {rec}")
        
        return critical_passed

def main():
    """Fonction principale"""
    validator = BackendValidator()
    
    try:
        success = validator.run_validation()
        
        # Sauvegarder les résultats
        log_filename = f"backend_validation_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(log_filename, "w") as f:
            json.dump(validator.results, f, indent=2)
        
        print(f"\n💾 Résultats sauvegardés: {log_filename}")
        
        if success:
            print("\n🎉 VALIDATION BACKEND RÉUSSIE!")
            print("✅ Le système backend est prêt pour l'intégration frontend")
            return True
        else:
            print("\n⚠️  VALIDATION BACKEND AVEC PROBLÈMES")
            print("❌ Corriger les problèmes avant de continuer")
            return False
            
    except Exception as e:
        print(f"\n❌ ERREUR LORS DE LA VALIDATION: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)