"""
Script de diagnostic pour vérifier pourquoi la création ne s'affiche pas
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

def debug_creation_display():
    """Diagnostiquer le problème d'affichage après création"""
    print("=" * 80)
    print("DIAGNOSTIC DU PROBLÈME D'AFFICHAGE APRÈS CRÉATION")
    print("=" * 80)
    
    # 1. Récupérer un employeur
    print("\n1️⃣ Récupération d'un employeur...")
    try:
        response = requests.get(f"{BASE_URL}/employers", timeout=5)
        response.raise_for_status()
        employers = response.json()
        
        if not employers:
            print("   ⚠️  Aucun employeur")
            return
        
        employer_id = employers[0]['id']
        print(f"   ✓ Employeur ID: {employer_id}")
    except Exception as e:
        print(f"   ✗ Erreur: {e}")
        return
    
    # 2. Vérifier l'arbre AVANT création
    print(f"\n2️⃣ Vérification de l'arbre AVANT création...")
    try:
        response = requests.get(
            f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/tree",
            timeout=5
        )
        print(f"   Status code: {response.status_code}")
        
        if response.status_code == 200:
            tree_before = response.json()
            print(f"   ✓ Arbre récupéré:")
            print(f"      Total: {tree_before.get('total_units', 0)} structures")
            print(f"      Racines: {len(tree_before.get('tree', []))} établissements")
        else:
            print(f"   ⚠️  Status: {response.status_code}")
            print(f"      Réponse: {response.text}")
    except Exception as e:
        print(f"   ✗ Erreur: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"      Détails: {e.response.text}")
    
    # 3. Créer une structure
    print(f"\n3️⃣ Création d'une nouvelle structure...")
    timestamp = datetime.now().strftime('%H%M%S')
    
    try:
        response = requests.post(
            f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/nodes",
            json={
                "name": f"Test Display {timestamp}",
                "code": f"DISP{timestamp}",
                "level": "etablissement",
                "parent_id": None,
                "description": "Test affichage"
            },
            timeout=5
        )
        print(f"   Status code: {response.status_code}")
        response.raise_for_status()
        node = response.json()
        node_id = node['id']
        print(f"   ✓ Structure créée:")
        print(f"      ID: {node_id}")
        print(f"      Nom: {node['name']}")
        print(f"      Level: {node['level']}")
        print(f"      Active: {node.get('is_active', 'N/A')}")
    except Exception as e:
        print(f"   ✗ Erreur création: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"      Status: {e.response.status_code}")
            print(f"      Détails: {e.response.text}")
        return
    
    # 4. Vérifier l'arbre APRÈS création
    print(f"\n4️⃣ Vérification de l'arbre APRÈS création...")
    try:
        response = requests.get(
            f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/tree",
            timeout=5
        )
        print(f"   Status code: {response.status_code}")
        
        if response.status_code == 200:
            tree_after = response.json()
            print(f"   ✓ Arbre récupéré:")
            print(f"      Total: {tree_after.get('total_units', 0)} structures")
            print(f"      Racines: {len(tree_after.get('tree', []))} établissements")
            
            # Chercher notre structure
            found = False
            for root in tree_after.get('tree', []):
                if root['id'] == node_id:
                    found = True
                    print(f"   ✓ Structure trouvée dans l'arbre:")
                    print(f"      {json.dumps(root, indent=6)}")
                    break
            
            if not found:
                print(f"   ⚠️  Structure NON trouvée dans l'arbre!")
                print(f"      Structures présentes:")
                for root in tree_after.get('tree', []):
                    print(f"        - ID {root['id']}: {root['name']}")
        else:
            print(f"   ⚠️  Status: {response.status_code}")
            print(f"      Réponse: {response.text}")
    except Exception as e:
        print(f"   ✗ Erreur: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"      Détails: {e.response.text}")
    
    # 5. Vérifier directement dans la base
    print(f"\n5️⃣ Vérification directe du nœud créé...")
    try:
        response = requests.get(
            f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/nodes/{node_id}",
            timeout=5
        )
        print(f"   Status code: {response.status_code}")
        
        if response.status_code == 200:
            node_data = response.json()
            print(f"   ✓ Nœud trouvé:")
            print(f"      {json.dumps(node_data, indent=6)}")
        elif response.status_code == 404:
            print(f"   ⚠️  Nœud NON trouvé (404)")
        else:
            print(f"   ⚠️  Status: {response.status_code}")
            print(f"      Réponse: {response.text}")
    except Exception as e:
        print(f"   ✗ Erreur: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"      Détails: {e.response.text}")
    
    # 6. Vérifier les options en cascade
    print(f"\n6️⃣ Vérification des options en cascade...")
    try:
        response = requests.get(
            f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/cascading-options",
            timeout=5
        )
        print(f"   Status code: {response.status_code}")
        
        if response.status_code == 200:
            options = response.json()
            print(f"   ✓ Options récupérées: {len(options)} établissements")
            
            found = False
            for option in options:
                if option['id'] == node_id:
                    found = True
                    print(f"   ✓ Structure trouvée dans les options:")
                    print(f"      {json.dumps(option, indent=6)}")
                    break
            
            if not found:
                print(f"   ⚠️  Structure NON trouvée dans les options!")
                print(f"      Options disponibles:")
                for option in options:
                    print(f"        - ID {option['id']}: {option['name']}")
        else:
            print(f"   ⚠️  Status: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Erreur: {e}")
    
    # 7. Nettoyer
    print(f"\n7️⃣ Nettoyage...")
    try:
        response = requests.delete(
            f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/nodes/{node_id}",
            params={'force': False},
            timeout=5
        )
        if response.status_code == 200:
            print(f"   ✓ Structure supprimée")
        else:
            print(f"   ⚠️  Suppression: {response.status_code}")
    except Exception as e:
        print(f"   ⚠️  Erreur nettoyage: {e}")
    
    print("\n" + "=" * 80)
    print("FIN DU DIAGNOSTIC")
    print("=" * 80)

if __name__ == "__main__":
    debug_creation_display()
