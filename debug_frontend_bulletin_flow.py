#!/usr/bin/env python3
"""
Diagnostic du flux complet de génération de bulletins depuis l'interface
"""

import requests
import json

BACKEND_URL = "http://localhost:8000"

def test_complete_bulletin_flow():
    """Test le flux complet comme l'interface utilisateur"""
    print("🔍 Diagnostic du flux complet de génération de bulletins")
    print("=" * 70)
    
    employer_id = 2  # Mandroso Services
    period = "2025-01"
    
    print(f"📋 Employeur: {employer_id} (Mandroso Services)")
    print(f"📅 Période: {period}")
    print()
    
    # 1. Vérifier l'employeur existe
    print("1️⃣ VÉRIFICATION EMPLOYEUR:")
    print("-" * 35)
    
    try:
        response = requests.get(f"{BACKEND_URL}/employers")
        if response.status_code == 200:
            employers = response.json()
            mandroso = next((emp for emp in employers if emp['id'] == employer_id), None)
            
            if mandroso:
                print(f"✅ Employeur trouvé: {mandroso['raison_sociale']}")
                print(f"   ID: {mandroso['id']}")
            else:
                print("❌ Employeur Mandroso Services non trouvé")
                return
        else:
            print(f"❌ Erreur récupération employeurs: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Exception: {e}")
        return
    
    print()
    
    # 2. Récupérer les données organisationnelles (comme l'interface)
    print("2️⃣ DONNÉES ORGANISATIONNELLES:")
    print("-" * 40)
    
    try:
        # Test endpoint hiérarchique
        response = requests.get(f"{BACKEND_URL}/employers/{employer_id}/organizational-data/hierarchical")
        print(f"Hierarchical endpoint status: {response.status_code}")
        
        if response.status_code == 200:
            org_data = response.json()
            print("📊 Données hiérarchiques:")
            for key, values in org_data.items():
                print(f"   {key}: {values}")
            
            has_hierarchical = any(len(values) > 0 for values in org_data.values())
            print(f"   Données hiérarchiques disponibles: {'✅' if has_hierarchical else '❌'}")
        else:
            print(f"❌ Erreur données hiérarchiques: {response.status_code}")
        
        print()
        
        # Test endpoint workers (fallback)
        response = requests.get(f"{BACKEND_URL}/employers/{employer_id}/organizational-data/workers")
        print(f"Workers endpoint status: {response.status_code}")
        
        if response.status_code == 200:
            worker_data = response.json()
            print("📊 Données des salariés:")
            for key, values in worker_data.items():
                print(f"   {key}: {values}")
        else:
            print(f"❌ Erreur données salariés: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    print()
    
    # 3. Tester les salariés de l'employeur
    print("3️⃣ SALARIÉS DE L'EMPLOYEUR:")
    print("-" * 35)
    
    try:
        response = requests.get(f"{BACKEND_URL}/workers")
        if response.status_code == 200:
            all_workers = response.json()
            mandroso_workers = [w for w in all_workers if w.get('employer_id') == employer_id]
            
            print(f"📊 {len(mandroso_workers)} salarié(s) trouvé(s):")
            
            for worker in mandroso_workers:
                print(f"   👤 {worker.get('prenom', '')} {worker.get('nom', '')} (ID: {worker['id']})")
                print(f"      - Matricule: {worker.get('matricule', 'N/A')}")
                print(f"      - Établissement: '{worker.get('etablissement', 'N/A')}'")
                print(f"      - Département: '{worker.get('departement', 'N/A')}'")
                print(f"      - Service: '{worker.get('service', 'N/A')}'")
                print(f"      - Unité: '{worker.get('unite', 'N/A')}'")
                print(f"      - Salaire base: {worker.get('salaire_base', 0)}")
        else:
            print(f"❌ Erreur récupération salariés: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Exception: {e}")
        return
    
    print()
    
    # 4. Test génération sans filtres (comme interface "Traiter TOUT")
    print("4️⃣ TEST GÉNÉRATION SANS FILTRES:")
    print("-" * 40)
    
    try:
        response = requests.get(f"{BACKEND_URL}/payroll/bulk-preview", params={
            'employer_id': employer_id,
            'period': period
        })
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            bulletins = response.json()
            print(f"✅ {len(bulletins)} bulletin(s) généré(s)")
            
            if bulletins:
                for i, bulletin in enumerate(bulletins):
                    worker = bulletin['worker']
                    print(f"   📄 Bulletin {i+1}: {worker['prenom']} {worker['nom']}")
                    print(f"      - Salaire brut: {bulletin.get('totaux', {}).get('brut_total', 'N/A')}")
            else:
                print("⚠️ Aucun bulletin généré")
        else:
            try:
                error_data = response.json()
                print(f"❌ Erreur: {error_data}")
            except:
                print(f"❌ Erreur: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    print()
    
    # 5. Test avec filtres spécifiques (valeurs réelles du salarié)
    print("5️⃣ TEST AVEC FILTRES SPÉCIFIQUES:")
    print("-" * 40)
    
    if mandroso_workers:
        worker = mandroso_workers[0]
        etablissement = worker.get('etablissement')
        departement = worker.get('departement')
        
        print(f"🎯 Test avec les valeurs du salarié {worker.get('prenom', '')} {worker.get('nom', '')}:")
        print(f"   - Établissement: '{etablissement}'")
        print(f"   - Département: '{departement}'")
        
        # Test avec établissement
        if etablissement:
            try:
                response = requests.get(f"{BACKEND_URL}/payroll/bulk-preview", params={
                    'employer_id': employer_id,
                    'period': period,
                    'etablissement': etablissement
                })
                
                print(f"   Status avec établissement '{etablissement}': {response.status_code}")
                
                if response.status_code == 200:
                    bulletins = response.json()
                    print(f"   ✅ {len(bulletins)} bulletin(s) avec filtre établissement")
                else:
                    try:
                        error_data = response.json()
                        print(f"   ❌ Erreur: {error_data}")
                    except:
                        print(f"   ❌ Erreur: {response.text}")
            except Exception as e:
                print(f"   ❌ Exception: {e}")
        
        # Test avec département
        if departement:
            try:
                response = requests.get(f"{BACKEND_URL}/payroll/bulk-preview", params={
                    'employer_id': employer_id,
                    'period': period,
                    'departement': departement
                })
                
                print(f"   Status avec département '{departement}': {response.status_code}")
                
                if response.status_code == 200:
                    bulletins = response.json()
                    print(f"   ✅ {len(bulletins)} bulletin(s) avec filtre département")
                else:
                    try:
                        error_data = response.json()
                        print(f"   ❌ Erreur: {error_data}")
                    except:
                        print(f"   ❌ Erreur: {response.text}")
            except Exception as e:
                print(f"   ❌ Exception: {e}")
    
    print()
    
    # 6. Test URL complète comme l'interface
    print("6️⃣ TEST URL COMPLÈTE (SIMULATION INTERFACE):")
    print("-" * 50)
    
    if mandroso_workers:
        worker = mandroso_workers[0]
        etablissement = worker.get('etablissement')
        
        if etablissement:
            # Simuler l'URL que l'interface génère
            test_url = f"/payslips-bulk/{employer_id}/{period}?etablissement={etablissement}"
            print(f"🌐 URL simulée: {test_url}")
            
            # Test de l'API correspondante
            try:
                response = requests.get(f"{BACKEND_URL}/payroll/bulk-preview", params={
                    'employer_id': employer_id,
                    'period': period,
                    'etablissement': etablissement
                })
                
                print(f"Status: {response.status_code}")
                
                if response.status_code == 200:
                    bulletins = response.json()
                    print(f"✅ {len(bulletins)} bulletin(s) - Simulation interface réussie")
                    
                    if bulletins:
                        print("📄 Détails des bulletins:")
                        for bulletin in bulletins:
                            worker_info = bulletin['worker']
                            totaux = bulletin.get('totaux', {})
                            print(f"   - {worker_info['prenom']} {worker_info['nom']}")
                            print(f"     Brut: {totaux.get('brut_total', 0)} Ar")
                            print(f"     Net: {totaux.get('net_total', 0)} Ar")
                    else:
                        print("⚠️ Bulletins vides malgré le succès de l'API")
                else:
                    try:
                        error_data = response.json()
                        print(f"❌ Erreur simulation interface: {error_data}")
                    except:
                        print(f"❌ Erreur simulation interface: {response.text}")
            except Exception as e:
                print(f"❌ Exception simulation interface: {e}")
    
    print()
    print("🎯 DIAGNOSTIC COMPLET TERMINÉ")

if __name__ == "__main__":
    test_complete_bulletin_flow()