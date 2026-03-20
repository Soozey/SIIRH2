#!/usr/bin/env python3
"""
Correction de l'incohérence entre données hiérarchiques et données des salariés
"""

import requests
import json

BACKEND_URL = "http://localhost:8000"

def analyze_data_mismatch():
    """Analyse l'incohérence des données organisationnelles"""
    print("🔍 Analyse de l'incohérence des données organisationnelles")
    print("=" * 70)
    
    employer_id = 2  # Mandroso Services
    
    # 1. Récupérer les structures hiérarchiques
    print("1️⃣ STRUCTURES HIÉRARCHIQUES:")
    print("-" * 35)
    
    try:
        response = requests.get(f"{BACKEND_URL}/organizational-structures")
        if response.status_code == 200:
            structures = response.json()
            mandroso_structures = [s for s in structures if s.get('employer_id') == employer_id]
            
            print(f"📊 {len(mandroso_structures)} structure(s) hiérarchique(s) trouvée(s):")
            for struct in mandroso_structures:
                print(f"   🏢 {struct['name']} (ID: {struct['id']})")
                print(f"      - Type: {struct['type']}")
                print(f"      - Parent: {struct.get('parent_id', 'Racine')}")
        else:
            print(f"❌ Erreur récupération structures: {response.status_code}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    print()
    
    # 2. Récupérer les salariés et leurs affectations
    print("2️⃣ AFFECTATIONS DES SALARIÉS:")
    print("-" * 35)
    
    try:
        response = requests.get(f"{BACKEND_URL}/workers")
        if response.status_code == 200:
            all_workers = response.json()
            mandroso_workers = [w for w in all_workers if w.get('employer_id') == employer_id]
            
            print(f"📊 {len(mandroso_workers)} salarié(s) de Mandroso:")
            for worker in mandroso_workers:
                print(f"   👤 {worker.get('prenom', '')} {worker.get('nom', '')} (ID: {worker['id']})")
                print(f"      - Établissement: '{worker.get('etablissement', 'N/A')}'")
                print(f"      - Département: '{worker.get('departement', 'N/A')}'")
                print(f"      - Service: '{worker.get('service', 'N/A')}'")
                print(f"      - Unité: '{worker.get('unite', 'N/A')}'")
        else:
            print(f"❌ Erreur récupération salariés: {response.status_code}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    print()
    
    # 3. Proposer des solutions
    print("3️⃣ SOLUTIONS PROPOSÉES:")
    print("-" * 30)
    
    print("🔧 OPTION 1: Mettre à jour l'affectation du salarié")
    print("   - Changer l'établissement de Jeanne de '54' vers 'Mandroso Formation'")
    print("   - Changer le département de '55' vers 'EN LIGNE' ou 'SWEETY'")
    print()
    
    print("🔧 OPTION 2: Créer des structures correspondant aux valeurs actuelles")
    print("   - Créer un établissement '54' dans les structures hiérarchiques")
    print("   - Créer un département '55' dans les structures hiérarchiques")
    print()
    
    print("🔧 OPTION 3: Utiliser les données des salariés comme référence")
    print("   - Modifier l'interface pour afficher '54' au lieu de 'Mandroso Formation'")
    
    return mandroso_workers

def fix_worker_assignment():
    """Corrige l'affectation du salarié pour correspondre aux structures hiérarchiques"""
    print("\n🛠️ CORRECTION DE L'AFFECTATION DU SALARIÉ:")
    print("-" * 50)
    
    # Récupérer le salarié Jeanne
    try:
        response = requests.get(f"{BACKEND_URL}/workers")
        if response.status_code == 200:
            all_workers = response.json()
            jeanne = next((w for w in all_workers if w.get('employer_id') == 2 and 'Jeanne' in w.get('prenom', '')), None)
            
            if jeanne:
                print(f"👤 Salarié trouvé: {jeanne['prenom']} {jeanne['nom']} (ID: {jeanne['id']})")
                print(f"   Affectation actuelle:")
                print(f"   - Établissement: '{jeanne.get('etablissement', 'N/A')}'")
                print(f"   - Département: '{jeanne.get('departement', 'N/A')}'")
                
                # Proposer la mise à jour
                new_data = {
                    "etablissement": "Mandroso Formation",
                    "departement": "EN LIGNE"
                }
                
                print(f"\n🔄 Proposition de mise à jour:")
                print(f"   - Nouvel établissement: '{new_data['etablissement']}'")
                print(f"   - Nouveau département: '{new_data['departement']}'")
                
                # Effectuer la mise à jour
                update_response = requests.put(f"{BACKEND_URL}/workers/{jeanne['id']}", json={
                    **jeanne,
                    **new_data
                })
                
                if update_response.status_code == 200:
                    print("✅ Mise à jour réussie!")
                    
                    # Tester la génération de bulletins après mise à jour
                    print("\n🧪 Test génération bulletins après correction:")
                    
                    # Test avec nouveau filtre
                    test_response = requests.get(f"{BACKEND_URL}/payroll/bulk-preview", params={
                        'employer_id': 2,
                        'period': '2025-01',
                        'etablissement': 'Mandroso Formation'
                    })
                    
                    if test_response.status_code == 200:
                        bulletins = test_response.json()
                        print(f"✅ {len(bulletins)} bulletin(s) généré(s) avec filtre 'Mandroso Formation'")
                        
                        if bulletins:
                            for bulletin in bulletins:
                                worker = bulletin['worker']
                                print(f"   📄 {worker['prenom']} {worker['nom']}")
                                print(f"      - Établissement: {worker.get('etablissement', 'N/A')}")
                                print(f"      - Département: {worker.get('departement', 'N/A')}")
                        
                        return True
                    else:
                        print(f"❌ Erreur test bulletins: {test_response.status_code}")
                else:
                    print(f"❌ Erreur mise à jour: {update_response.status_code}")
                    try:
                        error_data = update_response.json()
                        print(f"   Détails: {error_data}")
                    except:
                        print(f"   Détails: {update_response.text}")
            else:
                print("❌ Salarié Jeanne non trouvé")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    return False

def test_bulletin_calculation():
    """Test le calcul des bulletins pour identifier pourquoi brut/net = 0"""
    print("\n🧮 TEST CALCUL DES BULLETINS:")
    print("-" * 40)
    
    try:
        # Test bulletin individuel pour Jeanne
        response = requests.get(f"{BACKEND_URL}/payroll/preview", params={
            'worker_id': 2032,  # ID de Jeanne
            'period': '2025-01'
        })
        
        if response.status_code == 200:
            bulletin = response.json()
            
            print("📄 Détails du bulletin de Jeanne:")
            print(f"   Salarié: {bulletin['worker']['prenom']} {bulletin['worker']['nom']}")
            print(f"   Période: {bulletin['period']}")
            
            totaux = bulletin.get('totaux', {})
            print(f"   💰 Totaux:")
            print(f"      - Brut total: {totaux.get('brut_total', 0)} Ar")
            print(f"      - Net total: {totaux.get('net_total', 0)} Ar")
            print(f"      - Cotisations: {totaux.get('cotisations_total', 0)} Ar")
            
            lines = bulletin.get('lines', [])
            print(f"   📋 {len(lines)} ligne(s) de calcul:")
            for line in lines[:5]:  # Afficher les 5 premières lignes
                print(f"      - {line.get('label', 'N/A')}: {line.get('montant', 0)} Ar")
            
            if totaux.get('brut_total', 0) == 0:
                print("\n⚠️ PROBLÈME IDENTIFIÉ: Brut total = 0")
                print("   Causes possibles:")
                print("   - Salaire de base non configuré")
                print("   - Erreur dans le calcul de paie")
                print("   - Données manquantes (VHM, type régime, etc.)")
                
                # Vérifier les données du salarié
                worker_data = bulletin['worker']
                print(f"\n🔍 Vérification données salarié:")
                print(f"   - Salaire base: {worker_data.get('salaire_base', 'N/A')} Ar")
                print(f"   - VHM: {worker_data.get('vhm', 'N/A')}")
                print(f"   - Catégorie prof: {worker_data.get('categorie_prof', 'N/A')}")
                print(f"   - Secteur: {worker_data.get('secteur', 'N/A')}")
        else:
            print(f"❌ Erreur génération bulletin: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Détails: {error_data}")
            except:
                print(f"   Détails: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")

def main():
    """Fonction principale"""
    print("🚀 Correction du problème de filtrage organisationnel")
    print("=" * 70)
    
    # 1. Analyser l'incohérence
    workers = analyze_data_mismatch()
    
    # 2. Tester le calcul des bulletins
    test_bulletin_calculation()
    
    # 3. Corriger l'affectation
    if workers:
        print("\n" + "="*70)
        choice = input("Voulez-vous corriger l'affectation du salarié ? (o/n): ").lower().strip()
        
        if choice == 'o':
            success = fix_worker_assignment()
            if success:
                print("\n🎉 CORRECTION RÉUSSIE!")
                print("L'utilisateur peut maintenant utiliser le filtre 'Mandroso Formation'")
            else:
                print("\n❌ CORRECTION ÉCHOUÉE")
        else:
            print("\n💡 RECOMMANDATIONS:")
            print("1. Corriger manuellement l'affectation de Jeanne RAFARAVAVY")
            print("2. Ou créer des structures '54' et '55' dans la hiérarchie")
            print("3. Ou utiliser les filtres '54' et '55' au lieu des noms")

if __name__ == "__main__":
    main()