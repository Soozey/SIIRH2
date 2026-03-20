"""
Test complet du workflow de création et affichage des structures organisationnelles
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

def test_creation_workflow():
    """Test le workflow complet de création et affichage"""
    print("=" * 80)
    print("TEST DU WORKFLOW DE CRÉATION ET AFFICHAGE")
    print("=" * 80)
    
    # 1. Récupérer un employeur
    print("\n1️⃣ Récupération d'un employeur...")
    response = requests.get(f"{BASE_URL}/employers", timeout=5)
    response.raise_for_status()
    employers = response.json()
    
    if not employers:
        print("   ⚠️  Aucun employeur trouvé")
        return False
    
    employer_id = employers[0]['id']
    print(f"   ✓ Employeur ID: {employer_id}")
    
    # 2. Créer un établissement
    print(f"\n2️⃣ Création d'un établissement...")
    timestamp = datetime.now().strftime('%H%M%S')
    
    response = requests.post(
        f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/nodes",
        json={
            "name": f"Établissement Test {timestamp}",
            "code": f"ETB{timestamp}",
            "level": "etablissement",
            "parent_id": None,
            "description": "Test workflow"
        },
        timeout=5
    )
    response.raise_for_status()
    etablissement = response.json()
    etablissement_id = etablissement['id']
    print(f"   ✓ Établissement créé: {etablissement['name']} (ID: {etablissement_id})")
    
    # 3. Vérifier que l'établissement apparaît dans l'arbre
    print(f"\n3️⃣ Vérification de l'affichage dans l'arbre...")
    response = requests.get(
        f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/tree",
        timeout=5
    )
    response.raise_for_status()
    tree_data = response.json()
    
    found = False
    for node in tree_data.get('tree', []):
        if node['id'] == etablissement_id:
            found = True
            print(f"   ✓ Établissement trouvé dans l'arbre")
            break
    
    if not found:
        print(f"   ✗ Établissement NON trouvé dans l'arbre!")
        return False
    
    # 4. Créer un département sous l'établissement
    print(f"\n4️⃣ Création d'un département...")
    response = requests.post(
        f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/nodes",
        json={
            "name": f"Département Test {timestamp}",
            "code": f"DEP{timestamp}",
            "level": "departement",
            "parent_id": etablissement_id,
            "description": "Test département"
        },
        timeout=5
    )
    response.raise_for_status()
    departement = response.json()
    departement_id = departement['id']
    print(f"   ✓ Département créé: {departement['name']} (ID: {departement_id})")
    
    # 5. Vérifier que le département apparaît sous l'établissement
    print(f"\n5️⃣ Vérification de la hiérarchie...")
    response = requests.get(
        f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/tree",
        timeout=5
    )
    response.raise_for_status()
    tree_data = response.json()
    
    found_dept = False
    for node in tree_data.get('tree', []):
        if node['id'] == etablissement_id:
            for child in node.get('children', []):
                if child['id'] == departement_id:
                    found_dept = True
                    print(f"   ✓ Département trouvé sous l'établissement")
                    break
            break
    
    if not found_dept:
        print(f"   ✗ Département NON trouvé sous l'établissement!")
        return False
    
    # 6. Créer un service sous le département
    print(f"\n6️⃣ Création d'un service...")
    response = requests.post(
        f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/nodes",
        json={
            "name": f"Service Test {timestamp}",
            "code": f"SRV{timestamp}",
            "level": "service",
            "parent_id": departement_id,
            "description": "Test service"
        },
        timeout=5
    )
    response.raise_for_status()
    service = response.json()
    service_id = service['id']
    print(f"   ✓ Service créé: {service['name']} (ID: {service_id})")
    
    # 7. Vérifier la hiérarchie complète
    print(f"\n7️⃣ Vérification de la hiérarchie complète...")
    response = requests.get(
        f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/tree",
        timeout=5
    )
    response.raise_for_status()
    tree_data = response.json()
    
    found_service = False
    for node in tree_data.get('tree', []):
        if node['id'] == etablissement_id:
            for dept in node.get('children', []):
                if dept['id'] == departement_id:
                    for srv in dept.get('children', []):
                        if srv['id'] == service_id:
                            found_service = True
                            print(f"   ✓ Service trouvé sous le département")
                            print(f"   ✓ Hiérarchie complète: {node['name']} > {dept['name']} > {srv['name']}")
                            break
                    break
            break
    
    if not found_service:
        print(f"   ✗ Service NON trouvé sous le département!")
        return False
    
    # 8. Vérifier les options en cascade
    print(f"\n8️⃣ Vérification des options en cascade...")
    
    # Établissements (parent_id=None)
    response = requests.get(
        f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/cascading-options",
        params={"parent_id": None},
        timeout=5
    )
    response.raise_for_status()
    etablissements = response.json()
    
    found_etb = any(e['id'] == etablissement_id for e in etablissements)
    print(f"   {'✓' if found_etb else '✗'} Établissement dans les options racine")
    
    # Départements (parent_id=etablissement_id)
    response = requests.get(
        f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/cascading-options",
        params={"parent_id": etablissement_id},
        timeout=5
    )
    response.raise_for_status()
    departements = response.json()
    
    found_dept = any(d['id'] == departement_id for d in departements)
    print(f"   {'✓' if found_dept else '✗'} Département dans les options de l'établissement")
    
    # Services (parent_id=departement_id)
    response = requests.get(
        f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/cascading-options",
        params={"parent_id": departement_id},
        timeout=5
    )
    response.raise_for_status()
    services = response.json()
    
    found_srv = any(s['id'] == service_id for s in services)
    print(f"   {'✓' if found_srv else '✗'} Service dans les options du département")
    
    # 9. Nettoyer (supprimer en cascade)
    print(f"\n9️⃣ Nettoyage...")
    response = requests.delete(
        f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/nodes/{etablissement_id}",
        params={'force': True},
        timeout=5
    )
    
    if response.status_code == 200:
        print(f"   ✓ Hiérarchie supprimée avec succès")
    else:
        print(f"   ⚠️  Erreur de suppression: {response.status_code}")
    
    print("\n" + "=" * 80)
    print("✅ TEST RÉUSSI - Le workflow de création et affichage fonctionne correctement!")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    try:
        success = test_creation_workflow()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
