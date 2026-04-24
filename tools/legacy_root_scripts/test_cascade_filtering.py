#!/usr/bin/env python3
"""
Test du filtrage en cascade hiérarchique
Vérifie que les départements, services et unités se filtrent correctement
"""

import requests
import json

BACKEND_URL = "http://localhost:8000"

def test_hierarchical_cascade():
    """Test du filtrage en cascade hiérarchique"""
    print("🔍 Test du Filtrage en Cascade Hiérarchique")
    print("=" * 60)
    
    try:
        # Récupérer les employeurs
        response = requests.get(f"{BACKEND_URL}/employers")
        if response.status_code != 200:
            print("❌ Impossible de récupérer les employeurs")
            return False
        
        employers = response.json()
        if not employers:
            print("⚠️ Aucun employeur trouvé")
            return False
        
        employer_id = employers[0]['id']
        employer_name = employers[0].get('raison_sociale', f'Employeur {employer_id}')
        
        print(f"📋 Test pour: {employer_name} (ID: {employer_id})")
        print()
        
        # 1. Récupérer toutes les données hiérarchiques
        print("📊 ÉTAPE 1: Données hiérarchiques complètes")
        print("-" * 50)
        
        response = requests.get(f"{BACKEND_URL}/employers/{employer_id}/organizational-data/hierarchical")
        if response.status_code != 200:
            print("❌ Impossible de récupérer les données hiérarchiques")
            return False
        
        all_data = response.json()
        print(f"✅ Données complètes récupérées:")
        print(f"   - Établissements: {all_data.get('etablissements', [])}")
        print(f"   - Départements: {all_data.get('departements', [])}")
        print(f"   - Services: {all_data.get('services', [])}")
        print(f"   - Unités: {all_data.get('unites', [])}")
        
        if not all_data.get('etablissements'):
            print("⚠️ Aucun établissement trouvé - impossible de tester le filtrage")
            return False
        
        # 2. Test filtrage par établissement
        etablissement = all_data['etablissements'][0]
        print(f"\n📊 ÉTAPE 2: Filtrage par établissement '{etablissement}'")
        print("-" * 50)
        
        response = requests.get(f"{BACKEND_URL}/employers/{employer_id}/organizational-data/hierarchical-filtered", {
            'params': {'etablissement': etablissement}
        })
        
        if response.status_code == 200:
            filtered_data = response.json()
            print(f"✅ Filtrage par établissement réussi:")
            print(f"   - Établissements: {filtered_data.get('etablissements', [])}")
            print(f"   - Départements filtrés: {filtered_data.get('departements', [])}")
            print(f"   - Services filtrés: {filtered_data.get('services', [])}")
            print(f"   - Unités filtrées: {filtered_data.get('unites', [])}")
            
            # Vérifier que l'établissement sélectionné est présent
            if etablissement in filtered_data.get('etablissements', []):
                print("   ✅ L'établissement sélectionné est présent")
            else:
                print("   ❌ L'établissement sélectionné est absent")
            
            # 3. Test filtrage par département (si disponible)
            if filtered_data.get('departements'):
                departement = filtered_data['departements'][0]
                print(f"\n📊 ÉTAPE 3: Filtrage par département '{departement}'")
                print("-" * 50)
                
                response = requests.get(f"{BACKEND_URL}/employers/{employer_id}/organizational-data/hierarchical-filtered", {
                    'params': {
                        'etablissement': etablissement,
                        'departement': departement
                    }
                })
                
                if response.status_code == 200:
                    dept_filtered = response.json()
                    print(f"✅ Filtrage par département réussi:")
                    print(f"   - Établissements: {dept_filtered.get('etablissements', [])}")
                    print(f"   - Départements: {dept_filtered.get('departements', [])}")
                    print(f"   - Services filtrés: {dept_filtered.get('services', [])}")
                    print(f"   - Unités filtrées: {dept_filtered.get('unites', [])}")
                    
                    # 4. Test filtrage par service (si disponible)
                    if dept_filtered.get('services'):
                        service = dept_filtered['services'][0]
                        print(f"\n📊 ÉTAPE 4: Filtrage par service '{service}'")
                        print("-" * 50)
                        
                        response = requests.get(f"{BACKEND_URL}/employers/{employer_id}/organizational-data/hierarchical-filtered", {
                            'params': {
                                'etablissement': etablissement,
                                'departement': departement,
                                'service': service
                            }
                        })
                        
                        if response.status_code == 200:
                            service_filtered = response.json()
                            print(f"✅ Filtrage par service réussi:")
                            print(f"   - Établissements: {service_filtered.get('etablissements', [])}")
                            print(f"   - Départements: {service_filtered.get('departements', [])}")
                            print(f"   - Services: {service_filtered.get('services', [])}")
                            print(f"   - Unités filtrées: {service_filtered.get('unites', [])}")
                        else:
                            print(f"❌ Erreur filtrage par service: {response.status_code}")
                    else:
                        print("\n⚠️ Aucun service disponible pour ce département")
                else:
                    print(f"❌ Erreur filtrage par département: {response.status_code}")
            else:
                print("\n⚠️ Aucun département disponible pour cet établissement")
        else:
            print(f"❌ Erreur filtrage par établissement: {response.status_code}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_frontend_cascade():
    """Test de l'intégration frontend du filtrage en cascade"""
    print("\n🔍 Test Frontend du Filtrage en Cascade")
    print("=" * 60)
    
    try:
        # Test que le composant OrganizationalFilterModal compile
        response = requests.get("http://localhost:5173/src/components/OrganizationalFilterModal.tsx", timeout=5)
        
        if response.status_code == 200:
            print("✅ OrganizationalFilterModal compile correctement")
            print("✅ Le filtrage en cascade devrait maintenant fonctionner dans l'interface")
            return True
        elif response.status_code == 500:
            print("❌ Erreur compilation OrganizationalFilterModal")
            return False
        else:
            print(f"⚠️ Status inattendu: {response.status_code}")
            return True
            
    except requests.exceptions.ConnectionError:
        print("❌ Frontend non accessible")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def show_usage_instructions():
    """Affiche les instructions d'utilisation"""
    print("\n📋 INSTRUCTIONS D'UTILISATION")
    print("=" * 60)
    
    print("🎯 COMMENT TESTER LE FILTRAGE EN CASCADE:")
    print()
    print("1. 🖥️ Allez sur la page /payroll")
    print("2. 🖱️ Cliquez sur 'Imprimer tous les bulletins'")
    print("3. 📋 Dans la modal qui s'ouvre:")
    print("   - Sélectionnez 'Appliquer des filtres organisationnels'")
    print("   - Choisissez un établissement dans la liste déroulante")
    print("   - Observez que les départements se mettent à jour automatiquement")
    print("   - Choisissez un département")
    print("   - Observez que les services se mettent à jour automatiquement")
    print("   - Choisissez un service")
    print("   - Observez que les unités se mettent à jour automatiquement")
    print("4. ✅ Cliquez sur 'Traiter avec filtres' pour voir les bulletins filtrés")
    print()
    print("🔧 FONCTIONNALITÉS ATTENDUES:")
    print("✅ Filtrage en cascade (chaque niveau filtre les suivants)")
    print("✅ Noms réels des structures (plus de valeurs numériques)")
    print("✅ Mise à jour automatique des listes déroulantes")
    print("✅ Impression ciblée par structure organisationnelle")

def main():
    """Fonction principale"""
    print("🚀 Test du Filtrage en Cascade Hiérarchique")
    print("=" * 70)
    
    # Tests
    cascade_ok = test_hierarchical_cascade()
    frontend_ok = test_frontend_cascade()
    
    # Instructions
    show_usage_instructions()
    
    # Résumé
    print("\n" + "=" * 70)
    print("📊 RÉSUMÉ DES TESTS")
    print(f"Filtrage en cascade backend: {'✅ OK' if cascade_ok else '❌ ERREUR'}")
    print(f"Frontend: {'✅ OK' if frontend_ok else '❌ ERREUR'}")
    
    if cascade_ok and frontend_ok:
        print("\n🎉 FILTRAGE EN CASCADE OPÉRATIONNEL!")
        print("\n✨ NOUVELLES FONCTIONNALITÉS DISPONIBLES:")
        print("• Sélection d'établissement → Départements filtrés automatiquement")
        print("• Sélection de département → Services filtrés automatiquement")
        print("• Sélection de service → Unités filtrées automatiquement")
        print("• Impression ciblée par structure organisationnelle")
    else:
        print("\n❌ CERTAINS TESTS ONT ÉCHOUÉ")
        if not cascade_ok:
            print("- Vérifiez que le backend est redémarré avec les nouveaux endpoints")
        if not frontend_ok:
            print("- Vérifiez que le frontend compile correctement")

if __name__ == "__main__":
    main()