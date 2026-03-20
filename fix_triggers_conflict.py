#!/usr/bin/env python3
"""
Script pour corriger les conflits de triggers avec la vue organizational_paths
"""

import sqlite3
import os

def fix_triggers_conflict():
    """Supprime les triggers problématiques"""
    
    db_path = "siirh-backend/siirh.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Base de données non trouvée : {db_path}")
        return False
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            print("🔧 Suppression des triggers problématiques...")
            
            # Supprimer les triggers de organizational_paths qui causent des conflits
            triggers_to_remove = [
                "organizational_paths_insert_trigger",
                "organizational_paths_update_trigger", 
                "organizational_paths_delete_trigger"
            ]
            
            for trigger in triggers_to_remove:
                try:
                    cursor.execute(f"DROP TRIGGER IF EXISTS {trigger}")
                    print(f"   ✅ Trigger {trigger} supprimé")
                except Exception as e:
                    print(f"   ⚠️ Erreur suppression {trigger}: {e}")
            
            conn.commit()
            print("✅ Triggers problématiques supprimés")
            return True
            
    except Exception as e:
        print(f"❌ Erreur : {e}")
        return False

if __name__ == "__main__":
    fix_triggers_conflict()