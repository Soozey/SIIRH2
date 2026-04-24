#!/usr/bin/env python3
"""
Comparaison entre bulletin individuel et bulletin avec filtres
"""

import requests
import json

BACKEND_URL = "http://localhost:8000"

def compare_bulletins():
    """Compare le bulletin individuel vs avec filtres"""
    print("🔍 Comparaison bulletin individuel vs avec filtres")
    print("=" * 70)
    
    worker_id = 2032  # Jeanne RAFARAVAVY
    employer_id = 2   # Mandroso Services
    period = "2025-01"
    
    # 1. Test bulletin individuel (comme "Prévisualiser ce bulletin")
    print("1️⃣ BULLETIN INDIVIDUEL (Prévisualiser ce bulletin):")
    print("-" * 55)
    
    try:
        response = requests.get(f"{BACKEND_URL}/payroll/preview", params={
            'worker_id': worker_id,
            'period': period
        })
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            bulletin = response.json()
            worker_info = bulletin['worker']
            totaux = bulletin.get('totaux', {})
            
            print(f"✅ Bulletin individuel généré")
            print(f"   👤 {worker_info['prenom']} {worker_info['nom']}")
            print(f"   🏢 Établissement: '{worker_info.get('etablissement', 'N/A')}'")
            print(f"   🏬 Département: '{worker_info.get('departement', 'N/A')}'")
            print(f"   💰 Brut total: {totaux.get('brut_total', 0)} Ar")
            print(f"   💵 Net total: {totaux.get('net_total', 0)} Ar")
            
            individual_success = True
            individual_brut = totaux.get('brut_total', 0)
            individual_etablissement = worker_info.get('etablissement', '')
            individual_departement = worker_info.get('departement', '')
        else:
            print(f"❌ Erreur bulletin individuel: {response.status_code}")
            individual_success = False
            individual_brut = 0
            individual_etablissement = ''
            individual_departement = ''
    except Exception as e:
        print(f"❌ Exception: {e}")
        individual_success = False
        individual_brut = 0
        individual_etablissement = ''
        individual_departement = ''
    
    print()
    
    # 2. Test bulletin en masse SANS filtres
    print("2️⃣ BULLETIN EN MASSE SANS FILTRES:")
    print("-" * 40)
    
    try:
        response = requests.get(f"{BACKEND_URL}/payroll/bulk-preview", params={
            'employer_id': employer_id,
            'period': period
        })
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            bulletins = response.json()
            print(f"✅ {len(bulletins)} bulletin(s) en masse sans filtres")
            
            if bulletins:
                bulletin = bulletins[0]  # Jeanne est le seul salarié
                worker_info = bulletin['worker']
                totaux = bulletin.get('totaux', {})
                
                print(f"   👤 {worker_info['prenom']} {worker_info['nom']}")
                print(f"   🏢 Établissement: '{worker_info.get('etablissement', 'N/A')}'")
                print(f"   🏬 Département: '{worker_info.get('departement', 'N/A')}'")
                print(f"   💰 Brut total: {totaux.get('brut_total', 0)} Ar")
                print(f"   💵 Net total: {totaux.get('net_total', 0)} Ar")
                
                bulk_no_filter_success = True
                bulk_no_filter_brut = totaux.get('brut_total', 0)
            else:
                print("   ⚠️ Aucun bulletin trouvé")
                bulk_no_filter_success = False
                bulk_no_filter_brut = 0
        else:
            print(f"❌ Erreur bulk sans filtres: {response.status_code}")
            bulk_no_filter_success = False
            bulk_no_filter_brut = 0
    except Exception as e:
        print(f"❌ Exception: {e}")
        bulk_no_filter_success = False
        bulk_no_filter_brut = 0
    
    print()
    
    # 3. Test bulletin en masse AVEC filtres (établissement)
    print("3️⃣ BULLETIN EN MASSE AVEC FILTRE ÉTABLISSEMENT:")
    print("-" * 50)
    
    if individual_success and individual_etablissement:
        try:
            response = requests.get(f"{BACKEND_URL}/payroll/bulk-preview", params={
                'employer_id': employer_id,
                'period': period,
                'etablissement': individual_etablissement
            })
            
            print(f"Status: {response.status_code}")
            print(f"Filtre appliqué: établissement = '{individual_etablissement}'")
            
            if response.status_code == 200:
                bulletins = response.json()
                print(f"✅ {len(bulletins)} bulletin(s) avec filtre établissement")
                
                if bulletins:
                    bulletin = bulletins[0]
                    worker_info = bulletin['worker']
                    totaux = bulletin.get('totaux', {})
                    
                    print(f"   👤 {worker_info['prenom']} {worker_info['nom']}")
                    print(f"   🏢 Établissement: '{worker_info.get('etablissement', 'N/A')}'")
                    print(f"   🏬 Département: '{worker_info.get('departement', 'N/A')}'")
                    print(f"   💰 Brut total: {totaux.get('brut_total', 0)} Ar")
                    print(f"   💵 Net total: {totaux.get('net_total', 0)} Ar")
                    
                    bulk_with_filter_success = True
                    bulk_with_filter_brut = totaux.get('brut_total', 0)
                else:
                    print("   ⚠️ Aucun bulletin trouvé avec filtre")
                    bulk_with_filter_success = False
                    bulk_with_filter_brut = 0
            else:
                print(f"❌ Erreur bulk avec filtre: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Détails: {error_data}")
                except:
                    print(f"   Détails: {response.text}")
                bulk_with_filter_success = False
                bulk_with_filter_brut = 0
        except Exception as e:
            print(f"❌ Exception: {e}")
            bulk_with_filter_success = False
            bulk_with_filter_brut = 0
    else:
        print("⚠️ Impossible de tester (pas d'établissement ou échec individuel)")
        bulk_with_filter_success = False
        bulk_with_filter_brut = 0
    
    print()
    
    # 4. Test avec filtre département
    print("4️⃣ BULLETIN EN MASSE AVEC FILTRE DÉPARTEMENT:")
    print("-" * 48)
    
    if individual_success and individual_departement:
        try:
            response = requests.get(f"{BACKEND_URL}/payroll/bulk-preview", params={
                'employer_id': employer_id,
                'period': period,
                'departement': individual_departement
            })
            
            print(f"Status: {response.status_code}")
            print(f"Filtre appliqué: département = '{individual_departement}'")
            
            if response.status_code == 200:
                bulletins = response.json()
                print(f"✅ {len(bulletins)} bulletin(s) avec filtre département")
                
                if bulletins:
                    bulletin = bulletins[0]
                    totaux = bulletin.get('totaux', {})
                    print(f"   💰 Brut total: {totaux.get('brut_total', 0)} Ar")
                    bulk_dept_success = True
                else:
                    print("   ⚠️ Aucun bulletin trouvé avec filtre département")
                    bulk_dept_success = False
            else:
                print(f"❌ Erreur bulk avec filtre département: {response.status_code}")
                bulk_dept_success = False
        except Exception as e:
            print(f"❌ Exception: {e}")
            bulk_dept_success = False
    else:
        print("⚠️ Impossible de tester (pas de département ou échec individuel)")
        bulk_dept_success = False
    
    print()
    
    # 5. Analyse comparative
    print("5️⃣ ANALYSE COMPARATIVE:")
    print("-" * 30)
    
    print(f"📊 Résultats:")
    print(f"   1. Bulletin individuel: {'✅' if individual_success else '❌'} (Brut: {individual_brut} Ar)")
    print(f"   2. Bulk sans filtres: {'✅' if bulk_no_filter_success else '❌'} (Brut: {bulk_no_filter_brut} Ar)")
    print(f"   3. Bulk avec filtre établissement: {'✅' if bulk_with_filter_success else '❌'} (Brut: {bulk_with_filter_brut} Ar)")
    print(f"   4. Bulk avec filtre département: {'✅' if bulk_dept_success else '❌'}")
    
    print(f"\n🔍 Diagnostic:")
    
    if individual_success and not bulk_with_filter_success:
        print("❌ PROBLÈME IDENTIFIÉ: Le filtrage organisationnel ne fonctionne pas")
        print("🔧 Causes possibles:")
        print("   - Incohérence entre les valeurs d'établissement/département")
        print("   - Problème dans la logique de filtrage du backend")
        print("   - Erreur dans la requête SQL avec filtres")
        
        print(f"\n📋 Données du salarié:")
        print(f"   - Établissement: '{individual_etablissement}'")
        print(f"   - Département: '{individual_departement}'")
        
    elif individual_success and bulk_with_filter_success and individual_brut != bulk_with_filter_brut:
        print("⚠️ PROBLÈME PARTIEL: Le filtrage fonctionne mais les montants diffèrent")
        print("🔧 Possible problème dans le calcul avec filtres")
        
    elif individual_success and bulk_with_filter_success and individual_brut == bulk_with_filter_brut:
        print("✅ TOUT FONCTIONNE: Le filtrage organisationnel est opérationnel")
        
    else:
        print("❌ PROBLÈME GÉNÉRAL: Le calcul de paie ne fonctionne pas du tout")

def test_specific_filter_values():
    """Test avec des valeurs de filtres spécifiques"""
    print("\n🧪 TEST AVEC VALEURS SPÉCIFIQUES:")
    print("-" * 40)
    
    employer_id = 2
    period = "2025-01"
    
    # Valeurs connues après nos corrections
    test_filters = [
        {"etablissement": "Mandroso Formation"},
        {"departement": "EN LIGNE"},
        {"etablissement": "Mandroso Formation", "departement": "EN LIGNE"},
        {"etablissement": "54"},  # Ancienne valeur
        {"departement": "55"},    # Ancienne valeur
    ]
    
    for i, filters in enumerate(test_filters, 1):
        print(f"\n{i}. Test avec filtres: {filters}")
        
        try:
            params = {
                'employer_id': employer_id,
                'period': period,
                **filters
            }
            
            response = requests.get(f"{BACKEND_URL}/payroll/bulk-preview", params=params)
            
            if response.status_code == 200:
                bulletins = response.json()
                print(f"   ✅ {len(bulletins)} bulletin(s) trouvé(s)")
                
                if bulletins:
                    for bulletin in bulletins:
                        worker = bulletin['worker']
                        totaux = bulletin.get('totaux', {})
                        print(f"      👤 {worker['prenom']} {worker['nom']}")
                        print(f"         Établissement: '{worker.get('etablissement', 'N/A')}'")
                        print(f"         Département: '{worker.get('departement', 'N/A')}'")
                        print(f"         Brut: {totaux.get('brut_total', 0)} Ar")
            else:
                print(f"   ❌ Erreur: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")

def main():
    """Fonction principale"""
    compare_bulletins()
    test_specific_filter_values()

if __name__ == "__main__":
    main()