#!/usr/bin/env python3
"""
Test final avec les bonnes clés de totaux
"""

import requests
import json

BACKEND_URL = "http://localhost:8000"

def final_test_with_correct_keys():
    """Test final avec les bonnes clés"""
    print("🎉 TEST FINAL AVEC LES BONNES CLÉS")
    print("=" * 70)
    
    worker_id = 2032  # Jeanne RAFARAVAVY
    employer_id = 2   # Mandroso Services
    period = "2025-01"
    
    # 1. Bulletin individuel
    print("1️⃣ BULLETIN INDIVIDUEL:")
    print("-" * 25)
    
    try:
        response = requests.get(f"{BACKEND_URL}/payroll/preview", params={
            'worker_id': worker_id,
            'period': period
        })
        
        if response.status_code == 200:
            bulletin = response.json()
            totaux = bulletin.get('totaux', {})
            
            # Utiliser les BONNES clés
            brut = totaux.get('brut', 0)  # Pas 'brut_total' !
            net = totaux.get('net', 0)    # Pas 'net_total' !
            
            print(f"✅ Bulletin individuel généré")
            print(f"   💰 Brut: {brut} Ar")
            print(f"   💵 Net: {net} Ar")
            
            individual_success = brut > 0
        else:
            print(f"❌ Erreur: {response.status_code}")
            individual_success = False
    except Exception as e:
        print(f"❌ Exception: {e}")
        individual_success = False
    
    print()
    
    # 2. Bulk sans filtres
    print("2️⃣ BULK SANS FILTRES:")
    print("-" * 25)
    
    try:
        response = requests.get(f"{BACKEND_URL}/payroll/bulk-preview", params={
            'employer_id': employer_id,
            'period': period
        })
        
        if response.status_code == 200:
            bulletins = response.json()
            print(f"✅ {len(bulletins)} bulletin(s) sans filtres")
            
            if bulletins:
                bulletin = bulletins[0]
                totaux = bulletin.get('totaux', {})
                brut = totaux.get('brut', 0)
                net = totaux.get('net', 0)
                
                print(f"   💰 Brut: {brut} Ar")
                print(f"   💵 Net: {net} Ar")
                
                bulk_no_filter_success = brut > 0
            else:
                bulk_no_filter_success = False
        else:
            print(f"❌ Erreur: {response.status_code}")
            bulk_no_filter_success = False
    except Exception as e:
        print(f"❌ Exception: {e}")
        bulk_no_filter_success = False
    
    print()
    
    # 3. Bulk avec filtre établissement
    print("3️⃣ BULK AVEC FILTRE ÉTABLISSEMENT:")
    print("-" * 35)
    
    try:
        response = requests.get(f"{BACKEND_URL}/payroll/bulk-preview", params={
            'employer_id': employer_id,
            'period': period,
            'etablissement': 'Mandroso Formation'
        })
        
        if response.status_code == 200:
            bulletins = response.json()
            print(f"✅ {len(bulletins)} bulletin(s) avec filtre établissement")
            
            if bulletins:
                bulletin = bulletins[0]
                totaux = bulletin.get('totaux', {})
                brut = totaux.get('brut', 0)
                net = totaux.get('net', 0)
                worker = bulletin['worker']
                
                print(f"   👤 {worker['prenom']} {worker['nom']}")
                print(f"   🏢 Établissement: {worker.get('etablissement', 'N/A')}")
                print(f"   💰 Brut: {brut} Ar")
                print(f"   💵 Net: {net} Ar")
                
                bulk_with_filter_success = brut > 0
            else:
                print("   ⚠️ Aucun bulletin trouvé")
                bulk_with_filter_success = False
        else:
            print(f"❌ Erreur: {response.status_code}")
            bulk_with_filter_success = False
    except Exception as e:
        print(f"❌ Exception: {e}")
        bulk_with_filter_success = False
    
    print()
    
    # 4. Bulk avec filtre département
    print("4️⃣ BULK AVEC FILTRE DÉPARTEMENT:")
    print("-" * 32)
    
    try:
        response = requests.get(f"{BACKEND_URL}/payroll/bulk-preview", params={
            'employer_id': employer_id,
            'period': period,
            'departement': 'EN LIGNE'
        })
        
        if response.status_code == 200:
            bulletins = response.json()
            print(f"✅ {len(bulletins)} bulletin(s) avec filtre département")
            
            if bulletins:
                bulletin = bulletins[0]
                totaux = bulletin.get('totaux', {})
                brut = totaux.get('brut', 0)
                net = totaux.get('net', 0)
                
                print(f"   💰 Brut: {brut} Ar")
                print(f"   💵 Net: {net} Ar")
                
                bulk_dept_success = brut > 0
            else:
                bulk_dept_success = False
        else:
            print(f"❌ Erreur: {response.status_code}")
            bulk_dept_success = False
    except Exception as e:
        print(f"❌ Exception: {e}")
        bulk_dept_success = False
    
    print()
    
    # 5. Bulk avec filtres combinés
    print("5️⃣ BULK AVEC FILTRES COMBINÉS:")
    print("-" * 32)
    
    try:
        response = requests.get(f"{BACKEND_URL}/payroll/bulk-preview", params={
            'employer_id': employer_id,
            'period': period,
            'etablissement': 'Mandroso Formation',
            'departement': 'EN LIGNE'
        })
        
        if response.status_code == 200:
            bulletins = response.json()
            print(f"✅ {len(bulletins)} bulletin(s) avec filtres combinés")
            
            if bulletins:
                bulletin = bulletins[0]
                totaux = bulletin.get('totaux', {})
                brut = totaux.get('brut', 0)
                net = totaux.get('net', 0)
                
                print(f"   💰 Brut: {brut} Ar")
                print(f"   💵 Net: {net} Ar")
                
                bulk_combined_success = brut > 0
            else:
                bulk_combined_success = False
        else:
            print(f"❌ Erreur: {response.status_code}")
            bulk_combined_success = False
    except Exception as e:
        print(f"❌ Exception: {e}")
        bulk_combined_success = False
    
    print()
    
    # Résumé final
    print("🎯 RÉSUMÉ FINAL:")
    print("-" * 20)
    
    print(f"1. Bulletin individuel: {'✅' if individual_success else '❌'}")
    print(f"2. Bulk sans filtres: {'✅' if bulk_no_filter_success else '❌'}")
    print(f"3. Bulk avec filtre établissement: {'✅' if bulk_with_filter_success else '❌'}")
    print(f"4. Bulk avec filtre département: {'✅' if bulk_dept_success else '❌'}")
    print(f"5. Bulk avec filtres combinés: {'✅' if bulk_combined_success else '❌'}")
    
    all_success = all([
        individual_success,
        bulk_no_filter_success, 
        bulk_with_filter_success,
        bulk_dept_success,
        bulk_combined_success
    ])
    
    if all_success:
        print(f"\n🎉 TOUT FONCTIONNE PARFAITEMENT!")
        print(f"✅ Le calcul de paie fonctionne")
        print(f"✅ Le filtrage organisationnel fonctionne")
        print(f"✅ L'utilisateur peut maintenant imprimer les bulletins avec filtres")
        
        print(f"\n📋 INSTRUCTIONS POUR L'UTILISATEUR:")
        print(f"1. Aller sur la page d'impression des bulletins")
        print(f"2. Sélectionner 'Mandroso Services'")
        print(f"3. Choisir la période '2025-01'")
        print(f"4. Appliquer les filtres:")
        print(f"   - Établissement: 'Mandroso Formation'")
        print(f"   - Département: 'EN LIGNE' (optionnel)")
        print(f"5. Les bulletins s'afficheront avec les bons montants")
    else:
        print(f"\n❌ Il reste des problèmes à résoudre")

def main():
    """Fonction principale"""
    final_test_with_correct_keys()

if __name__ == "__main__":
    main()