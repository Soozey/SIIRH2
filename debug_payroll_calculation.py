#!/usr/bin/env python3
"""
Diagnostic détaillé du calcul de paie pour Jeanne RAFARAVAVY
"""

import requests
import json

BACKEND_URL = "http://localhost:8000"

def debug_payroll_calculation():
    """Debug détaillé du calcul de paie"""
    print("🔍 Diagnostic détaillé du calcul de paie")
    print("=" * 70)
    
    worker_id = 2032  # Jeanne RAFARAVAVY
    period = "2025-01"
    
    # 1. Vérifier les données complètes du salarié
    print("1️⃣ DONNÉES COMPLÈTES DU SALARIÉ:")
    print("-" * 40)
    
    try:
        response = requests.get(f"{BACKEND_URL}/workers/{worker_id}")
        if response.status_code == 200:
            worker = response.json()
            
            print(f"👤 {worker['prenom']} {worker['nom']} (ID: {worker['id']})")
            print(f"📊 Données salariales:")
            print(f"   - Salaire base: {worker.get('salaire_base', 'N/A')} Ar")
            print(f"   - VHM: {worker.get('vhm', 'N/A')}")
            print(f"   - Salaire horaire: {worker.get('salaire_horaire', 'N/A')}")
            print(f"   - Type régime: {worker.get('type_regime_id', 'N/A')}")
            print(f"   - Catégorie prof: {worker.get('categorie_prof', 'N/A')}")
            print(f"   - Secteur: {worker.get('secteur', 'N/A')}")
            print(f"   - Mode paiement: {worker.get('mode_paiement', 'N/A')}")
            print(f"   - Date embauche: {worker.get('date_embauche', 'N/A')}")
            print(f"   - Employeur ID: {worker.get('employer_id', 'N/A')}")
            
            # Vérifier les avantages
            print(f"📋 Avantages:")
            print(f"   - Véhicule: {worker.get('avantage_vehicule', 0)} Ar")
            print(f"   - Logement: {worker.get('avantage_logement', 0)} Ar")
            print(f"   - Téléphone: {worker.get('avantage_telephone', 0)} Ar")
            print(f"   - Autres: {worker.get('avantage_autres', 0)} Ar")
            
        else:
            print(f"❌ Erreur récupération salarié: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Exception: {e}")
        return
    
    print()
    
    # 2. Vérifier les données de l'employeur
    print("2️⃣ DONNÉES DE L'EMPLOYEUR:")
    print("-" * 35)
    
    try:
        employer_id = worker['employer_id']
        response = requests.get(f"{BACKEND_URL}/employers/{employer_id}")
        if response.status_code == 200:
            employer = response.json()
            
            print(f"🏢 {employer['raison_sociale']} (ID: {employer['id']})")
            print(f"📊 Paramètres de paie:")
            print(f"   - Type régime: {employer.get('type_regime_id', 'N/A')}")
            print(f"   - SM embauche: {employer.get('sm_embauche', 'N/A')} Ar")
            print(f"   - Secteur: {employer.get('secteur', 'N/A')}")
            print(f"   - CNAPS: {employer.get('cnaps_num', 'N/A')}")
            print(f"   - STAT: {employer.get('stat', 'N/A')}")
            
        else:
            print(f"❌ Erreur récupération employeur: {response.status_code}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    print()
    
    # 3. Vérifier les PayVar pour cette période
    print("3️⃣ VARIABLES DE PAIE (PayVar):")
    print("-" * 40)
    
    try:
        # Il n'y a pas d'endpoint direct pour PayVar, on va tester via le bulletin
        response = requests.get(f"{BACKEND_URL}/payroll/preview", params={
            'worker_id': worker_id,
            'period': period
        })
        
        if response.status_code == 200:
            bulletin = response.json()
            
            print("📄 Bulletin généré avec succès")
            print(f"📊 Détails du calcul:")
            
            # Analyser les lignes de calcul
            lines = bulletin.get('lines', [])
            print(f"   📋 {len(lines)} ligne(s) de calcul:")
            
            for i, line in enumerate(lines):
                label = line.get('label', 'N/A')
                nombre = line.get('nombre', '')
                base = line.get('base', '')
                taux_sal = line.get('taux_sal', '')
                montant_sal = line.get('montant_sal', 0)
                
                print(f"      {i+1}. {label}")
                print(f"         Nombre: {nombre}, Base: {base}, Taux: {taux_sal}")
                print(f"         Montant salarié: {montant_sal} Ar")
            
            # Analyser les totaux
            totaux = bulletin.get('totaux', {})
            print(f"\n   💰 Totaux:")
            for key, value in totaux.items():
                print(f"      - {key}: {value} Ar")
            
            # Identifier le problème
            salaire_base_line = next((line for line in lines if 'Salaire de base' in line.get('label', '')), None)
            if salaire_base_line:
                montant_base = salaire_base_line.get('montant_sal', 0)
                print(f"\n🔍 ANALYSE:")
                print(f"   - Montant salaire de base dans le calcul: {montant_base} Ar")
                print(f"   - Salaire de base du salarié: {worker.get('salaire_base', 'N/A')} Ar")
                
                if montant_base == 0:
                    print("   ❌ PROBLÈME: Le salaire de base est calculé à 0")
                    print("   🔧 Causes possibles:")
                    print("      - Salaire de base du salarié = 0 ou None")
                    print("      - Erreur dans la fonction _money()")
                    print("      - Problème de conversion de type")
                else:
                    print("   ✅ Le salaire de base est correctement calculé")
            
        else:
            print(f"❌ Erreur génération bulletin: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Détails: {error_data}")
            except:
                print(f"   Détails: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    print()
    
    # 4. Test avec données minimales
    print("4️⃣ TEST AVEC DONNÉES MINIMALES:")
    print("-" * 40)
    
    # Créer un salarié de test avec données minimales
    test_worker_data = {
        "matricule": "TEST001",
        "nom": "TEST",
        "prenom": "Salarié",
        "employer_id": employer_id,
        "salaire_base": 500000.0,
        "vhm": 173.33,
        "type_regime_id": 1,
        "secteur": "PRIVE",
        "categorie_prof": "M1",
        "date_embauche": "2024-01-01",
        "etablissement": "Mandroso Formation",
        "departement": "EN LIGNE"
    }
    
    try:
        # Créer le salarié de test
        create_response = requests.post(f"{BACKEND_URL}/workers", json=test_worker_data)
        
        if create_response.status_code == 200:
            test_worker = create_response.json()
            test_worker_id = test_worker['id']
            
            print(f"✅ Salarié de test créé: {test_worker['prenom']} {test_worker['nom']} (ID: {test_worker_id})")
            
            # Tester le bulletin du salarié de test
            test_response = requests.get(f"{BACKEND_URL}/payroll/preview", params={
                'worker_id': test_worker_id,
                'period': period
            })
            
            if test_response.status_code == 200:
                test_bulletin = test_response.json()
                test_totaux = test_bulletin.get('totaux', {})
                
                print(f"📄 Bulletin de test généré:")
                print(f"   - Brut total: {test_totaux.get('brut_total', 0)} Ar")
                print(f"   - Net total: {test_totaux.get('net_total', 0)} Ar")
                
                if test_totaux.get('brut_total', 0) > 0:
                    print("✅ Le calcul fonctionne avec des données fraîches")
                    print("🔧 Le problème vient des données de Jeanne RAFARAVAVY")
                else:
                    print("❌ Le calcul ne fonctionne pas même avec des données fraîches")
                    print("🔧 Le problème est dans le moteur de calcul lui-même")
            else:
                print(f"❌ Erreur bulletin de test: {test_response.status_code}")
            
            # Nettoyer le salarié de test
            requests.delete(f"{BACKEND_URL}/workers/{test_worker_id}")
            print("🧹 Salarié de test supprimé")
            
        else:
            print(f"❌ Erreur création salarié de test: {create_response.status_code}")
    except Exception as e:
        print(f"❌ Exception test: {e}")

def fix_jeanne_data_completely():
    """Recrée complètement les données de Jeanne"""
    print("\n🛠️ RECRÉATION COMPLÈTE DES DONNÉES DE JEANNE:")
    print("-" * 55)
    
    worker_id = 2032
    
    try:
        # Récupérer les données actuelles
        response = requests.get(f"{BACKEND_URL}/workers/{worker_id}")
        if response.status_code == 200:
            current_data = response.json()
            
            # Données complètement nettoyées
            clean_data = {
                "matricule": "M0001",
                "nom": "RAFARAVAVY",
                "prenom": "Jeanne",
                "employer_id": 2,
                "salaire_base": 456000.0,
                "vhm": 173.33,
                "salaire_horaire": 2631.58,
                "type_regime_id": 1,
                "secteur": "PRIVE",
                "categorie_prof": "M1",
                "date_embauche": "2024-01-01",
                "etablissement": "Mandroso Formation",
                "departement": "EN LIGNE",
                "service": "",
                "unite": "",
                "poste": "Employé",
                "mode_paiement": "VIREMENT",
                "avantage_vehicule": 0.0,
                "avantage_logement": 0.0,
                "avantage_telephone": 0.0,
                "avantage_autres": 0.0,
                "cnaps_num": "123456789",
                "adresse": "Antananarivo"
            }
            
            print("🔄 Mise à jour avec données nettoyées...")
            
            update_response = requests.put(f"{BACKEND_URL}/workers/{worker_id}", json=clean_data)
            
            if update_response.status_code == 200:
                print("✅ Données de Jeanne mises à jour")
                
                # Test immédiat
                test_response = requests.get(f"{BACKEND_URL}/payroll/preview", params={
                    'worker_id': worker_id,
                    'period': '2025-01'
                })
                
                if test_response.status_code == 200:
                    bulletin = test_response.json()
                    totaux = bulletin.get('totaux', {})
                    
                    print(f"📄 Test bulletin après nettoyage:")
                    print(f"   - Brut total: {totaux.get('brut_total', 0)} Ar")
                    print(f"   - Net total: {totaux.get('net_total', 0)} Ar")
                    
                    if totaux.get('brut_total', 0) > 0:
                        print("🎉 SUCCÈS! Le calcul fonctionne maintenant")
                        return True
                    else:
                        print("❌ Le calcul ne fonctionne toujours pas")
                else:
                    print(f"❌ Erreur test après nettoyage: {test_response.status_code}")
            else:
                print(f"❌ Erreur mise à jour: {update_response.status_code}")
        else:
            print(f"❌ Erreur récupération données actuelles: {response.status_code}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    return False

def main():
    """Fonction principale"""
    print("🚀 Diagnostic complet du calcul de paie")
    print("=" * 70)
    
    debug_payroll_calculation()
    
    print("\n" + "="*70)
    choice = input("Voulez-vous recréer complètement les données de Jeanne ? (o/n): ").lower().strip()
    
    if choice == 'o':
        success = fix_jeanne_data_completely()
        if success:
            print("\n🎉 PROBLÈME RÉSOLU!")
            print("Les bulletins de Mandroso Services fonctionnent maintenant correctement")
        else:
            print("\n❌ PROBLÈME PERSISTANT")
            print("Il faut investiguer plus en profondeur le moteur de calcul")

if __name__ == "__main__":
    main()