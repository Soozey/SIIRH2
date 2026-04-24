#!/usr/bin/env python3
"""
Script pour diagnostiquer et résoudre les problèmes de suppression d'employeur
"""

import requests
import json

BACKEND_URL = "http://localhost:8000"

def check_employer_constraints(employer_id):
    """Vérifie toutes les contraintes qui empêchent la suppression d'un employeur"""
    print(f"🔍 Diagnostic pour l'employeur ID {employer_id}")
    print("=" * 50)
    
    constraints = {
        'workers': 0,
        'organizational_structures': 0,
        'payroll_runs': 0,
        'other_references': []
    }
    
    try:
        # 1. Vérifier les salariés
        response = requests.get(f"{BACKEND_URL}/workers")
        if response.status_code == 200:
            workers = response.json()
            employer_workers = [w for w in workers if w.get('employer_id') == employer_id]
            constraints['workers'] = len(employer_workers)
            print(f"👥 Salariés liés: {constraints['workers']}")
            
            if employer_workers:
                print("   Salariés trouvés:")
                for worker in employer_workers[:5]:  # Afficher les 5 premiers
                    print(f"   - {worker.get('prenom', '')} {worker.get('nom', '')} (ID: {worker.get('id')})")
                if len(employer_workers) > 5:
                    print(f"   ... et {len(employer_workers) - 5} autres")
        
        # 2. Vérifier les structures organisationnelles
        try:
            response = requests.get(f"{BACKEND_URL}/organizational-structure/{employer_id}/tree")
            if response.status_code == 200:
                tree_data = response.json()
                if tree_data.get('tree'):
                    def count_structures(nodes):
                        count = 0
                        for node in nodes:
                            count += 1
                            if node.get('children'):
                                count += count_structures(node['children'])
                        return count
                    
                    constraints['organizational_structures'] = count_structures(tree_data['tree'])
                    print(f"🏢 Structures organisationnelles: {constraints['organizational_structures']}")
        except:
            print("🏢 Structures organisationnelles: Impossible de vérifier")
        
        # 3. Vérifier les bulletins de paie
        try:
            response = requests.get(f"{BACKEND_URL}/payroll")
            if response.status_code == 200:
                payrolls = response.json()
                employer_payrolls = [p for p in payrolls if p.get('employer_id') == employer_id]
                constraints['payroll_runs'] = len(employer_payrolls)
                print(f"💰 Bulletins de paie: {constraints['payroll_runs']}")
        except:
            print("💰 Bulletins de paie: Impossible de vérifier")
        
        return constraints
        
    except Exception as e:
        print(f"❌ Erreur lors du diagnostic: {e}")
        return None

def get_employer_info(employer_id):
    """Récupère les informations de l'employeur"""
    try:
        response = requests.get(f"{BACKEND_URL}/employers")
        if response.status_code == 200:
            employers = response.json()
            employer = next((e for e in employers if e['id'] == employer_id), None)
            if employer:
                print(f"📋 Employeur: {employer.get('nom', 'N/A')}")
                print(f"   SIRET: {employer.get('siret', 'N/A')}")
                print(f"   Adresse: {employer.get('adresse', 'N/A')}")
                return employer
        return None
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des infos employeur: {e}")
        return None

def clean_employer_data(employer_id, force=False):
    """Nettoie les données liées à un employeur pour permettre sa suppression"""
    print(f"\n🧹 Nettoyage des données pour l'employeur ID {employer_id}")
    
    if not force:
        confirm = input("⚠️ Cette action va supprimer TOUTES les données liées à cet employeur. Continuer? (oui/non): ")
        if confirm.lower() not in ['oui', 'o', 'yes', 'y']:
            print("❌ Nettoyage annulé")
            return False
    
    try:
        # 1. Supprimer les salariés
        response = requests.get(f"{BACKEND_URL}/workers")
        if response.status_code == 200:
            workers = response.json()
            employer_workers = [w for w in workers if w.get('employer_id') == employer_id]
            
            for worker in employer_workers:
                try:
                    delete_response = requests.delete(f"{BACKEND_URL}/workers/{worker['id']}")
                    if delete_response.status_code in [200, 204]:
                        print(f"   ✅ Salarié supprimé: {worker.get('prenom', '')} {worker.get('nom', '')}")
                    else:
                        print(f"   ❌ Erreur suppression salarié {worker['id']}: {delete_response.status_code}")
                except Exception as e:
                    print(f"   ❌ Erreur suppression salarié {worker['id']}: {e}")
        
        # 2. Supprimer les structures organisationnelles
        try:
            response = requests.get(f"{BACKEND_URL}/organizational-structure/{employer_id}/tree")
            if response.status_code == 200:
                tree_data = response.json()
                if tree_data.get('tree'):
                    def collect_structure_ids(nodes, ids_list):
                        for node in nodes:
                            ids_list.append(node['id'])
                            if node.get('children'):
                                collect_structure_ids(node['children'], ids_list)
                    
                    structure_ids = []
                    collect_structure_ids(tree_data['tree'], structure_ids)
                    
                    # Supprimer dans l'ordre inverse (enfants d'abord)
                    for structure_id in reversed(structure_ids):
                        try:
                            delete_response = requests.delete(f"{BACKEND_URL}/organizational-structure/{structure_id}?force=true")
                            if delete_response.status_code in [200, 204]:
                                print(f"   ✅ Structure supprimée: ID {structure_id}")
                            else:
                                print(f"   ❌ Erreur suppression structure {structure_id}: {delete_response.status_code}")
                        except Exception as e:
                            print(f"   ❌ Erreur suppression structure {structure_id}: {e}")
        except Exception as e:
            print(f"   ⚠️ Erreur lors de la suppression des structures: {e}")
        
        print("✅ Nettoyage terminé")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du nettoyage: {e}")
        return False

def test_employer_deletion(employer_id):
    """Teste la suppression de l'employeur après nettoyage"""
    print(f"\n🗑️ Test de suppression de l'employeur ID {employer_id}")
    
    try:
        response = requests.delete(f"{BACKEND_URL}/employers/{employer_id}")
        
        if response.status_code in [200, 204]:
            print("✅ Employeur supprimé avec succès!")
            return True
        else:
            print(f"❌ Erreur lors de la suppression: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"   Détail: {error_detail}")
            except:
                print(f"   Réponse: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de la suppression: {e}")
        return False

def main():
    """Fonction principale"""
    print("🔧 Diagnostic et Nettoyage d'Employeur")
    print("=" * 60)
    
    # Trouver l'employeur "Test Deletion Company"
    try:
        response = requests.get(f"{BACKEND_URL}/employers")
        if response.status_code == 200:
            employers = response.json()
            test_employer = None
            
            for emp in employers:
                if "Test Deletion" in emp.get('nom', ''):
                    test_employer = emp
                    break
            
            if test_employer:
                employer_id = test_employer['id']
                print(f"🎯 Employeur trouvé: {test_employer['nom']} (ID: {employer_id})")
                
                # Diagnostic
                get_employer_info(employer_id)
                constraints = check_employer_constraints(employer_id)
                
                if constraints:
                    total_constraints = (constraints['workers'] + 
                                       constraints['organizational_structures'] + 
                                       constraints['payroll_runs'])
                    
                    if total_constraints > 0:
                        print(f"\n⚠️ {total_constraints} contrainte(s) empêchent la suppression")
                        
                        # Proposer le nettoyage
                        print("\n🧹 Options de nettoyage:")
                        print("1. Nettoyer automatiquement toutes les données liées")
                        print("2. Annuler")
                        
                        choice = input("Votre choix (1/2): ")
                        
                        if choice == "1":
                            if clean_employer_data(employer_id):
                                # Tester la suppression
                                test_employer_deletion(employer_id)
                        else:
                            print("❌ Nettoyage annulé")
                    else:
                        print("\n✅ Aucune contrainte détectée, test de suppression...")
                        test_employer_deletion(employer_id)
            else:
                print("❌ Employeur 'Test Deletion Company' non trouvé")
                print("\nEmployeurs disponibles:")
                for emp in employers:
                    print(f"   - {emp.get('nom', 'N/A')} (ID: {emp['id']})")
        else:
            print("❌ Impossible de récupérer la liste des employeurs")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    main()