"""
Test pour vérifier que le frontend peut maintenant afficher les structures créées
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_frontend_format():
    """Vérifie que le format de l'API correspond à ce que le frontend attend"""
    print("=" * 80)
    print("TEST DU FORMAT POUR LE FRONTEND")
    print("=" * 80)
    
    # Récupérer un employeur
    print("\n1️⃣ Récupération d'un employeur...")
    response = requests.get(f"{BASE_URL}/employers", timeout=5)
    response.raise_for_status()
    employers = response.json()
    
    if not employers:
        print("   ⚠️  Aucun employeur")
        return False
    
    employer_id = employers[0]['id']
    print(f"   ✓ Employeur ID: {employer_id}")
    
    # Récupérer l'arbre
    print(f"\n2️⃣ Récupération de l'arbre...")
    response = requests.get(
        f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/tree",
        timeout=5
    )
    response.raise_for_status()
    data = response.json()
    
    print(f"   ✓ Réponse reçue")
    print(f"\n   Structure de la réponse:")
    print(f"   {json.dumps(list(data.keys()), indent=6)}")
    
    # Vérifier le format
    print(f"\n3️⃣ Vérification du format...")
    
    has_tree = 'tree' in data
    has_total_units = 'total_units' in data
    tree_is_array = isinstance(data.get('tree'), list)
    
    print(f"   {'✓' if has_tree else '✗'} Clé 'tree' présente")
    print(f"   {'✓' if has_total_units else '✗'} Clé 'total_units' présente")
    print(f"   {'✓' if tree_is_array else '✗'} 'tree' est un tableau")
    
    if has_tree and tree_is_array:
        tree = data['tree']
        print(f"   ✓ Nombre d'établissements: {len(tree)}")
        
        if len(tree) > 0:
            print(f"\n   Exemple de structure:")
            example = tree[0]
            print(f"   - ID: {example.get('id')}")
            print(f"   - Nom: {example.get('name')}")
            print(f"   - Level: {example.get('level')}")
            print(f"   - Children: {len(example.get('children', []))} enfant(s)")
    
    if has_total_units:
        print(f"   ✓ Total d'unités: {data['total_units']}")
    
    # Vérifier que le format correspond à ce que le frontend attend
    print(f"\n4️⃣ Validation pour le frontend...")
    
    # Le frontend fait: const tree = Array.isArray(treeData?.tree) ? treeData.tree : [];
    frontend_compatible = has_tree and tree_is_array
    
    if frontend_compatible:
        print(f"   ✅ FORMAT COMPATIBLE AVEC LE FRONTEND")
        print(f"   Le code frontend `treeData?.tree` fonctionnera correctement")
    else:
        print(f"   ❌ FORMAT INCOMPATIBLE")
        if not has_tree:
            print(f"      Manque la clé 'tree'")
        if not tree_is_array:
            print(f"      'tree' n'est pas un tableau")
    
    print("\n" + "=" * 80)
    
    return frontend_compatible

if __name__ == "__main__":
    try:
        success = test_frontend_format()
        if success:
            print("✅ Le format de l'API est compatible avec le frontend!")
        else:
            print("❌ Le format de l'API n'est PAS compatible avec le frontend!")
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
