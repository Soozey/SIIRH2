#!/usr/bin/env python3
"""
Test spécifique du filtrage en cascade avec vérification détaillée
"""

import requests
import json

BACKEND_URL = "http://localhost:8000"

def test_specific_filtering():
    """Test spécifique du filtrage avec vérifications détaillées"""
    print("🔍 Test Spécifique du Filtrage en Cascade")
    print("=" * 60)
    
    try:
        employer_id = 1  # Karibo Services
        
        print("📊 TESTS DE FILTRAGE DÉTAILLÉS:")
        print("-" * 50)
        
        # Test 1: Filtrage par JICA (devrait retourner seulement AWC comme département)
        print("\n🏢 TEST 1: Filtrage par établissement 'JICA'")
        response = requests.get(f"{BACKEND_URL}/employers/{employer_id}/organizational-data/hierarchical-filtered", {
            'params': {'etablissement': 'JICA'}
        })
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Réponse reçue:")
            print(f"   - Établissements: {data.get('etablissements', [])}")
            print(f"   - Départements: {data.get('departements', [])}")
            print(f"   - Services: {data.get('services', [])}")
            print(f"   - Unités: {data.get('unites', [])}")
            
            # Vérifications
            expected_departments = ['AWC']  # Seul département sous JICA
            actual_departments = data.get('departements', [])
            
            if actual_departments == expected_departments:
                print("   ✅ SUCCÈS: Filtrage par établissement fonctionne!")
            else:
                print(f"   ❌ ÉCHEC: Attendu {expected_departments}, reçu {actual_departments}")
        else:
            print(f"   ❌ Erreur HTTP: {response.status_code}")
        
        # Test 2: Filtrage par SIRAMA (devrait retourner seulement AMBILOBE comme département)
        print("\n🏢 TEST 2: Filtrage par établissement 'SIRAMA'")
        response = requests.get(f"{BACKEND_URL}/employers/{employer_id}/organizational-data/hierarchical-filtered", {
            'params': {'etablissement': 'SIRAMA'}
        })
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Réponse reçue:")
            print(f"   - Établissements: {data.get('etablissements', [])}")
            print(f"   - Départements: {data.get('departements', [])}")
            print(f"   - Services: {data.get('services', [])}")
            print(f"   - Unités: {data.get('unites', [])}")
            
            # Vérifications
            expected_departments = ['AMBILOBE']  # Seul département sous SIRAMA
            actual_departments = data.get('departements', [])
            
            if actual_departments == expected_departments:
                print("   ✅ SUCCÈS: Filtrage par établissement fonctionne!")
            else:
                print(f"   ❌ ÉCHEC: Attendu {expected_departments}, reçu {actual_departments}")
        else:
            print(f"   ❌ Erreur HTTP: {response.status_code}")
        
        # Test 3: Filtrage par département AMBILOBE (devrait retourner PLANTATION 1 et PLANTATION 2)
        print("\n🏬 TEST 3: Filtrage par département 'AMBILOBE'")
        response = requests.get(f"{BACKEND_URL}/employers/{employer_id}/organizational-data/hierarchical-filtered", {
            'params': {'departement': 'AMBILOBE'}
        })
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Réponse reçue:")
            print(f"   - Établissements: {data.get('etablissements', [])}")
            print(f"   - Départements: {data.get('departements', [])}")
            print(f"   - Services: {data.get('services', [])}")
            print(f"   - Unités: {data.get('unites', [])}")
            
            # Vérifications
            expected_services = ['PLANTATION 1', 'PLANTATION 2']  # Services sous AMBILOBE
            actual_services = sorted(data.get('services', []))
            
            if actual_services == sorted(expected_services):
                print("   ✅ SUCCÈS: Filtrage par département fonctionne!")
            else:
                print(f"   ❌ ÉCHEC: Attendu {sorted(expected_services)}, reçu {actual_services}")
        else:
            print(f"   ❌ Erreur HTTP: {response.status_code}")
        
        # Test 4: Filtrage par service PLANTATION 1 (devrait retourner HECTARE1 et HECTARE2)
        print("\n👥 TEST 4: Filtrage par service 'PLANTATION 1'")
        response = requests.get(f"{BACKEND_URL}/employers/{employer_id}/organizational-data/hierarchical-filtered", {
            'params': {'service': 'PLANTATION 1'}
        })
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Réponse reçue:")
            print(f"   - Établissements: {data.get('etablissements', [])}")
            print(f"   - Départements: {data.get('departements', [])}")
            print(f"   - Services: {data.get('services', [])}")
            print(f"   - Unités: {data.get('unites', [])}")
            
            # Vérifications
            expected_units = ['HECTARE1', 'HECTARE2']  # Unités sous PLANTATION 1
            actual_units = sorted(data.get('unites', []))
            
            if actual_units == sorted(expected_units):
                print("   ✅ SUCCÈS: Filtrage par service fonctionne!")
            else:
                print(f"   ❌ ÉCHEC: Attendu {sorted(expected_units)}, reçu {actual_units}")
        else:
            print(f"   ❌ Erreur HTTP: {response.status_code}")
        
        # Test 5: Aucun filtre (devrait retourner tout)
        print("\n🌐 TEST 5: Aucun filtre (données complètes)")
        response = requests.get(f"{BACKEND_URL}/employers/{employer_id}/organizational-data/hierarchical")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Données complètes:")
            print(f"   - Établissements: {data.get('etablissements', [])}")
            print(f"   - Départements: {data.get('departements', [])}")
            print(f"   - Services: {data.get('services', [])}")
            print(f"   - Unités: {data.get('unites', [])}")
        else:
            print(f"   ❌ Erreur HTTP: {response.status_code}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

def main():
    """Fonction principale"""
    print("🚀 Test Spécifique du Filtrage Hiérarchique")
    print("=" * 70)
    
    test_specific_filtering()
    
    print("\n📋 RÉSULTATS ATTENDUS:")
    print("=" * 70)
    print("✅ JICA → Départements: ['AWC']")
    print("✅ SIRAMA → Départements: ['AMBILOBE']") 
    print("✅ AMBILOBE → Services: ['PLANTATION 1', 'PLANTATION 2']")
    print("✅ PLANTATION 1 → Unités: ['HECTARE1', 'HECTARE2']")
    print("\n💡 Si les tests échouent, redémarrez le backend pour appliquer les changements!")

if __name__ == "__main__":
    main()