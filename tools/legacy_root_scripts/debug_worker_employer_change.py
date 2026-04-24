"""
Script de diagnostic - Changement d'employeur d'un salarié
Vérifie comment les données sont stockées et filtrées
"""
import psycopg2
from datetime import datetime

# Connexion à la base de données
conn = psycopg2.connect(
    host="127.0.0.1",
    port=5432,
    database="db_siirh_app",
    user="postgres",
    password="tantely123"
)
cur = conn.cursor()

print("=" * 80)
print("🔍 DIAGNOSTIC - CHANGEMENT D'EMPLOYEUR D'UN SALARIÉ")
print("=" * 80)
print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 1. Vérifier la structure de la table workers
print("1️⃣ STRUCTURE DE LA TABLE WORKERS")
print("-" * 80)
cur.execute("""
    SELECT column_name, data_type, is_nullable
    FROM information_schema.columns
    WHERE table_name = 'workers'
    AND column_name IN ('id', 'employer_id', 'nom', 'prenom', 'etablissement', 'departement', 'service', 'unite')
    ORDER BY ordinal_position
""")
columns = cur.fetchall()
for col in columns:
    print(f"  {col[0]:20} {col[1]:20} {'NULL' if col[2] == 'YES' else 'NOT NULL'}")

# 2. Lister tous les salariés avec leurs affectations
print("\n2️⃣ LISTE DES SALARIÉS ET LEURS AFFECTATIONS")
print("-" * 80)
cur.execute("""
    SELECT 
        w.id,
        w.employer_id,
        e.raison_sociale as employer_name,
        w.nom,
        w.prenom,
        w.etablissement,
        w.departement,
        w.service,
        w.unite
    FROM workers w
    LEFT JOIN employers e ON w.employer_id = e.id
    ORDER BY w.employer_id, w.nom
""")
workers = cur.fetchall()
print(f"  Total: {len(workers)} salariés\n")
for w in workers:
    print(f"  ID {w[0]:3} | Employer {w[1]} ({w[2]:20}) | {w[3]} {w[4]}")
    if w[5] or w[6] or w[7] or w[8]:
        print(f"         Org: Étab={w[5]}, Dép={w[6]}, Serv={w[7]}, Unité={w[8]}")

# 3. Vérifier les structures organisationnelles disponibles
print("\n3️⃣ STRUCTURES ORGANISATIONNELLES PAR EMPLOYEUR")
print("-" * 80)
cur.execute("""
    SELECT 
        employer_id,
        COUNT(*) as total_structures
    FROM hierarchical_organizational_nodes
    GROUP BY employer_id
    ORDER BY employer_id
""")
org_counts = cur.fetchall()
for emp_id, count in org_counts:
    cur.execute("SELECT raison_sociale FROM employers WHERE id = %s", (emp_id,))
    emp_name = cur.fetchone()[0]
    print(f"  Employer {emp_id} ({emp_name}): {count} structures")
    
    # Détail par niveau
    cur.execute("""
        SELECT level, COUNT(*) as count
        FROM hierarchical_organizational_nodes
        WHERE employer_id = %s
        GROUP BY level
        ORDER BY 
            CASE level
                WHEN 'etablissement' THEN 1
                WHEN 'departement' THEN 2
                WHEN 'service' THEN 3
                WHEN 'unite' THEN 4
            END
    """, (emp_id,))
    levels = cur.fetchall()
    for level, count in levels:
        print(f"    - {level}: {count}")

# 4. Vérifier le type de données dans les champs organisationnels des workers
print("\n4️⃣ TYPE DE DONNÉES DANS LES CHAMPS ORGANISATIONNELS")
print("-" * 80)
cur.execute("""
    SELECT 
        w.id,
        w.nom,
        w.etablissement,
        pg_typeof(w.etablissement) as etab_type,
        w.departement,
        pg_typeof(w.departement) as dep_type
    FROM workers w
    WHERE w.etablissement IS NOT NULL OR w.departement IS NOT NULL
    LIMIT 5
""")
type_samples = cur.fetchall()
if type_samples:
    print("  Échantillon de données:")
    for sample in type_samples:
        print(f"    {sample[1]}: établissement='{sample[2]}' (type: {sample[3]})")
else:
    print("  ⚠️  Aucun salarié avec affectation organisationnelle")

# 5. Simuler un changement d'employeur
print("\n5️⃣ SIMULATION - CHANGEMENT D'EMPLOYEUR")
print("-" * 80)
print("  Scénario: Un salarié de Karibo (ID 1) est transféré à Mandroso (ID 2)")
print("  Question: Les filtres organisationnels fonctionnent-ils après le transfert?")
print()

# Vérifier si un salarié de Karibo a des affectations organisationnelles
cur.execute("""
    SELECT id, nom, prenom, etablissement, departement
    FROM workers
    WHERE employer_id = 1
    AND (etablissement IS NOT NULL OR departement IS NOT NULL)
    LIMIT 1
""")
karibo_worker = cur.fetchone()

if karibo_worker:
    worker_id, nom, prenom, etab, dep = karibo_worker
    print(f"  Salarié trouvé: {nom} {prenom} (ID {worker_id})")
    print(f"  Affectation actuelle: Établissement='{etab}', Département='{dep}'")
    print()
    print("  ⚠️  PROBLÈME IDENTIFIÉ:")
    print("  Si ce salarié est transféré à Mandroso (employer_id = 2),")
    print("  les champs 'etablissement' et 'departement' contiennent encore")
    print("  les NOMS des structures de Karibo (ex: 'JICA', 'IT Department').")
    print()
    print("  Mais Mandroso n'a PAS ces structures!")
    print("  Le filtrage par établissement='JICA' ne retournera rien pour Mandroso.")
    print()
    print("  💡 SOLUTION:")
    print("  1. Utiliser les IDs des structures au lieu des noms")
    print("  2. Modifier l'endpoint /payroll/bulk-preview pour filtrer par ID")
    print("  3. Ajouter une jointure avec hierarchical_organizational_nodes")
else:
    print("  ℹ️  Aucun salarié de Karibo avec affectation organisationnelle")

# 6. Vérifier le format des filtres envoyés par le frontend
print("\n6️⃣ FORMAT DES FILTRES ENVOYÉS PAR LE FRONTEND")
print("-" * 80)
print("  Le modal OrganizationalFilterModalOptimized envoie:")
print("  - etablissement: ID (number) - ex: 40")
print("  - departement: ID (number) - ex: 41")
print("  - service: ID (number) - ex: 42")
print("  - unite: ID (number) - ex: 43")
print()
print("  Mais l'endpoint /payroll/bulk-preview filtre par:")
print("  - models.Worker.etablissement == etablissement (string)")
print("  - models.Worker.departement == departement (string)")
print()
print("  ❌ INCOMPATIBILITÉ: ID vs NOM")

print("\n" + "=" * 80)
print("📋 RÉSUMÉ DU PROBLÈME")
print("=" * 80)
print("1. Le modal envoie des IDs de structures (40, 41, 42, 43)")
print("2. L'endpoint filtre par NOMS de structures ('JICA', 'IT Department')")
print("3. Quand un salarié change d'employeur, ses champs organisationnels")
print("   contiennent encore les noms de l'ancien employeur")
print("4. Le filtrage ne fonctionne pas correctement")
print()
print("🔧 SOLUTION REQUISE:")
print("Modifier l'endpoint /payroll/bulk-preview pour:")
print("1. Accepter des IDs au lieu de noms")
print("2. Faire une jointure avec hierarchical_organizational_nodes")
print("3. Filtrer les salariés par les IDs de leurs structures")

cur.close()
conn.close()
