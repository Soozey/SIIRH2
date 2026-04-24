import psycopg2

DB_CONFIG = {
    'host': 'localhost',
    'database': 'siirh_db',
    'user': 'siirh_user',
    'password': 'siirh_password',
    'port': 5432
}

try:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'organizational_nodes');")
    exists = cursor.fetchone()[0]
    
    if exists:
        print("Table organizational_nodes existe deja")
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'organizational_nodes' ORDER BY ordinal_position;")
        columns = cursor.fetchall()
        print(f"Colonnes: {[col[0] for col in columns]}")
    else:
        print("Table organizational_nodes n'existe pas")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Erreur: {e}")