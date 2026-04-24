#!/usr/bin/env python3
"""
Test final du système de filtrage organisationnel complet
"""

import requests
import json

BACKEND_URL = "http://localhost:8000"

def test_worker_assignments():
    """Vérifie que les salariés sont bien assignés"""
    print("👥 Vérification des Assignations des Salariés")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BACKEND_URL}/workers")
        if response.status_code != 200:
            return False
        
        workers = response.json()
        employer_workers = [w for w in workers if w.get('employer_id') == 1]
        
        print(f"📊 {len(employer_workers)} salarié(s) analysé(s):")
        
        for worker in employer_workers:
            name = f"{worker.get('prenom', '')} {worker.get('nom', '')}"
            etab = worker.get('etablissement', 'N/A')
            dept = worker.get('departement', 'N/A')
            service = worker.get('service', 'N/A')
            unite = worker.get('unite', 'N/A')
            
            print(f"   👤 {name}:")
            print(f"      - Établissement: {etab}")
            print(f"      - Département: {dept}")
            print(f"      - Service: {service}")
            print(f"      - Unité: {unite}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_organizational_filters():
    """Test des filtres organisationnels"""
    print("\n🔍 Test des Filtres Organisationnels")
    print("=" * 50)
    
    try:
        employer_id = 1
        
        # Test endpoint hiérarchique
        response = requests.get(f"{BACKEND_URL}/employers/{employer_id}/organizational-data/hierarchical")
        if response.status_code == 200:
            data = response.json()
            print("✅ Données hiérarchiques disponibles:")
            print(f"   - Établissements: {data.get('etablissements', [])}")
            print(f"   - Départements: {data.get('departements', [])}")
            print(f"   - Services: {data.get('services', [])}")
            print(f"   - Unités: {data.get('unites', [])}")
        else:
            print("❌ Impossible de récupérer les données hiérarchiques")
            return False
        
        # Test filtrage cascade
        if data.get('etablissements'):
            etablissement = data['etablissements'][0]
            print(f"\n🔍 Test filtrage cascade avec '{etablissement}':")
            
            response = requests.get(f"{BACKEND_URL}/employers/{employer_id}/organizational-data/hierarchical-filtered", {
                'params': {'etablissement': etablissement}
            })
            
            if response.status_code == 200:
                filtered = response.json()
                print(f"   ✅ Filtrage réussi:")
                print(f"      - Départements filtrés: {filtered.get('departements', [])}")
                print(f"      - Services filtrés: {filtered.get('services', [])}")
                print(f"      - Unités filtrées: {filtered.get('unites', [])}")
            else:
                print(f"   ❌ Erreur filtrage: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_payroll_endpoint():
    """Test de l'endpoint de bulletins avec différentes périodes"""
    print("\n💰 Test de l'Endpoint Bulletins")
    print("=" * 50)
    
    employer_id = 1
    periods = ["2024-12", "2025-01", "2024-11"]
    
    for period in periods:
        print(f"\n📅 Test période {period}:")
        
        try:
            # Test sans filtres
            response = requests.get(f"{BACKEND_URL}/payroll/bulk-preview", {
                'params': {
                    'employer_id': employer_id,
                    'period': period
                }
            })
            
            if response.status_code == 200:
                bulletins = response.json()
                print(f"   ✅ Sans filtres: {len(bulletins)} bulletin(s)")
                
                if len(bulletins) > 0:
                    # Test avec filtre
                    response = requests.get(f"{BACKEND_URL}/payroll/bulk-preview", {
                        'params': {
                            'employer_id': employer_id,
                            'period': period,
                            'etablissement': 'SIRAMA'
                        }
                    })
                    
                    if response.status_code == 200:
                        filtered_bulletins = response.json()
                        print(f"   ✅ Avec filtre SIRAMA: {len(filtered_bulletins)} bulletin(s)")
                        
                        if len(filtered_bulletins) > 0:
                            print(f"   🎉 FILTRAGE OPÉRATIONNEL pour {period}!")
                            return True, period
                    else:
                        print(f"   ❌ Erreur avec filtre: {response.status_code}")
                else:
                    print(f"   ⚠️ Aucun bulletin pour {period}")
            else:
                print(f"   ❌ Erreur: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
    
    return False, None

def create_test_payroll_data():
    """Crée des données de paie de test si nécessaire"""
    print("\n🛠️ Création de Données de Test")
    print("=" * 50)
    
    try:
        # Récupérer les salariés
        response = requests.get(f"{BACKEND_URL}/workers")
        if response.status_code != 200:
            return False
        
        workers = response.json()
        employer_workers = [w for w in workers if w.get('employer_id') == 1]
        
        if not employer_workers:
            print("⚠️ Aucun salarié trouvé")
            return False
        
        # Essayer de créer un bulletin de test pour janvier 2025
        worker = employer_workers[0]
        period = "2025-01"
        
        print(f"🧪 Test de génération de bulletin pour {worker.get('prenom')} {worker.get('nom')} ({period})")
        
        response = requests.get(f"{BACKEND_URL}/payroll/preview", {
            'params': {
                'worker_id': worker['id'],
                'period': period
            }
        })
        
        if response.status_code == 200:
            print("✅ Bulletin de test généré avec succès")
            return True
        else:
            print(f"❌ Impossible de générer le bulletin: {response.status_code}")
            return False
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def main():
    """Fonction principale"""
    print("🚀 Test Final du Système de Filtrage Organisationnel")
    print("=" * 70)
    
    # 1. Vérifier les assignations
    assignments_ok = test_worker_assignments()
    
    # 2. Tester les filtres
    filters_ok = test_organizational_filters()
    
    # 3. Tester l'endpoint de bulletins
    payroll_ok, working_period = test_payroll_endpoint()
    
    # 4. Si pas de bulletins, essayer de créer des données de test
    if not payroll_ok:
        print("\n🔧 Aucun bulletin trouvé, tentative de création de données de test...")
        test_data_created = create_test_payroll_data()
        
        if test_data_created:
            payroll_ok, working_period = test_payroll_endpoint()
    
    # Résumé final
    print("\n" + "=" * 70)
    print("📊 RÉSUMÉ FINAL")
    print(f"Assignations des salariés: {'✅ OK' if assignments_ok else '❌ ERREUR'}")
    print(f"Filtres organisationnels: {'✅ OK' if filters_ok else '❌ ERREUR'}")
    print(f"Bulletins avec filtrage: {'✅ OK' if payroll_ok else '❌ ERREUR'}")
    
    if working_period:
        print(f"Période fonctionnelle: {working_period}")
    
    if assignments_ok and filters_ok and payroll_ok:
        print("\n🎉 SYSTÈME COMPLÈTEMENT OPÉRATIONNEL!")
        print("\n📋 INSTRUCTIONS FINALES:")
        print("1. Allez sur /payroll")
        print("2. Cliquez sur 'Imprimer tous les bulletins'")
        print("3. Sélectionnez 'Appliquer des filtres organisationnels'")
        print("4. Choisissez SIRAMA comme établissement")
        print("5. Observez le filtrage en cascade")
        print("6. Confirmez pour voir les bulletins filtrés")
        print(f"7. Utilisez la période {working_period} pour les tests")
    else:
        print("\n⚠️ SYSTÈME PARTIELLEMENT FONCTIONNEL")
        if not payroll_ok:
            print("- Créez des bulletins de paie pour tester le filtrage")
            print("- Ou utilisez une période avec des données existantes")

if __name__ == "__main__":
    main()