"""
Vérifier quelles tables existent pour les structures organisationnelles
"""
import psycopg2

conn = psycopg2.connect(
    host="127.0.0.1",
    port=5432,
    database="db_siirh_app",
    user="postgres",
    password="tantely123"
)
cur = conn.cursor()

print("Tables contenant 'organizational':")
cur.execute("""
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'public'
    AND table_name LIKE '%organization%'
    ORDER BY table_name
""")
tables = cur.fetchall()
for table in tables:
    print(f"  - {table[0]}")
    
    # Compter les enregistrements
    cur.execute(f"SELECT COUNT(*) FROM {table[0]}")
    count = cur.fetchone()[0]
    print(f"    ({count} enregistrements)")

cur.close()
conn.close()
