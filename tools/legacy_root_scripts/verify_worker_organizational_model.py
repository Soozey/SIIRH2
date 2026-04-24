#!/usr/bin/env python3
"""
Script pour vérifier le modèle organisationnel des travailleurs
"""

import psycopg2
import psycopg2.extras

def verify_worker_organizational_model():
    """Vérifie le modèle organisationnel des travailleurs"""
    
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
                
                print("🔍 Vérification du modèle organisationnel des travailleurs")
                print("=" * 60)
                
                # 1. Vérifier la structure de la table workers
                print("\n1️⃣ Structure de la table workers (colonnes organisationnelles):")
                cursor.execute("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns 
                    WHERE table_name = 'workers' 
                    AND column_name IN ('etablissement', 'departement', 'service', 'unite', 
                                       'establishment_id', 'department_id', 'service_id', 'unit_id',
                                       'organizational_unit_id')
                    ORDER BY column_name
                """)
                columns = cursor.fetchall()
                
                for col in columns:
                    nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
                    default = f" DEFAULT {col['column_default']}" if col['column_default'] else ""
                    print(f"   - {col['column_name']}: {col['data_type']} {nullable}{default}")
                
                # 2. Vérifier les contraintes de clé étrangère
                print("\n2️⃣ Contraintes de clé étrangère:")
                cursor.execute("""
                    SELECT 
                        tc.constraint_name,
                        kcu.column_name,
                        ccu.table_name AS foreign_table_name,
                        ccu.column_name AS foreign_column_name
                    FROM information_schema.table_constraints tc
                    JOIN information_schema.key_column_usage kcu 
                        ON tc.constraint_name = kcu.constraint_name
                    JOIN information_schema.constraint_column_usage ccu 
                        ON ccu.constraint_name = tc.constraint_name
                    WHERE tc.table_name = 'workers' 
                    AND tc.constraint_type = 'FOREIGN KEY'
                    AND kcu.column_name LIKE '%organizational%'
                """)
                fk_constraints = cursor.fetchall()
                
                for fk in fk_constraints:
                    print(f"   - {fk['column_name']} → {fk['foreign_table_name']}.{fk['foreign_column_name']}")
                
                # 3. Vérifier l'état actuel des assignations
                print("\n3️⃣ État actuel des assignations organisationnelles:")
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_workers,
                        COUNT(organizational_unit_id) as with_org_unit,
                        COUNT(etablissement) as with_etablissement,
                        COUNT(departement) as with_departement,
                        COUNT(service) as with_service,
                        COUNT(unite) as with_unite
                    FROM workers
                """)
                stats = cursor.fetchone()
                
                print(f"   Total travailleurs: {stats['total_workers']}")
                print(f"   Avec organizational_unit_id: {stats['with_org_unit']} ({stats['with_org_unit']/stats['total_workers']*100:.1f}%)")
                print(f"   Avec etablissement (texte): {stats['with_etablissement']} ({stats['with_etablissement']/stats['total_workers']*100:.1f}%)")
                print(f"   Avec departement (texte): {stats['with_departement']} ({stats['with_departement']/stats['total_workers']*100:.1f}%)")
                print(f"   Avec service (texte): {stats['with_service']} ({stats['with_service']/stats['total_workers']*100:.1f}%)")
                print(f"   Avec unite (texte): {stats['with_unite']} ({stats['with_unite']/stats['total_workers']*100:.1f}%)")
                
                # 4. Tester la logique de traversée hiérarchique (simuler les propriétés)
                print("\n4️⃣ Test de la logique de traversée hiérarchique:")
                
                # Récupérer un travailleur avec une assignation organisationnelle (s'il y en a)
                cursor.execute("""
                    SELECT w.id, w.matricule, w.nom, w.organizational_unit_id,
                           ou.name as unit_name, ou.level as unit_level
                    FROM workers w
                    LEFT JOIN organizational_units ou ON w.organizational_unit_id = ou.id
                    LIMIT 5
                """)
                workers = cursor.fetchall()
                
                for worker in workers:
                    print(f"   👤 {worker['matricule']} - {worker['nom']}")
                    
                    if worker['organizational_unit_id']:
                        print(f"      🏢 Unité assignée: {worker['unit_name']} ({worker['unit_level']})")
                        
                        # Simuler la traversée hiérarchique
                        unit_id = worker['organizational_unit_id']
                        hierarchy_path = []
                        
                        # Remonter la hiérarchie
                        current_id = unit_id
                        while current_id:
                            cursor.execute("""
                                SELECT id, name, level, parent_id
                                FROM organizational_units
                                WHERE id = %s
                            """, (current_id,))
                            unit = cursor.fetchone()
                            
                            if unit:
                                hierarchy_path.insert(0, f"{unit['level']}: {unit['name']}")
                                current_id = unit['parent_id']
                            else:
                                break
                        
                        print(f"      📍 Chemin hiérarchique: {' → '.join(hierarchy_path)}")
                    else:
                        print(f"      🏢 Aucune assignation organisationnelle")
                
                # 5. Recommandations
                print("\n5️⃣ Recommandations:")
                
                if stats['with_org_unit'] == 0:
                    print("   💡 Aucun travailleur n'est assigné à la hiérarchie organisationnelle")
                    print("   💡 Prochaine étape: Migrer les travailleurs vers la hiérarchie")
                    
                    if stats['with_etablissement'] > 0 or stats['with_departement'] > 0:
                        print("   💡 Des assignations texte existent - migration possible")
                    else:
                        print("   💡 Aucune assignation existante - assignation manuelle nécessaire")
                
                else:
                    print(f"   ✅ {stats['with_org_unit']} travailleurs utilisent la hiérarchie")
                    
                    if stats['with_etablissement'] > 0:
                        print("   ⚠️  Des assignations texte coexistent - nettoyage recommandé")
                
                # 6. Vérifier si des colonnes individuelles sont nécessaires
                print("\n6️⃣ Analyse du besoin de colonnes individuelles:")
                
                print("   📋 Modèle actuel: organizational_unit_id (référence unique)")
                print("   📋 Modèle spec: establishment_id, department_id, service_id, unit_id")
                print()
                print("   ✅ Avantages du modèle actuel:")
                print("      - Cohérence garantie (pas de combinaisons invalides)")
                print("      - Simplicité (une seule référence)")
                print("      - Traversée automatique de la hiérarchie")
                print()
                print("   ⚠️  Avantages du modèle spec:")
                print("      - Requêtes directes par niveau")
                print("      - Filtrage plus simple")
                print("      - Compatibilité avec l'ancien système")
                print()
                print("   💡 Recommandation: Garder le modèle actuel mais ajouter des vues")
                print("      ou des propriétés calculées pour faciliter les requêtes")
                
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_worker_organizational_model()