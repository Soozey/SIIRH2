"""
Script pour corriger l'affichage des structures organisationnelles de Jeanne.
Le problème: Les IDs stockés (57, 60, 61) n'existent pas dans organizational_nodes.
Solution: Réinitialiser les champs à NULL pour que le composant affiche correctement.
"""

import psycopg2
from psycopg2.extras import RealDictCursor

# Configuration de la base de données PostgreSQL
DB_CONFIG = {
    'dbname': 'db_siirh_app',
    'user': 'postgres',
    'password': 'tantely123',
    'host': '127.0.0.1',
    'port': '5432'
}

def fix_jeanne_organizational_data():
    """Corrige les données organisationnelles de Jeanne"""
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("=" * 80)
        print("CORRECTION DES DONNÉES ORGANISATIONNELLES DE JEANNE")
        print("=" * 80)
        
        # 1. Trouver Jeanne
        cursor.execute("""
            SELECT 
                id, 
                matricule, 
                nom, 
                prenom, 
                employer_id,
                etablissement,
                departement,
                service,
                unite
            FROM workers 
            WHERE LOWER(nom) LIKE '%jeanne%' OR LOWER(prenom) LIKE '%jeanne%'
            LIMIT 1
        """)
        
        jeanne = cursor.fetchone()
        
        if not jeanne:
            print("❌ Jeanne non trouvée")
            return
        
        print(f"\n✅ Jeanne trouvée:")
        print(f"  ID: {jeanne['id']}")
        print(f"  Matricule: {jeanne['matricule']}")
        print(f"  Nom: {jeanne['prenom']} {jeanne['nom']}")
        print(f"  Employer ID: {jeanne['employer_id']}")
        print()
        
        print("VALEURS ACTUELLES:")
        print(f"  Établissement: '{jeanne['etablissement']}'")
        print(f"  Département: '{jeanne['departement']}'")
        print(f"  Service: '{jeanne['service']}'")
        print(f"  Unité: '{jeanne['unite']}'")
        print()
        
        # 2. Vérifier si ces IDs existent dans organizational_nodes
        print("VÉRIFICATION DES IDs DANS ORGANIZATIONAL_NODES:")
        
        ids_to_check = []
        if jeanne['etablissement']:
            ids_to_check.append(int(jeanne['etablissement']))
        if jeanne['departement']:
            ids_to_check.append(int(jeanne['departement']))
        if jeanne['service']:
            ids_to_check.append(int(jeanne['service']))
        
        if ids_to_check:
            cursor.execute("""
                SELECT id, level, name, employer_id
                FROM organizational_nodes
                WHERE id = ANY(%s)
            """, (ids_to_check,))
            
            existing_nodes = cursor.fetchall()
            
            if existing_nodes:
                print(f"  ✅ {len(existing_nodes)} nœud(s) trouvé(s):")
                for node in existing_nodes:
                    print(f"    - ID {node['id']}: {node['level']} - {node['name']} (Employer: {node['employer_id']})")
            else:
                print(f"  ❌ Aucun nœud trouvé pour les IDs: {ids_to_check}")
                print(f"  ⚠️  Ces IDs sont invalides ou appartiennent à un autre système")
        
        print()
        
        # 3. Proposer la correction
        print("SOLUTION PROPOSÉE:")
        print("  Option 1: Réinitialiser tous les champs à NULL")
        print("  Option 2: Créer les structures organisationnelles manquantes")
        print()
        
        choice = input("Choisir l'option (1 ou 2, ou 'q' pour quitter): ").strip()
        
        if choice == '1':
            # Réinitialiser à NULL
            print("\n📝 Réinitialisation des champs organisationnels à NULL...")
            
            cursor.execute("""
                UPDATE workers 
                SET 
                    etablissement = NULL,
                    departement = NULL,
                    service = NULL,
                    unite = NULL
                WHERE id = %s
            """, (jeanne['id'],))
            
            conn.commit()
            
            print("✅ Champs réinitialisés avec succès!")
            print()
            print("RÉSULTAT:")
            print("  - Jeanne n'aura plus de structure organisationnelle assignée")
            print("  - Le composant affichera correctement les options disponibles")
            print("  - L'utilisateur pourra sélectionner les structures appropriées")
            
        elif choice == '2':
            # Créer les structures manquantes
            print("\n📝 Création des structures organisationnelles...")
            
            employer_id = jeanne['employer_id']
            
            # Créer l'établissement
            cursor.execute("""
                INSERT INTO organizational_nodes 
                (employer_id, parent_id, level, name, code, is_active)
                VALUES (%s, NULL, 'etablissement', 'Établissement Principal', 'ETAB001', true)
                RETURNING id
            """, (employer_id,))
            
            etab_id = cursor.fetchone()['id']
            print(f"  ✅ Établissement créé (ID: {etab_id})")
            
            # Créer le département
            cursor.execute("""
                INSERT INTO organizational_nodes 
                (employer_id, parent_id, level, name, code, is_active)
                VALUES (%s, %s, 'departement', 'Département Général', 'DEPT001', true)
                RETURNING id
            """, (employer_id, etab_id))
            
            dept_id = cursor.fetchone()['id']
            print(f"  ✅ Département créé (ID: {dept_id})")
            
            # Créer le service
            cursor.execute("""
                INSERT INTO organizational_nodes 
                (employer_id, parent_id, level, name, code, is_active)
                VALUES (%s, %s, 'service', 'Service Administration', 'SERV001', true)
                RETURNING id
            """, (employer_id, dept_id))
            
            serv_id = cursor.fetchone()['id']
            print(f"  ✅ Service créé (ID: {serv_id})")
            
            # Mettre à jour Jeanne avec les nouveaux IDs
            cursor.execute("""
                UPDATE workers 
                SET 
                    etablissement = %s,
                    departement = %s,
                    service = %s,
                    unite = NULL
                WHERE id = %s
            """, (str(etab_id), str(dept_id), str(serv_id), jeanne['id']))
            
            conn.commit()
            
            print("\n✅ Structures créées et Jeanne mise à jour avec succès!")
            print()
            print("RÉSULTAT:")
            print(f"  - Établissement: {etab_id}")
            print(f"  - Département: {dept_id}")
            print(f"  - Service: {serv_id}")
            print("  - Le composant affichera maintenant correctement ces structures")
            
        else:
            print("\n❌ Opération annulée")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 80)
        print("CORRECTION TERMINÉE")
        print("=" * 80)
        
    except psycopg2.Error as e:
        print(f"❌ Erreur de base de données: {e}")
        if conn:
            conn.rollback()
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        import traceback
        traceback.print_exc()
        if conn:
            conn.rollback()

if __name__ == "__main__":
    fix_jeanne_organizational_data()
