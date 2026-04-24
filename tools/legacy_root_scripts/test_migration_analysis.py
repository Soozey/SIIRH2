#!/usr/bin/env python3
"""
Test de l'analyse de migration
"""

import requests

def test_migration_analysis():
    print("🧪 TEST ANALYSE DE MIGRATION")
    print("=" * 40)
    
    try:
        response = requests.get("http://localhost:8000/api/matricules/migration/analysis")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Analyse réussie:")
            print(f"   Complexité: {data.get('complexity')}")
            print(f"   Durée: {data.get('estimated_duration')}")
            print(f"   Issues: {data.get('issues_count')}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    test_migration_analysis()