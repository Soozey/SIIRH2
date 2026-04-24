#!/usr/bin/env python3
"""
Test spécifique pour reproduire l'erreur 500 lors de la création d'un travailleur.
"""

import requests
import json

def test_worker_creation():
    """Test la création d'un travailleur avec les données du frontend"""
    
    print("🧪 Test de création d'un travailleur avec données organisationnelles...")
    
    # Données exactes comme envoyées par le frontend
    test_data = {
        'employer_id': 1,
        'matricule': 'TEST002',
        'nom': 'TEST',
        'prenom': 'User',
        'sexe': 'M',
        'type_regime_id': 1,
        'salaire_base': 1000000.0,
        'salaire_horaire': 5000.0,
        'vhm': 200.0,
        'horaire_hebdo': 40.0,
        'nature_contrat': 'CDI',
        'etablissement': '28',  # String comme envoyé par le frontend
        'departement': '30',
        'service': '36',
        'unite': '',
        'avantage_vehicule': 0.0,
        'avantage_logement': 0.0,
        'avantage_telephone': 0.0,
        'avantage_autres': 0.0,
        'solde_conge_initial': 0.0,
        'nombre_enfant': 0,
        'duree_essai_jours': 0,
        'jours_preavis_deja_faits': 0,
        'valeur_point': 0.0
    }
    
    try:
        print("📤 Envoi de la requête POST /workers...")
        response = requests.post('http://localhost:8000/workers', json=test_data, timeout=10)
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 500:
            print("❌ ERREUR 500 REPRODUITE!")
            print("📄 Réponse du serveur:")
            print(response.text)
            return False
            
        elif response.status_code == 422:
            print("⚠️ Erreur de validation (422)")
            try:
                error_details = response.json()
                print("📄 Détails de l'erreur:")
                print(json.dumps(error_details, indent=2))
            except:
                print("📄 Réponse brute:")
                print(response.text)
            return False
            
        elif response.status_code in [200, 201]:
            print("✅ Création réussie!")
            try:
                worker = response.json()
                worker_id = worker.get('id')
                print(f"👤 Worker créé avec ID: {worker_id}")
                
                # Nettoyer le worker de test
                if worker_id:
                    print("🧹 Nettoyage du worker de test...")
                    delete_resp = requests.delete(f'http://localhost:8000/workers/{worker_id}')
                    print(f"🗑️ Suppression: {delete_resp.status_code}")
                    
            except Exception as e:
                print(f"⚠️ Erreur lors du parsing de la réponse: {e}")
            return True
            
        else:
            print(f"⚠️ Status inattendu: {response.status_code}")
            print("📄 Réponse:")
            print(response.text[:500])
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return False

def test_organizational_data_formats():
    """Test différents formats de données organisationnelles"""
    
    print("\n🏢 Test des formats de données organisationnelles...")
    
    test_cases = [
        {
            'name': 'Strings vides',
            'data': {'etablissement': '', 'departement': '', 'service': '', 'unite': ''}
        },
        {
            'name': 'Strings avec IDs',
            'data': {'etablissement': '28', 'departement': '30', 'service': '36', 'unite': ''}
        },
        {
            'name': 'Integers',
            'data': {'etablissement': 28, 'departement': 30, 'service': 36, 'unite': None}
        },
        {
            'name': 'Mixed (problématique potentielle)',
            'data': {'etablissement': '28', 'departement': 30, 'service': '', 'unite': None}
        }
    ]
    
    base_data = {
        'employer_id': 1,
        'matricule': 'TEST_ORG',
        'nom': 'TEST',
        'prenom': 'Org',
        'salaire_base': 1000000.0,
        'salaire_horaire': 5000.0,
        'vhm': 200.0,
        'horaire_hebdo': 40.0,
    }
    
    for i, test_case in enumerate(test_cases):
        print(f"\n{i+1}. Test: {test_case['name']}")
        
        test_data = {**base_data, **test_case['data']}
        test_data['matricule'] = f"TEST_ORG_{i+1}"
        
        try:
            response = requests.post('http://localhost:8000/workers', json=test_data, timeout=5)
            status_icon = "✅" if response.status_code in [200, 201] else "❌" if response.status_code == 500 else "⚠️"
            print(f"   {status_icon} Status: {response.status_code}")
            
            if response.status_code == 500:
                print(f"   💥 ERREUR 500 avec format: {test_case['name']}")
                print(f"   📄 Erreur: {response.text[:200]}")
            elif response.status_code in [200, 201]:
                # Nettoyer
                try:
                    worker_id = response.json().get('id')
                    if worker_id:
                        requests.delete(f'http://localhost:8000/workers/{worker_id}')
                except:
                    pass
                    
        except Exception as e:
            print(f"   ❌ Erreur: {e}")

def main():
    print("🚨 Diagnostic des erreurs 500 - Création de travailleurs")
    print("=" * 60)
    
    # Test de base
    success = test_worker_creation()
    
    if not success:
        print("\n❌ Erreur détectée lors de la création de base")
    
    # Test des formats organisationnels
    test_organizational_data_formats()
    
    print("\n📋 Résumé:")
    print("  - Si une erreur 500 est reproduite, vérifiez les logs du backend")
    print("  - Les erreurs 422 indiquent des problèmes de validation")
    print("  - Les erreurs de format organisationnel peuvent causer des 500")
    
    print("\n💡 Pour plus de détails sur l'erreur 500:")
    print("  1. Vérifiez les logs du backend dans la console où il s'exécute")
    print("  2. Reproduisez l'action dans l'interface utilisateur")
    print("  3. Notez l'URL exacte qui cause l'erreur dans F12 > Network")

if __name__ == "__main__":
    main()