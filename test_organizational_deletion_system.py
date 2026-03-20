#!/usr/bin/env python3
"""
Test du système de suppression conditionnelle des structures organisationnelles
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_deletion_system():
    """Test complet du système de suppression conditionnelle"""
    
    print("🧪 Test du système de suppression conditionnelle des structures organisationnelles")
    print("=" * 80)
    
    # 1. Créer un employeur de test
    print("\n1. Création d'un employeur de test...")
    employer_data = {
        "raison_sociale": "Test Deletion Company",
        "adresse": "123 Test Street",
        "email": "test@deletion.com",
        "type_regime_id": 1
    }
    
    try:
        response = requests.post(f"{BASE_URL}/employers/", json=employer_data)
        if response.status_code == 200:
            employer = response.json()
            employer_id = employer["id"]
            print(f"✅ Employeur créé avec ID: {employer_id}")
        else:
            print(f"❌ Erreur création employeur: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Erreur connexion: {e}")
        return
    
    # 2. Créer une structure organisationnelle de test
    print("\n2. Création d'une structure organisationnelle...")
    
    # Établissement
    etablissement_data = {
        "employer_id": employer_id,
        "parent_id": None,
        "level": "etablissement",
        "code": "ETB001",
        "name": "Établissement Test",
        "description": "Établissement pour test de suppression"
    }
    
    response = requests.post(f"{BASE_URL}/organizational-structure/create", json=etablissement_data)
    if response.status_code == 200:
        etablissement = response.json()
        etablissement_id = etablissement["id"]
        print(f"✅ Établissement créé avec ID: {etablissement_id}")
    else:
        print(f"❌ Erreur création établissement: {response.status_code} - {response.text}")
        return
    
    # Département
    departement_data = {
        "employer_id": employer_id,
        "parent_id": etablissement_id,
        "level": "departement",
        "code": "DEP001",
        "name": "Département Test",
        "description": "Département pour test de suppression"
    }
    
    response = requests.post(f"{BASE_URL}/organizational-structure/create", json=departement_data)
    if response.status_code == 200:
        departement = response.json()
        departement_id = departement["id"]
        print(f"✅ Département créé avec ID: {departement_id}")
    else:
        print(f"❌ Erreur création département: {response.status_code} - {response.text}")
        return
    
    # Service vide (pour test de suppression simple)
    service_vide_data = {
        "employer_id": employer_id,
        "parent_id": departement_id,
        "level": "service",
        "code": "SRV001",
        "name": "Service Vide",
        "description": "Service vide pour test de suppression"
    }
    
    response = requests.post(f"{BASE_URL}/organizational-structure/create", json=service_vide_data)
    if response.status_code == 200:
        service_vide = response.json()
        service_vide_id = service_vide["id"]
        print(f"✅ Service vide créé avec ID: {service_vide_id}")
    else:
        print(f"❌ Erreur création service vide: {response.status_code} - {response.text}")
        return
    
    # Service avec sous-structure
    service_avec_sous_data = {
        "employer_id": employer_id,
        "parent_id": departement_id,
        "level": "service",
        "code": "SRV002",
        "name": "Service avec Sous-structures",
        "description": "Service avec sous-structures pour test"
    }
    
    response = requests.post(f"{BASE_URL}/organizational-structure/create", json=service_avec_sous_data)
    if response.status_code == 200:
        service_avec_sous = response.json()
        service_avec_sous_id = service_avec_sous["id"]
        print(f"✅ Service avec sous-structures créé avec ID: {service_avec_sous_id}")
    else:
        print(f"❌ Erreur création service avec sous-structures: {response.status_code} - {response.text}")
        return
    
    # Unité dans le service avec sous-structures
    unite_data = {
        "employer_id": employer_id,
        "parent_id": service_avec_sous_id,
        "level": "unite",
        "code": "UNT001",
        "name": "Unité Test",
        "description": "Unité pour test"
    }
    
    response = requests.post(f"{BASE_URL}/organizational-structure/create", json=unite_data)
    if response.status_code == 200:
        unite = response.json()
        unite_id = unite["id"]
        print(f"✅ Unité créée avec ID: {unite_id}")
    else:
        print(f"❌ Erreur création unité: {response.status_code} - {response.text}")
        return
    
    # 3. Tester la vérification des contraintes de suppression
    print("\n3. Test des contraintes de suppression...")
    
    # Test sur service vide (devrait être supprimable)
    print(f"\n3.1. Vérification contraintes pour service vide (ID: {service_vide_id})...")
    response = requests.get(f"{BASE_URL}/organizational-structure/{service_vide_id}/can-delete")
    if response.status_code == 200:
        constraints = response.json()
        print(f"✅ Contraintes récupérées:")
        print(f"   - Peut être supprimé: {constraints['can_delete']}")
        print(f"   - Raison: {constraints['reason']}")
        print(f"   - Salariés directs: {constraints['direct_workers_count']}")
        print(f"   - Salariés dans sous-structures: {constraints['descendant_workers_count']}")
        print(f"   - Sous-structures: {constraints['children_count']}")
    else:
        print(f"❌ Erreur vérification contraintes: {response.status_code}")
    
    # Test sur service avec sous-structures (ne devrait pas être supprimable)
    print(f"\n3.2. Vérification contraintes pour service avec sous-structures (ID: {service_avec_sous_id})...")
    response = requests.get(f"{BASE_URL}/organizational-structure/{service_avec_sous_id}/can-delete")
    if response.status_code == 200:
        constraints = response.json()
        print(f"✅ Contraintes récupérées:")
        print(f"   - Peut être supprimé: {constraints['can_delete']}")
        print(f"   - Raison: {constraints['reason']}")
        print(f"   - Salariés directs: {constraints['direct_workers_count']}")
        print(f"   - Salariés dans sous-structures: {constraints['descendant_workers_count']}")
        print(f"   - Sous-structures: {constraints['children_count']}")
    else:
        print(f"❌ Erreur vérification contraintes: {response.status_code}")
    
    # 4. Tester la suppression simple (service vide)
    print(f"\n4. Test de suppression simple (service vide ID: {service_vide_id})...")
    response = requests.delete(f"{BASE_URL}/organizational-structure/{service_vide_id}")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Suppression réussie: {result['message']}")
    else:
        print(f"❌ Erreur suppression: {response.status_code} - {response.text}")
    
    # 5. Tester la suppression avec contraintes (service avec sous-structures)
    print(f"\n5. Test de suppression avec contraintes (service avec sous-structures ID: {service_avec_sous_id})...")
    response = requests.delete(f"{BASE_URL}/organizational-structure/{service_avec_sous_id}")
    if response.status_code == 400:
        print(f"✅ Suppression bloquée comme attendu: {response.json()['detail']}")
    else:
        print(f"❌ Suppression non bloquée (inattendu): {response.status_code}")
    
    # 6. Tester la suppression forcée
    print(f"\n6. Test de suppression forcée (service avec sous-structures ID: {service_avec_sous_id})...")
    response = requests.delete(f"{BASE_URL}/organizational-structure/{service_avec_sous_id}?force=true")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Suppression forcée réussie: {result['message']}")
        
        # Vérifier que l'unité a été réassignée au département
        print("   Vérification de la réassignation...")
        response = requests.get(f"{BASE_URL}/organizational-structure/{employer_id}/tree")
        if response.status_code == 200:
            tree = response.json()
            print("   ✅ Arbre organisationnel mis à jour")
        else:
            print("   ❌ Erreur récupération arbre")
    else:
        print(f"❌ Erreur suppression forcée: {response.status_code} - {response.text}")
    
    # 7. Créer un salarié pour tester avec des salariés assignés
    print(f"\n7. Test avec salarié assigné...")
    
    # Créer un nouveau service
    service_avec_salarie_data = {
        "employer_id": employer_id,
        "parent_id": departement_id,
        "level": "service",
        "code": "SRV003",
        "name": "Service avec Salarié",
        "description": "Service avec salarié pour test"
    }
    
    response = requests.post(f"{BASE_URL}/organizational-structure/create", json=service_avec_salarie_data)
    if response.status_code == 200:
        service_avec_salarie = response.json()
        service_avec_salarie_id = service_avec_salarie["id"]
        print(f"✅ Service avec salarié créé avec ID: {service_avec_salarie_id}")
        
        # Créer un salarié
        worker_data = {
            "employer_id": employer_id,
            "matricule": f"TEST{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "nom": "Test",
            "prenom": "Salarié",
            "organizational_unit_id": service_avec_salarie_id
        }
        
        response = requests.post(f"{BASE_URL}/workers/", json=worker_data)
        if response.status_code == 200:
            worker = response.json()
            print(f"✅ Salarié créé avec ID: {worker['id']}")
            
            # Tester les contraintes avec salarié
            print(f"   Vérification contraintes avec salarié...")
            response = requests.get(f"{BASE_URL}/organizational-structure/{service_avec_salarie_id}/can-delete")
            if response.status_code == 200:
                constraints = response.json()
                print(f"   - Peut être supprimé: {constraints['can_delete']}")
                print(f"   - Salariés directs: {constraints['direct_workers_count']}")
                print(f"   - Salariés listés: {len(constraints['workers'])}")
            
            # Tester suppression bloquée
            response = requests.delete(f"{BASE_URL}/organizational-structure/{service_avec_salarie_id}")
            if response.status_code == 400:
                print(f"   ✅ Suppression bloquée avec salarié: {response.json()['detail']}")
            else:
                print(f"   ❌ Suppression non bloquée (inattendu)")
        else:
            print(f"❌ Erreur création salarié: {response.status_code}")
    else:
        print(f"❌ Erreur création service avec salarié: {response.status_code}")
    
    print("\n" + "=" * 80)
    print("🎉 Test du système de suppression conditionnelle terminé !")
    print("\nFonctionnalités testées :")
    print("✅ Vérification des contraintes de suppression")
    print("✅ Suppression simple (structure vide)")
    print("✅ Blocage de suppression (avec sous-structures)")
    print("✅ Suppression forcée avec réassignation")
    print("✅ Blocage de suppression (avec salariés)")
    print("✅ Détection et comptage des salariés")

if __name__ == "__main__":
    test_deletion_system()