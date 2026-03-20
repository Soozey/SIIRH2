#!/usr/bin/env python3
"""
Debug du comportement réel de l'interface utilisateur
"""

import requests
import json
from urllib.parse import urlencode

BACKEND_URL = "http://localhost:8000"

def debug_frontend_real_behavior():
    """Debug le comportement réel de l'interface"""
    print("🔍 Debug du comportement réel de l'interface utilisateur")
    print("=" * 70)
    
    employer_id = 2   # Mandroso Services
    period = "2025-01"
    
    print(f"📋 Paramètres de test:")
    print(f"   - Employeur ID: {employer_id}")
    print(f"   - Période: {period}")
    print()
    
    # 1. Vérifier d'abord les données actuelles du salarié
    print("1️⃣ VÉRIFICATION DONNÉES ACTUELLES DU SALARIÉ:")
    print("-" * 50)
    
    try:
        response = requests.get(f"{BACKEND_URL}/workers")
        if response.status_code == 200:
            workers = response.json()
            mandroso_workers = [w for w in workers if w.get('employer_id') == employer_id]
            
            if mandroso_workers:
                worker = mandroso_workers[0]
                print(f"👤 {worker['prenom']} {worker['nom']} (ID: {worker['id']})")
                print(f"   - Établissement: '{worker.get('etablissement', 'N/A')}'")
                print(f"   - Département: '{worker.get('departement', 'N/A')}'")
                print(f"   - Service: '{worker.get('service', 'N/A')}'")
                print(f"   - Unité: '{worker.get('unite', 'N/A')}'")
                
                current_etablissement = worker.get('etablissement', '')
                current_departement = worker.get('departement', '')
            else:
                print("❌ Aucun salarié trouvé pour Mandroso Services")
                return
        else:
            print(f"❌ Erreur récupération salariés: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Exception: {e}")
        return
    
    print()
    
    # 2. Tester différents formats d'URL comme l'interface pourrait les générer
    print("2️⃣ TEST DIFFÉRENTS FORMATS D'URL:")
    print("-" * 40)
    
    # Formats possibles que l'interface pourrait utiliser
    test_scenarios = [
        {
            "name": "URL avec query string (comme React Router)",
            "url": f"/payslips-bulk/{employer_id}/{period}?etablissement={current_etablissement}",
            "params": {
                'employer_id': employer_id,
                'period': period,
                'etablissement': current_etablissement
            }
        },
        {
            "name": "URL avec query string encodée",
            "url": f"/payslips-bulk/{employer_id}/{period}?{urlencode({'etablissement': current_etablissement})}",
            "params": {
                'employer_id': employer_id,
                'period': period,
                'etablissement': current_etablissement
            }
        },
        {
            "name": "Paramètres avec espaces (non encodés)",
            "url": f"/payslips-bulk/{employer_id}/{period}?etablissement=Mandroso Formation",
            "params": {
                'employer_id': employer_id,
                'period': period,
                'etablissement': 'Mandroso Formation'
            }
        },
        {
            "name": "Paramètres avec espaces (encodés)",
            "url": f"/payslips-bulk/{employer_id}/{period}?etablissement=Mandroso%20Formation",
            "params": {
                'employer_id': employer_id,
                'period': period,
                'etablissement': 'Mandroso Formation'
            }
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{i}. {scenario['name']}:")
        print(f"   URL simulée: {scenario['url']}")
        
        try:
            response = requests.get(f"{BACKEND_URL}/payroll/bulk-preview", params=scenario['params'])
            
            print(f"   Status: {response.status_code}")
            print(f"   URL réelle: {response.url}")
            
            if response.status_code == 200:
                bulletins = response.json()
                print(f"   ✅ {len(bulletins)} bulletin(s) trouvé(s)")
                
                if bulletins:
                    bulletin = bulletins[0]
                    totaux = bulletin.get('totaux', {})
                    brut = totaux.get('brut', 0)
                    worker_info = bulletin['worker']
                    
                    print(f"      👤 {worker_info['prenom']} {worker_info['nom']}")
                    print(f"      🏢 Établissement: '{worker_info.get('etablissement', 'N/A')}'")
                    print(f"      💰 Brut: {brut} Ar")
                else:
                    print(f"   ⚠️ Aucun bulletin dans la réponse")
            else:
                print(f"   ❌ Erreur: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"      Détails: {error_data}")
                except:
                    print(f"      Détails: {response.text}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    print()
    
    # 3. Tester avec les données organisationnelles disponibles
    print("3️⃣ TEST AVEC DONNÉES ORGANISATIONNELLES DISPONIBLES:")
    print("-" * 55)
    
    try:
        # Récupérer les données organisationnelles comme l'interface
        org_response = requests.get(f"{BACKEND_URL}/employers/{employer_id}/organizational-data/hierarchical")
        
        if org_response.status_code == 200:
            org_data = org_response.json()
            
            print("📊 Données organisationnelles disponibles:")
            for key, values in org_data.items():
                print(f"   {key}: {values}")
            
            # Tester avec chaque valeur disponible
            etablissements = org_data.get('etablissements', [])
            departements = org_data.get('departements', [])
            
            for etablissement in etablissements:
                print(f"\n🧪 Test avec établissement: '{etablissement}'")
                
                response = requests.get(f"{BACKEND_URL}/payroll/bulk-preview", params={
                    'employer_id': employer_id,
                    'period': period,
                    'etablissement': etablissement
                })
                
                if response.status_code == 200:
                    bulletins = response.json()
                    print(f"   ✅ {len(bulletins)} bulletin(s) avec '{etablissement}'")
                    
                    if bulletins:
                        bulletin = bulletins[0]
                        worker_info = bulletin['worker']
                        print(f"      👤 {worker_info['prenom']} {worker_info['nom']}")
                        print(f"      🏢 Établissement du salarié: '{worker_info.get('etablissement', 'N/A')}'")
                        
                        # Vérifier la correspondance
                        if worker_info.get('etablissement') == etablissement:
                            print(f"      ✅ CORRESPONDANCE PARFAITE")
                        else:
                            print(f"      ❌ PAS DE CORRESPONDANCE")
                            print(f"         Attendu: '{etablissement}'")
                            print(f"         Trouvé: '{worker_info.get('etablissement', 'N/A')}'")
                else:
                    print(f"   ❌ Erreur avec '{etablissement}': {response.status_code}")
            
            for departement in departements:
                print(f"\n🧪 Test avec département: '{departement}'")
                
                response = requests.get(f"{BACKEND_URL}/payroll/bulk-preview", params={
                    'employer_id': employer_id,
                    'period': period,
                    'departement': departement
                })
                
                if response.status_code == 200:
                    bulletins = response.json()
                    print(f"   ✅ {len(bulletins)} bulletin(s) avec '{departement}'")
                    
                    if bulletins:
                        bulletin = bulletins[0]
                        worker_info = bulletin['worker']
                        print(f"      👤 {worker_info['prenom']} {worker_info['nom']}")
                        print(f"      🏬 Département du salarié: '{worker_info.get('departement', 'N/A')}'")
                        
                        # Vérifier la correspondance
                        if worker_info.get('departement') == departement:
                            print(f"      ✅ CORRESPONDANCE PARFAITE")
                        else:
                            print(f"      ❌ PAS DE CORRESPONDANCE")
                            print(f"         Attendu: '{departement}'")
                            print(f"         Trouvé: '{worker_info.get('departement', 'N/A')}'")
                else:
                    print(f"   ❌ Erreur avec '{departement}': {response.status_code}")
        else:
            print(f"❌ Erreur récupération données organisationnelles: {org_response.status_code}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    print()
    
    # 4. Recommandations
    print("4️⃣ RECOMMANDATIONS:")
    print("-" * 25)
    
    print("🔧 Pour identifier le problème exact:")
    print("1. Ouvrez les outils de développement (F12) dans votre navigateur")
    print("2. Allez dans l'onglet 'Network' (Réseau)")
    print("3. Essayez d'imprimer avec filtres dans l'interface")
    print("4. Regardez l'appel API qui est fait vers /payroll/bulk-preview")
    print("5. Vérifiez les paramètres exacts envoyés")
    print()
    print("📋 Vérifiez aussi:")
    print("- Que l'établissement sélectionné correspond exactement à celui du salarié")
    print("- Que les paramètres ne contiennent pas de caractères spéciaux")
    print("- Que l'encodage des URL est correct")

def test_exact_interface_simulation():
    """Simule exactement ce que fait l'interface PayslipsBulk"""
    print("\n🎯 SIMULATION EXACTE DE L'INTERFACE:")
    print("-" * 45)
    
    # Simuler le flux exact de PayslipsBulk.tsx
    employer_id = 2
    period = "2025-01"
    
    # Paramètres comme dans l'interface (avec searchParams)
    search_params = {
        'etablissement': 'Mandroso Formation',
        # 'departement': 'EN LIGNE',  # Optionnel
    }
    
    print(f"🌐 Simulation du composant PayslipsBulk:")
    print(f"   useParams: employerId={employer_id}, period={period}")
    print(f"   searchParams: {search_params}")
    
    # Construction des paramètres comme dans le code
    params = {
        'employer_id': employer_id,
        'period': period
    }
    
    # Ajouter les filtres comme dans le code
    for key, value in search_params.items():
        if value:
            params[key] = value
    
    print(f"   Paramètres finaux: {params}")
    
    try:
        response = requests.get(f"{BACKEND_URL}/payroll/bulk-preview", params=params)
        
        print(f"   Status: {response.status_code}")
        print(f"   URL: {response.url}")
        
        if response.status_code == 200:
            bulletins = response.json()
            print(f"   ✅ {len(bulletins)} bulletin(s) - Interface simulation réussie")
            
            if bulletins:
                bulletin = bulletins[0]
                totaux = bulletin.get('totaux', {})
                brut = totaux.get('brut', 0)
                print(f"      💰 Brut: {brut} Ar")
            else:
                print(f"      ⚠️ Liste vide - C'est ça le problème!")
        else:
            print(f"   ❌ Erreur simulation: {response.status_code}")
            try:
                error_data = response.json()
                print(f"      Détails: {error_data}")
            except:
                print(f"      Détails: {response.text}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")

def main():
    """Fonction principale"""
    debug_frontend_real_behavior()
    test_exact_interface_simulation()

if __name__ == "__main__":
    main()