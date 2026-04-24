#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_hierarchical_api():
    """Test des endpoints de l'API hiérarchique"""
    
    try:
        # Test 1: Récupérer l'arbre hiérarchique (vide pour l'instant)
        print("Test 1: GET /employers/1/hierarchical-organization/tree")
        response = requests.get(f"{BASE_URL}/employers/1/hierarchical-organization/tree")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Arbre récupéré: {len(data.get('nodes', []))} nœuds")
        else:
            print(f"❌ Erreur {response.status_code}: {response.text}")
            return False
        
        # Test 2: Récupérer les options en cascade (établissements)
        print("\nTest 2: GET /employers/1/hierarchical-organization/cascading-options")
        response = requests.get(f"{BASE_URL}/employers/1/hierarchical-organization/cascading-options")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Options cascade récupérées: {len(data)} options")
        else:
            print(f"❌ Erreur {response.status_code}: {response.text}")
            return False
        
        # Test 3: Créer un établissement
        print("\nTest 3: POST /employers/1/hierarchical-organization/nodes (Établissement)")
        etablissement_data = {
            "parent_id": None,
            "level": "etablissement",
            "name": "Siège Social",
            "code": "SIEGE",
            "description": "Établissement principal"
        }
        
        response = requests.post(
            f"{BASE_URL}/employers/1/hierarchical-organization/nodes",
            json=etablissement_data
        )
        
        if response.status_code == 200:
            etablissement = response.json()
            etablissement_id = etablissement["id"]
            print(f"✅ Établissement créé: {etablissement['name']} (ID: {etablissement_id})")
        else:
            print(f"❌ Erreur {response.status_code}: {response.text}")
            return False
        
        # Test 4: Créer un département
        print("\nTest 4: POST /employers/1/hierarchical-organization/nodes (Département)")
        departement_data = {
            "parent_id": etablissement_id,
            "level": "departement",
            "name": "Ressources Humaines",
            "code": "RH",
            "description": "Département des ressources humaines"
        }
        
        response = requests.post(
            f"{BASE_URL}/employers/1/hierarchical-organization/nodes",
            json=departement_data
        )
        
        if response.status_code == 200:
            departement = response.json()
            departement_id = departement["id"]
            print(f"✅ Département créé: {departement['name']} (ID: {departement_id})")
        else:
            print(f"❌ Erreur {response.status_code}: {response.text}")
            return False
        
        # Test 5: Vérifier l'arbre hiérarchique mis à jour
        print("\nTest 5: Vérification de l'arbre hiérarchique")
        response = requests.get(f"{BASE_URL}/employers/1/hierarchical-organization/tree")
        
        if response.status_code == 200:
            data = response.json()
            nodes = data.get('nodes', [])
            print(f"✅ Arbre mis à jour: {len(nodes)} nœuds")
            
            # Afficher la structure
            for node in nodes:
                print(f"  - {node['level']}: {node['name']} (ID: {node['id']}, Parent: {node.get('parent_id', 'None')})")
        else:
            print(f"❌ Erreur {response.status_code}: {response.text}")
            return False
        
        # Test 6: Tester le filtrage en cascade
        print("\nTest 6: Filtrage en cascade - départements de l'établissement")
        response = requests.get(
            f"{BASE_URL}/employers/1/hierarchical-organization/cascading-options",
            params={"parent_id": etablissement_id}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Départements trouvés: {len(data)} options")
            for option in data:
                print(f"  - {option['name']} (ID: {option['id']})")
        else:
            print(f"❌ Erreur {response.status_code}: {response.text}")
            return False
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter au serveur. Assurez-vous que le backend est démarré sur le port 8000.")
        return False
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Test de l'API hiérarchique organisationnelle")
    print("=" * 50)
    
    success = test_hierarchical_api()
    
    print("\n" + "=" * 50)
    print(f"{'✅ Tous les tests réussis!' if success else '❌ Certains tests ont échoué'}")
    
    sys.exit(0 if success else 1)