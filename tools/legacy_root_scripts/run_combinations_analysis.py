#!/usr/bin/env python3
"""
Exécution de l'analyse des combinaisons organisationnelles
Tâche 1.2 : Créer un script d'analyse des combinaisons organisationnelles
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import defaultdict, Counter
import os

def analyze_organizational_combinations():
    """Analyse complète des combinaisons organisationnelles"""
    
    print("🚀 ANALYSE DES COMBINAISONS ORGANISATIONNELLES")
    print("Tâche 1.2 : Créer un script d'analyse des combinaisons organisationnelles")
    print("Requirements: 4.1, 4.3")
    print("=" * 80)
    
    db_path = "siirh-backend/siirh.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Base de données non trouvée : {db_path}")
        return False
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            print("🔍 Extraction des combinaisons organisationnelles...")
            
            # Récupérer toutes les combinaisons avec les IDs des salariés
            cursor.execute("""
                SELECT 
                    employer_id,
                    etablissement, 
                    departement, 
                    service, 
                    unite,
                    GROUP_CONCAT(id) as worker_ids,
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
            print(f"   ✅ {len(combinations)} combinaisons uniques extraites")
            
            if not combinations:
                print("⚠️  Aucune combinaison organisationnelle trouvée")
                return True
            
            # Analyser la cohérence hiérarchique
            print("\n🔍 Analyse de la cohérence hiérarchique...")
            
            complete_paths = 0
            incomplete_paths = 0
            inconsistencies = []
            hierarchy_violations = []
            orphaned_elements = []
            
            # Construire les relations hiérarchiques
            etablissement_to_dept = defaultdict(set)
            dept_to_service = defaultdict(set)
            service_to_unite = defaultdict(set)
            
            # Statistiques par niveau
            level_stats = {
                "level_1_only": 0,
                "level_2_max": 0,
                "level_3_max": 0,
                "level_4_complete": 0
            }
            
            for combo in combinations:
                employer_id, etab, dept, serv, unite, worker_ids_str, worker_count = combo
                
                # Déterminer le niveau hiérarchique
                if unite:
                    level = 4
                    level_stats["level_4_complete"] += 1
                elif serv:
                    level = 3
                    level_stats["level_3_max"] += 1
                elif dept:
                    level = 2
                    level_stats["level_2_max"] += 1
                elif etab:
                    level = 1
                    level_stats["level_1_only"] += 1
                else:
                    level = 0
                
                # Vérifier la complétude du chemin
                is_complete = False
                missing_levels = []
                
                if level == 1 and etab:
                    is_complete = True
                elif level == 2 and etab and dept:
                    is_complete = True
                elif level == 3 and etab and dept and serv:
                    is_complete = True
                elif level == 4 and etab and dept and serv and unite:
                    is_complete = True
                else:
                    if level >= 2 and not etab:
                        missing_levels.append("etablissement")
                    if level >= 3 and not dept:
                        missing_levels.append("departement")
                    if level >= 4 and not serv:
                        missing_levels.append("service")
                
                if is_complete:
                    complete_paths += 1
                else:
                    incomplete_paths += 1
                    if missing_levels:
                        inconsistencies.append({
                            "type": "incomplete_path",
                            "employer_id": employer_id,
                            "etablissement": etab,
                            "departement": dept,
                            "service": serv,
                            "unite": unite,
                            "missing_levels": missing_levels,
                            "worker_count": worker_count,
                            "description": f"Chemin incomplet - niveaux manquants: {', '.join(missing_levels)}"
                        })
                
                # Construire les relations
                if etab and dept:
                    etablissement_to_dept[etab].add(dept)
                if dept and serv:
                    dept_to_service[dept].add(serv)
                if serv and unite:
                    service_to_unite[serv].add(unite)
            
            # Détecter les violations hiérarchiques
            print("   🔍 Détection des violations hiérarchiques...")
            
            # Départements rattachés à plusieurs établissements
            dept_to_etablissements = defaultdict(set)
            for etab, depts in etablissement_to_dept.items():
                for dept in depts:
                    dept_to_etablissements[dept].add(etab)
            
            for dept, etablissements in dept_to_etablissements.items():
                if len(etablissements) > 1:
                    hierarchy_violations.append({
                        "type": "department_multiple_establishments",
                        "department": dept,
                        "establishments": list(etablissements),
                        "description": f"Département '{dept}' rattaché à plusieurs établissements: {', '.join(etablissements)}"
                    })
            
            # Services rattachés à plusieurs départements
            service_to_depts = defaultdict(set)
            for dept, services in dept_to_service.items():
                for service in services:
                    service_to_depts[service].add(dept)
            
            for service, depts in service_to_depts.items():
                if len(depts) > 1:
                    hierarchy_violations.append({
                        "type": "service_multiple_departments",
                        "service": service,
                        "departments": list(depts),
                        "description": f"Service '{service}' rattaché à plusieurs départements: {', '.join(depts)}"
                    })
            
            # Unités rattachées à plusieurs services
            unite_to_services = defaultdict(set)
            for service, unites in service_to_unite.items():
                for unite in unites:
                    unite_to_services[unite].add(service)
            
            for unite, services in unite_to_services.items():
                if len(services) > 1:
                    hierarchy_violations.append({
                        "type": "unit_multiple_services",
                        "unit": unite,
                        "services": list(services),
                        "description": f"Unité '{unite}' rattachée à plusieurs services: {', '.join(services)}"
                    })
            
            # Générer les statistiques d'utilisation
            print("   📊 Génération des statistiques d'utilisation...")
            
            total_workers_affected = sum(combo[6] for combo in combinations)
            
            element_frequency = {
                "etablissements": Counter(),
                "departements": Counter(),
                "services": Counter(),
                "unites": Counter()
            }
            
            for combo in combinations:
                employer_id, etab, dept, serv, unite, worker_ids_str, worker_count = combo
                
                if etab:
                    element_frequency["etablissements"][etab] += worker_count
                if dept:
                    element_frequency["departements"][dept] += worker_count
                if serv:
                    element_frequency["services"][serv] += worker_count
                if unite:
                    element_frequency["unites"][unite] += worker_count
            
            # Calculer le score de complexité pour la migration
            complexity_score = (
                len(inconsistencies) * 2 +
                len(hierarchy_violations) * 3 +
                len(orphaned_elements) * 1 +
                incomplete_paths * 1 +
                len(combinations) * 0.1
            )
            
            # Déterminer l'approche recommandée
            if complexity_score <= 5:
                recommended_approach = "auto"
                estimated_duration = "low"
                risk_level = "low"
            elif complexity_score <= 15:
                recommended_approach = "semi_auto"
                estimated_duration = "medium"
                risk_level = "medium"
            else:
                recommended_approach = "manual"
                estimated_duration = "high"
                risk_level = "high"
            
            # Calculer le score de cohérence
            total_issues = len(inconsistencies) + len(hierarchy_violations) + len(orphaned_elements) + incomplete_paths
            consistency_score = max(0, 100 - (total_issues / len(combinations) * 100)) if combinations else 100
            
            # Afficher le résumé
            print("\n" + "=" * 80)
            print("📋 RÉSUMÉ DE L'ANALYSE DES COMBINAISONS ORGANISATIONNELLES")
            print("=" * 80)
            
            print(f"\n📊 STATISTIQUES GÉNÉRALES:")
            print(f"   • Combinaisons organisationnelles : {len(combinations)}")
            print(f"   • Salariés concernés : {total_workers_affected}")
            print(f"   • Score de cohérence : {consistency_score:.1f}/100")
            
            print(f"\n🔍 ANALYSE DE COHÉRENCE:")
            print(f"   • Chemins complets : {complete_paths}")
            print(f"   • Chemins incomplets : {incomplete_paths}")
            print(f"   • Incohérences détectées : {len(inconsistencies)}")
            print(f"   • Violations hiérarchiques : {len(hierarchy_violations)}")
            print(f"   • Éléments orphelins : {len(orphaned_elements)}")
            
            print(f"\n📈 DISTRIBUTION PAR NIVEAU:")
            print(f"   • Niveau 1 (Établissement) : {level_stats['level_1_only']}")
            print(f"   • Niveau 2 (Département) : {level_stats['level_2_max']}")
            print(f"   • Niveau 3 (Service) : {level_stats['level_3_max']}")
            print(f"   • Niveau 4 (Unité) : {level_stats['level_4_complete']}")
            
            print(f"\n🎯 STRATÉGIE DE MIGRATION:")
            print(f"   • Approche recommandée : {recommended_approach.upper()}")
            print(f"   • Score de complexité : {complexity_score:.1f}")
            print(f"   • Durée estimée : {estimated_duration.upper()}")
            print(f"   • Niveau de risque : {risk_level.upper()}")
            
            if hierarchy_violations:
                print(f"\n⚠️  VIOLATIONS HIÉRARCHIQUES:")
                for violation in hierarchy_violations[:3]:
                    print(f"   • {violation['description']}")
                if len(hierarchy_violations) > 3:
                    print(f"   • ... et {len(hierarchy_violations) - 3} autres")
            
            if inconsistencies:
                print(f"\n🔧 INCOHÉRENCES À RÉSOUDRE:")
                for inc in inconsistencies[:3]:
                    print(f"   • {inc['description']}")
                if len(inconsistencies) > 3:
                    print(f"   • ... et {len(inconsistencies) - 3} autres")
            
            # Sauvegarder les résultats
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"organizational_combinations_analysis_{timestamp}.json"
            
            results = {
                "analysis_date": datetime.now().isoformat(),
                "database_path": db_path,
                "summary": {
                    "total_combinations": len(combinations),
                    "total_workers_affected": total_workers_affected,
                    "consistency_score": round(consistency_score, 2),
                    "complexity_score": round(complexity_score, 2),
                    "recommended_approach": recommended_approach,
                    "estimated_duration": estimated_duration,
                    "risk_level": risk_level
                },
                "consistency_analysis": {
                    "complete_paths": complete_paths,
                    "incomplete_paths": incomplete_paths,
                    "inconsistencies": inconsistencies,
                    "hierarchy_violations": hierarchy_violations,
                    "orphaned_elements": orphaned_elements,
                    "level_statistics": level_stats
                },
                "combinations": [
                    {
                        "employer_id": combo[0],
                        "etablissement": combo[1],
                        "departement": combo[2],
                        "service": combo[3],
                        "unite": combo[4],
                        "worker_ids": combo[5].split(',') if combo[5] else [],
                        "worker_count": combo[6]
                    }
                    for combo in combinations
                ],
                "element_frequency": {
                    "etablissements": dict(element_frequency["etablissements"]),
                    "departements": dict(element_frequency["departements"]),
                    "services": dict(element_frequency["services"]),
                    "unites": dict(element_frequency["unites"])
                }
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False, default=str)
            
            print(f"\n💾 Résultats sauvegardés dans : {filename}")
            
            print("\n" + "=" * 80)
            print("✅ Analyse des combinaisons terminée avec succès !")
            print("=" * 80)
            
            print(f"\n🎯 PROCHAINES ÉTAPES:")
            print(f"   1. Examiner le fichier détaillé : {filename}")
            print(f"   2. Résoudre les incohérences identifiées si nécessaire")
            print(f"   3. Passer à la Tâche 2.1 : Créer la table organizational_nodes")
            
            return True
            
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse : {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = analyze_organizational_combinations()
    exit(0 if success else 1)