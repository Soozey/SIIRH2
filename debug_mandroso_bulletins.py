#!/usr/bin/env python3
"""
Diagnostic pour l'employeur Mandroso Services - problème "Aucun bulletin"
"""

import requests
import json

BACKEND_URL = "http://localhost:8000"

def find_mandroso_employer():
    """Trouve l'employeur Mandroso Services"""
    try:
        response = requests.get(f"{BACKEND_URL}/employers")
        if response.status_code != 200:
            return None
        
        employers = response.json()
        for employer in employers:
            if "Mandroso" in employer.get('raison_sociale', ''):
                return employer
        
        return None
    except:
        return None

def analyze_mandroso_data(employer):
    """Analyse les données de l'employeur Mandroso"""
    print(f"🔍 Analyse de {employer['raison_sociale']} (ID: {employer['id']})")
    print("=" * 60)
    
    employer_id = employer['id']
    
    # 1. Vérifier les salariés
    print("👥 SALARIÉS:")
    print("-" * 30)
    
    try:
        response = requests.get(f"{BACKEND_URL}/workers")
        if response.status_code == 200:
            workers = response.json()
            mandroso_workers = [w for w in workers if w.get('employer_id') == employer_id]
            
            print(f"📊 {len(mandroso_workers)} salarié(s) trouvé(s):")
            
            for worker in mandroso_workers:
                name = f"{worker.get('prenom', '')} {worker.get('nom', '')}"
                matricule = worker.get('matricule', 'N/A')
                salaire_base = worker.get('salaire_base', 0)
                
                print(f"   👤 {name} (Matricule: {matricule})")
                print(f"      - ID: {worker['id']}")
                print(f"      - Salaire base: {salaire_base}")
                print(f"      - Type régime: {worker.get('type_regime_id', 'N/A')}")
                print(f"      - VHM: {worker.get('vhm', 'N/A')}")
                print(f"      - Établissement: {worker.get('etablissement', 'N/A')}")
        else:
            print("❌ Impossible de récupérer les salariés")
            return False
    except Exception as e:
        print(f"❌ Erreur salariés: {e}")
        return False
    
    # 2. Tester l'endpoint bulk-preview avec différentes périodes
    print(f"\n💰 TEST BULLETINS:")
    print("-" * 30)
    
    periods = ["2025-01", "2024-12", "2024-11", "2024-10"]
    
    for period in periods:
        print(f"\n📅 Période {period}:")
        
        try:
            # Test sans filtres
            response = requests.get(f"{BACKEND_URL}/payroll/bulk-preview", params={
                'employer_id': employer_id,
                'period': period
            })
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                bulletins = response.json()
                print(f"   ✅ {len(bulletins)} bulletin(s) trouvé(s)")
                
                if len(bulletins) > 0:
                    print(f"   🎉 BULLETINS DISPONIBLES pour {period}!")
                    return True, period
                else:
                    print(f"   ⚠️ Aucun bulletin pour {period}")
            else:
                try:
                    error_data = response.json()
                    print(f"   ❌ Erreur: {error_data}")
                except:
                    print(f"   ❌ Erreur: {response.text}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    # 3. Tester l'endpoint preview individuel
    print(f"\n🧪 TEST BULLETIN INDIVIDUEL:")
    print("-" * 30)
    
    if mandroso_workers:
        worker = mandroso_workers[0]
        worker_id = worker['id']
        
        for period in periods:
            print(f"\n📅 {worker.get('prenom', '')} {worker.get('nom', '')} - {period}:")
            
            try:
                response = requests.get(f"{BACKEND_URL}/payroll/preview", params={
                    'worker_id': worker_id,
                    'period': period
                })
                
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    bulletin_data = response.json()
                    print(f"   ✅ Bulletin généré avec succès")
                    print(f"   💰 Salaire brut: {bulletin_data.get('brut_total', 'N/A')}")
                    return True, period
                else:
                    try:
                        error_data = response.json()
                        print(f"   ❌ Erreur: {error_data.get('detail', 'Erreur inconnue')}")
                    except:
                        print(f"   ❌ Erreur: {response.text}")
            except Exception as e:
                print(f"   ❌ Exception: {e}")
    
    return False, None

def suggest_solutions(employer, has_workers):
    """Suggère des solutions pour résoudre le problème"""
    print(f"\n💡 SOLUTIONS PROPOSÉES:")
    print("=" * 60)
    
    if not has_workers:
        print("🔧 PROBLÈME: Aucun salarié trouvé")
        print("📋 SOLUTIONS:")
        print("1. Créer un salarié pour cet employeur")
        print("2. Vérifier que les salariés sont bien assignés à cet employeur")
    else:
        print("🔧 PROBLÈME: Salariés présents mais aucun bulletin généré")
        print("📋 SOLUTIONS:")
        print("1. 💰 VÉRIFIER LES DONNÉES SALARIALES:")
        print("   - Salaire de base > 0")
        print("   - VHM configuré (ex: 173.33)")
        print("   - Type de régime assigné")
        print()
        print("2. 📅 VÉRIFIER LA PÉRIODE:")
        print("   - Utiliser une période récente (2025-01)")
        print("   - Vérifier le format YYYY-MM")
        print()
        print("3. 🔧 CRÉER UN BULLETIN MANUELLEMENT:")
        print("   - Aller sur /payroll")
        print("   - Sélectionner le salarié")
        print("   - Choisir la période 2025-01")
        print("   - Cliquer sur 'Prévisualiser ce bulletin'")
        print()
        print("4. 🏢 VÉRIFIER L'EMPLOYEUR:")
        print("   - Type de régime configuré")
        print("   - Paramètres de paie corrects")

def create_test_bulletin(employer_id, worker_id):
    """Essaie de créer un bulletin de test"""
    print(f"\n🛠️ CRÉATION D'UN BULLETIN DE TEST:")
    print("-" * 50)
    
    period = "2025-01"
    
    try:
        print(f"🧪 Génération bulletin pour salarié {worker_id}, période {period}...")
        
        response = requests.get(f"{BACKEND_URL}/payroll/preview", params={
            'worker_id': worker_id,
            'period': period
        })
        
        if response.status_code == 200:
            print("✅ Bulletin de test créé avec succès!")
            
            # Tester maintenant l'endpoint bulk
            response = requests.get(f"{BACKEND_URL}/payroll/bulk-preview", params={
                'employer_id': employer_id,
                'period': period
            })
            
            if response.status_code == 200:
                bulletins = response.json()
                print(f"✅ Bulk-preview fonctionne maintenant: {len(bulletins)} bulletin(s)")
                return True
            else:
                print(f"❌ Bulk-preview échoue encore: {response.status_code}")
        else:
            error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
            print(f"❌ Impossible de créer le bulletin: {error_data}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    return False

def main():
    """Fonction principale"""
    print("🚀 Diagnostic Mandroso Services - Problème Bulletins")
    print("=" * 70)
    
    # 1. Trouver l'employeur Mandroso
    employer = find_mandroso_employer()
    
    if not employer:
        print("❌ Employeur Mandroso Services non trouvé")
        
        # Lister tous les employeurs
        try:
            response = requests.get(f"{BACKEND_URL}/employers")
            if response.status_code == 200:
                employers = response.json()
                print("\n📋 Employeurs disponibles:")
                for emp in employers:
                    print(f"   - {emp.get('raison_sociale', 'N/A')} (ID: {emp['id']})")
        except:
            pass
        return
    
    # 2. Analyser les données
    success, working_period = analyze_mandroso_data(employer)
    
    # 3. Suggérer des solutions
    response = requests.get(f"{BACKEND_URL}/workers")
    has_workers = False
    if response.status_code == 200:
        workers = response.json()
        mandroso_workers = [w for w in workers if w.get('employer_id') == employer['id']]
        has_workers = len(mandroso_workers) > 0
        
        # 4. Essayer de créer un bulletin de test
        if has_workers and not success:
            worker_id = mandroso_workers[0]['id']
            success = create_test_bulletin(employer['id'], worker_id)
    
    suggest_solutions(employer, has_workers)
    
    # Résumé
    print(f"\n📊 RÉSUMÉ:")
    print(f"Employeur trouvé: ✅")
    print(f"Salariés présents: {'✅' if has_workers else '❌'}")
    print(f"Bulletins générés: {'✅' if success else '❌'}")
    
    if success and working_period:
        print(f"\n🎉 SOLUTION TROUVÉE!")
        print(f"Utilisez la période {working_period} pour tester l'impression")

if __name__ == "__main__":
    main()