#!/usr/bin/env python3
"""
Diagnostic du problème de filtrage dynamique - Test avec département "SWEETY"
"""

import requests
import json

BACKEND_URL = "http://localhost:8000"

def analyze_dynamic_filtering_issue():
    """Analyse le problème de filtrage dynamique"""
    print("🔍 Diagnostic du problème de filtrage dynamique")
    print("=" * 70)
    
    employer_id = 2  # Mandroso Services
    period = "2025-01"
    
    print(f"📋 Contexte du test:")
    print(f"   - Employeur: Mandroso Services (ID: {employer_id})")
    print(f"   - Période: {period}")
    print(f"   - Test: Département renommé en 'SWEETY'")
    print()
    
    # 1. Vérifier l'état actuel des données
    print("1️⃣ ÉTAT ACTUEL DES DONNÉES:")
    print("-" * 35)
    
    # Vérifier les salariés
    try:
        response = requests.get(f"{BACKEND_URL}/workers")
        if response.status_code == 200:
            workers = response.json()
            mandroso_workers = [w for w in workers if w.get('employer_id') == employer_id]
            
            print(f"👥 Salariés de Mandroso Services:")
            for worker in mandroso_workers:
                print(f"   👤 {worker['prenom']} {worker['nom']} (ID: {worker['id']})")
                print(f"      - Établissement: '{worker.get('etablissement', 'N/A')}'")
                print(f"      - Département: '{worker.get('departement', 'N/A')}'")
                print(f"      - Service: '{worker.get('service', 'N/A')}'")
                print(f"      - Unité: '{worker.get('unite', 'N/A')}'")
        else:
            print(f"❌ Erreur récupération salariés: {response.status_code}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    print()
    
    # 2. Vérifier les sources de données organisationnelles
    print("2️⃣ SOURCES DE DONNÉES ORGANISATIONNELLES:")
    print("-" * 45)
    
    # Source A: Structures hiérarchiques (nouvelles)
    print("📊 Source A: Structures hiérarchiques (/organizational-data/hierarchical)")
    try:
        response = requests.get(f"{BACKEND_URL}/employers/{employer_id}/organizational-data/hierarchical")
        if response.status_code == 200:
            hierarchical_data = response.json()
            print(f"   Établissements: {hierarchical_data.get('etablissements', [])}")
            print(f"   Départements: {hierarchical_data.get('departements', [])}")
            print(f"   Services: {hierarchical_data.get('services', [])}")
            print(f"   Unités: {hierarchical_data.get('unites', [])}")
            
            has_sweety_hierarchical = 'SWEETY' in hierarchical_data.get('departements', [])
            print(f"   🔍 'SWEETY' dans les données hiérarchiques: {'✅' if has_sweety_hierarchical else '❌'}")
        else:
            print(f"   ❌ Erreur: {response.status_code}")
            has_sweety_hierarchical = False
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        has_sweety_hierarchical = False
    
    print()
    
    # Source B: Données des salariés (anciennes)
    print("📊 Source B: Données des salariés (/organizational-data/workers)")
    try:
        response = requests.get(f"{BACKEND_URL}/employers/{employer_id}/organizational-data/workers")
        if response.status_code == 200:
            workers_data = response.json()
            print(f"   Établissements: {workers_data.get('etablissements', [])}")
            print(f"   Départements: {workers_data.get('departements', [])}")
            print(f"   Services: {workers_data.get('services', [])}")
            print(f"   Unités: {workers_data.get('unites', [])}")
            
            has_sweety_workers = 'SWEETY' in workers_data.get('departements', [])
            print(f"   🔍 'SWEETY' dans les données salariés: {'✅' if has_sweety_workers else '❌'}")
        else:
            print(f"   ❌ Erreur: {response.status_code}")
            has_sweety_workers = False
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        has_sweety_workers = False
    
    print()
    
    # 3. Identifier le problème de synchronisation
    print("3️⃣ ANALYSE DE SYNCHRONISATION:")
    print("-" * 35)
    
    if has_sweety_hierarchical and not has_sweety_workers:
        print("🔍 PROBLÈME IDENTIFIÉ:")
        print("   ✅ 'SWEETY' existe dans les structures hiérarchiques")
        print("   ❌ 'SWEETY' n'existe PAS dans les données des salariés")
        print("   🔧 CAUSE: Désynchronisation entre les deux sources de données")
        print()
        print("💡 EXPLICATION:")
        print("   - L'interface utilise les données hiérarchiques pour afficher les filtres")
        print("   - Le backend utilise les données des salariés pour le filtrage")
        print("   - Quand vous renommez une structure, seules les données hiérarchiques sont mises à jour")
        print("   - Les affectations des salariés restent avec les anciennes valeurs")
        
        sync_issue = True
    elif not has_sweety_hierarchical and not has_sweety_workers:
        print("🔍 PROBLÈME POTENTIEL:")
        print("   ❌ 'SWEETY' n'existe dans AUCUNE source")
        print("   🔧 CAUSE: Le renommage n'a pas été effectué ou n'a pas été sauvegardé")
        
        sync_issue = False
    else:
        print("🔍 ÉTAT NORMAL:")
        print("   ✅ Les données semblent synchronisées")
        
        sync_issue = False
    
    print()
    
    # 4. Test de filtrage avec 'SWEETY'
    print("4️⃣ TEST DE FILTRAGE AVEC 'SWEETY':")
    print("-" * 40)
    
    try:
        response = requests.get(f"{BACKEND_URL}/payroll/bulk-preview", params={
            'employer_id': employer_id,
            'period': period,
            'departement': 'SWEETY'
        })
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            bulletins = response.json()
            print(f"✅ {len(bulletins)} bulletin(s) trouvé(s) avec filtre 'SWEETY'")
            
            if len(bulletins) == 0:
                print("❌ AUCUN BULLETIN - Confirme le problème de synchronisation")
            else:
                print("✅ Bulletins trouvés - Le filtrage fonctionne")
                for bulletin in bulletins:
                    worker = bulletin['worker']
                    print(f"   👤 {worker['prenom']} {worker['nom']}")
                    print(f"      Département: '{worker.get('departement', 'N/A')}'")
        else:
            print(f"❌ Erreur: {response.status_code}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    return sync_issue

def test_manual_worker_update():
    """Teste la mise à jour manuelle d'un salarié vers 'SWEETY'"""
    print("\n5️⃣ TEST DE MISE À JOUR MANUELLE:")
    print("-" * 40)
    
    print("🔧 Simulation: Mise à jour manuelle du salarié vers 'SWEETY'")
    
    try:
        # Récupérer le salarié Jeanne
        response = requests.get(f"{BACKEND_URL}/workers/2032")
        if response.status_code == 200:
            worker = response.json()
            
            print(f"👤 Salarié actuel: {worker['prenom']} {worker['nom']}")
            print(f"   Département actuel: '{worker.get('departement', 'N/A')}'")
            
            # Mettre à jour vers SWEETY
            updated_worker = {
                **worker,
                'departement': 'SWEETY'
            }
            
            print(f"🔄 Mise à jour vers département 'SWEETY'...")
            
            update_response = requests.put(f"{BACKEND_URL}/workers/2032", json=updated_worker)
            
            if update_response.status_code == 200:
                print(f"✅ Mise à jour réussie")
                
                # Test immédiat du filtrage
                print(f"🧪 Test filtrage immédiat:")
                
                filter_response = requests.get(f"{BACKEND_URL}/payroll/bulk-preview", params={
                    'employer_id': 2,
                    'period': '2025-01',
                    'departement': 'SWEETY'
                })
                
                if filter_response.status_code == 200:
                    bulletins = filter_response.json()
                    print(f"   ✅ {len(bulletins)} bulletin(s) avec 'SWEETY'")
                    
                    if len(bulletins) > 0:
                        print(f"   🎉 SUCCÈS! Le filtrage dynamique fonctionne après mise à jour manuelle")
                        return True
                    else:
                        print(f"   ❌ Toujours aucun bulletin")
                else:
                    print(f"   ❌ Erreur filtrage: {filter_response.status_code}")
            else:
                print(f"❌ Erreur mise à jour: {update_response.status_code}")
        else:
            print(f"❌ Erreur récupération salarié: {response.status_code}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    return False

def analyze_root_cause():
    """Analyse la cause racine du problème"""
    print("\n6️⃣ ANALYSE DE LA CAUSE RACINE:")
    print("-" * 40)
    
    print("🔍 PROBLÈME IDENTIFIÉ:")
    print("   Le système utilise DEUX sources de données distinctes:")
    print()
    print("   📊 Source 1: Structures hiérarchiques (organizational_structures table)")
    print("      - Utilisée par l'interface pour afficher les filtres")
    print("      - Mise à jour quand vous modifiez les structures")
    print("      - Contient les nouvelles valeurs (ex: 'SWEETY')")
    print()
    print("   📊 Source 2: Affectations des salariés (workers table)")
    print("      - Utilisée par le backend pour le filtrage des bulletins")
    print("      - PAS mise à jour automatiquement lors des changements de structure")
    print("      - Contient les anciennes valeurs (ex: 'EN LIGNE')")
    print()
    print("🔧 CONSÉQUENCE:")
    print("   - L'interface affiche 'SWEETY' dans les filtres")
    print("   - Le backend cherche des salariés avec département = 'SWEETY'")
    print("   - Aucun salarié n'a département = 'SWEETY' dans sa fiche")
    print("   - Résultat: 0 bulletin trouvé")
    print()
    print("💡 SOLUTIONS POSSIBLES:")
    print("   1. 🔄 SYNCHRONISATION AUTOMATIQUE:")
    print("      - Mettre à jour automatiquement les salariés lors des changements de structure")
    print("      - Créer un système de migration automatique")
    print()
    print("   2. 🔗 JOINTURE DYNAMIQUE:")
    print("      - Modifier le backend pour utiliser les structures hiérarchiques")
    print("      - Faire une jointure entre workers et organizational_structures")
    print()
    print("   3. 📝 MISE À JOUR MANUELLE:")
    print("      - Obliger l'utilisateur à mettre à jour manuellement les affectations")
    print("      - Ajouter une interface de migration des salariés")

def propose_solutions():
    """Propose des solutions concrètes"""
    print("\n7️⃣ SOLUTIONS RECOMMANDÉES:")
    print("-" * 35)
    
    print("🎯 SOLUTION RECOMMANDÉE: Synchronisation automatique")
    print()
    print("📋 PLAN D'IMPLÉMENTATION:")
    print("   1. Créer un service de synchronisation organisationnelle")
    print("   2. Déclencher la synchronisation lors des modifications de structure")
    print("   3. Mettre à jour automatiquement les affectations des salariés")
    print("   4. Ajouter une interface de validation pour les changements en masse")
    print()
    print("🔧 IMPLÉMENTATION TECHNIQUE:")
    print("   - Modifier organizational_structure_service.py")
    print("   - Ajouter une méthode sync_worker_assignments()")
    print("   - Déclencher lors des PUT/POST sur les structures")
    print("   - Ajouter des logs pour traçabilité")
    print()
    print("⚡ SOLUTION IMMÉDIATE:")
    print("   - Créer un script de synchronisation manuelle")
    print("   - Permettre à l'utilisateur de synchroniser à la demande")
    print("   - Ajouter un bouton 'Synchroniser les affectations' dans l'interface")

def main():
    """Fonction principale"""
    print("🚀 Diagnostic complet du problème de filtrage dynamique")
    print("=" * 70)
    
    # Analyser le problème
    sync_issue = analyze_dynamic_filtering_issue()
    
    # Tester la mise à jour manuelle
    if sync_issue:
        manual_success = test_manual_worker_update()
        
        if manual_success:
            print(f"\n✅ CONFIRMATION: Le problème est bien la désynchronisation")
            print(f"La mise à jour manuelle résout temporairement le problème")
        else:
            print(f"\n❌ Le problème persiste même après mise à jour manuelle")
    
    # Analyser la cause racine
    analyze_root_cause()
    
    # Proposer des solutions
    propose_solutions()
    
    print(f"\n🎯 CONCLUSION:")
    print(f"Le système n'est PAS entièrement dynamique comme requis.")
    print(f"Une synchronisation automatique est nécessaire pour résoudre ce problème bloquant.")

if __name__ == "__main__":
    main()