#!/usr/bin/env python3
"""
Debug version of matricule analysis script
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'siirh-backend'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Configuration de la base de données
DATABASE_URL = "sqlite:///./siirh-backend/siirh.db"

def debug_analysis():
    """Version debug de l'analyse"""
    
    print("🔍 DEBUG: Démarrage de l'analyse...")
    
    try:
        print(f"🔗 DEBUG: Tentative de connexion à {DATABASE_URL}")
        engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=engine)
        session = Session()
        print("✅ DEBUG: Connexion établie")
        
        # Test simple: compter les salariés
        print("📊 DEBUG: Test de comptage des salariés...")
        count_query = text("SELECT COUNT(*) as total FROM workers")
        result = session.execute(count_query).fetchone()
        total_workers = result.total if result else 0
        print(f"✅ DEBUG: Total salariés trouvés: {total_workers}")
        
        if total_workers == 0:
            print("⚠️  DEBUG: Aucun salarié trouvé dans la base")
            return
        
        # Test: récupérer quelques salariés avec leurs matricules
        print("📋 DEBUG: Récupération d'échantillons de salariés...")
        sample_query = text("""
            SELECT id, matricule, nom, prenom 
            FROM workers 
            LIMIT 5
        """)
        
        workers = session.execute(sample_query).fetchall()
        print(f"✅ DEBUG: {len(workers)} salariés récupérés")
        
        for worker in workers:
            matricule_status = "✅ OUI" if worker.matricule and worker.matricule.strip() else "❌ NON"
            print(f"   - ID: {worker.id}, Matricule: {worker.matricule or 'VIDE'} ({matricule_status}), Nom: {worker.nom} {worker.prenom}")
        
        # Test: vérifier les matricules vides
        print("🔍 DEBUG: Vérification des matricules vides...")
        empty_matricule_query = text("""
            SELECT COUNT(*) as count_empty
            FROM workers 
            WHERE matricule IS NULL OR matricule = '' OR TRIM(matricule) = ''
        """)
        
        empty_result = session.execute(empty_matricule_query).fetchone()
        empty_count = empty_result.count_empty if empty_result else 0
        print(f"⚠️  DEBUG: Salariés sans matricule: {empty_count}")
        
        # Test: vérifier les doublons de noms
        print("👥 DEBUG: Vérification des homonymes...")
        duplicate_names_query = text("""
            SELECT nom, prenom, COUNT(*) as count_duplicates
            FROM workers 
            WHERE nom IS NOT NULL AND prenom IS NOT NULL
            GROUP BY nom, prenom
            HAVING COUNT(*) > 1
            LIMIT 3
        """)
        
        duplicates = session.execute(duplicate_names_query).fetchall()
        print(f"👥 DEBUG: Groupes d'homonymes trouvés: {len(duplicates)}")
        
        for dup in duplicates:
            print(f"   - {dup.nom} {dup.prenom}: {dup.count_duplicates} salariés")
        
        print("✅ DEBUG: Analyse de base terminée avec succès!")
        
    except Exception as e:
        print(f"❌ DEBUG: Erreur lors de l'analyse: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        if 'session' in locals():
            session.close()
            print("🔒 DEBUG: Session fermée")

if __name__ == "__main__":
    debug_analysis()