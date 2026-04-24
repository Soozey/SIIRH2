#!/usr/bin/env python3
"""
Script d'analyse de la structure organisationnelle actuelle
Tâche 1.1 : Analyser la structure de données actuelle
"""

import os
import sys
import json
from datetime import datetime
from collections import defaultdict, Counter

# Changer vers le répertoire backend
backend_path = os.path.join(os.path.dirname(__file__), 'siirh-backend')
os.chdir(backend_path)
sys.path.insert(0, backend_path)

def analyze_organizational_structure():
    """Analyse complète de la structure organisationnelle actuelle"""
    
    print("=" * 80)
    print("ANALYSE DE LA STRUCTURE ORGANISATIONNELLE ACTUELLE")
    print("=" * 80)
    print(f"Date d'analyse : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Import des modules backend
        from app.config.config import SessionLocal
        from app.models import Employer, Worker
        
        # Connexion à la base de données
        session = SessionLocal()
        
        # 1. Analyse des employeurs
        print("1. ANALYSE DES EMPLOYEURS")
        print("-" * 40)
        
        employers = session.query(Employer).all()
        print(f"Nombre total d'employeurs : {len(employers)}")
        
        # Analyse des listes organisationnelles JSON
        org_stats = {
            'etablissements': defaultdict(list),
            'departements': defaultdict(list), 
            'services': defaultdict(list),
            'unites': defaultdict(list)
        }
        
        for employer in employers:
            print(f"\nEmployeur : {employer.nom} (ID: {employer.id})")
            
            # Analyser chaque liste organisationnelle
            for field_name in ['etablissements', 'departements', 'services', 'unites']:
                field_value = getattr(employer, field_name, "[]")
                try:
                    items = json.loads(field_value) if field_value else []
                    print(f"  {field_name.capitalize()} : {len(items)} éléments")
                    if items:
                        print(f"    -> {items}")
                    org_stats[field_name][employer.id] = items
                except json.JSONDecodeError:
                    print(f"  {field_name.capitalize()} : ERREUR JSON - {field_value}")
                    org_stats[field_name][employer.id] = []
        
        # 2. Analyse des salariés
        print("\n\n2. ANALYSE DES SALARIÉS")
        print("-" * 40)
        
        workers = session.query(Worker).all()
        print(f"Nombre total de salariés : {len(workers)}")
        
        # Statistiques par employeur
        workers_by_employer = defaultdict(list)
        for worker in workers:
            workers_by_employer[worker.employer_id].append(worker)
        
        # Analyse des colonnes organisationnelles individuelles
        org_usage = {
            'etablissement': Counter(),
            'departement': Counter(),
            'service': Counter(),
            'unite': Counter()
        }
        
        combinations_used = defaultdict(set)
        
        for employer_id, employer_workers in workers_by_employer.items():
            print(f"\nEmployeur ID {employer_id} : {len(employer_workers)} salariés")
            
            employer_combinations = set()
            
            for worker in employer_workers:
                # Compter l'utilisation de chaque niveau
                etab = getattr(worker, 'etablissement', None) or ''
                dept = getattr(worker, 'departement', None) or ''
                serv = getattr(worker, 'service', None) or ''
                unit = getattr(worker, 'unite', None) or ''
                
                if etab: org_usage['etablissement'][etab] += 1
                if dept: org_usage['departement'][dept] += 1
                if serv: org_usage['service'][serv] += 1
                if unit: org_usage['unite'][unit] += 1
                
                # Enregistrer la combinaison complète
                combination = (etab, dept, serv, unit)
                employer_combinations.add(combination)
                combinations_used[employer_id].add(combination)
            
            print(f"  Combinaisons uniques utilisées : {len(employer_combinations)}")
            
            # Afficher les combinaisons les plus fréquentes
            combination_counts = Counter(employer_combinations)
            for combo, count in combination_counts.most_common(5):
                etab, dept, serv, unit = combo
                combo_str = " > ".join(filter(None, [etab, dept, serv, unit])) or "(vide)"
                print(f"    {combo_str} : {count} salariés")
        
        # 3. Analyse des patterns hiérarchiques
        print("\n\n3. ANALYSE DES PATTERNS HIÉRARCHIQUES")
        print("-" * 40)
        
        # Détecter les incohérences potentielles
        inconsistencies = []
        
        for employer_id, combinations in combinations_used.items():
            employer = next((e for e in employers if e.id == employer_id), None)
            if not employer:
                continue
                
            print(f"\nEmployeur : {employer.nom}")
            
            # Vérifier la cohérence avec les listes JSON
            employer_lists = {}
            for field_name in ['etablissements', 'departements', 'services', 'unites']:
                field_value = getattr(employer, field_name, "[]")
                try:
                    employer_lists[field_name] = set(json.loads(field_value) if field_value else [])
                except json.JSONDecodeError:
                    employer_lists[field_name] = set()
            
            # Extraire les valeurs utilisées par les salariés
            used_values = {
                'etablissements': set(),
                'departements': set(),
                'services': set(),
                'unites': set()
            }
            
            for etab, dept, serv, unit in combinations:
                if etab: used_values['etablissements'].add(etab)
                if dept: used_values['departements'].add(dept)
                if serv: used_values['services'].add(serv)
                if unit: used_values['unites'].add(unit)
            
            # Détecter les incohérences
            for field_name, used_set in used_values.items():
                defined_set = employer_lists[field_name]
                
                # Valeurs utilisées mais non définies
                undefined_used = used_set - defined_set
                if undefined_used:
                    inconsistency = {
                        'employer_id': employer_id,
                        'employer_name': employer.nom,
                        'field': field_name,
                        'type': 'undefined_used',
                        'values': list(undefined_used)
                    }
                    inconsistencies.append(inconsistency)
                    print(f"  ⚠️  {field_name} utilisés mais non définis : {undefined_used}")
                
                # Valeurs définies mais non utilisées
                unused_defined = defined_set - used_set
                if unused_defined:
                    print(f"  ℹ️  {field_name} définis mais non utilisés : {unused_defined}")
        
        # 4. Génération du rapport de synthèse
        print("\n\n4. RAPPORT DE SYNTHÈSE")
        print("-" * 40)
        
        total_combinations = sum(len(combos) for combos in combinations_used.values())
        print(f"Total des combinaisons organisationnelles uniques : {total_combinations}")
        print(f"Incohérences détectées : {len(inconsistencies)}")
        
        # Statistiques globales d'utilisation
        print("\nUtilisation globale par niveau :")
        for level, counter in org_usage.items():
            print(f"  {level.capitalize()} : {len(counter)} valeurs uniques, {sum(counter.values())} utilisations")
            if counter:
                most_common = counter.most_common(3)
                print(f"    Plus fréquents : {', '.join(f'{val}({count})' for val, count in most_common)}")
        
        # 5. Sauvegarde du rapport détaillé
        report_data = {
            'analysis_date': datetime.now().isoformat(),
            'summary': {
                'total_employers': len(employers),
                'total_workers': len(workers),
                'total_combinations': total_combinations,
                'inconsistencies_count': len(inconsistencies)
            },
            'employers': [
                {
                    'id': emp.id,
                    'name': emp.nom,
                    'workers_count': len(workers_by_employer.get(emp.id, [])),
                    'organizational_lists': {
                        field: json.loads(getattr(emp, field, "[]") or "[]")
                        for field in ['etablissements', 'departements', 'services', 'unites']
                    }
                }
                for emp in employers
            ],
            'usage_statistics': {
                level: dict(counter.most_common())
                for level, counter in org_usage.items()
            },
            'inconsistencies': inconsistencies,
            'combinations_by_employer': {
                str(emp_id): [list(combo) for combo in combos]
                for emp_id, combos in combinations_used.items()
            }
        }
        
        # Retourner au répertoire racine pour sauvegarder
        os.chdir('..')
        report_filename = f"organizational_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Rapport détaillé sauvegardé : {report_filename}")
        
        # 6. Recommandations pour la migration
        print("\n\n5. RECOMMANDATIONS POUR LA MIGRATION")
        print("-" * 40)
        
        if inconsistencies:
            print("⚠️  ACTIONS REQUISES AVANT MIGRATION :")
            for inc in inconsistencies:
                print(f"   - Employeur '{inc['employer_name']}' : ajouter {inc['values']} à {inc['field']}")
        else:
            print("✅ Aucune incohérence détectée - prêt pour la migration")
        
        print("\n📋 ÉTAPES RECOMMANDÉES :")
        print("   1. Corriger les incohérences détectées")
        print("   2. Créer la structure hiérarchique basée sur les patterns d'utilisation")
        print("   3. Migrer les données vers le nouveau modèle")
        print("   4. Valider l'intégrité après migration")
        
        return report_data
        
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse : {e}")
        import traceback
        traceback.print_exc()
        return None
        
    finally:
        if 'session' in locals():
            session.close()

if __name__ == "__main__":
    analyze_organizational_structure()