#!/usr/bin/env python3
import sqlite3

with sqlite3.connect('siirh-backend/siirh.db') as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='trigger'")
    triggers = [row[0] for row in cursor.fetchall()]
    print("Triggers existants:", triggers)
    
    # Supprimer tous les triggers d'audit qui pourraient causer des problèmes
    for trigger in triggers:
        if 'organizational' in trigger.lower():
            try:
                cursor.execute(f"DROP TRIGGER IF EXISTS {trigger}")
                print(f"Trigger {trigger} supprimé")
            except Exception as e:
                print(f"Erreur suppression {trigger}: {e}")
    
    conn.commit()
    print("Nettoyage terminé")