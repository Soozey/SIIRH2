#!/usr/bin/env python3
"""
Script pour vérifier les tables existantes dans la base de données
"""

import sqlite3
import os

def check_existing_tables():
    db_path = "siirh-backend/siirh.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Base de données non trouvée : {db_path}")
        return
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # Vérifier toutes les tables
        print("📊 Tables existantes :")
        cursor.execute("""
            SELECT name, type FROM sqlite_master 
            WHERE type IN ('table', 'view') 
            ORDER BY type, name
        """)
        
        for name, obj_type in cursor.fetchall():
            if 'organizational' in name.lower():
                print(f"   {obj_type}: {name}")
        
        # Vérifier spécifiquement organizational_paths
        cursor.execute("""
            SELECT name, type FROM sqlite_master 
            WHERE name LIKE '%organizational_paths%'
        """)
        
        print("\n🔍 Tables/vues organizational_paths :")
        results = cursor.fetchall()
        if results:
            for name, obj_type in results:
                print(f"   {obj_type}: {name}")
                
                # Si c'est une table, voir sa structure
                if obj_type == 'table':
                    cursor.execute(f"PRAGMA table_info({name})")
                    columns = cursor.fetchall()
                    print(f"     Colonnes: {len(columns)}")
                    for col in columns[:3]:  # Afficher les 3 premières colonnes
                        print(f"       - {col[1]} ({col[2]})")
        else:
            print("   Aucune table/vue organizational_paths trouvée")
        
        # Supprimer les tables problématiques
        print("\n🗑️ Suppression des tables existantes...")
        
        tables_to_drop = [
            "organizational_paths",
            "organizational_paths_materialized"
        ]
        
        for table in tables_to_drop:
            try:
                cursor.execute(f"DROP TABLE IF EXISTS {table}")
                cursor.execute(f"DROP VIEW IF EXISTS {table}")
                print(f"   ✅ {table} supprimé")
            except Exception as e:
                print(f"   ⚠️ Erreur suppression {table}: {e}")
        
        conn.commit()
        print("   ✅ Nettoyage terminé")

if __name__ == "__main__":
    check_existing_tables()