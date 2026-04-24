"""
Script pour créer des structures organisationnelles de test
pour permettre la sélection dans le formulaire des travailleurs.
"""

import psycopg2
from psycopg2.extras import RealDictCursor

DB_CONFIG = {
    'dbname': 'db_siirh_app',
    'user': 'postgres',
    'password': 'tantely123',
    'host': '127.0.0.1',
    'port': '5432'
}

def create_structures():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("=" * 80)
        print("CRÉATION DES STRUCTURES ORGANISATIONNELLES")
        print("=" * 80)
        
        # Trouver l'employeur de Jeanne
        cursor.execute("SELECT DISTINCT employer_id FROM workers WHERE id = 2032")
        result = cursor.fetchone()
        
        if not result:
            print("❌ Impossible de trouver l'employeur")
            return
        
        employer_id = result['employer_id']
        print(f"\n✅ Employeur trouvé: ID {employer_id}")
        
        # Vérifier si des structures existent déjà
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM organizational_nodes 
            WHERE employer_id = %s
        """, (employer_id,))
        
        existing_count = cursor.fetchone()['count']
        
        if existing_count > 0:
            print(f"\n⚠️  {existing_count} structure(s) existent déjà pour cet employeur")
            choice = input("Voulez-vous les supprimer et recréer? (o/n): ").strip().lower()
            
            if choice == 'o':
                cursor.execute("""
                    DELETE FROM organizational_nodes 
                    WHERE employer_id = %s
                """, (employer_id,))
                print("✅ Structures existantes supprimées")
            else:
                print("❌ Opération annulée")
                return
        
        print("\n📝 Création des structures organisationnelles...")
        
        # 1. Créer les établissements
        print("\n1. ÉTABLISSEMENTS")
        etablissements = [
            ("Siège Social", "SIEGE"),
            ("Agence Antananarivo", "AGENCE-TNR"),
        ]
        
        etab_ids = {}
        for name, code in etablissements:
            cursor.execute("""
                INSERT INTO organizational_nodes 
                (employer_id, parent_id, level, name, code, is_active, sort_order)
                VALUES (%s, NULL, 'etablissement', %s, %s, true, 0)
                RETURNING id
            """, (employer_id, name, code))
            
            etab_id = cursor.fetchone()['id']
            etab_ids[code] = etab_id
            print(f"  ✅ {name} (ID: {etab_id})")
        
        # 2. Créer les départements
        print("\n2. DÉPARTEMENTS")
        departements = [
            ("Direction Générale", "DG", "SIEGE"),
            ("Ressources Humaines", "RH", "SIEGE"),
            ("Comptabilité", "COMPTA", "SIEGE"),
            ("Commercial", "COMMERCIAL", "AGENCE-TNR"),
        ]
        
        dept_ids = {}
        for name, code, parent_code in departements:
            parent_id = etab_ids[parent_code]
            cursor.execute("""
                INSERT INTO organizational_nodes 
                (employer_id, parent_id, level, name, code, is_active, sort_order)
                VALUES (%s, %s, 'departement', %s, %s, true, 0)
                RETURNING id
            """, (employer_id, parent_id, name, code))
            
            dept_id = cursor.fetchone()['id']
            dept_ids[code] = dept_id
            print(f"  ✅ {name} (ID: {dept_id}, Parent: {parent_code})")
        
        # 3. Créer les services
        print("\n3. SERVICES")
        services = [
            ("Service Paie", "PAIE", "RH"),
            ("Service Recrutement", "RECRUTEMENT", "RH"),
            ("Service Comptabilité Générale", "COMPTA-GEN", "COMPTA"),
            ("Service Ventes", "VENTES", "COMMERCIAL"),
        ]
        
        service_ids = {}
        for name, code, parent_code in services:
            parent_id = dept_ids[parent_code]
            cursor.execute("""
                INSERT INTO organizational_nodes 
                (employer_id, parent_id, level, name, code, is_active, sort_order)
                VALUES (%s, %s, 'service', %s, %s, true, 0)
                RETURNING id
            """, (employer_id, parent_id, name, code))
            
            service_id = cursor.fetchone()['id']
            service_ids[code] = service_id
            print(f"  ✅ {name} (ID: {service_id}, Parent: {parent_code})")
        
        # 4. Créer les unités
        print("\n4. UNITÉS")
        unites = [
            ("Équipe Paie A", "PAIE-A", "PAIE"),
            ("Équipe Paie B", "PAIE-B", "PAIE"),
            ("Équipe Recrutement", "RECR-1", "RECRUTEMENT"),
        ]
        
        for name, code, parent_code in unites:
            parent_id = service_ids[parent_code]
            cursor.execute("""
                INSERT INTO organizational_nodes 
                (employer_id, parent_id, level, name, code, is_active, sort_order)
                VALUES (%s, %s, 'unite', %s, %s, true, 0)
                RETURNING id
            """, (employer_id, parent_id, name, code))
            
            unite_id = cursor.fetchone()['id']
            print(f"  ✅ {name} (ID: {unite_id}, Parent: {parent_code})")
        
        conn.commit()
        
        print("\n" + "=" * 80)
        print("✅ STRUCTURES CRÉÉES AVEC SUCCÈS!")
        print("=" * 80)
        
        print("\nRÉSUMÉ:")
        print(f"  - {len(etablissements)} établissement(s)")
        print(f"  - {len(departements)} département(s)")
        print(f"  - {len(services)} service(s)")
        print(f"  - {len(unites)} unité(s)")
        
        print("\n📋 PROCHAINES ÉTAPES:")
        print("  1. Rafraîchir la page du frontend")
        print("  2. Ouvrir 'Modifier le travailleur' pour Jeanne")
        print("  3. Les structures organisationnelles seront maintenant accessibles")
        print("  4. Sélectionner: Établissement → Département → Service → Unité")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        if conn:
            conn.rollback()

if __name__ == "__main__":
    create_structures()
