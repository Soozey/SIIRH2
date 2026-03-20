#!/usr/bin/env python3
"""
Diagnostic de l'assignation des salariés aux structures organisationnelles
"""

import requests
import json

BACKEND_URL = "http://localhost:8000"

def analyze_worker_assignments():
    """Analyse l'assignation des salariés aux structures organisationnelles"""
    print("🔍 Analyse de l'Assignation des Salariés")
    print("=" * 60)
    
    try:
        # Récupérer les employeurs
        response = requests.get(f"{BACKEND_URL}/employers")
        if response.status_code != 200:
            print("❌ Impossible de récupérer les employeurs")
            return
        
        employers = response.json()
        if not employers:
            print("⚠️ Aucun employeur trouvé")
            return
        
        employer_id = employers[0]['id']
        employer_name = employers[0].get('raison_sociale', f'Employeur {employer_id}')
        
        print(f"📋 Analyse pour: {employer_name} (ID: {employer_id})")
        print()
        
        # 1. Récupérer les structures hiérarchiques
        print("🏗️ STRUCTURES HIÉRARCHIQUES DISPONIBLES:")
        print("-" * 50)
        
        response = requests.get(f"{BACKEND_URL}/employers/{employer_id}/organizational-data/hierarchical")
        if response.status_code == 200:
            hierarchical_data = response.json()
            print(f"✅ Structures hiérarchiques:")
            print(f"   - Établissements: {hierarchical_data.get('etablissements', [])}")
            print(f"   - Départements: {hierarchical_data.get('departements', [])}")
            print(f"   - Services: {hierarchical_data.get('services', [])}")
            print(f"   - Unités: {hierarchical_data.get('unites', [])}")
        else:
            print("❌ Impossible de récupérer les structures hiérarchiques")
            return
        
        # 2. Récupérer les salariés et leurs assignations
        print("\n👥 ASSIGNATIONS DES SALARIÉS:")
        print("-" * 50)
        
        response = requests.get(f"{BACKEND_URL}/workers")
        if response.status_code != 200:
            print("❌ Impossible de récupérer les salariés")
            return
        
        workers = response.json()
        employer_workers = [w for w in workers if w.get('employer_id') == employer_id]
        
        if not employer_workers:
            print("⚠️ Aucun salarié trouvé pour cet employeur")
            return
        
        print(f"📊 {len(employer_workers)} salarié(s) trouvé(s):")
        
        # Analyser les assignations
        worker_assignments = {}
        for worker in employer_workers:
            assignment = {
                'etablissement': worker.get('etablissement', 'N/A'),
                'departement': worker.get('departement', 'N/A'),
                'service': worker.get('service', 'N/A'),
                'unite': worker.get('unite', 'N/A')
            }
            
            print(f"\n   👤 {worker.get('prenom', '')} {worker.get('nom', '')} (ID: {worker.get('id')})")
            print(f"      - Établissement: '{assignment['etablissement']}'")
            print(f"      - Département: '{assignment['departement']}'")
            print(f"      - Service: '{assignment['service']}'")
            print(f"      - Unité: '{assignment['unite']}'")
            
            # Stocker pour analyse
            key = f"{assignment['etablissement']}|{assignment['departement']}|{assignment['service']}|{assignment['unite']}"
            if key not in worker_assignments:
                worker_assignments[key] = []
            worker_assignments[key].append(worker)
        
        # 3. Analyser la correspondance
        print(f"\n🔍 ANALYSE DE CORRESPONDANCE:")
        print("-" * 50)
        
        hierarchical_etablissements = set(hierarchical_data.get('etablissements', []))
        hierarchical_departements = set(hierarchical_data.get('departements', []))
        hierarchical_services = set(hierarchical_data.get('services', []))
        hierarchical_unites = set(hierarchical_data.get('unites', []))
        
        worker_etablissements = set()
        worker_departements = set()
        worker_services = set()
        worker_unites = set()
        
        for worker in employer_workers:
            if worker.get('etablissement') and worker['etablissement'] != 'N/A':
                worker_etablissements.add(worker['etablissement'])
            if worker.get('departement') and worker['departement'] != 'N/A':
                worker_departements.add(worker['departement'])
            if worker.get('service') and worker['service'] != 'N/A':
                worker_services.add(worker['service'])
            if worker.get('unite') and worker['unite'] != 'N/A':
                worker_unites.add(worker['unite'])
        
        print(f"📊 COMPARAISON:")
        print(f"   Établissements:")
        print(f"      - Hiérarchiques: {sorted(hierarchical_etablissements)}")
        print(f"      - Salariés: {sorted(worker_etablissements)}")
        print(f"      - Correspondance: {hierarchical_etablissements & worker_etablissements}")
        
        print(f"   Départements:")
        print(f"      - Hiérarchiques: {sorted(hierarchical_departements)}")
        print(f"      - Salariés: {sorted(worker_departements)}")
        print(f"      - Correspondance: {hierarchical_departements & worker_departements}")
        
        print(f"   Services:")
        print(f"      - Hiérarchiques: {sorted(hierarchical_services)}")
        print(f"      - Salariés: {sorted(worker_services)}")
        print(f"      - Correspondance: {hierarchical_services & worker_services}")
        
        print(f"   Unités:")
        print(f"      - Hiérarchiques: {sorted(hierarchical_unites)}")
        print(f"      - Salariés: {sorted(worker_unites)}")
        print(f"      - Correspondance: {hierarchical_unites & worker_unites}")
        
        # 4. Test de l'endpoint bulk-preview avec filtres
        print(f"\n🧪 TEST DE L'ENDPOINT BULK-PREVIEW:")
        print("-" * 50)
        
        period = "2024-12"
        
        # Test sans filtres
        print(f"📋 Test sans filtres (période {period}):")
        response = requests.get(f"{BACKEND_URL}/payroll/bulk-preview", {
            'params': {
                'employer_id': employer_id,
                'period': period
            }
        })
        
        if response.status_code == 200:
            bulletins_all = response.json()
            print(f"   ✅ {len(bulletins_all)} bulletin(s) trouvé(s) sans filtres")
        else:
            print(f"   ❌ Erreur sans filtres: {response.status_code}")
            bulletins_all = []
        
        # Test avec filtre établissement
        if hierarchical_etablissements:
            etablissement = list(hierarchical_etablissements)[0]
            print(f"\n📋 Test avec filtre établissement '{etablissement}':")
            
            response = requests.get(f"{BACKEND_URL}/payroll/bulk-preview", {
                'params': {
                    'employer_id': employer_id,
                    'period': period,
                    'etablissement': etablissement
                }
            })
            
            if response.status_code == 200:
                bulletins_filtered = response.json()
                print(f"   ✅ {len(bulletins_filtered)} bulletin(s) trouvé(s) avec filtre")
                
                if len(bulletins_filtered) == 0 and len(bulletins_all) > 0:
                    print(f"   ⚠️ PROBLÈME: Aucun bulletin avec filtre mais {len(bulletins_all)} sans filtre")
                    print(f"   💡 Cela indique que les salariés ne sont pas assignés à '{etablissement}'")
            else:
                print(f"   ❌ Erreur avec filtre: {response.status_code}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

def suggest_solutions():
    """Suggère des solutions pour corriger le problème"""
    print("\n💡 SOLUTIONS PROPOSÉES:")
    print("=" * 60)
    
    print("🔧 PROBLÈME IDENTIFIÉ:")
    print("Les salariés ne sont pas assignés aux nouvelles structures hiérarchiques")
    print()
    print("🛠️ SOLUTIONS:")
    print()
    print("1. 📝 ASSIGNER MANUELLEMENT LES SALARIÉS")
    print("   - Aller sur la page Salariés")
    print("   - Modifier chaque salarié pour l'assigner aux bonnes structures")
    print("   - Remplacer les valeurs numériques par les vrais noms")
    print()
    print("2. 🔄 MIGRATION AUTOMATIQUE")
    print("   - Créer un script de migration")
    print("   - Mapper les anciennes valeurs vers les nouvelles structures")
    print("   - Mettre à jour tous les salariés en une fois")
    print()
    print("3. 🎯 SOLUTION RAPIDE POUR TEST")
    print("   - Créer quelques salariés de test")
    print("   - Les assigner aux structures hiérarchiques existantes")
    print("   - Tester l'impression avec ces salariés")

def main():
    """Fonction principale"""
    print("🚀 Diagnostic de l'Assignation des Salariés")
    print("=" * 70)
    
    analyze_worker_assignments()
    suggest_solutions()

if __name__ == "__main__":
    main()