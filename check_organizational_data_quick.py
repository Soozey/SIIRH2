"""
Vérification rapide des données organisationnelles
"""
import sqlite3

DB_PATH = "siirh-backend/siirh.db"

def check_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("📊 Données Organisationnelles\n")
    print("=" * 60)
    
    # Compter les nœuds par niveau
    cursor.execute("""
        SELECT level, COUNT(*) as count
        FROM organizational_nodes
        WHERE is_active = 1
        GROUP BY level
        ORDER BY level
    """)
    
    print("\n📈 Nœuds par niveau:")
    level_names = {1: "Établissements", 2: "Départements", 3: "Services", 4: "Unités"}
    for level, count in cursor.fetchall():
        print(f"   Niveau {level} ({level_names.get(level, 'Inconnu')}): {count}")
    
    # Lister tous les nœuds
    cursor.execute("""
        SELECT id, level, name, parent_id, is_active
        FROM organizational_nodes
        ORDER BY level, name
    """)
    
    print("\n📋 Tous les nœuds:")
    for row in cursor.fetchall():
        node_id, level, name, parent_id, is_active = row
        status = "✅" if is_active else "❌"
        parent_info = f"(parent: {parent_id})" if parent_id else "(racine)"
        print(f"   {status} [{level}] {name} {parent_info}")
    
    conn.close()
    print("\n" + "=" * 60)

if __name__ == "__main__":
    check_data()
