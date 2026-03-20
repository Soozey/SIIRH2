#!/usr/bin/env python3
"""
Script pour diagnostiquer spécifiquement l'employeur ID 26
"""

import requests
import json

BACKEND_URL = "http://localhost:8000"

def main():
    employer_id = 26
    
    print(f"🔍 Diagnostic détaillé pour l'employeur ID {employer_id}")
    print("=" * 60)
    
    # 1. Informations de l'employeur
    try:
        response = requests.get(f"{BACKEND_URL}/employers")
        if response.status_code == 200:
            employers = response.json()
            employer = next((e for e in employers if e['id'] == employer_id), None)
            if employer:
                print("📋 INFORMATIONS EMPLOYEUR:")
                for key, value in employer.items():
                    print(f"   {key}: {value}")
                print()
    except Exception as e:
        print(f"❌ Erreur récupération employeur: {e}")
    
    # 2. Salariés liés
    try:
        response = requests.get(f"{BACKEND_URL}/workers")
        if response.status_code == 200:
            workers = response.json()
            employer_workers = [w for w in workers if w.get('employer_id') == employer_id]
            print(f"👥 SALARIÉS LIÉS: {len(employer_workers)}")
            for worker in employer_workers:
                print(f"   - ID: {worker.get('id')}, Nom: {worker.get('prenom', '')} {worker.get('nom', '')}")
            print()
    except Exception as e:
        print(f"❌ Erreur récupération salariés: {e}")
    
    # 3. Structures organisationnelles
    try:
        response = requests.get(f"{BACKEND_URL}/organizational-structure/{employer_id}/tree")
        if response.status_code == 200:
            tree_data = response.json()
            print("🏢 STRUCTURES ORGANISATIONNELLES:")
            print(f"   Données: {json.dumps(tree_data, indent=2)}")
            print()
        else:
            print(f"🏢 STRUCTURES ORGANISATIONNELLES: Erreur {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur récupération structures: {e}")
    
    # 4. Test de suppression avec détails d'erreur
    print("🗑️ TEST DE SUPPRESSION:")
    try:
        response = requests.delete(f"{BACKEND_URL}/employers/{employer_id}")
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        if response.status_code != 200:
            try:
                error_data = response.json()
                print(f"   Erreur JSON: {json.dumps(error_data, indent=2)}")
            except:
                print(f"   Erreur texte: {response.text}")
        else:
            print("   ✅ Suppression réussie!")
            
    except Exception as e:
        print(f"❌ Erreur lors du test de suppression: {e}")
    
    # 5. Proposer le nettoyage
    print("\n🧹 NETTOYAGE AUTOMATIQUE:")
    confirm = input("Voulez-vous nettoyer automatiquement cet employeur? (oui/non): ")
    
    if confirm.lower() in ['oui', 'o', 'yes', 'y']:
        # Supprimer les salariés
        try:
            response = requests.get(f"{BACKEND_URL}/workers")
            if response.status_code == 200:
                workers = response.json()
                employer_workers = [w for w in workers if w.get('employer_id') == employer_id]
                
                for worker in employer_workers:
                    try:
                        delete_response = requests.delete(f"{BACKEND_URL}/workers/{worker['id']}")
                        print(f"   Salarié {worker['id']}: {delete_response.status_code}")
                    except Exception as e:
                        print(f"   Erreur salarié {worker['id']}: {e}")
        except Exception as e:
            print(f"❌ Erreur nettoyage salariés: {e}")
        
        # Supprimer les structures organisationnelles
        try:
            response = requests.get(f"{BACKEND_URL}/organizational-structure/{employer_id}/tree")
            if response.status_code == 200:
                tree_data = response.json()
                if tree_data.get('tree'):
                    def collect_ids(nodes, ids_list):
                        for node in nodes:
                            ids_list.append(node['id'])
                            if node.get('children'):
                                collect_ids(node['children'], ids_list)
                    
                    structure_ids = []
                    collect_ids(tree_data['tree'], structure_ids)
                    
                    for structure_id in reversed(structure_ids):
                        try:
                            delete_response = requests.delete(f"{BACKEND_URL}/organizational-structure/{structure_id}?force=true")
                            print(f"   Structure {structure_id}: {delete_response.status_code}")
                        except Exception as e:
                            print(f"   Erreur structure {structure_id}: {e}")
        except Exception as e:
            print(f"❌ Erreur nettoyage structures: {e}")
        
        # Nouveau test de suppression
        print("\n🗑️ NOUVEAU TEST DE SUPPRESSION:")
        try:
            response = requests.delete(f"{BACKEND_URL}/employers/{employer_id}")
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ Employeur supprimé avec succès!")
            else:
                try:
                    error_data = response.json()
                    print(f"   Erreur: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"   Erreur: {response.text}")
                    
        except Exception as e:
            print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    main()