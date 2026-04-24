#!/usr/bin/env python3
"""
Test de la correction du système de filtrage organisationnel
Vérifie que les nouvelles structures hiérarchiques sont utilisées
"""

import requests
import json

BACKEND_URL = "http://localhost:8000"

def test_new_hierarchical_endpoint():
    """Test du nouvel endpoint hiérarchique"""
    print("🔍 Test du Nouvel Endpoint Hiérarchique")
    print("=" * 50)
    
    try:
        # Récupérer les employeurs
        response = requests.get(f"{BACKEND_URL}/employers")
        if response.status_code != 200:
            print("❌ Impossible de récupérer les employeurs")
            return False
        
        employers = response.json()
        if not employers:
            print("⚠️ Aucun employeur trouvé")
            return False
        
        employer = employers[0]
        employer_id = employer['id']
        employer_name = employer.get('raison_sociale', f'Employeur {employer_id}')
        
        print(f"📋 Test pour: {employer_name} (ID: {employer_id})")
        
        # Test du nouvel endpoint hiérarchique
        response = requests.get(f"{BACKEND_URL}/employers/{employer_id}/organizational-data/hierarchical")
        
        if response.status_code == 200:
            hierarchical_data = response.json()
            print("✅ Nouvel endpoint hiérarchique fonctionne:")
            print(f"   - Établissements: {hierarchical_data.get('etablissements', [])}")
            print(f"   - Départements: {hierarchical_data.get('departements', [])}")
            print(f"   - Services: {hierarchical_data.get('services', [])}")
            print(f"   - Unités: {hierarchical_data.get('unites', [])}")
            
            # Vérifier qu'il n'y a pas de valeurs numériques
            all_values = (hierarchical_data.get('etablissements', []) + 
                         hierarchical_data.get('departements', []) + 
                         hierarchical_data.get('services', []) + 
                         hierarchical_data.get('unites', []))
            
            numeric_values = [v for v in all_values if str(v).isdigit()]
            
            if numeric_values:
                print(f"⚠️ Valeurs numériques trouvées: {numeric_values}")
                print("   Cela indique que les structures hiérarchiques contiennent encore des IDs")
            else:
                print("✅ Aucune valeur numérique - Les noms sont corrects!")
            
            return len(all_values) > 0 and len(numeric_values) == 0
        else:
            print(f"❌ Erreur endpoint hiérarchique: {response.status_code}")
            return False
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_frontend_integration():
    """Test de l'intégration frontend"""
    print("\n🔍 Test de l'Intégration Frontend")
    print("=" * 50)
    
    try:
        # Test que le composant OrganizationalFilterModal compile
        response = requests.get("http://localhost:5173/src/components/OrganizationalFilterModal.tsx", timeout=5)
        
        if response.status_code == 200:
            print("✅ OrganizationalFilterModal compile correctement")
            return True
        elif response.status_code == 500:
            print("❌ Erreur compilation OrganizationalFilterModal")
            return False
        else:
            print(f"⚠️ Status inattendu: {response.status_code}")
            return True
            
    except requests.exceptions.ConnectionError:
        print("❌ Frontend non accessible")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def create_test_structures():
    """Crée des structures de test si elles n'existent pas"""
    print("\n🏗️ Création de Structures de Test")
    print("=" * 50)
    
    try:
        # Récupérer les employeurs
        response = requests.get(f"{BACKEND_URL}/employers")
        if response.status_code != 200:
            print("❌ Impossible de récupérer les employeurs")
            return False
        
        employers = response.json()
        if not employers:
            print("⚠️ Aucun employeur trouvé")
            return False
        
        employer_id = employers[0]['id']
        
        # Vérifier s'il y a déjà des structures
        response = requests.get(f"{BACKEND_URL}/organizational-structure/{employer_id}/tree")
        if response.status_code == 200:
            tree_data = response.json()
            if tree_data.get('tree') and len(tree_data['tree']) > 0:
                print("✅ Des structures hiérarchiques existent déjà")
                return True
        
        # Créer des structures de test
        print("📋 Création de structures de test...")
        
        # 1. Créer un établissement
        etablissement_data = {
            "employer_id": employer_id,
            "level": "etablissement",
            "name": "Siège Social",
            "code": "SIEGE",
            "parent_id": None,
            "description": "Établissement principal"
        }
        
        response = requests.post(f"{BACKEND_URL}/organizational-structure/create", json=etablissement_data)
        if response.status_code == 200:
            etablissement = response.json()
            print(f"✅ Établissement créé: {etablissement['name']}")
            
            # 2. Créer un département
            departement_data = {
                "employer_id": employer_id,
                "level": "departement",
                "name": "Direction Générale",
                "code": "DG",
                "parent_id": etablissement['id'],
                "description": "Direction générale de l'entreprise"
            }
            
            response = requests.post(f"{BACKEND_URL}/organizational-structure/create", json=departement_data)
            if response.status_code == 200:
                departement = response.json()
                print(f"✅ Département créé: {departement['name']}")
                
                # 3. Créer un service
                service_data = {
                    "employer_id": employer_id,
                    "level": "service",
                    "name": "Service Ressources Humaines",
                    "code": "RH",
                    "parent_id": departement['id'],
                    "description": "Service de gestion des ressources humaines"
                }
                
                response = requests.post(f"{BACKEND_URL}/organizational-structure/create", json=service_data)
                if response.status_code == 200:
                    service = response.json()
                    print(f"✅ Service créé: {service['name']}")
                    return True
        
        print("❌ Erreur lors de la création des structures")
        return False
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def main():
    """Fonction principale"""
    print("🚀 Test de la Correction du Filtrage Organisationnel")
    print("=" * 60)
    
    # 1. Créer des structures de test si nécessaire
    structures_ok = create_test_structures()
    
    # 2. Tester le nouvel endpoint
    endpoint_ok = test_new_hierarchical_endpoint()
    
    # 3. Tester l'intégration frontend
    frontend_ok = test_frontend_integration()
    
    # Résumé
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DES TESTS")
    print(f"Structures de test: {'✅ OK' if structures_ok else '❌ ERREUR'}")
    print(f"Endpoint hiérarchique: {'✅ OK' if endpoint_ok else '❌ ERREUR'}")
    print(f"Frontend: {'✅ OK' if frontend_ok else '❌ ERREUR'}")
    
    if structures_ok and endpoint_ok and frontend_ok:
        print("\n🎉 CORRECTION RÉUSSIE!")
        print("\n📋 MAINTENANT VOUS DEVRIEZ VOIR:")
        print("1. Des noms réels dans les filtres (ex: 'Siège Social', 'Direction Générale')")
        print("2. Plus de valeurs numériques comme '27'")
        print("3. Un filtrage fonctionnel avec les vraies structures")
        print("\n🔧 POUR TESTER:")
        print("1. Allez sur /payroll")
        print("2. Cliquez sur 'Imprimer tous les bulletins'")
        print("3. Vérifiez que les filtres montrent les vrais noms")
    else:
        print("\n❌ CERTAINS TESTS ONT ÉCHOUÉ")
        if not structures_ok:
            print("- Créez des structures hiérarchiques via la gestion hiérarchique")
        if not endpoint_ok:
            print("- Vérifiez que le backend est redémarré")
        if not frontend_ok:
            print("- Vérifiez que le frontend compile correctement")

if __name__ == "__main__":
    main()