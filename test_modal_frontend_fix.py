"""
Test de validation du fix de l'erreur 500 du modal optimisé
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

def test_modal_endpoints():
    """Tester tous les endpoints utilisés par le modal optimisé"""
    print("=" * 80)
    print("TEST DU MODAL OPTIMISÉ - VALIDATION DU FIX")
    print("=" * 80)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    results = {
        "success": [],
        "errors": []
    }
    
    # 1. Test de l'endpoint des employeurs (utilisé au chargement du modal)
    print("1️⃣ Test: Chargement de la liste des employeurs")
    print("   Endpoint: GET /employers")
    try:
        response = requests.get(f"{BASE_URL}/employers", timeout=5)
        if response.status_code == 200:
            employers = response.json()
            print(f"   ✅ OK - {len(employers)} employeur(s) trouvé(s)")
            for emp in employers:
                print(f"      - ID: {emp['id']}, Nom: {emp['raison_sociale']}")
            results["success"].append("GET /employers")
            
            # Utiliser le premier employeur pour les tests suivants
            if employers:
                employer_id = employers[0]['id']
                print(f"\n   📌 Utilisation de l'employeur ID {employer_id} pour les tests suivants")
            else:
                print("   ⚠️  Aucun employeur trouvé - impossible de continuer les tests")
                return results
        else:
            print(f"   ❌ ERREUR {response.status_code}")
            results["errors"].append(f"GET /employers - Status {response.status_code}")
            return results
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        results["errors"].append(f"GET /employers - {str(e)}")
        return results
    
    print()
    
    # 2. Test de l'endpoint des établissements (niveau racine)
    print("2️⃣ Test: Chargement des établissements (niveau racine)")
    print(f"   Endpoint: GET /employers/{employer_id}/hierarchical-organization/cascading-options")
    print("   Params: parent_id=null")
    try:
        response = requests.get(
            f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/cascading-options",
            params={"parent_id": None},
            timeout=5
        )
        if response.status_code == 200:
            etablissements = response.json()
            print(f"   ✅ OK - {len(etablissements)} établissement(s) trouvé(s)")
            for etab in etablissements:
                print(f"      - ID: {etab['id']}, Nom: {etab['name']}, Niveau: {etab['level']}")
            results["success"].append("GET cascading-options (établissements)")
            
            # Utiliser le premier établissement pour les tests suivants
            if etablissements:
                etablissement_id = etablissements[0]['id']
                print(f"\n   📌 Utilisation de l'établissement ID {etablissement_id} pour les tests suivants")
            else:
                print("   ℹ️  Aucun établissement trouvé - tests de cascade limités")
                etablissement_id = None
        else:
            print(f"   ❌ ERREUR {response.status_code}")
            print(f"   Réponse: {response.text[:500]}")
            results["errors"].append(f"GET cascading-options (établissements) - Status {response.status_code}")
            etablissement_id = None
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        results["errors"].append(f"GET cascading-options (établissements) - {str(e)}")
        etablissement_id = None
    
    print()
    
    # 3. Test de l'endpoint des départements (si établissement disponible)
    if etablissement_id:
        print("3️⃣ Test: Chargement des départements (filtrage en cascade)")
        print(f"   Endpoint: GET /employers/{employer_id}/hierarchical-organization/cascading-options")
        print(f"   Params: parent_id={etablissement_id}")
        try:
            response = requests.get(
                f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/cascading-options",
                params={"parent_id": etablissement_id},
                timeout=5
            )
            if response.status_code == 200:
                departements = response.json()
                print(f"   ✅ OK - {len(departements)} département(s) trouvé(s)")
                for dept in departements:
                    print(f"      - ID: {dept['id']}, Nom: {dept['name']}, Niveau: {dept['level']}")
                results["success"].append("GET cascading-options (départements)")
                
                # Utiliser le premier département pour les tests suivants
                if departements:
                    departement_id = departements[0]['id']
                    print(f"\n   📌 Utilisation du département ID {departement_id} pour les tests suivants")
                else:
                    print("   ℹ️  Aucun département trouvé - tests de cascade limités")
                    departement_id = None
            else:
                print(f"   ❌ ERREUR {response.status_code}")
                print(f"   Réponse: {response.text[:500]}")
                results["errors"].append(f"GET cascading-options (départements) - Status {response.status_code}")
                departement_id = None
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            results["errors"].append(f"GET cascading-options (départements) - {str(e)}")
            departement_id = None
        
        print()
        
        # 4. Test de l'endpoint des services (si département disponible)
        if departement_id:
            print("4️⃣ Test: Chargement des services (filtrage en cascade)")
            print(f"   Endpoint: GET /employers/{employer_id}/hierarchical-organization/cascading-options")
            print(f"   Params: parent_id={departement_id}")
            try:
                response = requests.get(
                    f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/cascading-options",
                    params={"parent_id": departement_id},
                    timeout=5
                )
                if response.status_code == 200:
                    services = response.json()
                    print(f"   ✅ OK - {len(services)} service(s) trouvé(s)")
                    for svc in services:
                        print(f"      - ID: {svc['id']}, Nom: {svc['name']}, Niveau: {svc['level']}")
                    results["success"].append("GET cascading-options (services)")
                    
                    # Utiliser le premier service pour les tests suivants
                    if services:
                        service_id = services[0]['id']
                        print(f"\n   📌 Utilisation du service ID {service_id} pour les tests suivants")
                    else:
                        print("   ℹ️  Aucun service trouvé - tests de cascade limités")
                        service_id = None
                else:
                    print(f"   ❌ ERREUR {response.status_code}")
                    print(f"   Réponse: {response.text[:500]}")
                    results["errors"].append(f"GET cascading-options (services) - Status {response.status_code}")
                    service_id = None
            except Exception as e:
                print(f"   ❌ Exception: {e}")
                results["errors"].append(f"GET cascading-options (services) - {str(e)}")
                service_id = None
            
            print()
            
            # 5. Test de l'endpoint des unités (si service disponible)
            if service_id:
                print("5️⃣ Test: Chargement des unités (filtrage en cascade)")
                print(f"   Endpoint: GET /employers/{employer_id}/hierarchical-organization/cascading-options")
                print(f"   Params: parent_id={service_id}")
                try:
                    response = requests.get(
                        f"{BASE_URL}/employers/{employer_id}/hierarchical-organization/cascading-options",
                        params={"parent_id": service_id},
                        timeout=5
                    )
                    if response.status_code == 200:
                        unites = response.json()
                        print(f"   ✅ OK - {len(unites)} unité(s) trouvée(s)")
                        for unite in unites:
                            print(f"      - ID: {unite['id']}, Nom: {unite['name']}, Niveau: {unite['level']}")
                        results["success"].append("GET cascading-options (unités)")
                    else:
                        print(f"   ❌ ERREUR {response.status_code}")
                        print(f"   Réponse: {response.text[:500]}")
                        results["errors"].append(f"GET cascading-options (unités) - Status {response.status_code}")
                except Exception as e:
                    print(f"   ❌ Exception: {e}")
                    results["errors"].append(f"GET cascading-options (unités) - {str(e)}")
                
                print()
    
    # Résumé
    print("=" * 80)
    print("RÉSUMÉ DES TESTS")
    print("=" * 80)
    print()
    
    print(f"✅ Tests réussis: {len(results['success'])}")
    for test in results['success']:
        print(f"   - {test}")
    print()
    
    if results['errors']:
        print(f"❌ Tests échoués: {len(results['errors'])}")
        for error in results['errors']:
            print(f"   - {error}")
        print()
    
    # Verdict final
    print("=" * 80)
    if not results['errors']:
        print("✅ TOUS LES TESTS SONT PASSÉS!")
        print()
        print("Le modal optimisé devrait fonctionner correctement.")
        print("L'erreur 500 était causée par une erreur de syntaxe TypeScript qui a été corrigée.")
        print()
        print("Actions à faire:")
        print("1. Redémarrer le serveur de développement frontend si nécessaire")
        print("2. Ouvrir la page /payroll dans le navigateur")
        print("3. Cliquer sur 'Imprimer tous les bulletins'")
        print("4. Vérifier que le modal s'ouvre sans erreur 500")
        print("5. Tester le filtrage en cascade")
    else:
        print("❌ CERTAINS TESTS ONT ÉCHOUÉ")
        print()
        print("Vérifier les erreurs ci-dessus et corriger les problèmes.")
    print("=" * 80)
    
    return results

if __name__ == "__main__":
    results = test_modal_endpoints()
    exit(0 if not results["errors"] else 1)
