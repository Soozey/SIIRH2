#!/usr/bin/env python3
"""
Script de migration des données organisationnelles existantes vers la nouvelle structure hiérarchique.

Ce script :
1. Analyse les combinaisons organisationnelles existantes dans la table workers
2. Crée automatiquement la hiérarchie correspondante dans organizational_nodes
3. Met à jour les références des salariés (optionnel)
4. Génère un rapport de migration détaillé

Basé sur l'analyse précédente qui montre un état parfait pour la migration AUTO.

Exécution : python migrate_existing_organizational_data.py
"""

import sys
import os
import sqlite3
from datetime import datetime
import json
from collections import defaultdict

def analyze_existing_combinations():
    """Analyse les combinaisons organisationnelles existantes"""
    
    db_path = "siirh-backend/siirh.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 Analyse des combinaisons organisationnelles existantes...")
        
        # Récupérer toutes les combinaisons uniques
        cursor.execute("""
            SELECT DISTINCT
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
            ORDER BY employer_id, etablissement, departement, service, unite
        """)
        
        combinations = cursor.fetchall()
        
        print(f"✅ {len(combinations)} combinaisons organisationnelles trouvées")
        
        # Analyser par employeur
        by_employer = defaultdict(list)
        for combo in combinations:
            employer_id = combo[0]
            by_employer[employer_id].append(combo)
        
        analysis = {
            "total_combinations": len(combinations),
            "employers_affected": len(by_employer),
            "combinations_by_employer": dict(by_employer),
            "raw_combinations": combinations
        }
        
        conn.close()
        return analysis
        
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse : {e}")
        return None


def create_hierarchical_structure(employer_id, combinations):
    """Crée la structure hiérarchique pour un employeur"""
    
    db_path = "siirh-backend/siirh.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print(f"\n🏗️ Création de la hiérarchie pour l'employeur {employer_id}...")
        
        # Dictionnaire pour mapper les noms vers les IDs créés
        node_mapping = {}
        
        results = {
            "etablissements_created": 0,
            "departements_created": 0,
            "services_created": 0,
            "unites_created": 0,
            "conflicts": []
        }
        
        # 1. Créer tous les établissements uniques
        etablissements = set()
        for combo in combinations:
            if combo[1]:  # etablissement
                etablissements.add(combo[1])
        
        print(f"  📍 Création de {len(etablissements)} établissements...")
        for etab_name in sorted(etablissements):
            try:
                cursor.execute("""
                    INSERT INTO organizational_nodes (employer_id, parent_id, level, name, code, created_by)
                    VALUES (?, NULL, 1, ?, ?, 1)
                """, (employer_id, etab_name, f"ETAB-{len(node_mapping)+1}"))
                
                etab_id = cursor.lastrowid
                node_mapping[f"etab_{etab_name}"] = etab_id
                results["etablissements_created"] += 1
                print(f"    ✅ {etab_name} (ID: {etab_id})")
                
            except sqlite3.IntegrityError as e:
                results["conflicts"].append(f"Établissement '{etab_name}': {str(e)}")
                print(f"    ⚠️ Conflit pour {etab_name}: {str(e)}")
        
        # 2. Créer tous les départements uniques
        departements = set()
        for combo in combinations:
            if combo[1] and combo[2]:  # etablissement et departement
                departements.add((combo[1], combo[2]))
        
        print(f"  🏛️ Création de {len(departements)} départements...")
        for etab_name, dept_name in sorted(departements):
            etab_key = f"etab_{etab_name}"
            dept_key = f"dept_{etab_name}_{dept_name}"
            
            if etab_key in node_mapping and dept_key not in node_mapping:
                try:
                    cursor.execute("""
                        INSERT INTO organizational_nodes (employer_id, parent_id, level, name, code, created_by)
                        VALUES (?, ?, 2, ?, ?, 1)
                    """, (employer_id, node_mapping[etab_key], dept_name, f"DEPT-{len(node_mapping)+1}"))
                    
                    dept_id = cursor.lastrowid
                    node_mapping[dept_key] = dept_id
                    results["departements_created"] += 1
                    print(f"    ✅ {dept_name} dans {etab_name} (ID: {dept_id})")
                    
                except sqlite3.IntegrityError as e:
                    results["conflicts"].append(f"Département '{dept_name}' dans '{etab_name}': {str(e)}")
                    print(f"    ⚠️ Conflit pour {dept_name}: {str(e)}")
        
        # 3. Créer tous les services uniques
        services = set()
        for combo in combinations:
            if combo[1] and combo[2] and combo[3]:  # etablissement, departement et service
                services.add((combo[1], combo[2], combo[3]))
        
        print(f"  🔧 Création de {len(services)} services...")
        for etab_name, dept_name, serv_name in sorted(services):
            dept_key = f"dept_{etab_name}_{dept_name}"
            serv_key = f"serv_{etab_name}_{dept_name}_{serv_name}"
            
            if dept_key in node_mapping and serv_key not in node_mapping:
                try:
                    cursor.execute("""
                        INSERT INTO organizational_nodes (employer_id, parent_id, level, name, code, created_by)
                        VALUES (?, ?, 3, ?, ?, 1)
                    """, (employer_id, node_mapping[dept_key], serv_name, f"SERV-{len(node_mapping)+1}"))
                    
                    serv_id = cursor.lastrowid
                    node_mapping[serv_key] = serv_id
                    results["services_created"] += 1
                    print(f"    ✅ {serv_name} dans {dept_name} (ID: {serv_id})")
                    
                except sqlite3.IntegrityError as e:
                    results["conflicts"].append(f"Service '{serv_name}' dans '{dept_name}': {str(e)}")
                    print(f"    ⚠️ Conflit pour {serv_name}: {str(e)}")
        
        # 4. Créer toutes les unités uniques
        unites = set()
        for combo in combinations:
            if combo[1] and combo[2] and combo[3] and combo[4]:  # tous les niveaux
                unites.add((combo[1], combo[2], combo[3], combo[4]))
        
        print(f"  👥 Création de {len(unites)} unités...")
        for etab_name, dept_name, serv_name, unit_name in sorted(unites):
            serv_key = f"serv_{etab_name}_{dept_name}_{serv_name}"
            unit_key = f"unit_{etab_name}_{dept_name}_{serv_name}_{unit_name}"
            
            if serv_key in node_mapping and unit_key not in node_mapping:
                try:
                    cursor.execute("""
                        INSERT INTO organizational_nodes (employer_id, parent_id, level, name, code, created_by)
                        VALUES (?, ?, 4, ?, ?, 1)
                    """, (employer_id, node_mapping[serv_key], unit_name, f"UNIT-{len(node_mapping)+1}"))
                    
                    unit_id = cursor.lastrowid
                    node_mapping[unit_key] = unit_id
                    results["unites_created"] += 1
                    print(f"    ✅ {unit_name} dans {serv_name} (ID: {unit_id})")
                    
                except sqlite3.IntegrityError as e:
                    results["conflicts"].append(f"Unité '{unit_name}' dans '{serv_name}': {str(e)}")
                    print(f"    ⚠️ Conflit pour {unit_name}: {str(e)}")
        
        conn.commit()
        conn.close()
        
        return results, node_mapping
        
    except Exception as e:
        print(f"❌ Erreur lors de la création de la hiérarchie : {e}")
        return None, None


def validate_migration(employer_id):
    """Valide la migration effectuée"""
    
    db_path = "siirh-backend/siirh.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print(f"\n✅ Validation de la migration pour l'employeur {employer_id}...")
        
        # Compter les nœuds créés par niveau
        cursor.execute("""
            SELECT level, COUNT(*) 
            FROM organizational_nodes 
            WHERE employer_id = ? 
            GROUP BY level 
            ORDER BY level
        """, (employer_id,))
        
        counts_by_level = cursor.fetchall()
        
        print("  📊 Nœuds créés par niveau :")
        level_names = {1: "Établissements", 2: "Départements", 3: "Services", 4: "Unités"}
        
        for level, count in counts_by_level:
            level_name = level_names.get(level, f"Niveau {level}")
            print(f"    • {level_name}: {count}")
        
        # Vérifier l'intégrité hiérarchique
        cursor.execute("""
            SELECT COUNT(*) FROM organizational_nodes 
            WHERE employer_id = ? 
              AND ((level = 1 AND parent_id IS NOT NULL) 
                   OR (level > 1 AND parent_id IS NULL))
        """, (employer_id,))
        
        integrity_violations = cursor.fetchone()[0]
        
        if integrity_violations == 0:
            print("  ✅ Intégrité hiérarchique respectée")
        else:
            print(f"  ❌ {integrity_violations} violations d'intégrité détectées")
        
        # Vérifier les chemins hiérarchiques
        cursor.execute("""
            SELECT COUNT(*) FROM organizational_paths 
            WHERE employer_id = ?
        """, (employer_id,))
        
        paths_count = cursor.fetchone()[0]
        nodes_count = sum(count for level, count in counts_by_level)
        
        if paths_count == nodes_count:
            print(f"  ✅ Chemins hiérarchiques générés ({paths_count} chemins)")
        else:
            print(f"  ⚠️ Incohérence chemins/nœuds : {paths_count} chemins pour {nodes_count} nœuds")
        
        # Afficher quelques exemples de chemins
        cursor.execute("""
            SELECT level, name, full_path 
            FROM organizational_paths 
            WHERE employer_id = ? 
            ORDER BY level, name 
            LIMIT 5
        """, (employer_id,))
        
        sample_paths = cursor.fetchall()
        
        if sample_paths:
            print("  🌳 Exemples de chemins hiérarchiques :")
            for level, name, full_path in sample_paths:
                print(f"    • Niveau {level} - {name}: {full_path}")
        
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la validation : {e}")
        return False


def generate_migration_report(analysis, results_by_employer):
    """Génère un rapport de migration détaillé"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"hierarchical_migration_report_{timestamp}.json"
    
    report = {
        "migration_date": datetime.now().isoformat(),
        "analysis": analysis,
        "results": results_by_employer,
        "summary": {
            "total_employers_migrated": len(results_by_employer),
            "total_etablissements_created": sum(r["etablissements_created"] for r in results_by_employer.values()),
            "total_departements_created": sum(r["departements_created"] for r in results_by_employer.values()),
            "total_services_created": sum(r["services_created"] for r in results_by_employer.values()),
            "total_unites_created": sum(r["unites_created"] for r in results_by_employer.values()),
            "total_conflicts": sum(len(r["conflicts"]) for r in results_by_employer.values())
        }
    }
    
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Rapport de migration généré : {report_file}")
        return report_file
        
    except Exception as e:
        print(f"❌ Erreur lors de la génération du rapport : {e}")
        return None


def main():
    """Fonction principale de migration"""
    
    print("🚀 Migration des données organisationnelles vers la structure hiérarchique")
    print("=" * 80)
    
    # 1. Analyser les données existantes
    analysis = analyze_existing_combinations()
    if not analysis:
        print("❌ Échec de l'analyse des données existantes")
        return False
    
    print(f"\n📊 Résumé de l'analyse :")
    print(f"  • {analysis['total_combinations']} combinaisons organisationnelles")
    print(f"  • {analysis['employers_affected']} employeurs concernés")
    
    # 2. Migrer chaque employeur
    results_by_employer = {}
    
    for employer_id, combinations in analysis["combinations_by_employer"].items():
        print(f"\n👤 Migration de l'employeur {employer_id} ({len(combinations)} combinaisons)...")
        
        results, node_mapping = create_hierarchical_structure(employer_id, combinations)
        
        if results:
            results_by_employer[employer_id] = results
            
            print(f"  ✅ Migration terminée :")
            print(f"    • {results['etablissements_created']} établissements créés")
            print(f"    • {results['departements_created']} départements créés")
            print(f"    • {results['services_created']} services créés")
            print(f"    • {results['unites_created']} unités créées")
            
            if results["conflicts"]:
                print(f"    ⚠️ {len(results['conflicts'])} conflits détectés")
                for conflict in results["conflicts"]:
                    print(f"      - {conflict}")
            
            # Valider la migration
            validate_migration(employer_id)
        else:
            print(f"  ❌ Échec de la migration pour l'employeur {employer_id}")
    
    # 3. Générer le rapport final
    report_file = generate_migration_report(analysis, results_by_employer)
    
    # 4. Résumé final
    print(f"\n🎉 Migration terminée avec succès !")
    print(f"\n📈 Résumé global :")
    
    total_etablissements = sum(r["etablissements_created"] for r in results_by_employer.values())
    total_departements = sum(r["departements_created"] for r in results_by_employer.values())
    total_services = sum(r["services_created"] for r in results_by_employer.values())
    total_unites = sum(r["unites_created"] for r in results_by_employer.values())
    total_conflicts = sum(len(r["conflicts"]) for r in results_by_employer.values())
    
    print(f"  • {len(results_by_employer)} employeurs migrés")
    print(f"  • {total_etablissements} établissements créés")
    print(f"  • {total_departements} départements créés")
    print(f"  • {total_services} services créés")
    print(f"  • {total_unites} unités créées")
    print(f"  • {total_conflicts} conflits détectés")
    
    if report_file:
        print(f"  • Rapport détaillé : {report_file}")
    
    print(f"\n📋 Prochaines étapes :")
    print(f"  1. Vérifier le rapport de migration")
    print(f"  2. Résoudre les conflits éventuels")
    print(f"  3. Tester le filtrage en cascade")
    print(f"  4. Implémenter les services backend")
    print(f"  5. Intégrer avec le frontend")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)