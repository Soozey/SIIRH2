#!/usr/bin/env python3
"""
Script pour créer la table organizational_nodes dans la base de données PostgreSQL
"""

import psycopg2
import sys
from datetime import datetime

# Configuration de la base de données
DB_CONFIG = {
    'host': 'localhost',
    'database': 'siirh_db',
    'user': 'siirh_user',
    'password': 'siirh_password',
    'port': 5432
}

def create_organizational_table():
    """Crée la table organizational_nodes avec toutes les contraintes"""
    
    sql_script = """
    -- Table principale pour la hiérarchie organisationnelle
    CREATE TABLE IF NOT EXISTS organizational_nodes (
        id SERIAL PRIMARY KEY,
        employer_id INTEGER NOT NULL REFERENCES employers(id) ON DELETE CASCADE,
        parent_id INTEGER REFERENCES organizational_nodes(id) ON DELETE CASCADE,
        level VARCHAR(20) NOT NULL CHECK (level IN ('etablissement', 'departement', 'service', 'unite')),
        name VARCHAR(255) NOT NULL,
        path TEXT, -- Chemin hiérarchique complet (ex: "Siège > RH > Paie")
        sort_order INTEGER DEFAULT 0,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        
        -- Contraintes d'intégrité hiérarchique
        CONSTRAINT chk_level_hierarchy CHECK (
            (level = 'etablissement' AND parent_id IS NULL) OR
            (level = 'departement' AND parent_id IS NOT NULL) OR
            (level = 'service' AND parent_id IS NOT NULL) OR
            (level = 'unite' AND parent_id IS NOT NULL)
        ),
        
        -- Contrainte d'unicité par employeur et niveau
        CONSTRAINT uq_employer_parent_name UNIQUE (employer_id, parent_id, name)
    );

    -- Index pour les performances
    CREATE INDEX IF NOT EXISTS idx_organizational_nodes_employer ON organizational_nodes(employer_id);
    CREATE INDEX IF NOT EXISTS idx_organizational_nodes_parent ON organizational_nodes(parent_id);
    CREATE INDEX IF NOT EXISTS idx_organizational_nodes_level ON organizational_nodes(level);
    CREATE INDEX IF NOT EXISTS idx_organizational_nodes_path ON organizational_nodes(path);
    CREATE INDEX IF NOT EXISTS idx_organizational_nodes_active ON organizational_nodes(is_active);
    """
    
    try:
        # Connexion à la base de données
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("🔄 Création de la table organizational_nodes...")
        
        # Exécuter le script
        cursor.execute(sql_script)
        conn.commit()
        
        print('✅ Table organizational_nodes créée avec succès')
        
        # Vérifier que la table existe
        cursor.execute("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'organizational_nodes'
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        print(f'✅ Table créée avec {len(columns)} colonnes:')
        for col in columns:
            print(f'  - {col[0]} ({col[1]}) - Nullable: {col[2]}')
        
        # Vérifier les contraintes
        cursor.execute("""
            SELECT constraint_name, constraint_type 
            FROM information_schema.table_constraints 
            WHERE table_name = 'organizational_nodes';
        """)
        
        constraints = cursor.fetchall()
        print(f'✅ Contraintes créées ({len(constraints)}):')
        for constraint in constraints:
            print(f'  - {constraint[0]} ({constraint[1]})')
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f'❌ Erreur lors de la création de la table: {e}')
        return False

if __name__ == "__main__":
    success = create_organizational_table()
    if success:
        print("\n🎉 Table organizational_nodes prête pour l'utilisation !")
    else:
        print("\n💥 Échec de la création de la table")
        sys.exit(1)