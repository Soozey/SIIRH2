"""
Script de diagnostic pour identifier le problème de suppression
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

def debug_deletion():
    """Diagnostiquer le problème de suppression"""
    print("=" * 80)
    print("DIAGNOSTIC DU PROBLÈME DE SUPPRESSION")
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
    
    # 2. Créer une structure de test simple
    print("\n2️⃣ Création d'une structure de test...")
    timestamp = datetime.now().strftime('%H%M%S')
    
    try:
        response = requests.post(
            f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/nodes",
            json={
                "name": f"Test Delete {timestamp}",
                "code": f"DEL{timestamp}",
                "level": "etablissement",
                "parent_id": None,
                "description": "Test suppression"
            },
            timeout=5
        )
        response.raise_for_status()
        node = response.json()
        node_id = node['id']
        print(f"   ✓ Structure créée (ID: {node_id})")
    except Exception as e:
        print(f"   ✗ Erreur création: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"      Détails: {e.response.text}")
        return
    
    # 3. Vérifier les infos de suppression
    print(f"\n3️⃣ Vérification des infos de suppression...")
    try:
        response = requests.get(
            f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/nodes/{node_id}/deletion-info",
            timeout=5
        )
        print(f"   Status code: {response.status_code}")
        response.raise_for_status()
        deletion_info = response.json()
        
        print(f"   ✓ Infos récupérées:")
        print(f"      {json.dumps(deletion_info, indent=6)}")
    except Exception as e:
        print(f"   ✗ Erreur: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"      Status: {e.response.status_code}")
            print(f"      Détails: {e.response.text}")
    
    # 4. Tenter la suppression
    print(f"\n4️⃣ Tentative de suppression (force=False)...")
    try:
        response = requests.delete(
            f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/nodes/{node_id}",
            params={'force': False},
            timeout=10
        )
        print(f"   Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✓ Suppression réussie!")
            print(f"      {json.dumps(result, indent=6)}")
        else:
            print(f"   ⚠️  Status inattendu: {response.status_code}")
            print(f"      Réponse: {response.text}")
            
    except requests.exceptions.Timeout:
        print(f"   ✗ TIMEOUT - La requête a pris plus de 10 secondes!")
        print(f"      Le backend ne répond pas")
    except Exception as e:
        print(f"   ✗ Erreur: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"      Status: {e.response.status_code}")
            print(f"      Détails: {e.response.text}")
    
    # 5. Vérifier si la structure existe toujours
    print(f"\n5️⃣ Vérification de l'existence de la structure...")
    try:
        response = requests.get(
            f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/nodes/{node_id}",
            timeout=5
        )
        if response.status_code == 200:
            print(f"   ⚠️  La structure existe toujours")
        elif response.status_code == 404:
            print(f"   ✓ La structure a été supprimée")
        else:
            print(f"   ? Status: {response.status_code}")
    except Exception as e:
        print(f"   Erreur: {e}")
    
    print("\n" + "=" * 80)
    print("FIN DU DIAGNOSTIC")
    print("=" * 80)

if __name__ == "__main__":
    debug_deletion()
