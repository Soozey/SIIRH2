#!/usr/bin/env python3
"""
Vérification des données actuelles du salarié Jeanne RAFARAVAVY
"""

import requests
import json

BACKEND_URL = "http://localhost:8000"

def verify_current_worker_data():
    """Vérifie les données actuelles du salarié"""
    print("🔍 Vérification des données actuelles de Jeanne RAFARAVAVY")
    print("=" * 70)
    
    # 1. Récupérer directement le salarié par ID
    print("1️⃣ DONNÉES DIRECTES DU SALARIÉ (ID: 2032):")
    print("-" * 45)
    
    try:
        response = requests.get(f"{BACKEND_URL}/workers/2032")
        if response.status_code == 200:
            worker = response.json()
            
            print(f"👤 {worker['prenom']} {worker['nom']} (ID: {worker['id']})")
            print(f"📊 Affectation organisationnelle ACTUELLE:")
            print(f"   - Employeur ID: {worker.get('employer_id')}")
            print(f"   - Établissement: '{worker.get('etablissement')}'")
            print(f"   - Département: '{worker.get('departement')}'")
            print(f"   - Service: '{worker.get('service')}'")
            print(f"   - Unité: '{worker.get('unite')}'")
            
            current_etablissement = worker.get('etablissement')
            current_departement = worker.get('departement')
            
            # Vérifier si ce sont les anciennes valeurs numériques
            if current_etablissement == "54" or current_departement == "55":
                print(f"\n❌ PROBLÈME IDENTIFIÉ!")
                print(f"   Le salarié utilise encore les ANCIENNES valeurs numériques:")
                print(f"   - Établissement: '{current_etablissement}' (devrait être 'Mandroso Formation')")
                print(f"   - Département: '{current_departement}' (devrait être 'EN LIGNE')")
                return "old_values", worker
            else:
                print(f"\n✅ Le salarié utilise les NOUVELLES valeurs textuelles")
                return "new_values", worker
        else:
            print(f"❌ Erreur récupération salarié: {response.status_code}")
            return "error", None
    except Exception as e:
        print(f"❌ Exception: {e}")
        return "error", None

def verify_organizational_data_sources():
    """Vérifie les différentes sources de données organisationnelles"""
    print("\n2️⃣ VÉRIFICATION DES SOURCES DE DONNÉES ORGANISATIONNELLES:")
    print("-" * 60)
    
    employer_id = 2
    
    # Source 1: Données hiérarchiques
    print("📊 Source 1: Données hiérarchiques (/organizational-data/hierarchical)")
    try:
        response = requests.get(f"{BACKEND_URL}/employers/{employer_id}/organizational-data/hierarchical")
        if response.status_code == 200:
            hierarchical_data = response.json()
            print(f"   Établissements: {hierarchical_data.get('etablissements', [])}")
            print(f"   Départements: {hierarchical_data.get('departements', [])}")
        else:
            print(f"   ❌ Erreur: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Source 2: Données des salariés
    print("\n📊 Source 2: Données des salariés (/organizational-data/workers)")
    try:
        response = requests.get(f"{BACKEND_URL}/employers/{employer_id}/organizational-data/workers")
        if response.status_code == 200:
            workers_data = response.json()
            print(f"   Établissements: {workers_data.get('etablissements', [])}")
            print(f"   Départements: {workers_data.get('departements', [])}")
        else:
            print(f"   ❌ Erreur: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")

def test_filtering_with_actual_values(worker_data):
    """Teste le filtrage avec les vraies valeurs actuelles du salarié"""
    print("\n3️⃣ TEST FILTRAGE AVEC VALEURS ACTUELLES:")
    print("-" * 45)
    
    if not worker_data:
        print("❌ Pas de données salarié disponibles")
        return
    
    employer_id = worker_data.get('employer_id')
    period = "2025-01"
    etablissement = worker_data.get('etablissement')
    departement = worker_data.get('departement')
    
    print(f"🧪 Test avec les valeurs ACTUELLES du salarié:")
    print(f"   - Employeur: {employer_id}")
    print(f"   - Période: {period}")
    print(f"   - Établissement: '{etablissement}'")
    print(f"   - Département: '{departement}'")
    
    # Test 1: Sans filtres
    print(f"\n1. Test SANS filtres:")
    try:
        response = requests.get(f"{BACKEND_URL}/payroll/bulk-preview", params={
            'employer_id': employer_id,
            'period': period
        })
        
        if response.status_code == 200:
            bulletins = response.json()
            print(f"   ✅ {len(bulletins)} bulletin(s) sans filtres")
        else:
            print(f"   ❌ Erreur: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 2: Avec filtre établissement (valeur actuelle)
    print(f"\n2. Test AVEC filtre établissement '{etablissement}':")
    try:
        response = requests.get(f"{BACKEND_URL}/payroll/bulk-preview", params={
            'employer_id': employer_id,
            'period': period,
            'etablissement': etablissement
        })
        
        if response.status_code == 200:
            bulletins = response.json()
            print(f"   ✅ {len(bulletins)} bulletin(s) avec filtre établissement")
            
            if len(bulletins) == 0:
                print(f"   ❌ AUCUN BULLETIN! C'est le problème!")
                print(f"   🔍 L'interface cherche probablement une autre valeur")
            else:
                print(f"   ✅ Bulletins trouvés avec la valeur actuelle")
        else:
            print(f"   ❌ Erreur: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 3: Avec filtre département (valeur actuelle)
    print(f"\n3. Test AVEC filtre département '{departement}':")
    try:
        response = requests.get(f"{BACKEND_URL}/payroll/bulk-preview", params={
            'employer_id': employer_id,
            'period': period,
            'departement': departement
        })
        
        if response.status_code == 200:
            bulletins = response.json()
            print(f"   ✅ {len(bulletins)} bulletin(s) avec filtre département")
            
            if len(bulletins) == 0:
                print(f"   ❌ AUCUN BULLETIN! C'est le problème!")
        else:
            print(f"   ❌ Erreur: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")

def test_filtering_with_interface_values():
    """Teste avec les valeurs que l'interface pourrait utiliser"""
    print("\n4️⃣ TEST AVEC VALEURS QUE L'INTERFACE UTILISE:")
    print("-" * 50)
    
    employer_id = 2
    period = "2025-01"
    
    # Valeurs que l'interface pourrait utiliser (basées sur les données hiérarchiques)
    interface_values = [
        {"etablissement": "Mandroso Formation"},
        {"departement": "EN LIGNE"},
        {"departement": "SWEETY"},
        {"etablissement": "Mandroso Formation", "departement": "EN LIGNE"}
    ]
    
    for i, filters in enumerate(interface_values, 1):
        print(f"\n{i}. Test avec filtres interface: {filters}")
        
        params = {
            'employer_id': employer_id,
            'period': period,
            **filters
        }
        
        try:
            response = requests.get(f"{BACKEND_URL}/payroll/bulk-preview", params=params)
            
            if response.status_code == 200:
                bulletins = response.json()
                print(f"   ✅ {len(bulletins)} bulletin(s)")
                
                if len(bulletins) == 0:
                    print(f"   ❌ AUCUN BULLETIN - L'interface ne trouve rien!")
                else:
                    print(f"   ✅ Bulletins trouvés - L'interface devrait fonctionner")
            else:
                print(f"   ❌ Erreur: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")

def fix_worker_data_if_needed(status, worker_data):
    """Corrige les données du salarié si nécessaire"""
    if status == "old_values" and worker_data:
        print("\n5️⃣ CORRECTION DES DONNÉES DU SALARIÉ:")
        print("-" * 40)
        
        print("🔧 Le salarié utilise encore les anciennes valeurs numériques.")
        print("   Correction nécessaire pour correspondre aux données hiérarchiques.")
        
        corrected_data = {
            **worker_data,
            "etablissement": "Mandroso Formation",
            "departement": "EN LIGNE"
        }
        
        print(f"\n🔄 Mise à jour:")
        print(f"   Ancien établissement: '{worker_data.get('etablissement')}' → 'Mandroso Formation'")
        print(f"   Ancien département: '{worker_data.get('departement')}' → 'EN LIGNE'")
        
        try:
            response = requests.put(f"{BACKEND_URL}/workers/{worker_data['id']}", json=corrected_data)
            
            if response.status_code == 200:
                print(f"   ✅ Correction appliquée avec succès!")
                
                # Test immédiat après correction
                print(f"\n🧪 Test immédiat après correction:")
                test_response = requests.get(f"{BACKEND_URL}/payroll/bulk-preview", params={
                    'employer_id': 2,
                    'period': '2025-01',
                    'etablissement': 'Mandroso Formation'
                })
                
                if test_response.status_code == 200:
                    bulletins = test_response.json()
                    print(f"   ✅ {len(bulletins)} bulletin(s) après correction")
                    
                    if len(bulletins) > 0:
                        print(f"   🎉 PROBLÈME RÉSOLU! L'interface devrait maintenant fonctionner")
                        return True
                    else:
                        print(f"   ❌ Toujours aucun bulletin")
                else:
                    print(f"   ❌ Erreur test: {test_response.status_code}")
            else:
                print(f"   ❌ Erreur correction: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    return False

def main():
    """Fonction principale"""
    print("🚀 Vérification complète des données organisationnelles")
    print("=" * 70)
    
    # 1. Vérifier les données actuelles
    status, worker_data = verify_current_worker_data()
    
    # 2. Vérifier les sources de données
    verify_organizational_data_sources()
    
    # 3. Tester avec les valeurs actuelles
    if worker_data:
        test_filtering_with_actual_values(worker_data)
    
    # 4. Tester avec les valeurs interface
    test_filtering_with_interface_values()
    
    # 5. Corriger si nécessaire
    if status == "old_values":
        success = fix_worker_data_if_needed(status, worker_data)
        if success:
            print(f"\n🎉 SOLUTION TROUVÉE ET APPLIQUÉE!")
            print(f"L'interface de filtrage devrait maintenant fonctionner correctement.")
        else:
            print(f"\n❌ PROBLÈME PERSISTANT")
            print(f"Il faut investiguer plus en profondeur.")
    elif status == "new_values":
        print(f"\n🤔 MYSTÈRE")
        print(f"Les données semblent correctes mais l'interface ne fonctionne pas.")
        print(f"Il faut vérifier les logs backend avec les messages de debug ajoutés.")

if __name__ == "__main__":
    main()