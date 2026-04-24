#!/usr/bin/env python3
"""
Script pour identifier précisément l'URL qui cause l'erreur 500
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_with_different_scenarios():
    """Test différents scénarios qui pourraient causer l'erreur 500"""
    
    print("🔍 IDENTIFICATION PRÉCISE DE L'ERREUR 500")
    print("=" * 50)
    
    # Scénario 1: Test avec tous les employeurs existants
    print("\n1️⃣ Test avec tous les employeurs existants...")
    try:
        response = requests.get(f"{BASE_URL}/employers")
        if response.status_code == 200:
            employers = response.json()
            print(f"   Trouvé {len(employers)} employeurs")
            
            for employer in employers:
                employer_id = employer['id']
                print(f"\n   Test employeur ID {employer_id} ({employer.get('raison_sociale', 'N/A')}):")
                
                # Test tree
                try:
                    tree_response = requests.get(f"{BASE_URL}/organizational-structure/{employer_id}/tree")
                    if tree_response.status_code == 500:
                        print(f"   ❌ ERREUR 500 sur /organizational-structure/{employer_id}/tree")
                        print(f"   Response: {tree_response.text[:200]}")
                        return f"/organizational-structure/{employer_id}/tree"
                    else:
                        print(f"   ✅ Tree: {tree_response.status_code}")
                except Exception as e:
                    print(f"   ❌ Exception tree: {e}")
                
                # Test validate
                try:
                    validate_response = requests.get(f"{BASE_URL}/organizational-structure/{employer_id}/validate")
                    if validate_response.status_code == 500:
                        print(f"   ❌ ERREUR 500 sur /organizational-structure/{employer_id}/validate")
                        return f"/organizational-structure/{employer_id}/validate"
                    else:
                        print(f"   ✅ Validate: {validate_response.status_code}")
                except Exception as e:
                    print(f"   ❌ Exception validate: {e}")
                
                # Test children
                try:
                    children_response = requests.get(f"{BASE_URL}/organizational-structure/{employer_id}/children")
                    if children_response.status_code == 500:
                        print(f"   ❌ ERREUR 500 sur /organizational-structure/{employer_id}/children")
                        return f"/organizational-structure/{employer_id}/children"
                    else:
                        print(f"   ✅ Children: {children_response.status_code}")
                except Exception as e:
                    print(f"   ❌ Exception children: {e}")
        else:
            print(f"   ❌ Erreur récupération employeurs: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Exception employeurs: {e}")
    
    # Scénario 2: Test avec des IDs d'unités organisationnelles
    print("\n2️⃣ Test avec des unités organisationnelles existantes...")
    try:
        # Récupérer des unités existantes
        tree_response = requests.get(f"{BASE_URL}/organizational-structure/1/tree")
        if tree_response.status_code == 200:
            tree_data = tree_response.json()
            
            def extract_unit_ids(tree_node):
                ids = []
                if isinstance(tree_node, dict) and 'id' in tree_node:
                    ids.append(tree_node['id'])
                    if 'children' in tree_node:
                        for child in tree_node['children']:
                            ids.extend(extract_unit_ids(child))
                elif isinstance(tree_node, list):
                    for item in tree_node:
                        ids.extend(extract_unit_ids(item))
                return ids
            
            unit_ids = extract_unit_ids(tree_data.get('tree', []))
            print(f"   Trouvé {len(unit_ids)} unités organisationnelles")
            
            for unit_id in unit_ids[:5]:  # Test les 5 premières
                print(f"\n   Test unité ID {unit_id}:")
                
                # Test can-delete
                try:
                    delete_response = requests.get(f"{BASE_URL}/organizational-structure/{unit_id}/can-delete")
                    if delete_response.status_code == 500:
                        print(f"   ❌ ERREUR 500 sur /organizational-structure/{unit_id}/can-delete")
                        return f"/organizational-structure/{unit_id}/can-delete"
                    else:
                        print(f"   ✅ Can-delete: {delete_response.status_code}")
                except Exception as e:
                    print(f"   ❌ Exception can-delete: {e}")
        else:
            print(f"   ❌ Impossible de récupérer l'arbre: {tree_response.status_code}")
    except Exception as e:
        print(f"   ❌ Exception unités: {e}")
    
    # Scénario 3: Test des endpoints workers
    print("\n3️⃣ Test des endpoints workers...")
    try:
        workers_response = requests.get(f"{BASE_URL}/workers")
        if workers_response.status_code == 500:
            print(f"   ❌ ERREUR 500 sur /workers")
            return "/workers"
        else:
            print(f"   ✅ Workers: {workers_response.status_code}")
            
            if workers_response.status_code == 200:
                workers = workers_response.json()
                print(f"   Trouvé {len(workers)} workers")
                
                # Test quelques workers individuels
                for worker in workers[:3]:  # Test les 3 premiers
                    worker_id = worker.get('id')
                    if worker_id:
                        try:
                            worker_response = requests.get(f"{BASE_URL}/workers/{worker_id}")
                            if worker_response.status_code == 500:
                                print(f"   ❌ ERREUR 500 sur /workers/{worker_id}")
                                return f"/workers/{worker_id}"
                            else:
                                print(f"   ✅ Worker {worker_id}: {worker_response.status_code}")
                        except Exception as e:
                            print(f"   ❌ Exception worker {worker_id}: {e}")
    except Exception as e:
        print(f"   ❌ Exception workers: {e}")
    
    # Scénario 4: Test des endpoints avec paramètres
    print("\n4️⃣ Test des endpoints avec paramètres...")
    
    test_urls = [
        "/organizational-structure/1/choices?level=etablissement",
        "/organizational-structure/1/choices?level=departement&parent_id=1",
        "/organizational-structure/validate-combination?employer_id=1",
        "/workers?employer_id=1",
    ]
    
    for url in test_urls:
        try:
            print(f"   Test: {url}")
            response = requests.get(f"{BASE_URL}{url}")
            if response.status_code == 500:
                print(f"   ❌ ERREUR 500 sur {url}")
                return url
            else:
                print(f"   ✅ {response.status_code}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    return None

def simulate_frontend_behavior():
    """Simuler exactement le comportement du frontend"""
    
    print("\n🎯 SIMULATION DU COMPORTEMENT FRONTEND")
    print("-" * 40)
    
    # Séquence typique du frontend
    sequence = [
        ("Chargement initial", "/employers"),
        ("Sélection employeur", "/organizational-structure/1/tree"),
        ("Validation hiérarchie", "/organizational-structure/1/validate"),
        ("Récupération enfants", "/organizational-structure/1/children"),
        ("Chargement workers", "/workers"),
    ]
    
    for step_name, url in sequence:
        try:
            print(f"\n   {step_name}: {url}")
            response = requests.get(f"{BASE_URL}{url}")
            
            if response.status_code == 500:
                print(f"   ❌ ERREUR 500 DÉTECTÉE!")
                print(f"   Étape: {step_name}")
                print(f"   URL: {url}")
                print(f"   Response: {response.text[:300]}")
                return url
            else:
                print(f"   ✅ {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    return None

if __name__ == "__main__":
    print("🚨 IDENTIFICATION DE L'ERREUR 500 APRÈS CTRL+F5")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%H:%M:%S')}")
    
    # Test des différents scénarios
    error_url_1 = test_with_different_scenarios()
    error_url_2 = simulate_frontend_behavior()
    
    # Résumé final
    print(f"\n📊 RÉSUMÉ FINAL")
    print("=" * 20)
    
    if error_url_1 or error_url_2:
        print("❌ ERREUR 500 IDENTIFIÉE:")
        if error_url_1:
            print(f"   Scénario 1: {error_url_1}")
        if error_url_2:
            print(f"   Scénario 2: {error_url_2}")
    else:
        print("✅ Aucune erreur 500 détectée dans les tests automatiques")
        print("\n💡 L'erreur pourrait être:")
        print("   1. Intermittente (liée à un timing spécifique)")
        print("   2. Liée à une action utilisateur spécifique")
        print("   3. Causée par un état particulier de l'application")
        print("\n🔍 Pour identifier l'erreur:")
        print("   1. Ouvrez F12 > Network dans votre navigateur")
        print("   2. Faites Ctrl+F5 pour recharger")
        print("   3. Cherchez les requêtes en rouge (status 500)")
        print("   4. Cliquez sur la requête pour voir l'URL exacte")
        print("   5. Partagez cette URL pour diagnostic précis")