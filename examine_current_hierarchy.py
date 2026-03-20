#!/usr/bin/env python3
"""
Script pour examiner la hiérarchie organisationnelle existante
"""

import psycopg2
import psycopg2.extras
from collections import defaultdict

def examine_hierarchy():
    """Examine la hiérarchie organisationnelle existante"""
    
    db_config = {
        'host': '127.0.0.1',
        'port': 5432,
        'database': 'db_siirh_app',
        'user': 'postgres',
        'password': 'tantely123'
    }
    
    try:
        with psycopg2.connect(**db_config) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                
                # Récupérer toutes les unités organisationnelles
                print("🌳 Hiérarchie organisationnelle existante:")
                cursor.execute("""
                    SELECT id, employer_id, parent_id, level, level_order, code, name, description, is_active
                    FROM organizational_units
                    ORDER BY employer_id, level_order, name
                """)
                units = cursor.fetchall()
                
                # Grouper par employeur
                by_employer = defaultdict(list)
                for unit in units:
                    by_employer[unit['employer_id']].append(unit)
                
                # Récupérer les noms des employeurs
                cursor.execute("SELECT id, raison_sociale FROM employers")
                employers = {emp['id']: emp['raison_sociale'] for emp in cursor.fetchall()}
                
                for employer_id, employer_units in by_employer.items():
                    employer_name = employers.get(employer_id, f"Employeur {employer_id}")
                    print(f"\n📊 {employer_name} (ID: {employer_id})")
                    print(f"   Unités organisationnelles: {len(employer_units)}")
                    
                    # Construire l'arbre hiérarchique
                    units_by_id = {unit['id']: unit for unit in employer_units}
                    roots = [unit for unit in employer_units if unit['parent_id'] is None]
                    
                    def print_tree(unit, indent=0):
                        prefix = "  " * indent + ("├─ " if indent > 0 else "")
                        status = "✅" if unit['is_active'] else "❌"
                        print(f"   {prefix}{status} {unit['level']} '{unit['name']}' (ID:{unit['id']}, Code:{unit['code']})")
                        
                        # Trouver les enfants
                        children = [u for u in employer_units if u['parent_id'] == unit['id']]
                        for child in sorted(children, key=lambda x: (x['level_order'], x['name'])):
                            print_tree(child, indent + 1)
                    
                    for root in sorted(roots, key=lambda x: (x['level_order'], x['name'])):
                        print_tree(root)
                
                # Vérifier l'utilisation par les workers
                print(f"\n👥 Utilisation par les travailleurs:")
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_workers,
                        COUNT(organizational_unit_id) as workers_with_org_unit,
                        COUNT(etablissement) as workers_with_etablissement,
                        COUNT(departement) as workers_with_departement,
                        COUNT(service) as workers_with_service,
                        COUNT(unite) as workers_with_unite
                    FROM workers
                """)
                worker_stats = cursor.fetchone()
                
                print(f"   Total travailleurs: {worker_stats['total_workers']}")
                print(f"   Avec organizational_unit_id: {worker_stats['workers_with_org_unit']}")
                print(f"   Avec etablissement (texte): {worker_stats['workers_with_etablissement']}")
                print(f"   Avec departement (texte): {worker_stats['workers_with_departement']}")
                print(f"   Avec service (texte): {worker_stats['workers_with_service']}")
                print(f"   Avec unite (texte): {worker_stats['workers_with_unite']}")
                
                # Vérifier les assignations spécifiques
                cursor.execute("""
                    SELECT w.id, w.matricule, w.nom, w.prenom, w.employer_id,
                           w.organizational_unit_id, ou.name as org_unit_name, ou.level as org_unit_level,
                           w.etablissement, w.departement, w.service, w.unite
                    FROM workers w
                    LEFT JOIN organizational_units ou ON w.organizational_unit_id = ou.id
                    ORDER BY w.employer_id, w.matricule
                """)
                workers = cursor.fetchall()
                
                print(f"\n📋 Détail des assignations:")
                for worker in workers:
                    employer_name = employers.get(worker['employer_id'], f"Employeur {worker['employer_id']}")
                    print(f"   👤 {worker['matricule']} - {worker['nom']} {worker['prenom']} ({employer_name})")
                    
                    if worker['organizational_unit_id']:
                        print(f"      🏢 Unité org: {worker['org_unit_name']} ({worker['org_unit_level']}) [ID:{worker['organizational_unit_id']}]")
                    else:
                        print(f"      🏢 Unité org: Non assigné")
                    
                    old_org = []
                    if worker['etablissement']:
                        old_org.append(f"Étab:{worker['etablissement']}")
                    if worker['departement']:
                        old_org.append(f"Dept:{worker['departement']}")
                    if worker['service']:
                        old_org.append(f"Serv:{worker['service']}")
                    if worker['unite']:
                        old_org.append(f"Unit:{worker['unite']}")
                    
                    if old_org:
                        print(f"      📝 Ancien format: {' → '.join(old_org)}")
                    else:
                        print(f"      📝 Ancien format: Aucune assignation")
                
                # Analyser la cohérence
                print(f"\n🔍 Analyse de cohérence:")
                
                # Vérifier les niveaux
                cursor.execute("""
                    SELECT level, level_order, COUNT(*) as count
                    FROM organizational_units
                    GROUP BY level, level_order
                    ORDER BY level_order
                """)
                level_stats = cursor.fetchall()
                
                print("   Niveaux organisationnels:")
                for stat in level_stats:
                    print(f"     - {stat['level']} (ordre {stat['level_order']}): {stat['count']} unités")
                
                # Vérifier les orphelins
                cursor.execute("""
                    SELECT COUNT(*) as orphan_count
                    FROM organizational_units ou1
                    WHERE ou1.parent_id IS NOT NULL 
                    AND NOT EXISTS (
                        SELECT 1 FROM organizational_units ou2 
                        WHERE ou2.id = ou1.parent_id
                    )
                """)
                orphan_count = cursor.fetchone()['orphan_count']
                
                if orphan_count > 0:
                    print(f"   ⚠️  {orphan_count} unités orphelines détectées")
                else:
                    print(f"   ✅ Aucune unité orpheline")
                
                # Vérifier les cycles
                print("   🔄 Vérification des cycles... (à implémenter)")
                
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    examine_hierarchy()