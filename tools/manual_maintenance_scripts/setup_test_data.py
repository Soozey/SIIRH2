#!/usr/bin/env python3
"""
Script pour initialiser la base de données avec des données de test
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'siirh-backend'))

from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from datetime import date
import json

# Configuration de la base de données
DATABASE_URL = "sqlite:///./siirh-backend/siirh.db"

def setup_test_data():
    """Initialise la base de données avec des données de test"""
    
    engine = create_engine(DATABASE_URL)
    
    # Importer les modèles après avoir configuré l'engine
    from app.models import Base, Employer, Worker
    
    # Créer les tables
    Base.metadata.create_all(bind=engine)
    
    session = Session(bind=engine)
    
    try:
        print("🏗️ Initialisation de la base de données...")
        
        # 1. Créer un employeur de test
        employer = session.query(Employer).first()
        if not employer:
            employer = Employer(
                raison_sociale="SIIRH Test Company",
                adresse="123 Rue de Test, Antananarivo",
                telephone="034 12 345 67",
                email="test@siirh.mg",
                activite="Développement logiciel",
                nif="123456789",
                stat="12345678901234",
                cnaps_num="CNaPS123456",
                sm_embauche=200000.0,
                etablissements=json.dumps(["Siège Social", "Agence Nord", "Agence Sud"]),
                departements=json.dumps(["Ressources Humaines", "Informatique", "Commercial", "Technique"]),
                services=json.dumps(["Recrutement", "Formation", "Développement", "Support", "Ventes", "Marketing"]),
                unites=json.dumps(["Équipe Alpha", "Équipe Beta", "Équipe Gamma"])
            )
            session.add(employer)
            session.flush()
            print(f"✅ Employeur créé : {employer.raison_sociale}")
        else:
            print(f"✅ Employeur existant : {employer.raison_sociale}")
        
        # 2. Créer des salariés de test avec différents cas de figure
        test_workers = [
            # Cas normaux avec matricules
            {
                "matricule": "E001AB001",
                "nom": "DUPONT",
                "prenom": "Jean",
                "etablissement": "Siège Social",
                "departement": "Ressources Humaines",
                "service": "Recrutement",
                "unite": "Équipe Alpha"
            },
            {
                "matricule": "E001CD002",
                "nom": "MARTIN",
                "prenom": "Marie",
                "etablissement": "Siège Social",
                "departement": "Informatique",
                "service": "Développement",
                "unite": "Équipe Beta"
            },
            {
                "matricule": "E001EF003",
                "nom": "BERNARD",
                "prenom": "Pierre",
                "etablissement": "Agence Nord",
                "departement": "Commercial",
                "service": "Ventes",
                "unite": None
            },
            # Cas problématiques : sans matricule
            {
                "matricule": None,
                "nom": "DURAND",
                "prenom": "Sophie",
                "etablissement": "Agence Sud",
                "departement": "Technique",
                "service": "Support",
                "unite": None
            },
            {
                "matricule": "",
                "nom": "MOREAU",
                "prenom": "Luc",
                "etablissement": "Siège Social",
                "departement": "Informatique",
                "service": "Développement",
                "unite": "Équipe Gamma"
            },
            # Cas d'homonymes
            {
                "matricule": "E001GH004",
                "nom": "MARTIN",
                "prenom": "Marie",  # Homonyme
                "etablissement": "Agence Nord",
                "departement": "Commercial",
                "service": "Marketing",
                "unite": None
            },
            {
                "matricule": "E001IJ005",
                "nom": "PETIT",
                "prenom": "Paul",
                "etablissement": "Siège Social",
                "departement": "Ressources Humaines",
                "service": "Formation",
                "unite": None
            },
            # Matricule problématique (trop court)
            {
                "matricule": "AB",
                "nom": "ROBERT",
                "prenom": "Claire",
                "etablissement": "Agence Sud",
                "departement": "Technique",
                "service": None,
                "unite": None
            }
        ]
        
        created_count = 0
        
        for worker_data in test_workers:
            # Vérifier si le salarié existe déjà
            existing = None
            if worker_data["matricule"]:
                existing = session.query(Worker).filter(Worker.matricule == worker_data["matricule"]).first()
            
            if existing:
                print(f"⚠️ Salarié {worker_data['matricule']} existe déjà")
                continue
            
            # Créer le salarié
            worker = Worker(
                employer_id=employer.id,
                matricule=worker_data["matricule"],
                nom=worker_data["nom"],
                prenom=worker_data["prenom"],
                etablissement=worker_data["etablissement"],
                departement=worker_data["departement"],
                service=worker_data["service"],
                unite=worker_data["unite"],
                poste=f"Poste {worker_data['nom']}",
                date_embauche=date.today(),
                salaire_base=2000000.0,
                vhm=173.33
            )
            
            session.add(worker)
            created_count += 1
            matricule_display = worker_data["matricule"] or "SANS_MATRICULE"
            print(f"✅ Salarié créé : {matricule_display} - {worker_data['nom']} {worker_data['prenom']}")
        
        session.commit()
        
        # Afficher un résumé
        total_workers = session.query(Worker).count()
        print(f"\n📊 RÉSUMÉ")
        print(f"   Salariés créés : {created_count}")
        print(f"   Total salariés : {total_workers}")
        print(f"   Employeur : {employer.raison_sociale}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation : {e}")
        session.rollback()
        return False
    finally:
        session.close()

if __name__ == "__main__":
    print("🚀 Initialisation des données de test pour l'analyse matricule")
    print("=" * 60)
    
    success = setup_test_data()
    
    if success:
        print("\n✅ Données de test créées avec succès !")
        print("📋 Vous pouvez maintenant exécuter l'analyse :")
        print("   python analyze_matricule_migration_data.py")
    else:
        print("\n❌ Échec de l'initialisation !")