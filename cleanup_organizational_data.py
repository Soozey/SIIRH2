#!/usr/bin/env python3
"""
Script pour nettoyer les données organisationnelles existantes
et préparer la migration vers l'utilisation complète de la hiérarchie
"""

import psycopg2
import psycopg2.extras
from datetime import datetime

def cleanup_organizational_data():
    """Nettoie les données organisationnelles existantes"""
    
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
                
                print("🧹 Nettoyage des données organisationnelles")
                print("=" * 50)
                
                # 1. Identifier les unités inactives ou de test
                print("\n1️⃣ Identification des unités à nettoyer...")
                
                cursor.execute("""
                    SELECT id, employer_id, level, name, code, is_active, parent_id, level_order
                    FROM organizational_units
                    WHERE is_active = false 
                       OR name ILIKE '%test%' 
                       OR code ILIKE '%test%'
                       OR name ILIKE '%suppression%'
                    ORDER BY employer_id, level_order, name
                """)
                units_to_clean = cursor.fetchall()
                
                print(f"   Unités à nettoyer: {len(units_to_clean)}")
                for unit in units_to_clean:
                    print(f"   - {unit['level']} '{unit['name']}' (Code: {unit['code']}, Active: {unit['is_active']})")
                
                # 2. Vérifier les dépendances (enfants)
                print("\n2️⃣ Vérification des dépendances...")
                
                units_with_children = []
                for unit in units_to_clean:
                    cursor.execute("""
                        SELECT COUNT(*) as child_count
                        FROM organizational_units
                        WHERE parent_id = %s
                    """, (unit['id'],))
                    child_count = cursor.fetchone()['child_count']
                    
                    if child_count > 0:
                        units_with_children.append((unit, child_count))
                        print(f"   ⚠️  '{unit['name']}' a {child_count} enfant(s)")
                
                # 3. Supprimer les unités sans enfants d'abord (ordre inverse de la hiérarchie)
                print("\n3️⃣ Suppression des unités sans dépendances...")
                
                # Trier par niveau décroissant (unités d'abord, puis services, départements, établissements)
                units_to_delete = [unit for unit in units_to_clean if unit['id'] not in [u[0]['id'] for u in units_with_children]]
                units_to_delete.sort(key=lambda x: -x['level_order'] if x['level_order'] else 0)  # Ordre décroissant
                
                deleted_count = 0
                for unit in units_to_delete:
                    try:
                        cursor.execute("DELETE FROM organizational_units WHERE id = %s", (unit['id'],))
                        print(f"   ✅ Supprimé: {unit['level']} '{unit['name']}'")
                        deleted_count += 1
                    except Exception as e:
                        print(f"   ❌ Erreur lors de la suppression de '{unit['name']}': {e}")
                
                print(f"   Total supprimé: {deleted_count} unités")
                
                # 4. Traiter les unités avec enfants (supprimer récursivement)
                print("\n4️⃣ Traitement des unités avec enfants...")
                
                def delete_recursive(unit_id, unit_name, level=0):
                    """Supprime récursivement une unité et ses enfants"""
                    indent = "  " * level
                    
                    # Récupérer les enfants
                    cursor.execute("""
                        SELECT id, name, level
                        FROM organizational_units
                        WHERE parent_id = %s
                    """, (unit_id,))
                    children = cursor.fetchall()
                    
                    # Supprimer les enfants d'abord
                    for child in children:
                        delete_recursive(child['id'], child['name'], level + 1)
                    
                    # Supprimer l'unité elle-même
                    try:
                        cursor.execute("DELETE FROM organizational_units WHERE id = %s", (unit_id,))
                        print(f"   {indent}✅ Supprimé: {unit_name}")
                        return True
                    except Exception as e:
                        print(f"   {indent}❌ Erreur lors de la suppression de '{unit_name}': {e}")
                        return False
                
                for unit, child_count in units_with_children:
                    print(f"   🔄 Suppression récursive de '{unit['name']}' et ses {child_count} enfant(s):")
                    delete_recursive(unit['id'], unit['name'])
                
                # 5. Vérifier l'état après nettoyage
                print("\n5️⃣ État après nettoyage...")
                
                cursor.execute("""
                    SELECT 
                        employer_id,
                        level,
                        COUNT(*) as count,
                        COUNT(CASE WHEN is_active = true THEN 1 END) as active_count
                    FROM organizational_units
                    GROUP BY employer_id, level
                    ORDER BY employer_id, 
                             CASE level 
                                WHEN 'etablissement' THEN 1
                                WHEN 'departement' THEN 2
                                WHEN 'service' THEN 3
                                WHEN 'unite' THEN 4
                                ELSE 5
                             END
                """)
                final_stats = cursor.fetchall()
                
                # Récupérer les noms des employeurs
                cursor.execute("SELECT id, raison_sociale FROM employers")
                employers = {emp['id']: emp['raison_sociale'] for emp in cursor.fetchall()}
                
                current_employer = None
                for stat in final_stats:
                    employer_name = employers.get(stat['employer_id'], f"Employeur {stat['employer_id']}")
                    
                    if current_employer != stat['employer_id']:
                        print(f"\n   📊 {employer_name}:")
                        current_employer = stat['employer_id']
                    
                    print(f"     - {stat['level']}: {stat['count']} total ({stat['active_count']} actives)")
                
                # 6. Recommandations pour la suite
                print("\n6️⃣ Recommandations pour la migration...")
                
                cursor.execute("SELECT COUNT(*) as total FROM organizational_units WHERE is_active = true")
                active_units = cursor.fetchone()['total']
                
                cursor.execute("SELECT COUNT(*) as total FROM workers WHERE organizational_unit_id IS NOT NULL")
                assigned_workers = cursor.fetchone()['total']
                
                print(f"   ✅ Unités organisationnelles actives: {active_units}")
                print(f"   👥 Travailleurs assignés à la hiérarchie: {assigned_workers}")
                
                if active_units > 0 and assigned_workers == 0:
                    print("   💡 Prochaine étape: Assigner les travailleurs aux unités organisationnelles")
                    print("   💡 Puis: Migrer les filtres pour utiliser la hiérarchie")
                    print("   💡 Enfin: Supprimer les anciens champs texte")
                
                print(f"\n✅ Nettoyage terminé!")
                
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    cleanup_organizational_data()