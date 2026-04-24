#!/usr/bin/env python3
"""
Test du MatriculeIntegrityService - Validation complète
Task 6.3: Test de la validation continue lors des modifications
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'siirh-backend'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.services.matricule_integrity_service import MatriculeIntegrityService, IntegrityLevel
import json
from datetime import datetime

def test_matricule_integrity_service():
    """Test complet du service d'intégrité des matricules"""
    
    # Configuration de la base de données
    DATABASE_URL = "postgresql://siirh_user:siirh_password@localhost:5432/siirh_db"
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    print("🔍 Test du MatriculeIntegrityService")
    print("=" * 60)
    
    with SessionLocal() as db:
        service = MatriculeIntegrityService(db)
        
        # Test 1: Validation complète d'intégrité
        print("\n1️⃣ Test de validation complète d'intégrité")
        print("-" * 40)
        
        try:
            report = service.validate_complete_integrity()
            
            print(f"✅ Rapport généré avec succès")
            print(f"   📊 Total checks: {report.total_checks}")
            print(f"   ✅ Passed: {report.passed_checks}")
            print(f"   ❌ Failed: {report.failed_checks}")
            print(f"   🎯 Status: {report.overall_status}")
            print(f"   📝 Issues: {len(report.issues)}")
            
            # Afficher les problèmes détectés
            for issue in report.issues:
                print(f"   🚨 {issue.level.value}: {issue.description}")
                print(f"      Category: {issue.category}")
                print(f"      Auto-fixable: {issue.auto_fixable}")
                print(f"      Affected records: {len(issue.affected_records)}")
            
            # Afficher les recommandations
            print(f"\n   📋 Recommandations:")
            for rec in report.recommendations:
                print(f"      {rec}")
            
        except Exception as e:
            print(f"❌ Erreur lors de la validation: {e}")
        
        # Test 2: Validation continue lors des modifications
        print("\n2️⃣ Test de validation continue")
        print("-" * 40)
        
        # Test CREATE operation
        test_data_create = {
            "matricule": "E001TEST001",
            "nom": "Test",
            "prenom": "Worker",
            "id": 999
        }
        
        try:
            result = service.validate_continuous_integrity("CREATE", test_data_create)
            
            print(f"✅ Validation CREATE: {result['status']}")
            print(f"   ⚠️  Warnings: {len(result['warnings'])}")
            print(f"   ❌ Errors: {len(result['errors'])}")
            print(f"   🔧 Auto-corrections: {len(result['auto_corrections'])}")
            
            for warning in result['warnings']:
                print(f"      ⚠️  {warning}")
            
            for error in result['errors']:
                print(f"      ❌ {error}")
            
            for correction in result['auto_corrections']:
                print(f"      🔧 {correction}")
            
        except Exception as e:
            print(f"❌ Erreur lors de la validation continue: {e}")
        
        # Test UPDATE operation
        test_data_update = {
            "matricule": "E001EXIST001",  # Matricule existant
            "nom": "Updated",
            "prenom": "Worker",
            "id": 1
        }
        
        try:
            result = service.validate_continuous_integrity("UPDATE", test_data_update)
            
            print(f"\n✅ Validation UPDATE: {result['status']}")
            print(f"   ⚠️  Warnings: {len(result['warnings'])}")
            print(f"   ❌ Errors: {len(result['errors'])}")
            
        except Exception as e:
            print(f"❌ Erreur lors de la validation UPDATE: {e}")
        
        # Test 3: Alertes critiques d'intégrité
        print("\n3️⃣ Test des alertes critiques")
        print("-" * 40)
        
        try:
            alerts = service.get_integrity_alerts()
            
            print(f"✅ {len(alerts)} alertes détectées")
            
            for alert in alerts:
                print(f"   🚨 {alert['type']}: {alert['message']}")
                print(f"      Category: {alert['category']}")
            
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des alertes: {e}")
        
        # Test 4: Auto-correction des problèmes
        print("\n4️⃣ Test d'auto-correction")
        print("-" * 40)
        
        try:
            # D'abord obtenir un rapport
            report = service.validate_complete_integrity()
            
            # Tenter les auto-corrections
            if report.issues:
                fix_results = service.auto_fix_issues(report)
                
                print(f"✅ Auto-corrections tentées: {fix_results['fixes_attempted']}")
                print(f"   ✅ Réussies: {fix_results['fixes_successful']}")
                print(f"   ❌ Échouées: {fix_results['fixes_failed']}")
                
                for detail in fix_results['details']:
                    print(f"      {detail['category']}: {detail['status']}")
            else:
                print("✅ Aucun problème à corriger")
            
        except Exception as e:
            print(f"❌ Erreur lors de l'auto-correction: {e}")
        
        # Test 5: Validation par employeur spécifique
        print("\n5️⃣ Test de validation par employeur")
        print("-" * 40)
        
        try:
            # Tester avec l'employeur 1
            report_emp1 = service.validate_complete_integrity(employer_id=1)
            
            print(f"✅ Validation employeur 1:")
            print(f"   📊 Total checks: {report_emp1.total_checks}")
            print(f"   ✅ Passed: {report_emp1.passed_checks}")
            print(f"   ❌ Failed: {report_emp1.failed_checks}")
            print(f"   🎯 Status: {report_emp1.overall_status}")
            
        except Exception as e:
            print(f"❌ Erreur lors de la validation par employeur: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Test du MatriculeIntegrityService terminé")

if __name__ == "__main__":
    test_matricule_integrity_service()