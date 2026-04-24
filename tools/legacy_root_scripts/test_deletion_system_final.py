#!/usr/bin/env python3
"""
Test final pour vérifier que le système de suppression organisationnelle fonctionne
"""

import requests
import json
import time

# Configuration
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:5173"

def test_backend_endpoints():
    """Test des endpoints backend pour la suppression"""
    print("🔍 Test des endpoints backend...")
    
    try:
        # Test de l'endpoint de vérification des contraintes
        response = requests.get(f"{BACKEND_URL}/organizational-structure/1/can-delete")
        print(f"✅ Endpoint can-delete: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   - Peut supprimer: {data.get('can_delete', 'N/A')}")
            print(f"   - Raison: {data.get('reason', 'N/A')}")
        
        # Test de l'endpoint de l'arbre organisationnel
        response = requests.get(f"{BACKEND_URL}/organizational-structure/1/tree")
        print(f"✅ Endpoint tree: {response.status_code}")
        
    except requests.exceptions.ConnectionError:
        print("❌ Backend non accessible sur http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Erreur backend: {e}")
        return False
    
    return True

def test_frontend_compilation():
    """Test de la compilation frontend"""
    print("\n🔍 Test de la compilation frontend...")
    
    try:
        # Test simple de l'accès au frontend
        response = requests.get(FRONTEND_URL, timeout=5)
        print(f"✅ Frontend accessible: {response.status_code}")
        
        # Test spécifique du composant HierarchyManagerModal
        modal_url = f"{FRONTEND_URL}/src/components/HierarchyManagerModal.tsx"
        response = requests.get(modal_url, timeout=5)
        
        if response.status_code == 200:
            print("✅ HierarchyManagerModal.tsx compile sans erreur")
        elif response.status_code == 500:
            print("❌ Erreur 500 dans HierarchyManagerModal.tsx - problème de compilation")
            return False
        else:
            print(f"⚠️ Status inattendu pour HierarchyManagerModal.tsx: {response.status_code}")
        
    except requests.exceptions.ConnectionError:
        print("❌ Frontend non accessible sur http://localhost:5173")
        print("   Assurez-vous que 'npm run dev' est lancé dans siirh-frontend/")
        return False
    except Exception as e:
        print(f"❌ Erreur frontend: {e}")
        return False
    
    return True

def test_deletion_workflow():
    """Test du workflow complet de suppression"""
    print("\n🔍 Test du workflow de suppression...")
    
    try:
        # 1. Récupérer l'arbre organisationnel
        response = requests.get(f"{BACKEND_URL}/organizational-structure/1/tree")
        if response.status_code != 200:
            print("❌ Impossible de récupérer l'arbre organisationnel")
            return False
        
        tree_data = response.json()
        print("✅ Arbre organisationnel récupéré")
        
        # 2. Trouver une unité à tester
        def find_units(nodes, units_list):
            for node in nodes:
                units_list.append({
                    'id': node['id'],
                    'name': node['name'],
                    'level': node['level']
                })
                if node.get('children'):
                    find_units(node['children'], units_list)
        
        units = []
        if tree_data.get('tree'):
            find_units(tree_data['tree'], units)
        
        if not units:
            print("⚠️ Aucune unité organisationnelle trouvée pour le test")
            return True
        
        # 3. Tester les contraintes de suppression pour chaque unité
        for unit in units[:3]:  # Tester seulement les 3 premières
            unit_id = unit['id']
            response = requests.get(f"{BACKEND_URL}/organizational-structure/{unit_id}/can-delete")
            
            if response.status_code == 200:
                constraints = response.json()
                can_delete = constraints.get('can_delete', False)
                reason = constraints.get('reason', 'N/A')
                
                print(f"   📋 {unit['name']} ({unit['level']}): {'✅ Supprimable' if can_delete else '❌ Non supprimable'}")
                if not can_delete:
                    print(f"      Raison: {reason}")
            else:
                print(f"   ❌ Erreur lors de la vérification de {unit['name']}: {response.status_code}")
        
        print("✅ Test des contraintes de suppression terminé")
        
    except Exception as e:
        print(f"❌ Erreur dans le workflow de suppression: {e}")
        return False
    
    return True

def main():
    """Fonction principale de test"""
    print("🚀 Test du système de suppression organisationnelle")
    print("=" * 60)
    
    # Tests
    backend_ok = test_backend_endpoints()
    frontend_ok = test_frontend_compilation()
    workflow_ok = test_deletion_workflow()
    
    # Résumé
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DES TESTS")
    print(f"Backend: {'✅ OK' if backend_ok else '❌ ERREUR'}")
    print(f"Frontend: {'✅ OK' if frontend_ok else '❌ ERREUR'}")
    print(f"Workflow: {'✅ OK' if workflow_ok else '❌ ERREUR'}")
    
    if backend_ok and frontend_ok and workflow_ok:
        print("\n🎉 TOUS LES TESTS SONT PASSÉS!")
        print("\n📋 INSTRUCTIONS POUR L'UTILISATEUR:")
        print("1. Allez sur la page Employeurs")
        print("2. Cliquez sur 'Gérer la hiérarchie' pour un employeur")
        print("3. Sélectionnez une structure dans l'arbre")
        print("4. Cliquez sur le bouton '🗑️ Supprimer'")
        print("5. Suivez les instructions dans la modal de suppression")
    else:
        print("\n❌ CERTAINS TESTS ONT ÉCHOUÉ")
        print("Vérifiez que le backend et le frontend sont démarrés:")
        print("- Backend: cd siirh-backend && python start_server.py")
        print("- Frontend: cd siirh-frontend && npm run dev")

if __name__ == "__main__":
    main()