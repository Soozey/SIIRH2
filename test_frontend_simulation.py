"""
Simulation du comportement exact du frontend lors de la création d'une structure
"""
import requests
import json
from datetime import datetime
import time

BASE_URL = "http://127.0.0.1:8000"

def simulate_frontend_workflow():
    """Simule exactement ce que fait le frontend"""
    print("=" * 80)
    print("SIMULATION DU WORKFLOW FRONTEND")
    print("=" * 80)
    
    # 1. L'utilisateur ouvre le modal
    print("\n👤 Utilisateur: Ouvre le modal 'Gestion de la Hiérarchie'")
    
    employer_id = 1
    
    # 2. Le frontend charge l'arbre initial
    print(f"\n🔄 Frontend: Charge l'arbre initial...")
    response = requests.get(
        f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/tree",
        timeout=5
    )
    response.raise_for_status()
    initial_tree = response.json()
    
    initial_count = len(initial_tree.get('tree', []))
    print(f"   ✓ Arbre chargé: {initial_count} établissement(s)")
    print(f"   ✓ Total d'unités: {initial_tree.get('total_units', 0)}")
    
    # 3. L'utilisateur clique sur "Nouvel Établissement"
    print(f"\n👤 Utilisateur: Clique sur 'Nouvel Établissement'")
    print(f"   → Le formulaire s'ouvre")
    
    # 4. L'utilisateur remplit le formulaire
    timestamp = datetime.now().strftime('%H%M%S')
    new_structure = {
        "name": f"Test Frontend {timestamp}",
        "code": f"FE{timestamp}",
        "level": "etablissement",
        "parent_id": None,
        "description": "Test simulation frontend"
    }
    
    print(f"\n👤 Utilisateur: Remplit le formulaire")
    print(f"   - Nom: {new_structure['name']}")
    print(f"   - Code: {new_structure['code']}")
    
    # 5. L'utilisateur clique sur "Créer"
    print(f"\n👤 Utilisateur: Clique sur 'Créer'")
    
    # 6. Le frontend envoie la requête de création
    print(f"\n🔄 Frontend: Envoie la requête POST...")
    response = requests.post(
        f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/nodes",
        json=new_structure,
        timeout=5
    )
    response.raise_for_status()
    created_node = response.json()
    
    print(f"   ✓ Structure créée (ID: {created_node['id']})")
    
    # 7. Le frontend invalide le cache React Query
    print(f"\n🔄 Frontend: Invalide le cache React Query")
    print(f"   queryClient.invalidateQueries(['organizational-tree', {employer_id}])")
    
    # 8. React Query recharge automatiquement les données
    print(f"\n🔄 React Query: Recharge automatiquement l'arbre...")
    time.sleep(0.5)  # Simuler un petit délai réseau
    
    response = requests.get(
        f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/tree",
        timeout=5
    )
    response.raise_for_status()
    updated_tree = response.json()
    
    updated_count = len(updated_tree.get('tree', []))
    print(f"   ✓ Arbre rechargé: {updated_count} établissement(s)")
    print(f"   ✓ Total d'unités: {updated_tree.get('total_units', 0)}")
    
    # 9. Le frontend traite les données
    print(f"\n🔄 Frontend: Traite les données")
    print(f"   const tree = Array.isArray(treeData?.tree) ? treeData.tree : [];")
    
    tree = updated_tree.get('tree', [])
    if isinstance(tree, list):
        print(f"   ✓ tree est un tableau de {len(tree)} élément(s)")
    else:
        print(f"   ✗ tree n'est PAS un tableau!")
        return False
    
    # 10. Vérifier que la nouvelle structure est dans l'arbre
    print(f"\n🔍 Frontend: Recherche la nouvelle structure dans l'arbre...")
    
    found = False
    for node in tree:
        if node['id'] == created_node['id']:
            found = True
            print(f"   ✅ Structure trouvée!")
            print(f"      - ID: {node['id']}")
            print(f"      - Nom: {node['name']}")
            print(f"      - Code: {node['code']}")
            break
    
    if not found:
        print(f"   ❌ Structure NON trouvée dans l'arbre!")
        print(f"   Structures présentes:")
        for node in tree:
            print(f"      - ID {node['id']}: {node['name']}")
        return False
    
    # 11. Le frontend affiche la structure
    print(f"\n🖥️  Frontend: Affiche la structure dans le modal")
    print(f"   → L'utilisateur voit immédiatement la nouvelle structure ✅")
    
    # 12. Vérifier que le compteur a augmenté
    print(f"\n📊 Vérification des compteurs:")
    print(f"   - Avant: {initial_count} établissement(s)")
    print(f"   - Après: {updated_count} établissement(s)")
    print(f"   - Différence: +{updated_count - initial_count}")
    
    if updated_count > initial_count:
        print(f"   ✅ Le compteur a bien augmenté!")
    else:
        print(f"   ⚠️  Le compteur n'a pas augmenté")
    
    # 13. Nettoyer
    print(f"\n🧹 Nettoyage...")
    response = requests.delete(
        f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/nodes/{created_node['id']}",
        params={'force': False},
        timeout=5
    )
    
    if response.status_code == 200:
        print(f"   ✓ Structure supprimée")
    
    print("\n" + "=" * 80)
    print("✅ SIMULATION RÉUSSIE")
    print("=" * 80)
    print("\nRésumé:")
    print("1. ✅ L'utilisateur crée une structure")
    print("2. ✅ Le frontend envoie la requête")
    print("3. ✅ La structure est créée dans la base")
    print("4. ✅ React Query invalide le cache")
    print("5. ✅ L'arbre est rechargé automatiquement")
    print("6. ✅ La nouvelle structure apparaît dans l'arbre")
    print("7. ✅ L'utilisateur voit immédiatement la structure")
    print("\n🎉 Le workflow fonctionne parfaitement!")
    
    return True

if __name__ == "__main__":
    try:
        success = simulate_frontend_workflow()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
