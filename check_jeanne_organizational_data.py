"""
Script de diagnostic pour vérifier les données organisationnelles de Jeanne
et comprendre pourquoi toutes les structures sont visibles lors de la modification.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import json

# Configuration de la base de données PostgreSQL
DB_CONFIG = {
    'dbname': 'db_siirh_app',
    'user': 'postgres',
    'password': 'tantely123',
    'host': '127.0.0.1',
    'port': '5432'
}

def check_jeanne_data():
    """Vérifie les données de Jeanne dans la base PostgreSQL"""
    
    try:
        # Connexion à la base de données
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("=" * 80)
        print("DIAGNOSTIC DES DONNÉES ORGANISATIONNELLES DE JEANNE")
        print("=" * 80)
        
        # 1. Rechercher Jeanne dans la table workers
        print("\n1. RECHERCHE DE JEANNE DANS LA TABLE WORKERS")
        print("-" * 80)
        
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
                unite,
                organizational_unit_id,
                poste,
                date_embauche
            FROM workers 
            WHERE LOWER(nom) LIKE '%jeanne%' OR LOWER(prenom) LIKE '%jeanne%'
            ORDER BY id
        """)
        
        jeanne_workers = cursor.fetchall()
        
        if not jeanne_workers:
            print("❌ Aucun travailleur trouvé avec le nom 'Jeanne'")
            return
        
        print(f"✅ {len(jeanne_workers)} travailleur(s) trouvé(s) avec 'Jeanne' dans le nom:")
        print()
        
        for worker in jeanne_workers:
            print(f"  ID: {worker['id']}")
            print(f"  Matricule: {worker['matricule']}")
            print(f"  Nom: {worker['nom']}")
            print(f"  Prénom: {worker['prenom']}")
            print(f"  Employer ID: {worker['employer_id']}")
            print(f"  Établissement: {worker['etablissement']} (Type: {type(worker['etablissement']).__name__})")
            print(f"  Département: {worker['departement']} (Type: {type(worker['departement']).__name__})")
            print(f"  Service: {worker['service']} (Type: {type(worker['service']).__name__})")
            print(f"  Unité: {worker['unite']} (Type: {type(worker['unite']).__name__})")
            print(f"  Organizational Unit ID: {worker['organizational_unit_id']}")
            print(f"  Poste: {worker['poste']}")
            print(f"  Date embauche: {worker['date_embauche']}")
            print()
        
        # 2. Vérifier la structure de la table workers
        print("\n2. STRUCTURE DE LA TABLE WORKERS (COLONNES ORGANISATIONNELLES)")
        print("-" * 80)
        
        cursor.execute("""
            SELECT 
                column_name, 
                data_type, 
                is_nullable,
                column_default
            FROM information_schema.columns 
            WHERE table_name = 'workers' 
            AND column_name IN ('etablissement', 'departement', 'service', 'unite', 'organizational_unit_id')
            ORDER BY ordinal_position
        """)
        
        columns = cursor.fetchall()
        
        for col in columns:
            print(f"  {col['column_name']}: {col['data_type']} (Nullable: {col['is_nullable']}, Default: {col['column_default']})")
        
        # 3. Comparer avec d'autres travailleurs
        print("\n3. COMPARAISON AVEC D'AUTRES TRAVAILLEURS")
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
                unite,
                organizational_unit_id
            FROM workers 
            WHERE employer_id = (SELECT employer_id FROM workers WHERE LOWER(nom) LIKE '%jeanne%' LIMIT 1)
            ORDER BY id
            LIMIT 10
        """)
        
        other_workers = cursor.fetchall()
        
        print(f"Autres travailleurs du même employeur:")
        print()
        
        for worker in other_workers:
            is_jeanne = 'jeanne' in worker['nom'].lower() or 'jeanne' in worker['prenom'].lower()
            marker = "👉 JEANNE" if is_jeanne else ""
            
            print(f"  {worker['id']} - {worker['prenom']} {worker['nom']} {marker}")
            print(f"    Établissement: '{worker['etablissement']}' (Empty: {not worker['etablissement']})")
            print(f"    Département: '{worker['departement']}' (Empty: {not worker['departement']})")
            print(f"    Service: '{worker['service']}' (Empty: {not worker['service']})")
            print(f"    Unité: '{worker['unite']}' (Empty: {not worker['unite']})")
            print(f"    Org Unit ID: {worker['organizational_unit_id']}")
            print()
        
        # 4. Vérifier les structures organisationnelles disponibles
        print("\n4. STRUCTURES ORGANISATIONNELLES DISPONIBLES")
        print("-" * 80)
        
        jeanne = jeanne_workers[0]
        employer_id = jeanne['employer_id']
        
        cursor.execute("""
            SELECT 
                id,
                level,
                name,
                parent_id,
                is_active
            FROM organizational_nodes
            WHERE employer_id = %s
            ORDER BY level, name
        """, (employer_id,))
        
        org_nodes = cursor.fetchall()
        
        print(f"Structures organisationnelles pour l'employeur {employer_id}:")
        print()
        
        by_level = {}
        for node in org_nodes:
            level = node['level']
            if level not in by_level:
                by_level[level] = []
            by_level[level].append(node)
        
        for level in ['etablissement', 'departement', 'service', 'unite']:
            if level in by_level:
                print(f"  {level.upper()}:")
                for node in by_level[level]:
                    print(f"    - ID: {node['id']}, Nom: {node['name']}, Parent: {node['parent_id']}, Actif: {node['is_active']}")
                print()
        
        # 5. Diagnostic du problème
        print("\n5. DIAGNOSTIC DU PROBLÈME")
        print("-" * 80)
        
        issues = []
        
        # Vérifier si les champs sont vides ou NULL
        if not jeanne['etablissement'] or jeanne['etablissement'] == '':
            issues.append("❌ Le champ 'etablissement' est vide ou NULL")
        else:
            print(f"✅ Établissement défini: '{jeanne['etablissement']}'")
        
        if not jeanne['departement'] or jeanne['departement'] == '':
            issues.append("❌ Le champ 'departement' est vide ou NULL")
        else:
            print(f"✅ Département défini: '{jeanne['departement']}'")
        
        if not jeanne['service'] or jeanne['service'] == '':
            issues.append("❌ Le champ 'service' est vide ou NULL")
        else:
            print(f"✅ Service défini: '{jeanne['service']}'")
        
        if not jeanne['unite'] or jeanne['unite'] == '':
            issues.append("❌ Le champ 'unite' est vide ou NULL")
        else:
            print(f"✅ Unité définie: '{jeanne['unite']}'")
        
        if not jeanne['organizational_unit_id']:
            issues.append("⚠️  Le champ 'organizational_unit_id' est NULL (système hiérarchique non utilisé)")
        else:
            print(f"✅ Organizational Unit ID défini: {jeanne['organizational_unit_id']}")
        
        print()
        
        if issues:
            print("PROBLÈMES DÉTECTÉS:")
            for issue in issues:
                print(f"  {issue}")
            print()
            print("CAUSE PROBABLE:")
            print("  Le composant CascadingOrganizationalSelect affiche toutes les structures")
            print("  lorsque les valeurs sont vides/NULL car il n'a pas de sélection initiale.")
            print()
            print("SOLUTION:")
            print("  1. Assigner des valeurs valides aux champs organisationnels de Jeanne")
            print("  2. Ou modifier le composant pour gérer les valeurs vides différemment")
        else:
            print("✅ Aucun problème détecté avec les données de Jeanne")
            print("   Le problème pourrait être dans le composant frontend")
        
        # 6. Générer un script de correction
        print("\n6. SCRIPT DE CORRECTION SUGGÉRÉ")
        print("-" * 80)
        
        if issues:
            # Trouver des valeurs par défaut
            cursor.execute("""
                SELECT id, name 
                FROM organizational_nodes 
                WHERE employer_id = %s AND level = 'etablissement' AND is_active = true
                LIMIT 1
            """, (employer_id,))
            
            default_etab = cursor.fetchone()
            
            if default_etab:
                print(f"""
-- Script SQL pour corriger les données de Jeanne
UPDATE workers 
SET 
    etablissement = '{default_etab['id']}',
    departement = NULL,  -- À définir après sélection de l'établissement
    service = NULL,      -- À définir après sélection du département
    unite = NULL         -- À définir après sélection du service
WHERE id = {jeanne['id']};

-- OU utiliser le système hiérarchique (recommandé):
-- UPDATE workers 
-- SET organizational_unit_id = <ID_UNITE_APPROPRIEE>
-- WHERE id = {jeanne['id']};
""")
            else:
                print("❌ Aucune structure organisationnelle trouvée pour cet employeur")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 80)
        print("DIAGNOSTIC TERMINÉ")
        print("=" * 80)
        
    except psycopg2.Error as e:
        print(f"❌ Erreur de connexion à la base de données: {e}")
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_jeanne_data()
