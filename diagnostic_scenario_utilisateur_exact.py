#!/usr/bin/env python3
"""
DIAGNOSTIC SCÉNARIO UTILISATEUR EXACT
=====================================
Reproduit exactement le scénario décrit par l'utilisateur:
1. Affecter Jeanne sur Mandroso Formation/AZER
2. Synchroniser et corriger
3. Valider les affectations
4. Appliquer filtres organisationnels (Mandroso Achat/AZER)
5. Cliquer "Traiter avec filtres"
6. Vérifier si Jeanne perd ses affectations
"""

import requests
import json
from datetime import datetime
import time

# Configuration
BASE_URL = "http://localhost:8000"
EMPLOYER_ID = 2  # Mandroso Services
JEANNE_ID = 2032  # Jeanne RAFARAVAVY

def log_step(step, description):
    """Log une étape avec timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"\n[{timestamp}] 👤 SCÉNARIO {step}: {description}")
    print("=" * 80)

def get_worker_state(worker_id):
    """Récupère l'état complet d'un salarié"""
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

def display_worker_state(worker, title):
    """Affiche l'état d'un salarié"""
    if not worker:
        print(f"📋 {title}: SALARIÉ NON TROUVÉ")
        return
    
    print(f"\n📋 {title}")
    print("-" * 60)
    print(f"   Nom: {worker.get('prenom', '')} {worker.get('nom', '')}")
    print(f"   Établissement: '{worker.get('etablissement', '')}'")
    print(f"   Département: '{worker.get('departement', '')}'")
    print(f"   Service: '{worker.get('service', '')}'")
    print(f"   Unité: '{worker.get('unite', '')}'")

def compare_worker_states(before, after, step_name):
    """Compare l'état d'un salarié avant/après"""
    print(f"\n🔍 COMPARAISON APRÈS {step_name}")
    print("-" * 60)
    
    if not before or not after:
        print("❌ Impossible de comparer - données manquantes")
        return True
    
    changes_detected = False
    fields = ['etablissement', 'departement', 'service', 'unite']
    
    for field in fields:
        before_val = before.get(field, '')
        after_val = after.get(field, '')
        
        if before_val != after_val:
            print(f"🚨 CHANGEMENT DÉTECTÉ - {field}:")
            print(f"   AVANT: '{before_val}'")
            print(f"   APRÈS: '{after_val}'")
            changes_detected = True
    
    if not changes_detected:
        print("✅ Aucun changement détecté")
    
    return changes_detected

def step1_affecter_jeanne():
    """Étape 1: Affecter Jeanne sur Mandroso Formation/AZER"""
    log_step("1", "AFFECTATION - Jeanne sur Mandroso Formation/AZER")
    
    # Récupérer d'abord les données actuelles de Jeanne
    jeanne = get_worker_state(JEANNE_ID)
    if not jeanne:
        print("❌ Impossible de récupérer Jeanne")
        return False
    
    # Préparer les données de mise à jour (comme le ferait le frontend)
    update_data = {
        "employer_id": jeanne.get('employer_id'),
        "matricule": jeanne.get('matricule'),
        "nom": jeanne.get('nom'),
        "prenom": jeanne.get('prenom'),
        "salaire_base": jeanne.get('salaire_base'),
        "salaire_horaire": jeanne.get('salaire_horaire'),
        "vhm": jeanne.get('vhm'),
        "horaire_hebdo": jeanne.get('horaire_hebdo'),
        # Affectation organisationnelle
        "etablissement": "Mandroso Formation",
        "departement": "AZER",
        "service": "",
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
    
    try:
        response = requests.put(f"{BASE_URL}/workers/{JEANNE_ID}", json=update_data)
        if response.status_code == 200:
            print("✅ Affectation réussie")
            updated_jeanne = response.json()
            print(f"   Établissement: '{updated_jeanne.get('etablissement', '')}'")
            print(f"   Département: '{updated_jeanne.get('departement', '')}'")
            return True
        else:
            print(f"❌ Erreur affectation: {response.status_code}")
            print(f"   Détails: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception affectation: {e}")
        return False

def step2_synchronisation():
    """Étape 2: Synchronisation et correction"""
    log_step("2", "SYNCHRONISATION - Validation et correction")
    
    # Validation
    try:
        response = requests.post(f"{BASE_URL}/organizational-structure/{EMPLOYER_ID}/sync-workers")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Validation synchronisation:")
            print(f"   Succès: {result.get('success')}")
            print(f"   Invalides détectées: {result.get('total_invalid_detected', 0)}")
        else:
            print(f"❌ Erreur validation: {response.status_code}")
    except Exception as e:
        print(f"❌ Exception validation: {e}")
    
    # Correction (force sync)
    try:
        response = requests.post(f"{BASE_URL}/organizational-structure/{EMPLOYER_ID}/force-sync-workers")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Correction synchronisation:")
            print(f"   Succès: {result.get('success')}")
            print(f"   Mises à jour: {result.get('total_updated', 0)}")
            return True
        else:
            print(f"❌ Erreur correction: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Exception correction: {e}")
        return False

def step3_validation_affectations():
    """Étape 3: Validation des affectations"""
    log_step("3", "VALIDATION - Vérification des affectations")
    
    jeanne = get_worker_state(JEANNE_ID)
    if jeanne:
        print(f"✅ État de Jeanne après synchronisation:")
        print(f"   Établissement: '{jeanne.get('etablissement', '')}'")
        print(f"   Département: '{jeanne.get('departement', '')}'")
        print(f"   Service: '{jeanne.get('service', '')}'")
        print(f"   Unité: '{jeanne.get('unite', '')}'")
        return True
    else:
        print("❌ Impossible de valider les affectations")
        return False

def step4_filtrage_organisationnel():
    """Étape 4: Application des filtres organisationnels"""
    log_step("4", "FILTRAGE - Application filtres Mandroso Achat/AZER")
    
    # Simuler exactement les appels du frontend OrganizationalFilterModal
    
    # 1. Chargement des employeurs (comme dans le modal)
    try:
        response = requests.get(f"{BASE_URL}/employers")
        print(f"   Chargement employeurs: {response.status_code}")
    except Exception as e:
        print(f"   Chargement employeurs: ERREUR - {e}")
    
    # 2. Chargement données organisationnelles hiérarchiques
    try:
        response = requests.get(f"{BASE_URL}/employers/{EMPLOYER_ID}/organizational-data/hierarchical")
        print(f"   Chargement org hiérarchiques: {response.status_code}")
    except Exception as e:
        print(f"   Chargement org hiérarchiques: ERREUR - {e}")
    
    # 3. Chargement données organisationnelles workers (fallback)
    try:
        response = requests.get(f"{BASE_URL}/employers/{EMPLOYER_ID}/organizational-data/workers")
        print(f"   Chargement org workers: {response.status_code}")
    except Exception as e:
        print(f"   Chargement org workers: ERREUR - {e}")
    
    # 4. Filtrage en cascade (comme dans le modal)
    try:
        response = requests.get(f"{BASE_URL}/employers/{EMPLOYER_ID}/organizational-data/hierarchical-filtered", params={
            'etablissement': 'Mandroso Achat'
        })
        print(f"   Filtrage cascade établissement: {response.status_code}")
    except Exception as e:
        print(f"   Filtrage cascade établissement: ERREUR - {e}")
    
    try:
        response = requests.get(f"{BASE_URL}/employers/{EMPLOYER_ID}/organizational-data/hierarchical-filtered", params={
            'etablissement': 'Mandroso Achat',
            'departement': 'AZER'
        })
        print(f"   Filtrage cascade complet: {response.status_code}")
        return True
    except Exception as e:
        print(f"   Filtrage cascade complet: ERREUR - {e}")
        return False

def step5_traiter_avec_filtres():
    """Étape 5: Cliquer "Traiter avec filtres" (bulk preview)"""
    log_step("5", "TRAITEMENT - Clic 'Traiter avec filtres'")
    
    # Simuler exactement l'appel fait par le frontend lors du clic "Traiter avec filtres"
    filters = {
        'employer_id': EMPLOYER_ID,
        'period': '2024-12',
        'etablissement': 'Mandroso Achat',
        'departement': 'AZER'
    }
    
    try:
        response = requests.get(f"{BASE_URL}/payroll/bulk-preview", params=filters)
        if response.status_code == 200:
            results = response.json()
            print(f"✅ Traitement avec filtres réussi:")
            print(f"   Filtres appliqués: Mandroso Achat / AZER")
            print(f"   Bulletins trouvés: {len(results)}")
            
            # Afficher les salariés trouvés
            for result in results:
                worker_info = result.get('worker', {})
                print(f"   - {worker_info.get('prenom', '')} {worker_info.get('nom', '')}")
            
            # Vérifier si Jeanne est exclue (comme décrit par l'utilisateur)
            jeanne_found = any(
                result.get('worker', {}).get('prenom') == 'Jeanne' and 
                result.get('worker', {}).get('nom') == 'RAFARAVAVY'
                for result in results
            )
            
            if not jeanne_found:
                print("🚨 PROBLÈME CONFIRMÉ: Jeanne est exclue du filtrage!")
                print("   Ceci correspond exactement au problème décrit par l'utilisateur")
            else:
                print("✅ Jeanne est incluse dans les résultats")
            
            return True
        else:
            print(f"❌ Erreur traitement: {response.status_code}")
            print(f"   Réponse: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception traitement: {e}")
        return False

def step6_verification_finale():
    """Étape 6: Retour page Travailleur - Vérification corruption"""
    log_step("6", "VÉRIFICATION FINALE - Retour page Travailleur")
    
    # Vérifier l'état de Jeanne après tout le processus
    jeanne = get_worker_state(JEANNE_ID)
    if jeanne:
        print(f"📊 État final de Jeanne:")
        print(f"   Établissement: '{jeanne.get('etablissement', '')}'")
        print(f"   Département: '{jeanne.get('departement', '')}'")
        print(f"   Service: '{jeanne.get('service', '')}'")
        print(f"   Unité: '{jeanne.get('unite', '')}'")
        
        # Vérifier si les champs sont vides (corruption)
        empty_fields = []
        for field in ['etablissement', 'departement', 'service', 'unite']:
            if not jeanne.get(field, '').strip():
                empty_fields.append(field)
        
        if empty_fields:
            print(f"🚨 CORRUPTION CONFIRMÉE: Champs vidés: {empty_fields}")
            return True
        else:
            print(f"✅ Affectations préservées")
            return False
    else:
        print(f"❌ Impossible de vérifier - salarié non trouvé")
        return True

def main():
    """Scénario principal reproduisant exactement le workflow utilisateur"""
    print("🚨 DIAGNOSTIC SCÉNARIO UTILISATEUR EXACT")
    print("================================================================================")
    print("Reproduction exacte du workflow décrit par l'utilisateur")
    print("================================================================================")
    
    # État initial
    log_step("INIT", "CAPTURE ÉTAT INITIAL")
    initial_jeanne = get_worker_state(JEANNE_ID)
    display_worker_state(initial_jeanne, "ÉTAT INITIAL - Jeanne RAFARAVAVY")
    
    # Workflow étape par étape
    success = True
    
    # Étape 1: Affectation
    if step1_affecter_jeanne():
        after_affectation = get_worker_state(JEANNE_ID)
        compare_worker_states(initial_jeanne, after_affectation, "AFFECTATION")
    else:
        success = False
    
    # Étape 2: Synchronisation
    if success and step2_synchronisation():
        after_sync = get_worker_state(JEANNE_ID)
        compare_worker_states(after_affectation, after_sync, "SYNCHRONISATION")
    else:
        success = False
    
    # Étape 3: Validation
    if success and step3_validation_affectations():
        after_validation = get_worker_state(JEANNE_ID)
        compare_worker_states(after_sync, after_validation, "VALIDATION")
    else:
        success = False
    
    # Étape 4: Filtrage
    if success and step4_filtrage_organisationnel():
        after_filtrage = get_worker_state(JEANNE_ID)
        compare_worker_states(after_validation, after_filtrage, "FILTRAGE ORGANISATIONNEL")
    else:
        success = False
    
    # Étape 5: Traitement avec filtres
    if success and step5_traiter_avec_filtres():
        after_traitement = get_worker_state(JEANNE_ID)
        compare_worker_states(after_filtrage, after_traitement, "TRAITEMENT AVEC FILTRES")
    else:
        success = False
    
    # Étape 6: Vérification finale
    corruption_detected = step6_verification_finale()
    
    # Résumé final
    log_step("RÉSUMÉ", "ANALYSE FINALE DU SCÉNARIO")
    
    if corruption_detected:
        print("🚨 CORRUPTION CONFIRMÉE!")
        print("   Le scénario utilisateur reproduit bien la corruption des données")
        print("   Les affectations organisationnelles sont perdues après le workflow")
    else:
        print("✅ Aucune corruption détectée")
        print("   Le workflow ne corrompt pas les données dans ce test")
    
    # État final
    final_jeanne = get_worker_state(JEANNE_ID)
    display_worker_state(final_jeanne, "ÉTAT FINAL - Jeanne RAFARAVAVY")
    
    print("\n🎯 CONCLUSIONS:")
    if corruption_detected:
        print("   1. La corruption se produit bien lors du workflow utilisateur")
        print("   2. Identifier l'étape exacte qui cause la perte des données")
        print("   3. Implémenter des protections pour préserver les affectations")
    else:
        print("   1. Les APIs backend préservent correctement les données")
        print("   2. La corruption pourrait venir d'interactions frontend spécifiques")
        print("   3. Tester avec des données réelles et des interactions utilisateur")

if __name__ == "__main__":
    main()