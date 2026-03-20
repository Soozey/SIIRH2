#!/usr/bin/env python3
"""
Revérification complète du problème de filtrage
"""

import requests
import json

BACKEND_URL = "http://localhost:8000"

def reverify_complete_filtering():
    """Revérification complète du système de filtrage"""
    print("🔍 REVÉRIFICATION COMPLÈTE DU FILTRAGE")
    print("=" * 70)
    
    employer_id = 2
    period = "2025-01"
    
    # 1. État actuel des données
    print("1️⃣ ÉTAT ACTUEL DES DONNÉES:")
    print("-" * 35)
    
    # Vérifier le salarié
    try:
        response = requests.get(f"{BACKEND_URL}/workers/2032")
        if response.status_code == 200:
            worker = response.json()
            print(f"👤 Salarié: {worker['prenom']} {worker['nom']} (ID: {worker['id']})")
            print(f"   Employeur ID: {worker.get('employer_id')}")
            print(f"   Établissement: '{worker.get('etablissement', 'N/A')}'")
            print(f"   Département: '{worker.get('departement', 'N/A')}'")
            print(f"   Service: '{worker.get('service', 'N/A')}'")
            print(f"   Unité: '{worker.get('unite', 'N/A')}'")
            
            current_departement = worker.get('departement', '')
        else:
            print(f"❌ Erreur récupération salarié: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Exception: {e}")
        return
    
    print()
    
    # 2. Données organisationnelles disponibles
    print("2️⃣ DONNÉES ORGANISATIONNELLES DISPONIBLES:")
    print("-" * 45)
    
    # Source hiérarchique
    try:
        response = requests.get(f"{BACKEND_URL}/employers/{employer_id}/organizational-data/hierarchical")
        if response.status_code == 200:
            hierarchical_data = response.json()
            print(f"📊 Données hiérarchiques:")
            print(f"   Établissements: {hierarchical_data.get('etablissements', [])}")
            print(f"   Départements: {hierarchical_data.get('departements', [])}")
            print(f"   Services: {hierarchical_data.get('services', [])}")
            print(f"   Unités: {hierarchical_data.get('unites', [])}")
            
            available_departements = hierarchical_data.get('departements', [])
        else:
            print(f"❌ Erreur données hiérarchiques: {response.status_code}")
            available_departements = []
    except Exception as e:
        print(f"❌ Exception: {e}")
        available_departements = []
    
    # Source salariés
    try:
        response = requests.get(f"{BACKEND_URL}/employers/{employer_id}/organizational-data/workers")
        if response.status_code == 200:
            workers_data = response.json()
            print(f"\n📊 Données des salariés:")
            print(f"   Établissements: {workers_data.get('etablissements', [])}")
            print(f"   Départements: {workers_data.get('departements', [])}")
            print(f"   Services: {workers_data.get('services', [])}")
            print(f"   Unités: {workers_data.get('unites', [])}")
        else:
            print(f"❌ Erreur données salariés: {response.status_code}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    print()
    
    # 3. Tests de filtrage systématiques
    print("3️⃣ TESTS DE FILTRAGE SYSTÉMATIQUES:")
    print("-" * 40)
    
    # Test sans filtres
    print("🧪 Test 1: SANS FILTRES")
    try:
        response = requests.get(f"{BACKEND_URL}/payroll/bulk-preview", params={
            'employer_id': employer_id,
            'period': period
        })
        
        if response.status_code == 200:
            bulletins = response.json()
            print(f"   ✅ {len(bulletins)} bulletin(s) sans filtres")
            
            if bulletins:
                worker_info = bulletins[0]['worker']
                print(f"   👤 {worker_info['prenom']} {worker_info['nom']}")
                print(f"      Établissement: '{worker_info.get('etablissement', 'N/A')}'")
                print(f"      Département: '{worker_info.get('departement', 'N/A')}'")
        else:
            print(f"   ❌ Erreur: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test avec département actuel du salarié
    print(f"\n🧪 Test 2: AVEC DÉPARTEMENT ACTUEL '{current_departement}'")
    try:
        response = requests.get(f"{BACKEND_URL}/payroll/bulk-preview", params={
            'employer_id': employer_id,
            'period': period,
            'departement': current_departement
        })
        
        if response.status_code == 200:
            bulletins = response.json()
            print(f"   ✅ {len(bulletins)} bulletin(s) avec département '{current_departement}'")
            
            if len(bulletins) == 0:
                print(f"   ❌ PROBLÈME: Aucun bulletin avec le département actuel du salarié!")
        else:
            print(f"   ❌ Erreur: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test avec chaque département disponible
    print(f"\n🧪 Test 3: AVEC CHAQUE DÉPARTEMENT DISPONIBLE")
    for dept in available_departements:
        print(f"   Test département '{dept}':")
        try:
            response = requests.get(f"{BACKEND_URL}/payroll/bulk-preview", params={
                'employer_id': employer_id,
                'period': period,
                'departement': dept
            })
            
            if response.status_code == 200:
                bulletins = response.json()
                print(f"      ✅ {len(bulletins)} bulletin(s)")
                
                if len(bulletins) == 0:
                    print(f"      ❌ Aucun bulletin pour '{dept}'")
                else:
                    worker_info = bulletins[0]['worker']
                    print(f"      👤 {worker_info['prenom']} {worker_info['nom']}")
                    print(f"         Département salarié: '{worker_info.get('departement', 'N/A')}'")
            else:
                print(f"      ❌ Erreur: {response.status_code}")
        except Exception as e:
            print(f"      ❌ Exception: {e}")
    
    print()
    
    # 4. Diagnostic de l'interface
    print("4️⃣ DIAGNOSTIC DE L'INTERFACE:")
    print("-" * 35)
    
    print("🔍 PROBLÈMES POTENTIELS:")
    print("   1. Cache du navigateur")
    print("   2. Différence entre API directe et interface")
    print("   3. Paramètres URL mal formés")
    print("   4. Erreurs JavaScript non visibles")
    print("   5. Problème de timing (requêtes asynchrones)")
    print()
    print("🔧 ACTIONS DE VÉRIFICATION:")
    print("   1. Ouvrez les outils de développement (F12)")
    print("   2. Allez dans l'onglet 'Network' (Réseau)")
    print("   3. Videz le cache (Ctrl+Shift+R)")
    print("   4. Essayez le filtrage dans l'interface")
    print("   5. Regardez l'appel API vers /payroll/bulk-preview")
    print("   6. Vérifiez les paramètres envoyés et la réponse reçue")

def test_interface_simulation():
    """Simule exactement ce que fait l'interface"""
    print("\n5️⃣ SIMULATION EXACTE DE L'INTERFACE:")
    print("-" * 45)
    
    # Simuler le flux exact de l'interface
    employer_id = 2
    period = "2025-01"
    
    # Étape 1: L'interface récupère les données organisationnelles
    print("Étape 1: Récupération des données organisationnelles")
    try:
        response = requests.get(f"{BACKEND_URL}/employers/{employer_id}/organizational-data/hierarchical")
        if response.status_code == 200:
            org_data = response.json()
            print(f"   ✅ Données récupérées: {org_data}")
            
            # Étape 2: L'utilisateur sélectionne un filtre
            if 'SWEETY' in org_data.get('departements', []):
                selected_filter = 'SWEETY'
                print(f"   ✅ 'SWEETY' disponible dans l'interface")
            else:
                print(f"   ❌ 'SWEETY' non disponible dans l'interface")
                return
        else:
            print(f"   ❌ Erreur récupération données: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return
    
    # Étape 3: L'interface construit l'URL avec filtres
    print(f"\nÉtape 2: Construction de l'URL avec filtre '{selected_filter}'")
    
    # Simuler la construction d'URL de React Router
    frontend_url = f"/payslips-bulk/{employer_id}/{period}?departement={selected_filter}"
    print(f"   URL frontend: {frontend_url}")
    
    # Étape 4: Le composant PayslipsBulk fait l'appel API
    print(f"\nÉtape 3: Appel API du composant PayslipsBulk")
    
    # Simuler exactement l'appel de PayslipsBulk.tsx
    params = {
        'employer_id': employer_id,
        'period': period,
        'departement': selected_filter
    }
    
    print(f"   Paramètres API: {params}")
    
    try:
        # Headers comme axios
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(f"{BACKEND_URL}/payroll/bulk-preview", params=params, headers=headers)
        
        print(f"   Status: {response.status_code}")
        print(f"   URL complète: {response.url}")
        
        if response.status_code == 200:
            bulletins = response.json()
            print(f"   ✅ {len(bulletins)} bulletin(s) retourné(s)")
            
            if len(bulletins) == 0:
                print(f"   ❌ PROBLÈME CONFIRMÉ: L'interface reçoit une liste vide")
                print(f"   🔍 Cause: Le salarié n'a pas le département '{selected_filter}'")
            else:
                print(f"   ✅ Bulletins trouvés - L'interface devrait fonctionner")
                for bulletin in bulletins:
                    worker = bulletin['worker']
                    totaux = bulletin.get('totaux', {})
                    print(f"      📄 {worker['prenom']} {worker['nom']}")
                    print(f"         Brut: {totaux.get('brut', 0)} Ar")
        else:
            print(f"   ❌ Erreur API: {response.status_code}")
            try:
                error_data = response.json()
                print(f"      Détails: {error_data}")
            except:
                print(f"      Détails: {response.text}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")

def provide_final_diagnosis():
    """Fournit le diagnostic final"""
    print("\n6️⃣ DIAGNOSTIC FINAL:")
    print("-" * 25)
    
    print("🎯 PROBLÈME IDENTIFIÉ:")
    print("   Le système fonctionne techniquement, mais il y a une incohérence")
    print("   entre ce que l'interface affiche et les données réelles.")
    print()
    print("🔍 CAUSES POSSIBLES:")
    print("   1. 📱 CACHE NAVIGATEUR: L'interface utilise des données en cache")
    print("   2. 🔄 SYNCHRONISATION: Les données ne sont pas synchronisées en temps réel")
    print("   3. 🎭 INTERFACE: L'interface affiche 'SWEETY' mais le salarié n'y est pas affecté")
    print("   4. ⏱️ TIMING: Problème de timing entre les requêtes")
    print()
    print("🔧 SOLUTIONS IMMÉDIATES:")
    print("   1. Vider le cache du navigateur (Ctrl+Shift+R)")
    print("   2. Redémarrer le backend pour charger les nouveaux endpoints")
    print("   3. Vérifier que le salarié est bien affecté au bon département")
    print("   4. Utiliser les outils de développement pour voir les vraies requêtes")
    print()
    print("💡 SOLUTION DÉFINITIVE:")
    print("   Implémenter la synchronisation automatique dans l'interface")
    print("   avec un bouton 'Actualiser' ou 'Synchroniser'")

def main():
    """Fonction principale"""
    reverify_complete_filtering()
    test_interface_simulation()
    provide_final_diagnosis()

if __name__ == "__main__":
    main()