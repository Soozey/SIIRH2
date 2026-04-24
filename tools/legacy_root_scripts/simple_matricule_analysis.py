#!/usr/bin/env python3
"""
Simple matricule analysis for migration planning
"""

import sqlite3
import json
from datetime import datetime
from collections import defaultdict, Counter

def analyze_matricule_system():
    """Analyze the current matricule system"""
    
    print("🚀 Analyse du système de matricules...")
    
    # Connect to database
    try:
        conn = sqlite3.connect("siirh-backend/siirh.db")
        conn.row_factory = sqlite3.Row  # Enable column access by name
        cursor = conn.cursor()
        print("✅ Connexion à la base établie")
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return
    
    analysis = {
        "timestamp": datetime.now().isoformat(),
        "total_workers": 0,
        "workers_with_matricule": 0,
        "workers_without_matricule": 0,
        "duplicate_names": [],
        "matricule_issues": [],
        "migration_complexity": "LOW",
        "recommendations": []
    }
    
    try:
        # 1. Count total workers
        print("\n📊 Analyse des salariés...")
        cursor.execute("SELECT COUNT(*) FROM workers")
        analysis["total_workers"] = cursor.fetchone()[0]
        print(f"   Total salariés: {analysis['total_workers']}")
        
        # 2. Analyze matricules
        print("\n🔢 Analyse des matricules...")
        cursor.execute("""
            SELECT id, matricule, nom, prenom, employer_id,
                   etablissement, departement, service, unite
            FROM workers
        """)
        
        workers = cursor.fetchall()
        workers_with_matricule = []
        workers_without_matricule = []
        name_groups = defaultdict(list)
        matricule_counts = Counter()
        
        for worker in workers:
            worker_dict = dict(worker)
            
            # Check matricule
            if worker['matricule'] and worker['matricule'].strip():
                workers_with_matricule.append(worker_dict)
                matricule_counts[worker['matricule']] += 1
            else:
                workers_without_matricule.append(worker_dict)
            
            # Group by name for homonym detection
            full_name = f"{worker['nom'] or ''} {worker['prenom'] or ''}".strip()
            if full_name:
                name_groups[full_name].append(worker_dict)
        
        analysis["workers_with_matricule"] = len(workers_with_matricule)
        analysis["workers_without_matricule"] = len(workers_without_matricule)
        
        print(f"   Avec matricule: {len(workers_with_matricule)}")
        print(f"   Sans matricule: {len(workers_without_matricule)}")
        
        # 3. Detect homonyms
        print("\n👥 Détection des homonymes...")
        duplicate_names = []
        for name, workers_list in name_groups.items():
            if len(workers_list) > 1:
                duplicate_names.append({
                    "name": name,
                    "count": len(workers_list),
                    "workers": [{"id": w["id"], "matricule": w["matricule"]} for w in workers_list]
                })
        
        analysis["duplicate_names"] = duplicate_names
        print(f"   Groupes d'homonymes: {len(duplicate_names)}")
        
        for dup in duplicate_names[:3]:  # Show first 3
            print(f"     - {dup['name']}: {dup['count']} salariés")
        
        # 4. Check matricule issues
        print("\n🔍 Vérification des matricules...")
        matricule_issues = []
        
        # Check for duplicate matricules
        for matricule, count in matricule_counts.items():
            if count > 1:
                matricule_issues.append({
                    "issue": "duplicate_matricule",
                    "matricule": matricule,
                    "count": count
                })
        
        # Check for short matricules
        for worker in workers_with_matricule:
            matricule = worker["matricule"]
            if len(matricule) < 3:
                matricule_issues.append({
                    "worker_id": worker["id"],
                    "issue": "too_short",
                    "matricule": matricule
                })
        
        analysis["matricule_issues"] = matricule_issues
        print(f"   Problèmes détectés: {len(matricule_issues)}")
        
        # 5. Determine migration complexity
        complexity_score = 0
        recommendations = []
        
        if len(workers_without_matricule) > 0:
            complexity_score += 2
            recommendations.append(f"Générer des matricules pour {len(workers_without_matricule)} salariés")
        
        if len(duplicate_names) > 5:
            complexity_score += 3
            recommendations.append(f"Gérer {len(duplicate_names)} groupes d'homonymes")
        elif len(duplicate_names) > 0:
            complexity_score += 1
            recommendations.append(f"Attention aux {len(duplicate_names)} groupes d'homonymes")
        
        if len(matricule_issues) > 3:
            complexity_score += 2
            recommendations.append(f"Corriger {len(matricule_issues)} problèmes de matricules")
        
        # Set complexity level
        if complexity_score >= 6:
            analysis["migration_complexity"] = "HIGH"
        elif complexity_score >= 3:
            analysis["migration_complexity"] = "MEDIUM"
        else:
            analysis["migration_complexity"] = "LOW"
        
        analysis["recommendations"] = recommendations
        
        # 6. Display summary
        print(f"\n📊 RÉSUMÉ DE L'ANALYSE")
        print(f"=" * 50)
        print(f"Total salariés: {analysis['total_workers']}")
        print(f"Avec matricule: {analysis['workers_with_matricule']}")
        print(f"Sans matricule: {analysis['workers_without_matricule']}")
        print(f"Groupes d'homonymes: {len(duplicate_names)}")
        print(f"Problèmes matricules: {len(matricule_issues)}")
        print(f"Complexité migration: {analysis['migration_complexity']}")
        
        if recommendations:
            print(f"\n📝 RECOMMANDATIONS:")
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec}")
        
        # 7. Save report
        report_filename = f"matricule_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Rapport sauvegardé: {report_filename}")
        
        # Show next steps
        print(f"\n🎯 PROCHAINES ÉTAPES:")
        if analysis["migration_complexity"] == "HIGH":
            print(f"   ⚠️  Migration complexe - Planifier une migration par étapes")
        elif analysis["migration_complexity"] == "MEDIUM":
            print(f"   ⚡ Migration moyenne - Prévoir des vérifications manuelles")
        else:
            print(f"   ✅ Migration simple - Procéder avec la migration automatique")
        
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
    analyze_matricule_system()