#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import psycopg2
import sys

DB_CONFIG = {
    'host': 'localhost',
    'database': 'siirh_db',
    'user': 'siirh_user',
    'password': 'siirh_password',
    'port': 5432,
    'client_encoding': 'utf8'
}

def create_organizational_table():
    """Crée la table organizational_nodes si elle n'existe pas"""
    
    create_table_sql = """
    -- Table principale pour la hiérarchie organisationnelle
    CREATE TABLE IF NOT EXISTS organizational_nodes (
        id SERIAL PRIMARY KEY,
        employer_id INTEGER NOT NULL REFERENCES employers(id) ON DELETE CASCADE,
        parent_id INTEGER REFERENCES organizational_nodes(id) ON DELETE CASCADE,
        level VARCHAR(20) NOT NULL CHECK (level IN ('etablissement', 'departement', 'service', 'unite')),
        name VARCHAR(255) NOT NULL,
        code VARCHAR(50),
        description TEXT,
        path TEXT,
        sort_order INTEGER DEFAULT 0,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_by INTEGER,
        updated_by INTEGER,
        
        -- Contraintes d'intégrité
        CONSTRAINT valid_hierarchy CHECK (
            (level = 'etablissement' AND parent_id IS NULL) OR 
            (level != 'etablissement' AND parent_id IS NOT NULL)
        ),
        CONSTRAINT unique_name_per_parent UNIQUE (employer_id, parent_id, name),
        CONSTRAINT no_self_reference CHECK (id != parent_id)
    );
    """
    
    create_indexes_sql = """
    -- Index pour les performances
    CREATE INDEX IF NOT EXISTS idx_organizational_nodes_employer ON organizational_nodes(employer_id);
    CREATE INDEX IF NOT EXISTS idx_organizational_nodes_parent ON organizational_nodes(parent_id);
    CREATE INDEX IF NOT EXISTS idx_organizational_nodes_level ON organizational_nodes(level);
    CREATE INDEX IF NOT EXISTS idx_organizational_nodes_path ON organizational_nodes(path);
    CREATE INDEX IF NOT EXISTS idx_organizational_nodes_active ON organizational_nodes(is_active);
    CREATE INDEX IF NOT EXISTS idx_organizational_nodes_hierarchy ON organizational_nodes(employer_id, parent_id, level);
    """
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("Création de la table organizational_nodes...")
        cursor.execute(create_table_sql)
        
        print("Création des index...")
        cursor.execute(create_indexes_sql)
        
        conn.commit()
        print("✅ Table organizational_nodes créée avec succès!")
        
        # Vérification
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'organizational_nodes' ORDER BY ordinal_position;")
        columns = cursor.fetchall()
        print(f"Colonnes créées: {[col[0] for col in columns]}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la création: {e}")
        return False

if __name__ == "__main__":
    success = create_organizational_table()
    sys.exit(0 if success else 1)