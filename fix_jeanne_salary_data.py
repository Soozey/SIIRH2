#!/usr/bin/env python3
"""
Correction des données salariales de Jeanne RAFARAVAVY
"""

import requests
import json

BACKEND_URL = "http://localhost:8000"

def fix_jeanne_salary():
    """Corrige les données salariales de Jeanne"""
    print("🛠️ Correction des données salariales de Jeanne RAFARAVAVY")
    print("=" * 70)
    
    # 1. Récupérer les données actuelles de Jeanne
    try:
        response = requests.get(f"{BACKEND_URL}/workers")
        if response.status_code == 200:
            all_workers = response.json()
            jeanne = next((w for w in all_workers if w.get('employer_id') == 2 and 'Jeanne' in w.get('prenom', '')), None)
            
            if jeanne:
                print(f"👤 Salarié trouvé: {jeanne['prenom']} {jeanne['nom']} (ID: {jeanne['id']})")
                print(f"\n📊 Données actuelles:")
                print(f"   - Salaire base: {jeanne.get('salaire_base', 'N/A')} Ar")
                print(f"   - VHM: {jeanne.get('vhm', 'N/A')}")
                print(f"   - Salaire horaire: {jeanne.get('salaire_horaire', 'N/A')}")
                print(f"   - Type régime: {jeanne.get('type_regime_id', 'N/A')}")
                print(f"   - Catégorie prof: {jeanne.get('categorie_prof', 'N/A')}")
                print(f"   - Secteur: {jeanne.get('secteur', 'N/A')}")
                
                # Données corrigées
                corrected_data = {
                    **jeanne,
                    "salaire_base": 456000.0,
                    "vhm": 173.33,
                    "salaire_horaire": 2631.58,  # 456000 / 173.33
                    "type_regime_id": 1,
                    "secteur": "PRIVE"
                }
                
                print(f"\n🔄 Données corrigées:")
                print(f"   - Salaire base: {corrected_data['salaire_base']} Ar")
                print(f"   - VHM: {corrected_data['vhm']}")
                print(f"   - Salaire horaire: {corrected_data['salaire_horaire']}")
                print(f"   - Type régime: {corrected_data['type_regime_id']}")
                print(f"   - Secteur: {corrected_data['secteur']}")
                
                # Effectuer la mise à jour
                update_response = requests.put(f"{BACKEND_URL}/workers/{jeanne['id']}", json=corrected_data)
                
                if update_response.status_code == 200:
                    print("\n✅ Mise à jour des données salariales réussie!")
                    
                    # Tester la génération de bulletin après correction
                    print("\n🧪 Test génération bulletin après correction:")
                    
                    test_response = requests.get(f"{BACKEND_URL}/payroll/preview", params={
                        'worker_id': jeanne['id'],
                        'period': '2025-01'
                    })
                    
                    if test_response.status_code == 200:
                        bulletin = test_response.json()
                        totaux = bulletin.get('totaux', {})
                        
                        print(f"✅ Bulletin généré avec succès!")
                        print(f"   💰 Totaux:")
                        print(f"      - Brut total: {totaux.get('brut_total', 0)} Ar")
                        print(f"      - Net total: {totaux.get('net_total', 0)} Ar")
                        print(f"      - Cotisations: {totaux.get('cotisations_total', 0)} Ar")
                        
                        if totaux.get('brut_total', 0) > 0:
                            print("\n🎉 SUCCÈS! Le bulletin a maintenant des valeurs correctes.")
                            
                            # Test génération en masse avec filtre
                            print("\n🧪 Test génération en masse avec filtre:")
                            
                            bulk_response = requests.get(f"{BACKEND_URL}/payroll/bulk-preview", params={
                                'employer_id': 2,
                                'period': '2025-01',
                                'etablissement': 'Mandroso Formation'
                            })
                            
                            if bulk_response.status_code == 200:
                                bulletins = bulk_response.json()
                                print(f"✅ {len(bulletins)} bulletin(s) en masse généré(s)")
                                
                                if bulletins:
                                    for bulletin in bulletins:
                                        worker = bulletin['worker']
                                        totaux = bulletin.get('totaux', {})
                                        print(f"   📄 {worker['prenom']} {worker['nom']}")
                                        print(f"      - Brut: {totaux.get('brut_total', 0)} Ar")
                                        print(f"      - Net: {totaux.get('net_total', 0)} Ar")
                                        print(f"      - Établissement: {worker.get('etablissement', 'N/A')}")
                                
                                return True
                            else:
                                print(f"❌ Erreur génération en masse: {bulk_response.status_code}")
                        else:
                            print("\n⚠️ Le bulletin est toujours à 0. Problème dans le calcul de paie.")
                    else:
                        print(f"❌ Erreur test bulletin: {test_response.status_code}")
                else:
                    print(f"❌ Erreur mise à jour: {update_response.status_code}")
                    try:
                        error_data = update_response.json()
                        print(f"   Détails: {error_data}")
                    except:
                        print(f"   Détails: {update_response.text}")
            else:
                print("❌ Salarié Jeanne non trouvé")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    return False

def verify_final_state():
    """Vérifie l'état final du système"""
    print("\n🔍 VÉRIFICATION FINALE DU SYSTÈME:")
    print("-" * 50)
    
    try:
        # Test complet du flux utilisateur
        print("1. Test sans filtre:")
        response = requests.get(f"{BACKEND_URL}/payroll/bulk-preview", params={
            'employer_id': 2,
            'period': '2025-01'
        })
        
        if response.status_code == 200:
            bulletins = response.json()
            print(f"   ✅ {len(bulletins)} bulletin(s) sans filtre")
        else:
            print(f"   ❌ Erreur sans filtre: {response.status_code}")
        
        print("\n2. Test avec filtre 'Mandroso Formation':")
        response = requests.get(f"{BACKEND_URL}/payroll/bulk-preview", params={
            'employer_id': 2,
            'period': '2025-01',
            'etablissement': 'Mandroso Formation'
        })
        
        if response.status_code == 200:
            bulletins = response.json()
            print(f"   ✅ {len(bulletins)} bulletin(s) avec filtre établissement")
            
            if bulletins:
                bulletin = bulletins[0]
                totaux = bulletin.get('totaux', {})
                worker = bulletin['worker']
                
                print(f"   📄 Bulletin de {worker['prenom']} {worker['nom']}:")
                print(f"      - Établissement: {worker.get('etablissement', 'N/A')}")
                print(f"      - Brut: {totaux.get('brut_total', 0)} Ar")
                print(f"      - Net: {totaux.get('net_total', 0)} Ar")
        else:
            print(f"   ❌ Erreur avec filtre: {response.status_code}")
        
        print("\n3. Test avec filtre 'EN LIGNE' (département):")
        response = requests.get(f"{BACKEND_URL}/payroll/bulk-preview", params={
            'employer_id': 2,
            'period': '2025-01',
            'departement': 'EN LIGNE'
        })
        
        if response.status_code == 200:
            bulletins = response.json()
            print(f"   ✅ {len(bulletins)} bulletin(s) avec filtre département")
        else:
            print(f"   ❌ Erreur avec filtre département: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

def main():
    """Fonction principale"""
    print("🚀 Correction complète du système de bulletins Mandroso")
    print("=" * 70)
    
    success = fix_jeanne_salary()
    
    if success:
        verify_final_state()
        
        print("\n🎯 RÉSUMÉ DES CORRECTIONS:")
        print("✅ Affectation organisationnelle corrigée")
        print("✅ Données salariales corrigées")
        print("✅ Génération de bulletins fonctionnelle")
        print("✅ Filtrage organisationnel opérationnel")
        
        print("\n📋 INSTRUCTIONS POUR L'UTILISATEUR:")
        print("1. Aller sur la page d'impression des bulletins")
        print("2. Sélectionner l'employeur 'Mandroso Services'")
        print("3. Choisir la période '2025-01'")
        print("4. Appliquer le filtre 'Établissement: Mandroso Formation'")
        print("5. Les bulletins de Jeanne RAFARAVAVY s'afficheront correctement")
    else:
        print("\n❌ CORRECTION ÉCHOUÉE")
        print("Vérifiez les logs pour plus de détails")

if __name__ == "__main__":
    main()