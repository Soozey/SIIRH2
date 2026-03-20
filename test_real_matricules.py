#!/usr/bin/env python3
"""
Test avec les vrais matricules de la base
"""

import requests
import json

def test_real_matricules():
    matricules = ["M001", "M0001", "M0002", "N0003"]
    
    print("🧪 TEST AVEC LES VRAIS MATRICULES")
    print("=" * 40)
    
    for matricule in matricules:
        print(f"\n🔍 Test matricule: {matricule}")
        
        # Test résolution
        try:
            response = requests.get(f"http://localhost:8000/api/matricules/resolve/{matricule}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Résolution: {data['full_name']}")
            else:
                print(f"   ❌ Résolution échouée: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Erreur résolution: {e}")
        
        # Test affectations
        try:
            response = requests.get(f"http://localhost:8000/api/matricules/assignments/{matricule}")
            if response.status_code == 200:
                data = response.json()
                if data:
                    print(f"   ✅ Affectation: {data.get('departement', 'N/A')}/{data.get('service', 'N/A')}")
                else:
                    print(f"   ⚠️  Aucune affectation")
            else:
                print(f"   ❌ Affectation échouée: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Erreur affectation: {e}")
    
    # Test recherche par nom
    print(f"\n🔍 Test recherche par nom: RAKOTO")
    try:
        response = requests.get("http://localhost:8000/api/matricules/search?query=RAKOTO")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Trouvé {len(data)} résultats")
            for result in data:
                print(f"      - {result['matricule']}: {result['full_name']}")
        else:
            print(f"   ❌ Recherche échouée: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erreur recherche: {e}")

if __name__ == "__main__":
    test_real_matricules()