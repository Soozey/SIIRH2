#!/usr/bin/env python3
"""
Script pour vérifier la structure organisationnelle existante
"""

import psycopg2
import psycopg2.extras

def check_existing_structure():
    """Vérifie la structure organisationnelle existante"""
    
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
                
                # Vérifier la structure de la table organizational_units
                print("🔍 Structure de la table organizational_units:")
                cursor.execute("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns 
                    WHERE table_name = 'organizational_units'
                    ORDER BY ordinal_position
                """)
                columns = cursor.fetchall()
                
                if columns:
                    for col in columns:
                        print(f"  - {col['column_name']}: {col['data_type']} {'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'}")
                        if col['column_default']:
                            print(f"    Default: {col['column_default']}")
                else:
                    print("  ❌ Table organizational_units n'existe pas")
                    return
                
                # Vérifier les contraintes
                print("\n🔗 Contraintes de la table:")
                cursor.execute("""
                    SELECT tc.constraint_name, tc.constraint_type, kcu.column_name
                    FROM information_schema.table_constraints tc
                    JOIN information_schema.key_column_usage kcu 
                        ON tc.constraint_name = kcu.constraint_name
                    WHERE tc.table_name = 'organizational_units'
                """)
                constraints = cursor.fetchall()
                
                for constraint in constraints:
                    print(f"  - {constraint['constraint_name']} ({constraint['constraint_type']}): {constraint['column_name']}")
                
                # Vérifier les index
                print("\n📊 Index de la table:")
                cursor.execute("""
                    SELECT indexname, indexdef
                    FROM pg_indexes
                    WHERE tablename = 'organizational_units'
                """)
                indexes = cursor.fetchall()
                
                for index in indexes:
                    print(f"  - {index['indexname']}: {index['indexdef']}")
                
                # Vérifier le contenu existant
                print("\n📋 Contenu existant:")
                cursor.execute("SELECT COUNT(*) as count FROM organizational_units")
                count = cursor.fetchone()['count']
                print(f"  - Nombre d'enregistrements: {count}")
                
                if count > 0:
                    cursor.execute("""
                        SELECT id, employer_id, level, name, parent_id, level_order
                        FROM organizational_units
                        ORDER BY employer_id, level_order, name
                        LIMIT 10
                    """)
                    records = cursor.fetchall()
                    
                    print("  - Exemples d'enregistrements:")
                    for record in records:
                        print(f"    • ID:{record['id']} - {record['level']} '{record['name']}' (Employeur:{record['employer_id']}, Parent:{record['parent_id']})")
                
                # Vérifier les modifications nécessaires pour le Worker
                print("\n👥 Structure de la table workers (colonnes organisationnelles):")
                cursor.execute("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns 
                    WHERE table_name = 'workers' 
                    AND column_name IN ('etablissement', 'departement', 'service', 'unite', 
                                       'establishment_id', 'department_id', 'service_id', 'unit_id',
                                       'organizational_unit_id')
                    ORDER BY column_name
                """)
                worker_columns = cursor.fetchall()
                
                for col in worker_columns:
                    print(f"  - {col['column_name']}: {col['data_type']} {'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'}")
                
                # Vérifier si la table organizational_structures existe déjà
                print("\n🔍 Vérification de la table organizational_structures:")
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'organizational_structures'
                    )
                """)
                structures_exists = cursor.fetchone()[0]
                
                if structures_exists:
                    print("  ✅ La table organizational_structures existe déjà")
                    cursor.execute("SELECT COUNT(*) as count FROM organizational_structures")
                    structures_count = cursor.fetchone()['count']
                    print(f"  - Nombre d'enregistrements: {structures_count}")
                else:
                    print("  ❌ La table organizational_structures n'existe pas encore")
                
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    check_existing_structure()