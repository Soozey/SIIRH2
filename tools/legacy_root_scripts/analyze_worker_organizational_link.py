"""
Analyser le lien entre workers et organizational_nodes
"""
import psycopg2
from datetime import datetime

conn = psycopg2.connect(
    host="127.0.0.1",
    port=5432,
    database="db_siirh_app",
    user="postgres",
    password="tantely123"
)
cur = conn.cursor()

print("=" * 80)
print("🔍 ANALYSE - LIEN WORKERS <-> ORGANIZATIONAL_NODES")
print("=" * 80)
print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 1. Vérifier les salariés avec affectations
print("1️⃣ SALARIÉS AVEC AFFECTATIONS ORGANISATIONNELLES")
print("-" * 80)
cur.execute("""
    SELECT 
        w.id,
        w.employer_id,
        e.raison_sociale,
        w.nom,
        w.prenom,
        w.etablissement,
        w.departement,
        w.service,
        w.unite
    FROM workers w
    LEFT JOIN employers e ON w.employer_id = e.id
    WHERE w.etablissement IS NOT NULL 
       OR w.departement IS NOT NULL
       OR w.service IS NOT NULL
       OR w.unite IS NOT NULL
    ORDER BY w.employer_id, w.id
""")
workers = cur.fetchall()
print(f"Total: {len(workers)} salariés avec affectations\n")

for w in workers:
    print(f"Salarié ID {w[0]}: {w[3]} {w[4]}")
    print(f"  Employer: {w[1]} - {w[2]}")
    print(f"  Établissement: {w[5]}")
    print(f"  Département: {w[6]}")
    print(f"  Service: {w[7]}")
    print(f"  Unité: {w[8]}")
    
    # Vérifier si ces IDs existent dans organizational_nodes
    if w[5]:  # etablissement
        cur.execute("""
            SELECT id, name, level, employer_id
            FROM organizational_nodes
            WHERE id = %s
        """, (int(w[5]) if w[5].isdigit() else 0,))
        node = cur.fetchone()
        if node:
            print(f"    ✅ Établissement trouvé: {node[1]} (level={node[2]}, employer={node[3]})")
        else:
            print(f"    ❌ Établissement ID {w[5]} NON TROUVÉ dans organizational_nodes")
    
    if w[6]:  # departement
        cur.execute("""
            SELECT id, name, level, employer_id
            FROM organizational_nodes
            WHERE id = %s
        """, (int(w[6]) if w[6].isdigit() else 0,))
        node = cur.fetchone()
        if node:
            print(f"    ✅ Département trouvé: {node[1]} (level={node[2]}, employer={node[3]})")
        else:
            print(f"    ❌ Département ID {w[6]} NON TROUVÉ dans organizational_nodes")
    
    print()

# 2. Vérifier les structures par employeur
print("\n2️⃣ STRUCTURES ORGANISATIONNELLES PAR EMPLOYEUR")
print("-" * 80)
cur.execute("""
    SELECT 
        employer_id,
        level,
        COUNT(*) as count
    FROM organizational_nodes
    GROUP BY employer_id, level
    ORDER BY employer_id, 
        CASE level
            WHEN 'etablissement' THEN 1
            WHEN 'departement' THEN 2
            WHEN 'service' THEN 3
            WHEN 'unite' THEN 4
        END
""")
org_summary = cur.fetchall()

current_employer = None
for emp_id, level, count in org_summary:
    if emp_id != current_employer:
        if current_employer is not None:
            print()
        cur.execute("SELECT raison_sociale FROM employers WHERE id = %s", (emp_id,))
        emp_name = cur.fetchone()[0]
        print(f"Employer {emp_id} - {emp_name}:")
        current_employer = emp_id
    print(f"  - {level}: {count}")

# 3. Problème identifié
print("\n" + "=" * 80)
print("🐛 PROBLÈME IDENTIFIÉ")
print("=" * 80)
print("1. Les champs workers.etablissement, departement, etc. contiennent des IDs (string)")
print("2. Ces IDs correspondent à organizational_nodes.id")
print("3. Mais l'endpoint /payroll/bulk-preview reçoit des IDs du modal")
print("4. Et compare directement: models.Worker.etablissement == etablissement")
print()
print("✅ BONNE NOUVELLE: Le format est déjà compatible (ID vs ID)")
print("❌ PROBLÈME: Comparaison string vs int")
print()
print("🔧 SOLUTION:")
print("Modifier l'endpoint pour convertir les IDs en string avant comparaison:")
print("  if etablissement:")
print("      query = query.filter(models.Worker.etablissement == str(etablissement))")

cur.close()
conn.close()
