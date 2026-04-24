#!/usr/bin/env python3
"""
Test avec les vrais noms de la base
"""

import requests

def test_correct_names():
    search_terms = ["RAKOTOBE", "Souzzy", "RAFARAVAVY", "Jeanne", "RAFALIMANANA", "HENINTSOA"]
    
    print("🔍 TEST AVEC LES VRAIS NOMS")
    print("=" * 40)
    
    for term in search_terms:
        print(f"\n🔍 Recherche: '{term}'")
        try:
            response = requests.get(f"http://localhost:8000/api/matricules/search?query={term}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ {len(data)} résultats")
                for result in data:
                    print(f"      - {result['matricule']}: {result['full_name']}")
            else:
                print(f"   ❌ Erreur {response.status_code}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")

if __name__ == "__main__":
    test_correct_names()