"""
Test rapide - Vérifier que l'employer ID est correctement passé au modal
"""
import requests
from datetime import datetime

def test_workers_endpoint():
    """Vérifier que l'endpoint workers retourne des données"""
    try:
        response = requests.get("http://127.0.0.1:8000/workers", timeout=5)
        if response.status_code == 200:
            workers = response.json()
            print(f"✅ Endpoint /workers accessible")
            print(f"   Nombre de salariés: {len(workers)}")
            if len(workers) > 0:
                first_worker = workers[0]
                print(f"   Premier salarié: {first_worker.get('nom')} {first_worker.get('prenom')}")
                print(f"   Employer ID: {first_worker.get('employer_id')}")
                return first_worker.get('employer_id')
            else:
                print("⚠️  Aucun salarié dans la base de données")
                return None
        else:
            print(f"❌ Erreur {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None

def test_employers_endpoint():
    """Vérifier que l'endpoint employers retourne des données"""
    try:
        response = requests.get("http://127.0.0.1:8000/employers", timeout=5)
        if response.status_code == 200:
            employers = response.json()
            print(f"✅ Endpoint /employers accessible")
            print(f"   Nombre d'employeurs: {len(employers)}")
            for emp in employers:
                print(f"   - ID {emp.get('id')}: {emp.get('raison_sociale')}")
            return employers
        else:
            print(f"❌ Erreur {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return []

def main():
    print("=" * 70)
    print("🔍 TEST - EMPLOYER ID DANS LE MODAL")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    print("1️⃣ Test de l'endpoint /workers")
    print("-" * 70)
    worker_employer_id = test_workers_endpoint()
    
    print("\n2️⃣ Test de l'endpoint /employers")
    print("-" * 70)
    employers = test_employers_endpoint()
    
    print("\n" + "=" * 70)
    print("📋 RÉSUMÉ")
    print("=" * 70)
    
    if worker_employer_id and len(employers) > 0:
        print("✅ Les données sont disponibles")
        print(f"\n🎯 INSTRUCTIONS POUR LE TEST:")
        print(f"   1. Ouvrir http://localhost:5173/payroll")
        print(f"   2. Vérifier qu'un salarié est sélectionné dans le dropdown")
        print(f"   3. Cliquer sur 'Imprimer tous les bulletins'")
        print(f"   4. Dans la console F12, vérifier:")
        print(f"      ✅ Log: [MODAL DEBUG] Modal opened with employer {worker_employer_id}")
        print(f"      ❌ PAS: [MODAL DEBUG] Modal opened with employer 0")
        print(f"\n   5. Cocher 'Filtrage par structure organisationnelle'")
        print(f"   6. Changer d'employeur dans le dropdown du modal")
        print(f"   7. Vérifier les logs de cache clearing")
    else:
        print("⚠️  Données manquantes - Vérifier la base de données")
        if not worker_employer_id:
            print("   - Aucun salarié trouvé")
        if len(employers) == 0:
            print("   - Aucun employeur trouvé")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
