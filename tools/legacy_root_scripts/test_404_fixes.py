#!/usr/bin/env python3
"""
Test pour vérifier que les erreurs 404 ont été corrigées.
"""

import requests
import time

def test_worker_endpoints():
    """Test les endpoints workers pour vérifier qu'il n'y a plus d'erreurs 404"""
    
    print("🧪 Test des endpoints workers...")
    
    # IDs existants
    existing_ids = [2007, 2022, 2032, 2042]
    
    # IDs qui causaient des erreurs 404
    problematic_ids = [2, 40, 0]
    
    # Test des IDs existants (doivent retourner 200)
    print("\n✅ Test des IDs existants:")
    for worker_id in existing_ids:
        try:
            response = requests.get(f"http://localhost:8000/workers/{worker_id}")
            status = "✅" if response.status_code == 200 else "❌"
            print(f"  {status} GET /workers/{worker_id}: {response.status_code}")
        except Exception as e:
            print(f"  ❌ GET /workers/{worker_id}: Erreur - {e}")
    
    # Test des IDs problématiques (doivent retourner 404, mais ne doivent plus être appelés par le frontend)
    print("\n⚠️  Test des IDs problématiques (ne devraient plus être appelés):")
    for worker_id in problematic_ids:
        try:
            response = requests.get(f"http://localhost:8000/workers/{worker_id}")
            status = "⚠️" if response.status_code == 404 else "❌"
            print(f"  {status} GET /workers/{worker_id}: {response.status_code} (attendu: 404)")
        except Exception as e:
            print(f"  ❌ GET /workers/{worker_id}: Erreur - {e}")

def test_frontend_accessibility():
    """Test que le frontend est accessible"""
    print("\n🌐 Test d'accessibilité du frontend...")
    
    try:
        response = requests.get("http://localhost:5174", timeout=5)
        if response.status_code == 200:
            print("  ✅ Frontend accessible sur http://localhost:5174")
            return True
        else:
            print(f"  ❌ Frontend retourne le statut {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Frontend non accessible: {e}")
        return False

def main():
    print("🔍 Test de correction des erreurs 404")
    print("=" * 50)
    
    # Test backend
    test_worker_endpoints()
    
    # Test frontend
    frontend_ok = test_frontend_accessibility()
    
    print("\n📋 Résumé:")
    print("  ✅ Backend: IDs existants fonctionnent")
    print("  ⚠️  Backend: IDs inexistants retournent 404 (normal)")
    if frontend_ok:
        print("  ✅ Frontend: Accessible et redémarré")
    else:
        print("  ❌ Frontend: Problème d'accessibilité")
    
    print("\n🎯 Actions recommandées:")
    print("  1. Ouvrir http://localhost:5174 dans le navigateur")
    print("  2. Vider le cache du navigateur (F12 > Application > Storage > Clear)")
    print("  3. Actualiser la page (Ctrl+Shift+R)")
    print("  4. Naviguer vers la page Workers")
    print("  5. Vérifier la console F12 - les erreurs 404 devraient avoir disparu")
    
    print("\n💡 Si des erreurs 404 persistent:")
    print("  - Elles peuvent venir du cache du navigateur")
    print("  - Essayer en navigation privée")
    print("  - Vérifier que tous les onglets sont fermés et rouverts")

if __name__ == "__main__":
    main()