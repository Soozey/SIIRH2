"""
Vérifier les structures organisationnelles pour Mandroso services
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

def check_mandroso():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("=" * 80)
        print("VÉRIFICATION DES STRUCTURES POUR MANDROSO SERVICES")
        print("=" * 80)
        
        # 1. Trouver l'employeur Mandroso
        cursor.execute("""
            SELECT id, raison_sociale
            FROM employers
            WHERE LOWER(raison_sociale) LIKE '%mandroso%'
        """)
        
        mandroso = cursor.fetchone()
        
        if not mandroso:
            print("❌ Employeur 'Mandroso' non trouvé")
            return
        
        print(f"\n✅ Employeur trouvé:")
        print(f"  ID: {mandroso['id']}")
        print(f"  Raison sociale: {mandroso['raison_sociale']}")
        
        # 2. Vérifier les structures dans organizational_nodes
        print(f"\n📊 STRUCTURES DANS ORGANIZATIONAL_NODES:")
        print("-" * 80)
        
        cursor.execute("""
            SELECT 
                id,
                level,
                name,
                code,
                parent_id,
                is_active
            FROM organizational_nodes
            WHERE employer_id = %s
            ORDER BY 
                CASE level
                    WHEN 'etablissement' THEN 1
                    WHEN 'departement' THEN 2
                    WHEN 'service' THEN 3
                    WHEN 'unite' THEN 4
                END,
                name
        """, (mandroso['id'],))
        
        nodes = cursor.fetchall()
        
        if nodes:
            print(f"✅ {len(nodes)} structure(s) trouvée(s):\n")
            
            by_level = {}
            for node in nodes:
                level = node['level']
                if level not in by_level:
                    by_level[level] = []
                by_level[level].append(node)
            
            for level in ['etablissement', 'departement', 'service', 'unite']:
                if level in by_level:
                    print(f"  {level.upper()}:")
                    for node in by_level[level]:
                        active = "✓" if node['is_active'] else "✗"
                        parent = f"(parent: {node['parent_id']})" if node['parent_id'] else "(racine)"
                        print(f"    [{active}] ID {node['id']}: {node['name']} {parent}")
                    print()
        else:
            print("❌ Aucune structure trouvée dans organizational_nodes")
        
        # 3. Vérifier les salariés de Mandroso
        print(f"\n👥 SALARIÉS DE MANDROSO:")
        print("-" * 80)
        
        cursor.execute("""
            SELECT 
                id,
                matricule,
                nom,
                prenom,
                etablissement,
                departement,
                service,
                unite
            FROM workers
            WHERE employer_id = %s
            ORDER BY nom, prenom
            LIMIT 10
        """, (mandroso['id'],))
        
        workers = cursor.fetchall()
        
        if workers:
            print(f"✅ {len(workers)} salarié(s) (affichage des 10 premiers):\n")
            for w in workers:
                print(f"  {w['prenom']} {w['nom']} (ID: {w['id']})")
                print(f"    Établissement: {w['etablissement']}")
                print(f"    Département: {w['departement']}")
                print(f"    Service: {w['service']}")
                print(f"    Unité: {w['unite']}")
                print()
        else:
            print("❌ Aucun salarié trouvé")
        
        # 4. Vérifier l'API endpoint
        print(f"\n🔌 TEST DE L'ENDPOINT API:")
        print("-" * 80)
        print(f"URL à tester: http://127.0.0.1:8000/employers/{mandroso['id']}/organization/cascading-options")
        print(f"Paramètre: parent_id=null (pour les établissements)")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_mandroso()
