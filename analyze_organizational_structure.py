#!/usr/bin/env python3
"""
Analyze current organizational structure and name-based references
"""

import sqlite3
import json
from datetime import datetime
from collections import defaultdict

def analyze_organizational_structure():
    """Analyze how organizational structure currently uses names vs matricules"""
    
    print("🏢 Analyse de la structure organisationnelle...")
    
    try:
        conn = sqlite3.connect("siirh-backend/siirh.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        print("✅ Connexion établie")
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return
    
    analysis = {
        "timestamp": datetime.now().isoformat(),
        "organizational_usage": {},
        "name_based_references": [],
        "matricule_based_references": [],
        "migration_impact": {}
    }
    
    try:
        # 1. Analyze current organizational assignments
        print("\n📋 Analyse des affectations organisationnelles...")
        cursor.execute("""
            SELECT 
                id, matricule, nom, prenom,
                etablissement, departement, service, unite,
                organizational_unit_id
            FROM workers
        """)
        
        workers = cursor.fetchall()
        
        # Count usage patterns
        org_patterns = {
            "using_old_fields": 0,
            "using_new_structure": 0,
            "using_both": 0,
            "no_organization": 0
        }
        
        name_based_refs = []
        matricule_based_refs = []
        
        for worker in workers:
            has_old_fields = any([
                worker['etablissement'],
                worker['departement'], 
                worker['service'],
                worker['unite']
            ])
            
            has_new_structure = worker['organizational_unit_id'] is not None
            
            if has_old_fields and has_new_structure:
                org_patterns["using_both"] += 1
            elif has_old_fields:
                org_patterns["using_old_fields"] += 1
                # This is a name-based reference
                name_based_refs.append({
                    "worker_id": worker['id'],
                    "worker_name": f"{worker['nom']} {worker['prenom']}",
                    "matricule": worker['matricule'],
                    "etablissement": worker['etablissement'],
                    "departement": worker['departement'],
                    "service": worker['service'],
                    "unite": worker['unite']
                })
            elif has_new_structure:
                org_patterns["using_new_structure"] += 1
                # This is potentially matricule-based
                matricule_based_refs.append({
                    "worker_id": worker['id'],
                    "worker_name": f"{worker['nom']} {worker['prenom']}",
                    "matricule": worker['matricule'],
                    "organizational_unit_id": worker['organizational_unit_id']
                })
            else:
                org_patterns["no_organization"] += 1
        
        analysis["organizational_usage"] = org_patterns
        analysis["name_based_references"] = name_based_refs
        analysis["matricule_based_references"] = matricule_based_refs
        
        print(f"   Utilisant anciens champs: {org_patterns['using_old_fields']}")
        print(f"   Utilisant nouvelle structure: {org_patterns['using_new_structure']}")
        print(f"   Utilisant les deux: {org_patterns['using_both']}")
        print(f"   Sans organisation: {org_patterns['no_organization']}")
        
        # 2. Analyze organizational units structure
        print("\n🏗️  Analyse de la structure organisationnelle...")
        cursor.execute("""
            SELECT id, employer_id, parent_id, level, code, name
            FROM organizational_units
            ORDER BY level_order, name
        """)
        
        org_units = cursor.fetchall()
        print(f"   Unités organisationnelles définies: {len(org_units)}")
        
        # Group by level
        units_by_level = defaultdict(list)
        for unit in org_units:
            units_by_level[unit['level']].append(dict(unit))
        
        for level, units in units_by_level.items():
            print(f"     {level}: {len(units)} unités")
        
        # 3. Determine migration impact
        print("\n🎯 Évaluation de l'impact de migration...")
        
        migration_impact = {
            "workers_to_migrate": org_patterns["using_old_fields"],
            "workers_already_migrated": org_patterns["using_new_structure"],
            "workers_with_conflicts": org_patterns["using_both"],
            "migration_priority": "HIGH" if org_patterns["using_old_fields"] > 0 else "LOW"
        }
        
        analysis["migration_impact"] = migration_impact
        
        print(f"   Salariés à migrer: {migration_impact['workers_to_migrate']}")
        print(f"   Salariés déjà migrés: {migration_impact['workers_already_migrated']}")
        print(f"   Conflits à résoudre: {migration_impact['workers_with_conflicts']}")
        print(f"   Priorité migration: {migration_impact['migration_priority']}")
        
        # 4. Show examples of name-based references
        if name_based_refs:
            print(f"\n📝 Exemples de références basées sur les noms:")
            for ref in name_based_refs[:3]:  # Show first 3
                org_path = " → ".join(filter(None, [
                    ref['etablissement'],
                    ref['departement'],
                    ref['service'],
                    ref['unite']
                ]))
                print(f"   - {ref['worker_name']} (ID: {ref['worker_id']}, Matricule: {ref['matricule']})")
                print(f"     Organisation: {org_path}")
        
        # 5. Save report
        report_filename = f"organizational_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Rapport sauvegardé: {report_filename}")
        
        # 6. Recommendations
        print(f"\n📋 RECOMMANDATIONS:")
        if migration_impact["workers_to_migrate"] > 0:
            print(f"   1. Migrer {migration_impact['workers_to_migrate']} salariés vers la structure par matricule")
            print(f"   2. Créer des unités organisationnelles pour remplacer les champs texte")
            print(f"   3. Établir des correspondances matricule → unité organisationnelle")
        
        if migration_impact["workers_with_conflicts"] > 0:
            print(f"   4. Résoudre {migration_impact['workers_with_conflicts']} conflits entre ancienne et nouvelle structure")
        
        if len(org_units) == 0:
            print(f"   5. Créer la structure organisationnelle hiérarchique de base")
        
        return analysis
        
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    finally:
        conn.close()
        print("🔒 Connexion fermée")

if __name__ == "__main__":
    analyze_organizational_structure()