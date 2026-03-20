#!/usr/bin/env python3
"""
Vérifier la structure de la table worker_organizational_assignments
"""

import sqlite3

def check_table_structure():
    """Vérifier la structure de la table"""
    
    conn = sqlite3.connect("siirh-backend/siirh.db")
    cursor = conn.cursor()
    
    try:
        # Récupérer le schéma de la table
        cursor.execute("""
            SELECT sql FROM sqlite_master 
            WHERE type='table' AND name='worker_organizational_assignments'
        """)
        
        schema = cursor.fetchone()
        if schema:
            print("📋 SCHÉMA DE LA TABLE worker_organizational_assignments:")
            print("=" * 60)
            print(schema[0])
            print()
        
        # Récupérer les index
        cursor.execute("""
            SELECT name, sql FROM sqlite_master 
            WHERE type='index' AND tbl_name='worker_organizational_assignments'
        """)
        
        indexes = cursor.fetchall()
        if indexes:
            print("🔍 INDEX SUR LA TABLE:")
            print("=" * 30)
            for idx in indexes:
                print(f"- {idx[0]}: {idx[1]}")
            print()
        
        # Vérifier les données existantes
        cursor.execute("""
            SELECT COUNT(*) as total,
                   COUNT(DISTINCT worker_matricule) as unique_workers,
                   COUNT(DISTINCT employer_id) as unique_employers
            FROM worker_organizational_assignments
        """)
        
        stats = cursor.fetchone()
        print("📊 STATISTIQUES DES DONNÉES:")
        print("=" * 30)
        print(f"Total des affectations: {stats[0]}")
        print(f"Workers uniques: {stats[1]}")
        print(f"Employeurs uniques: {stats[2]}")
        
        # Vérifier les contraintes d'unicité
        cursor.execute("""
            SELECT worker_matricule, employer_id, effective_date, COUNT(*) as count
            FROM worker_organizational_assignments
            GROUP BY worker_matricule, employer_id, effective_date
            HAVING COUNT(*) > 1
        """)
        
        duplicates = cursor.fetchall()
        if duplicates:
            print("\n⚠️  DOUBLONS DÉTECTÉS:")
            for dup in duplicates:
                print(f"- {dup[0]} / {dup[1]} / {dup[2]}: {dup[3]} occurrences")
        else:
            print("\n✅ Aucun doublon détecté")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    finally:
        conn.close()

if __name__ == "__main__":
    check_table_structure()