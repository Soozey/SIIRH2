#!/usr/bin/env python3
"""
Vérifier les matricules dans la base de données
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'siirh-backend'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Configuration PostgreSQL
DATABASE_URL = "postgresql+psycopg2://postgres:tantely123@127.0.0.1:5432/db_siirh_app"

def check_matricules():
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        print("📋 MATRICULES DANS LA BASE DE DONNÉES")
        print("=" * 50)
        
        # Matricules dans workers
        workers = db.execute(text("""
            SELECT id, matricule, nom, prenom, employer_id 
            FROM workers 
            WHERE matricule IS NOT NULL 
            ORDER BY id
        """)).fetchall()
        
        print(f"\n👥 WORKERS AVEC MATRICULES ({len(workers)}):")
        for worker in workers:
            print(f"   {worker.matricule} - {worker.nom} {worker.prenom} (ID: {worker.id}, Employer: {worker.employer_id})")
        
        # Matricules dans resolver
        resolver_entries = db.execute(text("""
            SELECT matricule, full_name, worker_id, employer_id 
            FROM matricule_name_resolver 
            WHERE is_active = 1
            ORDER BY matricule
        """)).fetchall()
        
        print(f"\n🔍 RESOLVER ENTRIES ({len(resolver_entries)}):")
        for entry in resolver_entries:
            print(f"   {entry.matricule} - {entry.full_name} (Worker: {entry.worker_id}, Employer: {entry.employer_id})")
        
        # Affectations organisationnelles
        assignments = db.execute(text("""
            SELECT worker_matricule, employer_id, departement, service 
            FROM worker_organizational_assignments 
            WHERE is_active = 1
            ORDER BY worker_matricule
        """)).fetchall()
        
        print(f"\n🏢 AFFECTATIONS ORGANISATIONNELLES ({len(assignments)}):")
        for assignment in assignments:
            print(f"   {assignment.worker_matricule} - {assignment.departement}/{assignment.service} (Employer: {assignment.employer_id})")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_matricules()