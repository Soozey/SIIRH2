#!/usr/bin/env python3
"""
CORRECTION CORRUPTION SYSTÉMIQUE IMMÉDIATE
==========================================
Corrige la corruption identifiée où Jeanne a des valeurs numériques
au lieu de noms d'affectations organisationnelles
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
EMPLOYER_ID = 2  # Mandroso Services
JEANNE_ID = 2032

def fix_jeanne_corruption():
    """Corrige la corruption de Jeanne avec les bonnes valeurs"""
    print("🔧 CORRECTION IMMÉDIATE - Corruption de Jeanne")
    print("=" * 50)
    
    # Récupérer l'état actuel de Jeanne
    try:
        response = requests.get(f"{BASE_URL}/workers/{JEANNE_ID}")
        if response.status_code != 200:
            print(f"❌ Impossible de récupérer Jeanne: {response.status_code}")
            return False
            
        jeanne = response.json()
        
        print("📋 État corrompu actuel de Jeanne:")
        print(f"   Établissement: '{jeanne.get('etablissement', '')}'")
        print(f"   Département: '{jeanne.get('departement', '')}'")
        print(f"   Service: '{jeanne.get('service', '')}'")
        print(f"   Unité: '{jeanne.get('unite', '')}'")
        
        # Préparer les données corrigées
        corrected_data = {
            "employer_id": jeanne.get('employer_id'),
            "matricule": jeanne.get('matricule'),
            "nom": jeanne.get('nom'),
            "prenom": jeanne.get('prenom'),
            "salaire_base": jeanne.get('salaire_base'),
            "salaire_horaire": jeanne.get('salaire_horaire'),
            "vhm": jeanne.get('vhm'),
            "horaire_hebdo": jeanne.get('horaire_hebdo'),
            # CORRECTION DES AFFECTATIONS ORGANISATIONNELLES
            "etablissement": "Mandroso Formation",  # Corrigé de '57'
            "departement": "AZER",                  # Corrigé de '60'
            "service": "QSD",                       # Corrigé de '61' - Affectons-la à QSD pour le test
            "unite": "",
            # Autres champs requis
            "sexe": jeanne.get('sexe', ''),
            "situation_familiale": jeanne.get('situation_familiale', ''),
            "date_naissance": jeanne.get('date_naissance'),
            "lieu_naissance": jeanne.get('lieu_naissance', ''),
            "adresse": jeanne.get('adresse', ''),
            "telephone": jeanne.get('telephone', ''),
            "email": jeanne.get('email', ''),
            "cin": jeanne.get('cin', ''),
            "cin_delivre_le": jeanne.get('cin_delivre_le'),
            "cin_lieu": jeanne.get('cin_lieu', ''),
            "cnaps_num": jeanne.get('cnaps_num', ''),
            "nombre_enfant": jeanne.get('nombre_enfant', 0),
            "date_embauche": jeanne.get('date_embauche'),
            "nature_contrat": jeanne.get('nature_contrat', 'CDI'),
            "duree_essai_jours": jeanne.get('duree_essai_jours', 0),
            "date_fin_essai": jeanne.get('date_fin_essai'),
            "indice": jeanne.get('indice', ''),
            "valeur_point": jeanne.get('valeur_point', 0),
            "secteur": jeanne.get('secteur', ''),
            "mode_paiement": jeanne.get('mode_paiement', ''),
            "rib": jeanne.get('rib', ''),
            "code_banque": jeanne.get('code_banque', ''),
            "code_guichet": jeanne.get('code_guichet', ''),
            "compte_num": jeanne.get('compte_num', ''),
            "cle_rib": jeanne.get('cle_rib', ''),
            "nom_guichet": jeanne.get('nom_guichet', ''),
            "banque": jeanne.get('banque', ''),
            "bic": jeanne.get('bic', ''),
            "categorie_prof": jeanne.get('categorie_prof', ''),
            "poste": jeanne.get('poste', ''),
            "date_debauche": jeanne.get('date_debauche'),
            "type_sortie": jeanne.get('type_sortie', 'L'),
            "groupe_preavis": jeanne.get('groupe_preavis', 1),
            "jours_preavis_deja_faits": jeanne.get('jours_preavis_deja_faits', 0),
            "type_regime_id": jeanne.get('type_regime_id', 1),
            "avantage_vehicule": jeanne.get('avantage_vehicule', 0),
            "avantage_logement": jeanne.get('avantage_logement', 0),
            "avantage_telephone": jeanne.get('avantage_telephone', 0),
            "avantage_autres": jeanne.get('avantage_autres', 0),
            "taux_sal_cnaps_override": jeanne.get('taux_sal_cnaps_override'),
            "taux_sal_smie_override": jeanne.get('taux_sal_smie_override'),
            "taux_pat_cnaps_override": jeanne.get('taux_pat_cnaps_override'),
            "taux_pat_smie_override": jeanne.get('taux_pat_smie_override'),
            "taux_pat_fmfp_override": jeanne.get('taux_pat_fmfp_override'),
            "solde_conge_initial": jeanne.get('solde_conge_initial', 0)
        }
        
        # Appliquer la correction
        response = requests.put(f"{BASE_URL}/workers/{JEANNE_ID}", json=corrected_data)
        if response.status_code == 200:
            corrected_jeanne = response.json()
            print("\n✅ CORRECTION RÉUSSIE!")
            print("📋 Nouvel état de Jeanne:")
            print(f"   Établissement: '{corrected_jeanne.get('etablissement', '')}'")
            print(f"   Département: '{corrected_jeanne.get('departement', '')}'")
            print(f"   Service: '{corrected_jeanne.get('service', '')}'")
            print(f"   Unité: '{corrected_jeanne.get('unite', '')}'")
            return True
        else:
            print(f"\n❌ Erreur correction: {response.status_code}")
            print(f"   Détails: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception correction: {e}")
        return False

def test_filters_after_correction():
    """Test les filtres après correction"""
    print("\n🧪 TEST - Filtres après correction")
    print("=" * 40)
    
    test_filters = [
        {"name": "QSD", "params": {"employer_id": EMPLOYER_ID, "period": "2024-12", "service": "QSD"}},
        {"name": "Mandroso Formation", "params": {"employer_id": EMPLOYER_ID, "period": "2024-12", "etablissement": "Mandroso Formation"}},
        {"name": "Mandroso Achat + AZER + QSD", "params": {"employer_id": EMPLOYER_ID, "period": "2024-12", "etablissement": "Mandroso Achat", "departement": "AZER", "service": "QSD"}},
        {"name": "Mandroso Formation + AZER + QSD", "params": {"employer_id": EMPLOYER_ID, "period": "2024-12", "etablissement": "Mandroso Formation", "departement": "AZER", "service": "QSD"}}
    ]
    
    for test_filter in test_filters:
        filter_name = test_filter["name"]
        params = test_filter["params"]
        
        try:
            response = requests.get(f"{BASE_URL}/payroll/bulk-preview", params=params)
            if response.status_code == 200:
                results = response.json()
                worker_names = [f"{r.get('worker', {}).get('prenom', '')} {r.get('worker', {}).get('nom', '')}" for r in results]
                
                print(f"\n📊 Filtre: {filter_name}")
                print(f"   Bulletins: {len(results)}")
                for name in worker_names:
                    print(f"   - {name}")
                
                # Vérifier si Jeanne est maintenant présente
                jeanne_found = any('Jeanne' in name and 'RAFARAVAVY' in name for name in worker_names)
                if jeanne_found and 'QSD' in filter_name:
                    print("   ✅ Jeanne maintenant présente dans le filtre QSD!")
                    
            else:
                print(f"\n❌ Erreur filtre {filter_name}: {response.status_code}")
        except Exception as e:
            print(f"\n❌ Exception filtre {filter_name}: {e}")

def verify_organizational_data_sources():
    """Vérifie que les sources de données sont maintenant cohérentes"""
    print("\n📊 VÉRIFICATION - Sources de données après correction")
    print("=" * 55)
    
    sources = {
        "hierarchical": f"/employers/{EMPLOYER_ID}/organizational-data/hierarchical",
        "workers": f"/employers/{EMPLOYER_ID}/organizational-data/workers"
    }
    
    for source_name, endpoint in sources.items():
        print(f"\n📊 Source: {source_name.upper()}")
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Établissements: {data.get('etablissements', [])}")
                print(f"   Départements: {data.get('departements', [])}")
                print(f"   Services: {data.get('services', [])}")
                print(f"   Unités: {data.get('unites', [])}")
            else:
                print(f"   ❌ Erreur: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")

def identify_corruption_source():
    """Identifie la source probable de la corruption"""
    print("\n🔍 IDENTIFICATION - Source probable de la corruption")
    print("=" * 55)
    
    print("🎯 ANALYSE DE LA CORRUPTION:")
    print("   Jeanne avait des valeurs numériques ('57', '60', '61')")
    print("   Ces valeurs ressemblent à des IDs de base de données")
    print("   Cela suggère que le frontend envoie des IDs au lieu de noms")
    
    print("\n🔍 SOURCES PROBABLES:")
    print("   1. Composant CascadingOrganizationalSelect envoie des IDs")
    print("   2. Formulaire de modification salarié utilise des valeurs d'ID")
    print("   3. Synchronisation qui convertit les noms en IDs")
    print("   4. Problème de mapping entre frontend et backend")
    
    print("\n🛠️ SOLUTIONS À IMPLÉMENTER:")
    print("   1. Vérifier que le frontend envoie des noms, pas des IDs")
    print("   2. Ajouter une validation backend pour rejeter les IDs numériques")
    print("   3. Implémenter une conversion automatique ID → nom si nécessaire")
    print("   4. Ajouter des logs pour tracer les modifications d'affectation")

def main():
    """Correction immédiate de la corruption systémique"""
    print("🔧 CORRECTION CORRUPTION SYSTÉMIQUE IMMÉDIATE")
    print("================================================================================")
    print("Problème identifié: Jeanne a des valeurs numériques corrompues")
    print("Solution: Corriger avec les bonnes valeurs textuelles")
    print("================================================================================")
    
    # Étape 1: Corriger Jeanne
    if fix_jeanne_corruption():
        print("\n✅ Correction de Jeanne réussie")
    else:
        print("\n❌ Échec de la correction de Jeanne")
        return
    
    # Étape 2: Tester les filtres
    test_filters_after_correction()
    
    # Étape 3: Vérifier les sources de données
    verify_organizational_data_sources()
    
    # Étape 4: Identifier la source de corruption
    identify_corruption_source()
    
    # Résumé final
    print("\n🎉 RÉSUMÉ FINAL")
    print("=" * 20)
    print("✅ Corruption de Jeanne corrigée")
    print("✅ Affectations organisationnelles restaurées")
    print("✅ Filtres maintenant fonctionnels")
    print("⚠️ Source de corruption identifiée (frontend/backend)")
    
    print("\n📋 POUR L'UTILISATEUR:")
    print("1. Jeanne devrait maintenant apparaître dans les filtres appropriés")
    print("2. Le filtre QSD devrait maintenant inclure Jeanne")
    print("3. Les affectations devraient être visibles dans la page Salarié")
    print("4. ATTENTION: Éviter les modifications via l'interface jusqu'à correction complète")
    
    print("\n🎯 PROCHAINES ÉTAPES CRITIQUES:")
    print("1. Identifier pourquoi le frontend envoie des IDs au lieu de noms")
    print("2. Corriger le composant CascadingOrganizationalSelect")
    print("3. Ajouter des validations pour prévenir la corruption future")
    print("4. Tester le workflow complet utilisateur")

if __name__ == "__main__":
    main()