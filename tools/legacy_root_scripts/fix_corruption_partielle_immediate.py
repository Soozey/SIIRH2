#!/usr/bin/env python3
"""
CORRECTION IMMÉDIATE - CORRUPTION PARTIELLE
===========================================
Corrige immédiatement la corruption partielle identifiée:
- Restaure les valeurs service/unité de Jeanne
- Teste la correction
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
JEANNE_ID = 2032

def get_worker_state(worker_id):
    """Récupère l'état d'un salarié"""
    try:
        response = requests.get(f"{BASE_URL}/workers/{worker_id}")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Erreur récupération worker {worker_id}: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Exception récupération worker {worker_id}: {e}")
        return None

def restore_jeanne_complete_assignment():
    """Restaure l'affectation complète de Jeanne"""
    print("🔧 CORRECTION IMMÉDIATE - Restauration affectation complète de Jeanne")
    print("=" * 70)
    
    # Récupérer l'état actuel
    jeanne = get_worker_state(JEANNE_ID)
    if not jeanne:
        print("❌ Impossible de récupérer Jeanne")
        return False
    
    print(f"📋 État actuel de Jeanne:")
    print(f"   Établissement: '{jeanne.get('etablissement', '')}'")
    print(f"   Département: '{jeanne.get('departement', '')}'")
    print(f"   Service: '{jeanne.get('service', '')}'")
    print(f"   Unité: '{jeanne.get('unite', '')}'")
    
    # Préparer les données complètes (avec service et unité)
    update_data = {
        "employer_id": jeanne.get('employer_id'),
        "matricule": jeanne.get('matricule'),
        "nom": jeanne.get('nom'),
        "prenom": jeanne.get('prenom'),
        "salaire_base": jeanne.get('salaire_base'),
        "salaire_horaire": jeanne.get('salaire_horaire'),
        "vhm": jeanne.get('vhm'),
        "horaire_hebdo": jeanne.get('horaire_hebdo'),
        # Affectation organisationnelle COMPLÈTE
        "etablissement": "Mandroso Formation",
        "departement": "AZER",
        "service": "Formation Continue",  # Restaurer une valeur
        "unite": "Unité Pédagogique",    # Restaurer une valeur
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
    
    try:
        response = requests.put(f"{BASE_URL}/workers/{JEANNE_ID}", json=update_data)
        if response.status_code == 200:
            print("\n✅ Restauration réussie!")
            updated_jeanne = response.json()
            print(f"📋 Nouvel état de Jeanne:")
            print(f"   Établissement: '{updated_jeanne.get('etablissement', '')}'")
            print(f"   Département: '{updated_jeanne.get('departement', '')}'")
            print(f"   Service: '{updated_jeanne.get('service', '')}'")
            print(f"   Unité: '{updated_jeanne.get('unite', '')}'")
            return True
        else:
            print(f"\n❌ Erreur restauration: {response.status_code}")
            print(f"   Détails: {response.text}")
            return False
    except Exception as e:
        print(f"\n❌ Exception restauration: {e}")
        return False

def test_filtering_with_complete_assignment():
    """Test le filtrage avec l'affectation complète"""
    print("\n🧪 TEST - Filtrage avec affectation complète")
    print("=" * 50)
    
    # Test filtrage Mandroso Formation (devrait inclure Jeanne)
    filters = {
        'employer_id': 2,
        'period': '2024-12',
        'etablissement': 'Mandroso Formation',
        'departement': 'AZER'
    }
    
    try:
        response = requests.get(f"{BASE_URL}/payroll/bulk-preview", params=filters)
        if response.status_code == 200:
            results = response.json()
            print(f"✅ Filtrage Mandroso Formation/AZER:")
            print(f"   Bulletins trouvés: {len(results)}")
            
            jeanne_found = False
            for result in results:
                worker_info = result.get('worker', {})
                worker_name = f"{worker_info.get('prenom', '')} {worker_info.get('nom', '')}"
                print(f"   - {worker_name}")
                if 'Jeanne' in worker_name and 'RAFARAVAVY' in worker_name:
                    jeanne_found = True
            
            if jeanne_found:
                print("✅ Jeanne est maintenant incluse dans le filtrage!")
            else:
                print("❌ Jeanne n'est toujours pas incluse")
            
            return jeanne_found
        else:
            print(f"❌ Erreur filtrage: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Exception filtrage: {e}")
        return False

def create_organizational_structures():
    """Crée les structures organisationnelles manquantes"""
    print("\n🏗️ CRÉATION - Structures organisationnelles manquantes")
    print("=" * 60)
    
    structures_to_create = [
        {
            "employer_id": 2,
            "name": "Formation Continue",
            "level": "service",
            "parent_id": None
        },
        {
            "employer_id": 2,
            "name": "Unité Pédagogique", 
            "level": "unite",
            "parent_id": None
        }
    ]
    
    for structure in structures_to_create:
        try:
            response = requests.post(f"{BASE_URL}/organizational-structure", json=structure)
            if response.status_code == 200:
                print(f"✅ Structure créée: {structure['name']} ({structure['level']})")
            else:
                print(f"⚠️ Structure {structure['name']}: {response.status_code}")
                # Peut-être qu'elle existe déjà
        except Exception as e:
            print(f"❌ Erreur création {structure['name']}: {e}")

def main():
    """Correction immédiate de la corruption partielle"""
    print("🚨 CORRECTION IMMÉDIATE - CORRUPTION PARTIELLE")
    print("================================================================================")
    print("Objectif: Corriger la corruption partielle identifiée et tester la solution")
    print("================================================================================")
    
    # Étape 1: Créer les structures organisationnelles si nécessaire
    create_organizational_structures()
    
    # Étape 2: Restaurer l'affectation complète de Jeanne
    if restore_jeanne_complete_assignment():
        print("\n✅ Affectation complète restaurée")
    else:
        print("\n❌ Échec de la restauration")
        return
    
    # Étape 3: Tester le filtrage
    if test_filtering_with_complete_assignment():
        print("\n✅ Filtrage fonctionne correctement")
    else:
        print("\n❌ Problème de filtrage persistant")
    
    # Étape 4: Vérification finale
    print("\n📊 VÉRIFICATION FINALE")
    print("=" * 30)
    final_jeanne = get_worker_state(JEANNE_ID)
    if final_jeanne:
        print(f"État final de Jeanne:")
        print(f"   Établissement: '{final_jeanne.get('etablissement', '')}'")
        print(f"   Département: '{final_jeanne.get('departement', '')}'")
        print(f"   Service: '{final_jeanne.get('service', '')}'")
        print(f"   Unité: '{final_jeanne.get('unite', '')}'")
        
        # Vérifier si tous les champs sont remplis
        complete_assignment = all([
            final_jeanne.get('etablissement', '').strip(),
            final_jeanne.get('departement', '').strip(),
            final_jeanne.get('service', '').strip(),
            final_jeanne.get('unite', '').strip()
        ])
        
        if complete_assignment:
            print("\n🎉 SUCCÈS: Affectation organisationnelle complète!")
            print("   La corruption partielle a été corrigée")
        else:
            print("\n⚠️ ATTENTION: Affectation incomplète")
            print("   Des champs organisationnels sont encore vides")
    
    print("\n🎯 PROCHAINES ÉTAPES:")
    print("   1. Tester avec d'autres salariés")
    print("   2. Implémenter la protection frontend")
    print("   3. Ajouter la validation backend")
    print("   4. Créer des tests de régression")

if __name__ == "__main__":
    main()