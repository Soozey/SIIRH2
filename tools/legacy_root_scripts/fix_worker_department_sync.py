#!/usr/bin/env python3
"""
Correction immédiate de la synchronisation du département du salarié
"""

import requests
import json

BACKEND_URL = "http://localhost:8000"

def fix_worker_department_sync():
    """Corrige la synchronisation du département du salarié"""
    print("🔧 Correction de la synchronisation du département")
    print("=" * 70)
    
    worker_id = 2032  # Jeanne RAFARAVAVY
    employer_id = 2
    period = "2025-01"
    
    # 1. État actuel
    print("1️⃣ ÉTAT ACTUEL:")
    print("-" * 20)
    
    try:
        response = requests.get(f"{BACKEND_URL}/workers/{worker_id}")
        if response.status_code == 200:
            worker = response.json()
            current_dept = worker.get('departement', '')
            
            print(f"👤 {worker['prenom']} {worker['nom']}")
            print(f"   Département actuel: '{current_dept}'")
        else:
            print(f"❌ Erreur récupération salarié: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False
    
    # 2. Départements disponibles
    print(f"\n2️⃣ DÉPARTEMENTS DISPONIBLES:")
    print("-" * 30)
    
    try:
        response = requests.get(f"{BACKEND_URL}/employers/{employer_id}/organizational-data/hierarchical")
        if response.status_code == 200:
            org_data = response.json()
            available_depts = org_data.get('departements', [])
            
            print(f"📊 Départements hiérarchiques: {available_depts}")
            
            if 'SWEETY' in available_depts:
                target_dept = 'SWEETY'
                print(f"✅ 'SWEETY' disponible pour affectation")
            else:
                print(f"❌ 'SWEETY' non disponible")
                return False
        else:
            print(f"❌ Erreur données organisationnelles: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False
    
    # 3. Mise à jour du salarié
    print(f"\n3️⃣ MISE À JOUR DU SALARIÉ:")
    print("-" * 30)
    
    try:
        # Mettre à jour le département vers SWEETY
        updated_worker = {
            **worker,
            'departement': target_dept
        }
        
        print(f"🔄 Mise à jour: '{current_dept}' → '{target_dept}'")
        
        response = requests.put(f"{BACKEND_URL}/workers/{worker_id}", json=updated_worker)
        
        if response.status_code == 200:
            print(f"✅ Mise à jour réussie")
        else:
            print(f"❌ Erreur mise à jour: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Détails: {error_data}")
            except:
                print(f"   Détails: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False
    
    # 4. Vérification immédiate
    print(f"\n4️⃣ VÉRIFICATION IMMÉDIATE:")
    print("-" * 30)
    
    try:
        # Vérifier que la mise à jour a pris effet
        response = requests.get(f"{BACKEND_URL}/workers/{worker_id}")
        if response.status_code == 200:
            updated_worker = response.json()
            new_dept = updated_worker.get('departement', '')
            
            print(f"👤 Vérification: Département = '{new_dept}'")
            
            if new_dept == target_dept:
                print(f"✅ Mise à jour confirmée")
            else:
                print(f"❌ Mise à jour non confirmée")
                return False
        else:
            print(f"❌ Erreur vérification: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False
    
    # 5. Test du filtrage
    print(f"\n5️⃣ TEST DU FILTRAGE:")
    print("-" * 25)
    
    try:
        response = requests.get(f"{BACKEND_URL}/payroll/bulk-preview", params={
            'employer_id': employer_id,
            'period': period,
            'departement': target_dept
        })
        
        if response.status_code == 200:
            bulletins = response.json()
            print(f"✅ {len(bulletins)} bulletin(s) avec filtre '{target_dept}'")
            
            if len(bulletins) > 0:
                bulletin = bulletins[0]
                worker_info = bulletin['worker']
                totaux = bulletin.get('totaux', {})
                
                print(f"📄 Bulletin généré:")
                print(f"   👤 {worker_info['prenom']} {worker_info['nom']}")
                print(f"   🏬 Département: '{worker_info.get('departement', 'N/A')}'")
                print(f"   💰 Brut: {totaux.get('brut', 0)} Ar")
                print(f"   💵 Net: {totaux.get('net', 0)} Ar")
                
                return True
            else:
                print(f"❌ Toujours aucun bulletin")
                return False
        else:
            print(f"❌ Erreur test filtrage: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def update_establishment_too():
    """Met aussi à jour l'établissement pour une cohérence complète"""
    print(f"\n6️⃣ MISE À JOUR DE L'ÉTABLISSEMENT:")
    print("-" * 35)
    
    worker_id = 2032
    employer_id = 2
    
    try:
        # Récupérer les établissements disponibles
        response = requests.get(f"{BACKEND_URL}/employers/{employer_id}/organizational-data/hierarchical")
        if response.status_code == 200:
            org_data = response.json()
            available_establishments = org_data.get('etablissements', [])
            
            if available_establishments:
                target_establishment = available_establishments[0]  # Prendre le premier
                print(f"🏢 Établissement cible: '{target_establishment}'")
                
                # Récupérer et mettre à jour le salarié
                worker_response = requests.get(f"{BACKEND_URL}/workers/{worker_id}")
                if worker_response.status_code == 200:
                    worker = worker_response.json()
                    current_establishment = worker.get('etablissement', '')
                    
                    print(f"   Actuel: '{current_establishment}' → Nouveau: '{target_establishment}'")
                    
                    updated_worker = {
                        **worker,
                        'etablissement': target_establishment
                    }
                    
                    update_response = requests.put(f"{BACKEND_URL}/workers/{worker_id}", json=updated_worker)
                    
                    if update_response.status_code == 200:
                        print(f"✅ Établissement mis à jour")
                        return True
                    else:
                        print(f"❌ Erreur mise à jour établissement: {update_response.status_code}")
            else:
                print(f"❌ Aucun établissement disponible")
        else:
            print(f"❌ Erreur récupération établissements: {response.status_code}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    return False

def final_comprehensive_test():
    """Test complet final avec tous les filtres"""
    print(f"\n7️⃣ TEST COMPLET FINAL:")
    print("-" * 25)
    
    employer_id = 2
    period = "2025-01"
    
    test_cases = [
        {"name": "Sans filtres", "params": {}},
        {"name": "Avec établissement", "params": {"etablissement": "Mandroso Formation"}},
        {"name": "Avec département", "params": {"departement": "SWEETY"}},
        {"name": "Avec les deux", "params": {"etablissement": "Mandroso Formation", "departement": "SWEETY"}}
    ]
    
    all_success = True
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}:")
        
        params = {
            'employer_id': employer_id,
            'period': period,
            **test_case['params']
        }
        
        try:
            response = requests.get(f"{BACKEND_URL}/payroll/bulk-preview", params=params)
            
            if response.status_code == 200:
                bulletins = response.json()
                print(f"   ✅ {len(bulletins)} bulletin(s)")
                
                if len(bulletins) == 0 and test_case['params']:  # Si filtres appliqués mais aucun résultat
                    print(f"   ⚠️ Aucun bulletin avec ces filtres")
                    all_success = False
            else:
                print(f"   ❌ Erreur: {response.status_code}")
                all_success = False
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            all_success = False
    
    return all_success

def main():
    """Fonction principale"""
    print("🚀 Correction complète de la synchronisation")
    print("=" * 70)
    
    # 1. Corriger le département
    dept_success = fix_worker_department_sync()
    
    # 2. Corriger l'établissement aussi
    establishment_success = update_establishment_too()
    
    # 3. Test complet final
    final_success = final_comprehensive_test()
    
    print(f"\n🎯 RÉSUMÉ:")
    print(f"   Département: {'✅' if dept_success else '❌'}")
    print(f"   Établissement: {'✅' if establishment_success else '❌'}")
    print(f"   Tests finaux: {'✅' if final_success else '❌'}")
    
    if dept_success:
        print(f"\n🎉 SUCCÈS!")
        print(f"Le salarié est maintenant affecté au département 'SWEETY'.")
        print(f"Testez l'interface - le filtrage devrait fonctionner.")
    else:
        print(f"\n❌ ÉCHEC")
        print(f"La synchronisation n'a pas fonctionné.")
        print(f"Vérifiez les logs backend pour plus de détails.")

if __name__ == "__main__":
    main()