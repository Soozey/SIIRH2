#!/usr/bin/env python3
"""
Debug de la recherche par nom
"""

import requests

def test_search_variations():
    search_terms = ["RAKOTO", "rakoto", "Jean", "JEAN", "Souzzy", "SOUZZY"]
    
    print("🔍 TEST DE RECHERCHE PAR NOM")
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
                print(f"   ❌ Erreur {response.status_code}: {response.text}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")

if __name__ == "__main__":
    test_search_variations()