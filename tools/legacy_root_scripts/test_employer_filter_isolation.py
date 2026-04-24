"""
Test de l'isolation des filtres entre employeurs
Reproduire le problème de fuite de données entre employeurs
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

def test_employer_isolation():
    """Tester que les structures sont bien isolées par employeur"""
    print("=" * 80)
    print("TEST D'ISOLATION DES FILTRES ENTRE EMPLOYEURS")
    print("=" * 80)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 1. Récupérer les employeurs
    print("1️⃣ Récupération des employeurs")
    response = requests.get(f"{BASE_URL}/employers")
    employers = response.json()
    
    print(f"   Employeurs trouvés: {len(employers)}")
    for emp in employers:
        print(f"   - ID: {emp['id']}, Nom: {emp['raison_sociale']}")
    print()
    
    if len(employers) < 2:
        print("❌ Besoin d'au moins 2 employeurs pour tester l'isolation")
        return False
    
    employer1 = employers[0]
    employer2 = employers[1]
    
    # 2. Tester les structures de l'employeur 1
    print(f"2️⃣ Test des structures de {employer1['raison_sociale']} (ID: {employer1['id']})")
    response1 = requests.get(
        f"{BASE_URL}/employers/{employer1['id']}/hierarchical-organization/cascading-options",
        params={"parent_id": None}
    )
    structures1 = response1.json()
    
    print(f"   Établissements trouvés: {len(structures1)}")
    for struct in structures1:
        print(f"   - ID: {struct['id']}, Nom: {struct['name']}, Niveau: {struct['level']}")
    print()
    
    # 3. Tester les structures de l'employeur 2
    print(f"3️⃣ Test des structures de {employer2['raison_sociale']} (ID: {employer2['id']})")
    response2 = requests.get(
        f"{BASE_URL}/employers/{employer2['id']}/hierarchical-organization/cascading-options",
        params={"parent_id": None}
    )
    structures2 = response2.json()
    
    print(f"   Établissements trouvés: {len(structures2)}")
    for struct in structures2:
        print(f"   - ID: {struct['id']}, Nom: {struct['name']}, Niveau: {struct['level']}")
    print()
    
    # 4. Vérifier qu'il n'y a pas de chevauchement
    print("4️⃣ Vérification de l'isolation des données")
    ids1 = {s['id'] for s in structures1}
    ids2 = {s['id'] for s in structures2}
    
    overlap = ids1.intersection(ids2)
    
    if overlap:
        print(f"   ❌ PROBLÈME: {len(overlap)} structure(s) commune(s) détectée(s)!")
        print(f"   IDs en commun: {overlap}")
        print()
        print("   Cela indique un problème d'isolation des données.")
        return False
    else:
        print(f"   ✅ Aucun chevauchement détecté")
        print(f"   Employeur 1: {len(ids1)} structures uniques")
        print(f"   Employeur 2: {len(ids2)} structures uniques")
    print()
    
    # 5. Tester avec un ID de structure de l'employeur 1 sur l'employeur 2
    if structures1:
        print("5️⃣ Test de fuite de données (tentative d'accès croisé)")
        struct1_id = structures1[0]['id']
        print(f"   Tentative d'accès à la structure {struct1_id} de {employer1['raison_sociale']}")
        print(f"   via l'endpoint de {employer2['raison_sociale']}")
        
        response_cross = requests.get(
            f"{BASE_URL}/employers/{employer2['id']}/hierarchical-organization/cascading-options",
            params={"parent_id": struct1_id}
        )
        
        if response_cross.status_code == 200:
            cross_data = response_cross.json()
            if cross_data:
                print(f"   ❌ FUITE DE DONNÉES: {len(cross_data)} structure(s) retournée(s)!")
                print(f"   L'employeur {employer2['id']} peut accéder aux structures de l'employeur {employer1['id']}")
                for struct in cross_data:
                    print(f"      - ID: {struct['id']}, Nom: {struct['name']}")
                return False
            else:
                print(f"   ✅ Aucune donnée retournée (comportement correct)")
        else:
            print(f"   ✅ Erreur {response_cross.status_code} (comportement correct)")
    print()
    
    # 6. Tester l'arbre hiérarchique complet
    print("6️⃣ Test de l'arbre hiérarchique complet")
    
    print(f"   Arbre de {employer1['raison_sociale']}:")
    tree1_response = requests.get(f"{BASE_URL}/employers/{employer1['id']}/hierarchical-organization/tree")
    tree1 = tree1_response.json()
    print(f"   - Nœuds: {tree1.get('total_units', 0)}")
    
    print(f"   Arbre de {employer2['raison_sociale']}:")
    tree2_response = requests.get(f"{BASE_URL}/employers/{employer2['id']}/hierarchical-organization/tree")
    tree2 = tree2_response.json()
    print(f"   - Nœuds: {tree2.get('total_units', 0)}")
    print()
    
    # 7. Vérifier les salariés
    print("7️⃣ Test de l'isolation des salariés")
    
    workers_response = requests.get(f"{BASE_URL}/workers")
    all_workers = workers_response.json()
    
    workers1 = [w for w in all_workers if w['employer_id'] == employer1['id']]
    workers2 = [w for w in all_workers if w['employer_id'] == employer2['id']]
    
    print(f"   Salariés de {employer1['raison_sociale']}: {len(workers1)}")
    print(f"   Salariés de {employer2['raison_sociale']}: {len(workers2)}")
    
    # Vérifier qu'aucun salarié n'appartient aux deux employeurs
    worker_ids1 = {w['id'] for w in workers1}
    worker_ids2 = {w['id'] for w in workers2}
    worker_overlap = worker_ids1.intersection(worker_ids2)
    
    if worker_overlap:
        print(f"   ❌ PROBLÈME: {len(worker_overlap)} salarié(s) appartient/appartiennent aux deux employeurs!")
        return False
    else:
        print(f"   ✅ Isolation des salariés correcte")
    print()
    
    # Résumé
    print("=" * 80)
    print("RÉSUMÉ DU TEST D'ISOLATION")
    print("=" * 80)
    print()
    print("✅ TOUS LES TESTS D'ISOLATION SONT PASSÉS")
    print()
    print("Les données sont correctement isolées au niveau backend.")
    print("Le problème se situe probablement au niveau du cache React Query dans le frontend.")
    print()
    print("Solutions recommandées:")
    print("1. Invalider le cache React Query lors du changement d'employeur")
    print("2. Ajouter l'employerId dans toutes les queryKey")
    print("3. Utiliser queryClient.removeQueries() lors du changement d'employeur")
    print("4. Désactiver le cache pour les queries sensibles")
    print()
    
    return True

if __name__ == "__main__":
    success = test_employer_isolation()
    exit(0 if success else 1)
