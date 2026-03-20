#!/usr/bin/env python3
"""
Test pour vérifier que le modal de suppression fonctionne
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_modal_integration():
    """Test de l'intégration du modal de suppression"""
    
    print("🧪 TEST DE L'INTÉGRATION DU MODAL DE SUPPRESSION")
    print("=" * 55)
    
    # 1. Vérifier que les endpoints fonctionnent
    print("\n1️⃣ Vérification des endpoints...")
    
    try:
        # Test employeurs
        response = requests.get(f"{BASE_URL}/employers")
        if response.status_code == 200:
            employers = response.json()
            print(f"   ✅ Employeurs: {len(employers)} trouvés")
            
            if employers:
                employer_id = employers[0]['id']
                print(f"   📋 Test avec employeur ID: {employer_id}")
                
                # Test arbre organisationnel
                response = requests.get(f"{BASE_URL}/organizational-structure/{employer_id}/tree")
                if response.status_code == 200:
                    tree_data = response.json()
                    print(f"   ✅ Arbre organisationnel: {tree_data['total_units']} unités")
                    
                    # Extraire quelques IDs d'unités pour test
                    def extract_unit_ids(nodes, ids_list):
                        for node in nodes:
                            if isinstance(node, dict) and 'id' in node:
                                ids_list.append({
                                    'id': node['id'],
                                    'name': node['name'],
                                    'level': node['level']
                                })
                                if 'children' in node:
                                    extract_unit_ids(node['children'], ids_list)
                    
                    unit_ids = []
                    extract_unit_ids(tree_data.get('tree', []), unit_ids)
                    
                    print(f"   📋 Unités disponibles pour test:")
                    for unit in unit_ids[:5]:  # Afficher les 5 premières
                        print(f"      - {unit['name']} (ID: {unit['id']}, {unit['level']})")
                    
                    # Test des contraintes de suppression
                    if unit_ids:
                        test_unit = unit_ids[0]
                        print(f"\n   🎯 Test contraintes pour: {test_unit['name']}")
                        
                        response = requests.get(f"{BASE_URL}/organizational-structure/{test_unit['id']}/can-delete")
                        if response.status_code == 200:
                            constraints = response.json()
                            print(f"      ✅ Contraintes récupérées:")
                            print(f"         - Supprimable: {constraints['can_delete']}")
                            print(f"         - Salariés: {constraints['direct_workers_count']}")
                            print(f"         - Sous-structures: {constraints['children_count']}")
                        else:
                            print(f"      ❌ Erreur contraintes: {response.status_code}")
                else:
                    print(f"   ❌ Erreur arbre: {response.status_code}")
        else:
            print(f"   ❌ Erreur employeurs: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # 2. Instructions pour l'utilisateur
    print(f"\n2️⃣ INSTRUCTIONS POUR L'UTILISATEUR:")
    print("=" * 40)
    print("📍 MAINTENANT DANS VOTRE INTERFACE:")
    print()
    print("1. Dans le modal 'Gestion de la Hiérarchie Organisationnelle'")
    print("   vous devriez voir un nouveau bouton rouge '🗑️ Supprimer'")
    print()
    print("2. ÉTAPES À SUIVRE:")
    print("   a) Cliquez sur une structure dans l'arbre (elle sera surlignée)")
    print("   b) Le bouton '🗑️ Supprimer' deviendra actif (rouge)")
    print("   c) Cliquez sur '🗑️ Supprimer'")
    print("   d) Un nouveau modal s'ouvrira avec les options de suppression")
    print()
    print("3. BOUTONS DANS L'EN-TÊTE DU MODAL:")
    print("   [+ Ajouter] [🗑️ Supprimer] [✕ Fermer]")
    print("                     ↑")
    print("               Nouveau bouton")
    print()
    print("4. INDICATEUR DE SÉLECTION:")
    print("   Quand vous cliquez sur une structure, vous verrez:")
    print("   '✓ Structure sélectionnée (ID: XX) - Vous pouvez maintenant la supprimer'")
    print()
    print("🎯 TESTEZ MAINTENANT:")
    print("   - Ouvrez le modal de hiérarchie")
    print("   - Cliquez sur une structure avec '✓ Supprimable' (verte)")
    print("   - Cliquez sur le bouton '🗑️ Supprimer'")
    print("   - Suivez les instructions du modal de suppression")

if __name__ == "__main__":
    test_modal_integration()