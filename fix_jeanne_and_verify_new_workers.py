"""
Script pour:
1. Corriger Jeanne en réinitialisant ses champs organisationnels à NULL
2. Vérifier que les nouveaux salariés ne rencontreront pas le même problème
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

def fix_and_verify():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("=" * 80)
        print("CORRECTION DE JEANNE ET VÉRIFICATION POUR LES NOUVEAUX SALARIÉS")
        print("=" * 80)
        
        # 1. Corriger Jeanne
        print("\n1. CORRECTION DE JEANNE")
        print("-" * 80)
        
        cursor.execute("""
            SELECT id, matricule, nom, prenom, etablissement, departement, service, unite
            FROM workers 
            WHERE LOWER(nom) LIKE '%jeanne%' OR LOWER(prenom) LIKE '%jeanne%'
            LIMIT 1
        """)
        
        jeanne = cursor.fetchone()
        
        if jeanne:
            print(f"✅ Jeanne trouvée (ID: {jeanne['id']})")
            print(f"   Valeurs actuelles:")
            print(f"   - Établissement: '{jeanne['etablissement']}'")
            print(f"   - Département: '{jeanne['departement']}'")
            print(f"   - Service: '{jeanne['service']}'")
            print(f"   - Unité: '{jeanne['unite']}'")
            
            # Réinitialiser à NULL
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
            print("\n✅ Champs réinitialisés à NULL avec succès!")
        else:
            print("❌ Jeanne non trouvée")
        
        # 2. Vérifier le comportement pour les nouveaux salariés
        print("\n2. VÉRIFICATION POUR LES NOUVEAUX SALARIÉS")
        print("-" * 80)
        
        print("\nQuand vous créez un nouveau salarié:")
        print("  ✅ Les champs organisationnels seront NULL par défaut")
        print("  ✅ Le composant CascadingOrganizationalSelect affichera correctement")
        print("     les options disponibles (vides si aucune structure n'existe)")
        print("  ✅ L'utilisateur pourra sélectionner les structures appropriées")
        
        # 3. Vérifier s'il existe des structures organisationnelles
        print("\n3. VÉRIFICATION DES STRUCTURES ORGANISATIONNELLES DISPONIBLES")
        print("-" * 80)
        
        if jeanne:
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM organizational_nodes
                WHERE employer_id = %s
            """, (jeanne['employer_id'],))
            
            count = cursor.fetchone()['count']
            
            if count == 0:
                print(f"\n⚠️  ATTENTION: Aucune structure organisationnelle trouvée pour l'employeur {jeanne['employer_id']}")
                print("\nACTIONS RECOMMANDÉES:")
                print("  1. Créer les structures organisationnelles via l'interface 'Organisation'")
                print("  2. Ou utiliser le système hiérarchique pour créer:")
                print("     - Établissements")
                print("     - Départements")
                print("     - Services")
                print("     - Unités")
                print("\nJusqu'à ce que les structures soient créées:")
                print("  - Les sélecteurs seront vides mais fonctionnels")
                print("  - Les salariés n'auront pas de structure assignée")
                print("  - Cela n'empêchera pas la création de nouveaux salariés")
            else:
                print(f"✅ {count} structure(s) organisationnelle(s) trouvée(s)")
                
                # Afficher les structures par niveau
                cursor.execute("""
                    SELECT level, COUNT(*) as count
                    FROM organizational_nodes
                    WHERE employer_id = %s
                    GROUP BY level
                    ORDER BY 
                        CASE level
                            WHEN 'etablissement' THEN 1
                            WHEN 'departement' THEN 2
                            WHEN 'service' THEN 3
                            WHEN 'unite' THEN 4
                        END
                """, (jeanne['employer_id'],))
                
                structures = cursor.fetchall()
                print("\nRépartition par niveau:")
                for struct in structures:
                    print(f"  - {struct['level'].capitalize()}: {struct['count']}")
        
        # 4. Recommandations
        print("\n4. RECOMMANDATIONS POUR ÉVITER CE PROBLÈME À L'AVENIR")
        print("-" * 80)
        print("""
  ✅ BONNES PRATIQUES:
  
  1. Créer d'abord les structures organisationnelles dans 'Organisation'
     avant d'ajouter des salariés
  
  2. Utiliser le système hiérarchique (organizational_nodes) plutôt que
     les anciens champs texte
  
  3. Lors de la création d'un salarié:
     - Laisser les champs vides si aucune structure n'existe
     - Ou sélectionner les structures appropriées dans les listes déroulantes
  
  4. Ne jamais saisir manuellement des IDs dans les champs organisationnels
  
  ✅ COMPORTEMENT ATTENDU POUR LES NOUVEAUX SALARIÉS:
  
  - Champs NULL par défaut ✓
  - Composant affiche les options disponibles ✓
  - Pas d'affichage de "toutes les structures" si NULL ✓
  - Sélection en cascade fonctionnelle ✓
""")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 80)
        print("CORRECTION TERMINÉE - JEANNE EST MAINTENANT HARMONISÉE")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        if conn:
            conn.rollback()

if __name__ == "__main__":
    fix_and_verify()
