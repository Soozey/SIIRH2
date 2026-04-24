#!/usr/bin/env python3
"""
Test de détection d'affectations invalides
"""

import requests
import json

def test_invalid_assignments():
    print('🔍 Test de détection d\'affectations invalides')
    print('=' * 55)

    # 1. Créer une affectation invalide temporairement
    print('1️⃣ Création d\'une affectation invalide pour test:')
    
    # Modifier temporairement un salarié avec une affectation inexistante
    worker_id = 2032  # Jeanne
    update_data = {
        "departement": "DEPARTEMENT_INEXISTANT"
    }
    
    response = requests.put(f'http://localhost:8000/workers/{worker_id}', json=update_data)
    if response.status_code == 200:
        print('   ✅ Affectation invalide créée pour test')
    else:
        print(f'   ❌ Erreur: {response.status_code}')

    print()

    # 2. Test de validation (doit détecter le problème)
    print('2️⃣ Test de validation - détection du problème:')
    response = requests.post('http://localhost:8000/organizational-structure/2/sync-workers')
    if response.status_code == 200:
        result = response.json()
        print(f'   Succès: {result["success"]}')
        print(f'   Modifications appliquées: {result["total_updated"]}')
        print(f'   Affectations invalides détectées: {result.get("total_invalid_detected", 0)}')
        print(f'   Message: {result.get("message", "N/A")}')
        
        if result.get("total_invalid_detected", 0) > 0:
            print('   Détails des problèmes détectés:')
            for structure_type, issues in result['details'].items():
                if issues:
                    for issue in issues:
                        print(f'     - {issue["worker_name"]}: {structure_type[:-1]} = "{issue["old_value"]}"')
                        print(f'       Options disponibles: {issue.get("available_options", [])}')
    else:
        print(f'   Erreur: {response.status_code}')

    print()

    # 3. Vérifier que les données ne sont toujours PAS modifiées
    print('3️⃣ Vérification que les données invalides sont préservées:')
    response = requests.get(f'http://localhost:8000/workers/{worker_id}')
    if response.status_code == 200:
        worker = response.json()
        print(f'   {worker["prenom"]} {worker["nom"]}:')
        print(f'     Département: {worker.get("departement", "N/A")} (doit rester invalide)')
    else:
        print(f'   Erreur: {response.status_code}')

    print()

    # 4. Restaurer l'affectation valide
    print('4️⃣ Restauration de l\'affectation valide:')
    restore_data = {
        "departement": "AZER"
    }
    
    response = requests.put(f'http://localhost:8000/workers/{worker_id}', json=restore_data)
    if response.status_code == 200:
        print('   ✅ Affectation valide restaurée')
    else:
        print(f'   ❌ Erreur: {response.status_code}')

    print()

    # 5. Validation finale
    print('5️⃣ Validation finale:')
    response = requests.post('http://localhost:8000/organizational-structure/2/sync-workers')
    if response.status_code == 200:
        result = response.json()
        print(f'   Affectations invalides: {result.get("total_invalid_detected", 0)}')
        if result.get("total_invalid_detected", 0) == 0:
            print('   ✅ Toutes les affectations sont maintenant valides')
    else:
        print(f'   Erreur: {response.status_code}')

if __name__ == "__main__":
    test_invalid_assignments()