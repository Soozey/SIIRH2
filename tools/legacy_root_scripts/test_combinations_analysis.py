#!/usr/bin/env python3
"""
Test simple pour l'analyse des combinaisons organisationnelles
"""

import sqlite3
import os
from collections import defaultdict

def test_database_connection():
    """Test de connexion à la base de données"""
    db_path = "siirh-backend/siirh.db"
    
    print("🔍 Test de connexion à la base de données...")
    print(f"Chemin: {db_path}")
    print(f"Existe: {os.path.exists(db_path)}")
    
    if not os.path.exists(db_path):
        print("❌ Base de données non trouvée")
        return False
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Test de base
            cursor.execute("SELECT COUNT(*) FROM workers")
            total_workers = cursor.fetchone()[0]
            print(f"✅ Total salariés: {total_workers}")
            
            # Test des combinaisons organisationnelles
            cursor.execute("""
                SELECT 
                    employer_id,
                    etablissement, 
                    departement, 
                    service, 
                    unite,
                    COUNT(*) as worker_count
                FROM workers 
                WHERE etablissement IS NOT NULL 
                   OR departement IS NOT NULL 
                   OR service IS NOT NULL 
                   OR unite IS NOT NULL
                GROUP BY employer_id, etablissement, departement, service, unite
                ORDER BY employer_id, worker_count DESC
            """)
            
            combinations = cursor.fetchall()
            print(f"✅ Combinaisons organisationnelles: {len(combinations)}")
            
            # Afficher quelques exemples
            print("\n📋 Exemples de combinaisons:")
            for i, combo in enumerate(combinations[:5]):
                employer_id, etab, dept, serv, unite, count = combo
                print(f"   {i+1}. Employeur {employer_id}: {etab} > {dept} > {serv} > {unite} ({count} salariés)")
            
            return True
            
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False

def analyze_hierarchy_patterns():
    """Analyse simple des patterns hiérarchiques"""
    db_path = "siirh-backend/siirh.db"
    
    print("\n🔍 Analyse des patterns hiérarchiques...")
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    etablissement, 
                    departement, 
                    service, 
                    unite,
                    COUNT(*) as worker_count
                FROM workers 
                WHERE etablissement IS NOT NULL 
                   OR departement IS NOT NULL 
                   OR service IS NOT NULL 
                   OR unite IS NOT NULL
                GROUP BY etablissement, departement, service, unite
                ORDER BY worker_count DESC
            """)
            
            combinations = cursor.fetchall()
            
            # Analyser les relations hiérarchiques
            etab_to_dept = defaultdict(set)
            dept_to_service = defaultdict(set)
            service_to_unite = defaultdict(set)
            
            complete_paths = 0
            incomplete_paths = 0
            
            for combo in combinations:
                etab, dept, serv, unite, count = combo
                
                # Vérifier si le chemin est complet
                if unite and serv and dept and etab:
                    complete_paths += 1
                elif serv and dept and etab:
                    complete_paths += 1
                elif dept and etab:
                    complete_paths += 1
                elif etab:
                    complete_paths += 1
                else:
                    incomplete_paths += 1
                
                # Construire les relations
                if etab and dept:
                    etab_to_dept[etab].add(dept)
                if dept and serv:
                    dept_to_service[dept].add(serv)
                if serv and unite:
                    service_to_unite[serv].add(unite)
            
            print(f"✅ Chemins hiérarchiques complets: {complete_paths}")
            print(f"⚠️  Chemins hiérarchiques incomplets: {incomplete_paths}")
            
            print(f"\n📊 Relations hiérarchiques détectées:")
            print(f"   • Établissements → Départements: {len(etab_to_dept)} relations")
            print(f"   • Départements → Services: {len(dept_to_service)} relations")
            print(f"   • Services → Unités: {len(service_to_unite)} relations")
            
            # Détecter les violations potentielles
            violations = 0
            
            # Départements rattachés à plusieurs établissements
            dept_to_etabs = defaultdict(set)
            for etab, depts in etab_to_dept.items():
                for dept in depts:
                    dept_to_etabs[dept].add(etab)
            
            for dept, etabs in dept_to_etabs.items():
                if len(etabs) > 1:
                    violations += 1
                    print(f"   ⚠️  Département '{dept}' rattaché à {len(etabs)} établissements")
            
            if violations == 0:
                print("✅ Aucune violation hiérarchique détectée")
            else:
                print(f"⚠️  {violations} violations hiérarchiques détectées")
            
            return True
            
    except Exception as e:
        print(f"❌ Erreur d'analyse: {e}")
        return False

def main():
    print("🚀 TEST D'ANALYSE DES COMBINAISONS ORGANISATIONNELLES")
    print("=" * 60)
    
    # Test 1: Connexion à la base de données
    if not test_database_connection():
        return False
    
    # Test 2: Analyse des patterns hiérarchiques
    if not analyze_hierarchy_patterns():
        return False
    
    print("\n" + "=" * 60)
    print("✅ Tests terminés avec succès !")
    print("🎯 Le script principal peut maintenant être exécuté")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)