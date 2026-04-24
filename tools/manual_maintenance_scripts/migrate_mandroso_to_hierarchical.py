"""
Migrer les structures organisationnelles de Mandroso depuis l'ancien système (texte)
vers le nouveau système hiérarchique (organizational_nodes)
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

def migrate_mandroso():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("=" * 80)
        print("MIGRATION DES STRUCTURES ORGANISATIONNELLES DE MANDROSO")
        print("=" * 80)
        
        # 1. Trouver Mandroso
        cursor.execute("SELECT id FROM employers WHERE LOWER(raison_sociale) LIKE '%mandroso%'")
        mandroso = cursor.fetchone()
        employer_id = mandroso['id']
        
        print(f"\n✅ Employeur Mandroso (ID: {employer_id})")
        
        # 2. Extraire toutes les valeurs uniques des salariés
        cursor.execute("""
            SELECT DISTINCT
                etablissement,
                departement,
                service,
                unite
            FROM workers
            WHERE employer_id = %s
            AND (etablissement IS NOT NULL OR departement IS NOT NULL OR service IS NOT NULL OR unite IS NOT NULL)
        """, (employer_id,))
        
        combinations = cursor.fetchall()
        
        # Collecter les valeurs uniques
        etablissements = set()
        departements = set()
        services = set()
        unites = set()
        
        for combo in combinations:
            if combo['etablissement']:
                etablissements.add(combo['etablissement'])
            if combo['departement']:
                departements.add(combo['departement'])
            if combo['service']:
                services.add(combo['service'])
            if combo['unite']:
                unites.add(combo['unite'])
        
        print(f"\n📊 STRUCTURES DÉTECTÉES:")
        print(f"  Établissements: {len(etablissements)} - {list(etablissements)}")
        print(f"  Départements: {len(departements)} - {list(departements)}")
        print(f"  Services: {len(services)} - {list(services)}")
        print(f"  Unités: {len(unites)} - {list(unites)}")
        
        # 3. Créer les structures hiérarchiques
        print(f"\n🔨 CRÉATION DES STRUCTURES HIÉRARCHIQUES:")
        print("-" * 80)
        
        created_nodes = {}
        
        # Créer les établissements
        for etab in sorted(etablissements):
            cursor.execute("""
                INSERT INTO organizational_nodes 
                (employer_id, parent_id, level, name, code, is_active)
                VALUES (%s, NULL, 'etablissement', %s, %s, true)
                RETURNING id
            """, (employer_id, etab, etab[:20]))
            
            etab_id = cursor.fetchone()['id']
            created_nodes[('etablissement', etab)] = etab_id
            print(f"  ✅ Établissement créé: {etab} (ID: {etab_id})")
        
        # Créer les départements (sous chaque établissement)
        for dept in sorted(departements):
            # Trouver l'établissement parent
            cursor.execute("""
                SELECT DISTINCT etablissement
                FROM workers
                WHERE employer_id = %s AND departement = %s AND etablissement IS NOT NULL
                LIMIT 1
            """, (employer_id, dept))
            
            parent_etab = cursor.fetchone()
            if parent_etab and parent_etab['etablissement']:
                parent_id = created_nodes.get(('etablissement', parent_etab['etablissement']))
                
                cursor.execute("""
                    INSERT INTO organizational_nodes 
                    (employer_id, parent_id, level, name, code, is_active)
                    VALUES (%s, %s, 'departement', %s, %s, true)
                    RETURNING id
                """, (employer_id, parent_id, dept, dept[:20]))
                
                dept_id = cursor.fetchone()['id']
                created_nodes[('departement', dept, parent_etab['etablissement'])] = dept_id
                print(f"  ✅ Département créé: {dept} sous {parent_etab['etablissement']} (ID: {dept_id})")
        
        # Créer les services (sous chaque département)
        for serv in sorted(services):
            # Trouver le département parent
            cursor.execute("""
                SELECT DISTINCT etablissement, departement
                FROM workers
                WHERE employer_id = %s AND service = %s 
                AND etablissement IS NOT NULL AND departement IS NOT NULL
                LIMIT 1
            """, (employer_id, serv))
            
            parent_info = cursor.fetchone()
            if parent_info and parent_info['departement']:
                parent_id = created_nodes.get(('departement', parent_info['departement'], parent_info['etablissement']))
                
                if parent_id:
                    cursor.execute("""
                        INSERT INTO organizational_nodes 
                        (employer_id, parent_id, level, name, code, is_active)
                        VALUES (%s, %s, 'service', %s, %s, true)
                        RETURNING id
                    """, (employer_id, parent_id, serv, serv[:20]))
                    
                    serv_id = cursor.fetchone()['id']
                    created_nodes[('service', serv, parent_info['departement'], parent_info['etablissement'])] = serv_id
                    print(f"  ✅ Service créé: {serv} sous {parent_info['departement']} (ID: {serv_id})")
        
        conn.commit()
        
        # 4. Mettre à jour les salariés avec les nouveaux IDs
        print(f"\n🔄 MISE À JOUR DES SALARIÉS:")
        print("-" * 80)
        
        cursor.execute("""
            SELECT id, matricule, nom, prenom, etablissement, departement, service
            FROM workers
            WHERE employer_id = %s
            AND etablissement IS NOT NULL
        """, (employer_id,))
        
        workers_to_update = cursor.fetchall()
        
        for worker in workers_to_update:
            # Trouver les IDs correspondants
            etab_id = created_nodes.get(('etablissement', worker['etablissement']))
            dept_id = created_nodes.get(('departement', worker['departement'], worker['etablissement'])) if worker['departement'] else None
            serv_id = created_nodes.get(('service', worker['service'], worker['departement'], worker['etablissement'])) if worker['service'] else None
            
            # Mettre à jour avec les IDs
            cursor.execute("""
                UPDATE workers
                SET 
                    etablissement = %s,
                    departement = %s,
                    service = %s
                WHERE id = %s
            """, (str(etab_id) if etab_id else None,
                  str(dept_id) if dept_id else None,
                  str(serv_id) if serv_id else None,
                  worker['id']))
            
            print(f"  ✅ {worker['prenom']} {worker['nom']}: Étab={etab_id}, Dept={dept_id}, Serv={serv_id}")
        
        conn.commit()
        
        print(f"\n✅ MIGRATION TERMINÉE AVEC SUCCÈS!")
        print(f"   - {len(created_nodes)} structures créées")
        print(f"   - {len(workers_to_update)} salariés mis à jour")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        if conn:
            conn.rollback()

if __name__ == "__main__":
    migrate_mandroso()
