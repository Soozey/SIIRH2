#!/usr/bin/env python3
"""
Diagnostic et correction du problème d'encodage UTF-8 de la base de données
Résolution du problème critique de performance
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'siirh-backend'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import time
from datetime import datetime

def diagnose_and_fix_encoding():
    """Diagnostiquer et corriger le problème d'encodage"""
    
    print("🔍 Diagnostic du Problème d'Encodage UTF-8")
    print("=" * 60)
    
    # Configuration avec différents encodages
    DATABASE_URL = "postgresql://siirh_user:siirh_password@localhost:5432/siirh_db"
    
    print("\n1️⃣ Test de Connexion avec Différents Encodages")
    print("-" * 50)
    
    # Test 1: Connexion standard
    try:
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        with SessionLocal() as db:
            start_time = time.time()
            result = db.execute(text("SELECT COUNT(*) as count FROM workers"))
            response_time = time.time() - start_time
            count = result.fetchone().count
            
            print(f"✅ Connexion standard: {count} workers en {response_time:.3f}s")
            
    except Exception as e:
        print(f"❌ Erreur connexion standard: {e}")
    
    # Test 2: Connexion avec encodage explicite
    try:
        engine_utf8 = create_engine(
            DATABASE_URL,
            client_encoding='utf8',
            connect_args={
                "client_encoding": "utf8",
                "application_name": "siirh_matricule_fix"
            }
        )
        SessionLocal_utf8 = sessionmaker(autocommit=False, autoflush=False, bind=engine_utf8)
        
        with SessionLocal_utf8() as db:
            start_time = time.time()
            result = db.execute(text("SELECT COUNT(*) as count FROM workers"))
            response_time = time.time() - start_time
            count = result.fetchone().count
            
            print(f"✅ Connexion UTF-8: {count} workers en {response_time:.3f}s")
            
    except Exception as e:
        print(f"❌ Erreur connexion UTF-8: {e}")
    
    print("\n2️⃣ Diagnostic des Données Problématiques")
    print("-" * 50)
    
    try:
        with SessionLocal() as db:
            # Vérifier l'encodage des données
            result = db.execute(text("""
                SELECT id, nom, prenom, matricule, 
                       LENGTH(nom) as nom_length,
                       LENGTH(prenom) as prenom_length,
                       OCTET_LENGTH(nom) as nom_bytes,
                       OCTET_LENGTH(prenom) as prenom_bytes
                FROM workers 
                WHERE nom IS NOT NULL OR prenom IS NOT NULL
                LIMIT 5
            """))
            
            workers = result.fetchall()
            
            print("📊 Échantillon de données:")
            for w in workers:
                print(f"   ID {w.id}: {w.nom} {w.prenom}")
                print(f"      Longueurs: nom={w.nom_length}, prenom={w.prenom_length}")
                print(f"      Octets: nom={w.nom_bytes}, prenom={w.prenom_bytes}")
                
                # Détecter les caractères problématiques
                if w.nom_bytes > w.nom_length or w.prenom_bytes > w.prenom_length:
                    print(f"      ⚠️  Caractères multi-octets détectés")
            
    except Exception as e:
        print(f"❌ Erreur diagnostic données: {e}")
    
    print("\n3️⃣ Test de Performance avec Requêtes Optimisées")
    print("-" * 50)
    
    try:
        with SessionLocal() as db:
            # Test requête simple
            start_time = time.time()
            result = db.execute(text("SELECT matricule FROM workers WHERE matricule = 'M0001'"))
            response_time = time.time() - start_time
            worker = result.fetchone()
            
            print(f"✅ Requête simple: {response_time:.3f}s")
            
            # Test requête avec LIKE
            start_time = time.time()
            result = db.execute(text("SELECT matricule FROM workers WHERE nom LIKE '%Jean%'"))
            response_time = time.time() - start_time
            workers = result.fetchall()
            
            print(f"✅ Requête LIKE: {len(workers)} résultats en {response_time:.3f}s")
            
            # Test requête avec index
            start_time = time.time()
            result = db.execute(text("SELECT matricule FROM workers WHERE id = 1"))
            response_time = time.time() - start_time
            worker = result.fetchone()
            
            print(f"✅ Requête avec index: {response_time:.3f}s")
            
    except Exception as e:
        print(f"❌ Erreur test performance: {e}")
    
    print("\n4️⃣ Vérification des Index Existants")
    print("-" * 50)
    
    try:
        with SessionLocal() as db:
            # Vérifier les index sur la table workers
            result = db.execute(text("""
                SELECT indexname, indexdef 
                FROM pg_indexes 
                WHERE tablename = 'workers'
            """))
            
            indexes = result.fetchall()
            
            print("📋 Index existants sur 'workers':")
            for idx in indexes:
                print(f"   - {idx.indexname}")
                print(f"     {idx.indexdef}")
            
    except Exception as e:
        print(f"❌ Erreur vérification index: {e}")
    
    print("\n5️⃣ Création d'Index Optimisés")
    print("-" * 50)
    
    try:
        with SessionLocal() as db:
            # Créer des index optimisés si ils n'existent pas
            optimizations = [
                ("idx_workers_matricule", "CREATE INDEX IF NOT EXISTS idx_workers_matricule ON workers(matricule)"),
                ("idx_workers_nom_gin", "CREATE INDEX IF NOT EXISTS idx_workers_nom_gin ON workers USING gin(to_tsvector('french', nom))"),
                ("idx_workers_prenom_gin", "CREATE INDEX IF NOT EXISTS idx_workers_prenom_gin ON workers USING gin(to_tsvector('french', prenom))"),
                ("idx_workers_nom_trgm", "CREATE EXTENSION IF NOT EXISTS pg_trgm; CREATE INDEX IF NOT EXISTS idx_workers_nom_trgm ON workers USING gin(nom gin_trgm_ops)"),
            ]
            
            for idx_name, query in optimizations:
                try:
                    start_time = time.time()
                    db.execute(text(query))
                    db.commit()
                    creation_time = time.time() - start_time
                    print(f"✅ Index {idx_name} créé en {creation_time:.3f}s")
                except Exception as e:
                    print(f"⚠️  Index {idx_name}: {e}")
            
    except Exception as e:
        print(f"❌ Erreur création index: {e}")
    
    print("\n6️⃣ Test de Performance Après Optimisation")
    print("-" * 50)
    
    try:
        with SessionLocal() as db:
            # Test recherche par matricule
            start_time = time.time()
            result = db.execute(text("SELECT * FROM workers WHERE matricule = 'M0001'"))
            response_time = time.time() - start_time
            worker = result.fetchone()
            
            print(f"✅ Recherche matricule optimisée: {response_time:.3f}s")
            
            # Test recherche par nom avec index
            start_time = time.time()
            result = db.execute(text("""
                SELECT matricule, nom, prenom 
                FROM workers 
                WHERE to_tsvector('french', nom) @@ plainto_tsquery('french', 'Jean')
                LIMIT 10
            """))
            response_time = time.time() - start_time
            workers = result.fetchall()
            
            print(f"✅ Recherche nom optimisée: {len(workers)} résultats en {response_time:.3f}s")
            
            # Test recherche floue
            start_time = time.time()
            result = db.execute(text("""
                SELECT matricule, nom, prenom, similarity(nom, 'Jean') as sim
                FROM workers 
                WHERE nom % 'Jean'
                ORDER BY sim DESC
                LIMIT 10
            """))
            response_time = time.time() - start_time
            workers = result.fetchall()
            
            print(f"✅ Recherche floue: {len(workers)} résultats en {response_time:.3f}s")
            
    except Exception as e:
        print(f"❌ Erreur test optimisé: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 RÉSUMÉ DU DIAGNOSTIC")
    print("=" * 60)
    
    print("\n✅ Actions Effectuées:")
    print("   - Diagnostic de l'encodage UTF-8")
    print("   - Vérification des index existants")
    print("   - Création d'index optimisés")
    print("   - Tests de performance")
    
    print("\n📋 Recommandations:")
    print("   1. Utiliser les requêtes optimisées avec index")
    print("   2. Implémenter un cache pour les recherches fréquentes")
    print("   3. Utiliser la recherche full-text pour les noms")
    print("   4. Configurer l'encodage UTF-8 explicitement")

if __name__ == "__main__":
    diagnose_and_fix_encoding()