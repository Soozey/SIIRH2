"""
Audit complet de la chaîne de transmission de l'ID Employeur
Identifier les points de blocage et de persistance du cache
"""
import requests
import json
from datetime import datetime
import time

BASE_URL = "http://127.0.0.1:8000"

def audit_employer_chain():
    """Auditer toute la chaîne de transmission de l'ID employeur"""
    print("=" * 80)
    print("AUDIT COMPLET - CHAÎNE DE TRANSMISSION ID EMPLOYEUR")
    print("=" * 80)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 1. Récupérer les employeurs
    print("1️⃣ ÉTAPE 1: Récupération des employeurs")
    print("-" * 80)
    response = requests.get(f"{BASE_URL}/employers")
    employers = response.json()
    
    print(f"Employeurs disponibles: {len(employers)}")
    for emp in employers:
        print(f"  - ID: {emp['id']}, Nom: {emp['raison_sociale']}")
    print()
    
    if len(employers) < 2:
        print("❌ Besoin d'au moins 2 employeurs pour l'audit")
        return
    
    employer1 = employers[0]
    employer2 = employers[1]
    
    # 2. Test avec Employeur 1
    print(f"2️⃣ ÉTAPE 2: Test avec {employer1['raison_sociale']} (ID: {employer1['id']})")
    print("-" * 80)
    
    # 2.1 Requête cascading-options
    print(f"2.1 Requête: GET /employers/{employer1['id']}/hierarchical-organization/cascading-options")
    print(f"    Params: parent_id=null")
    
    response1 = requests.get(
        f"{BASE_URL}/employers/{employer1['id']}/hierarchical-organization/cascading-options",
        params={"parent_id": None}
    )
    
    print(f"    Status: {response1.status_code}")
    print(f"    Headers: {dict(response1.headers)}")
    
    if response1.status_code == 200:
        data1 = response1.json()
        print(f"    Résultat: {len(data1)} structure(s)")
        for struct in data1:
            print(f"      - ID: {struct['id']}, Nom: {struct['name']}, Niveau: {struct['level']}")
            # CRITIQUE: Vérifier l'employer_id dans la réponse
            if 'employer_id' in struct:
                print(f"        employer_id dans réponse: {struct['employer_id']}")
                if struct['employer_id'] != employer1['id']:
                    print(f"        ⚠️  ALERTE: employer_id ne correspond pas!")
    print()
    
    # 2.2 Vérifier dans la base de données
    print(f"2.2 Vérification base de données pour employeur {employer1['id']}")
    # On va vérifier via l'arbre complet
    tree1_response = requests.get(f"{BASE_URL}/employers/{employer1['id']}/hierarchical-organization/tree")
    tree1 = tree1_response.json()
    print(f"    Arbre hiérarchique: {tree1.get('total_units', 0)} nœud(s)")
    
    # Analyser les nœuds de l'arbre
    if 'tree' in tree1 and tree1['tree']:
        print(f"    Analyse des nœuds:")
        for node in tree1['tree'][:3]:  # Premiers nœuds
            print(f"      - ID: {node['id']}, Nom: {node['name']}")
            if 'employer_id' in node:
                print(f"        employer_id: {node['employer_id']}")
    print()
    
    # 3. Attendre un peu (simuler le délai utilisateur)
    print("3️⃣ ÉTAPE 3: Pause de 2 secondes (simulation changement utilisateur)")
    print("-" * 80)
    time.sleep(2)
    print("    ✓ Pause terminée")
    print()
    
    # 4. Test avec Employeur 2
    print(f"4️⃣ ÉTAPE 4: Test avec {employer2['raison_sociale']} (ID: {employer2['id']})")
    print("-" * 80)
    
    # 4.1 Requête cascading-options
    print(f"4.1 Requête: GET /employers/{employer2['id']}/hierarchical-organization/cascading-options")
    print(f"    Params: parent_id=null")
    
    response2 = requests.get(
        f"{BASE_URL}/employers/{employer2['id']}/hierarchical-organization/cascading-options",
        params={"parent_id": None}
    )
    
    print(f"    Status: {response2.status_code}")
    print(f"    Headers: {dict(response2.headers)}")
    
    if response2.status_code == 200:
        data2 = response2.json()
        print(f"    Résultat: {len(data2)} structure(s)")
        for struct in data2:
            print(f"      - ID: {struct['id']}, Nom: {struct['name']}, Niveau: {struct['level']}")
            if 'employer_id' in struct:
                print(f"        employer_id dans réponse: {struct['employer_id']}")
                if struct['employer_id'] != employer2['id']:
                    print(f"        ⚠️  ALERTE: employer_id ne correspond pas!")
    print()
    
    # 5. Analyse critique: Vérifier si les IDs se chevauchent
    print("5️⃣ ÉTAPE 5: Analyse critique - Détection de pollution")
    print("-" * 80)
    
    if response1.status_code == 200 and response2.status_code == 200:
        data1 = response1.json()
        data2 = response2.json()
        
        ids1 = {s['id'] for s in data1}
        ids2 = {s['id'] for s in data2}
        names1 = {s['name'] for s in data1}
        names2 = {s['name'] for s in data2}
        
        print(f"Employeur 1 ({employer1['raison_sociale']}):")
        print(f"  - IDs: {ids1}")
        print(f"  - Noms: {names1}")
        print()
        
        print(f"Employeur 2 ({employer2['raison_sociale']}):")
        print(f"  - IDs: {ids2}")
        print(f"  - Noms: {names2}")
        print()
        
        # Vérifier le chevauchement
        id_overlap = ids1.intersection(ids2)
        name_overlap = names1.intersection(names2)
        
        if id_overlap:
            print(f"❌ POLLUTION DÉTECTÉE: {len(id_overlap)} ID(s) en commun!")
            print(f"   IDs en commun: {id_overlap}")
            print(f"   CAUSE: Les structures ne sont pas isolées par employeur")
        else:
            print(f"✅ Pas de chevauchement d'IDs")
        
        if name_overlap:
            print(f"⚠️  ATTENTION: {len(name_overlap)} nom(s) en commun!")
            print(f"   Noms en commun: {name_overlap}")
            print(f"   NOTE: Cela peut être normal si les noms sont identiques")
        else:
            print(f"✅ Pas de chevauchement de noms")
    print()
    
    # 6. Vérifier le service backend
    print("6️⃣ ÉTAPE 6: Audit du service backend")
    print("-" * 80)
    print("Vérification de la requête SQL utilisée...")
    print()
    
    # Simuler une requête avec un parent_id d'un autre employeur
    if response1.status_code == 200:
        data1 = response1.json()
        if data1:
            struct1_id = data1[0]['id']
            print(f"6.1 Test de fuite: Accès à la structure {struct1_id} de {employer1['raison_sociale']}")
            print(f"    via l'endpoint de {employer2['raison_sociale']}")
            
            response_cross = requests.get(
                f"{BASE_URL}/employers/{employer2['id']}/hierarchical-organization/cascading-options",
                params={"parent_id": struct1_id}
            )
            
            print(f"    Status: {response_cross.status_code}")
            
            if response_cross.status_code == 200:
                cross_data = response_cross.json()
                if cross_data:
                    print(f"    ❌ FUITE CRITIQUE: {len(cross_data)} structure(s) retournée(s)!")
                    print(f"    Le backend ne vérifie PAS l'appartenance à l'employeur!")
                    for struct in cross_data:
                        print(f"      - ID: {struct['id']}, Nom: {struct['name']}")
                    return False
                else:
                    print(f"    ✅ Aucune donnée retournée (correct)")
            else:
                print(f"    ✅ Erreur {response_cross.status_code} (correct)")
    print()
    
    # 7. Résumé et diagnostic
    print("=" * 80)
    print("DIAGNOSTIC FINAL")
    print("=" * 80)
    print()
    
    print("Points de vérification:")
    print()
    
    print("1. Backend API:")
    print(f"   - Isolation des structures: {'✅ OK' if not id_overlap else '❌ PROBLÈME'}")
    print(f"   - Validation employer_id: À vérifier dans le code")
    print()
    
    print("2. Hypothèses de pollution:")
    print()
    
    if len(data2) > 0 and len(data1) > 0:
        print("   ❌ HYPOTHÈSE 1: Cache React Query côté frontend")
        print("      - Le frontend réutilise les données de l'employeur précédent")
        print("      - Solution: Invalider le cache + staleTime: 0")
        print()
    
    if len(data2) == 0:
        print("   ✅ HYPOTHÈSE 2: Employeur 2 n'a pas de structures")
        print("      - C'est normal si Mandroso n'a pas de structures organisationnelles")
        print("      - Le problème vient du frontend qui affiche les structures de Karibo")
        print()
    
    print("3. Actions recommandées:")
    print()
    print("   A. Vérifier le code du service backend:")
    print("      - Fichier: siirh-backend/app/services/hierarchical_organizational_service.py")
    print("      - Méthode: get_cascading_options()")
    print("      - Vérifier: Filtre WHERE employer_id = ?")
    print()
    
    print("   B. Vérifier le code du router backend:")
    print("      - Fichier: siirh-backend/app/routers/hierarchical_organization.py")
    print("      - Endpoint: /employers/{employer_id}/hierarchical-organization/cascading-options")
    print("      - Vérifier: Utilisation correcte de employer_id")
    print()
    
    print("   C. Vérifier le frontend:")
    print("      - Fichier: siirh-frontend/src/components/OrganizationalFilterModalOptimized.tsx")
    print("      - Vérifier: queryKey contient bien selectedEmployerId")
    print("      - Vérifier: Cache invalidé lors du changement")
    print()
    
    print("   D. Vérifier la base de données:")
    print("      - Table: hierarchical_organizational_nodes")
    print("      - Vérifier: Colonne employer_id existe et est remplie")
    print("      - Vérifier: Pas de données orphelines")
    print()
    
    return True

if __name__ == "__main__":
    success = audit_employer_chain()
    exit(0 if success else 1)
