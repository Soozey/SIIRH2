#!/usr/bin/env python3
"""
Diagnostic critique de la persistance des données organisationnelles
Analyse des défauts de synchronisation entre les couches du système
"""

import requests
import json
import time

def diagnostic_persistance_critique():
    print('🚨 DIAGNOSTIC CRITIQUE - Persistance des données organisationnelles')
    print('=' * 80)

    # 1. Test de persistance après modification
    print('1️⃣ TEST DE PERSISTANCE - Modification et vérification immédiate')
    print('-' * 60)
    
    # Récupérer l'état initial de Jeanne
    response = requests.get('http://localhost:8000/workers/2032')
    if response.status_code == 200:
        jeanne_initial = response.json()
        print(f'   État initial Jeanne:')
        print(f'     Établissement: "{jeanne_initial.get("etablissement", "VIDE")}"')
        print(f'     Département: "{jeanne_initial.get("departement", "VIDE")}"')
    else:
        print(f'   ❌ Erreur récupération initiale: {response.status_code}')
        return

    # Modifier l'affectation vers "TEST_ETABLISSEMENT"
    print('\n   Modification vers "TEST_ETABLISSEMENT":')
    update_data = {
        "employer_id": jeanne_initial["employer_id"],
        "matricule": jeanne_initial["matricule"],
        "nom": jeanne_initial["nom"],
        "prenom": jeanne_initial["prenom"],
        "salaire_base": jeanne_initial["salaire_base"],
        "salaire_horaire": jeanne_initial["salaire_horaire"],
        "vhm": jeanne_initial["vhm"],
        "horaire_hebdo": jeanne_initial["horaire_hebdo"],
        "etablissement": "TEST_ETABLISSEMENT",  # MODIFICATION TEST
        "departement": "TEST_DEPARTEMENT",      # MODIFICATION TEST
        "service": jeanne_initial.get("service", ""),
        "unite": jeanne_initial.get("unite", ""),
        "sexe": jeanne_initial.get("sexe", ""),
        "situation_familiale": jeanne_initial.get("situation_familiale", ""),
        "adresse": jeanne_initial.get("adresse", ""),
        "telephone": jeanne_initial.get("telephone", ""),
        "email": jeanne_initial.get("email", ""),
        "cin": jeanne_initial.get("cin", ""),
        "cnaps_num": jeanne_initial.get("cnaps_num", ""),
        "nombre_enfant": jeanne_initial.get("nombre_enfant", 0),
        "date_embauche": jeanne_initial.get("date_embauche", "2025-01-01"),
        "type_regime_id": jeanne_initial.get("type_regime_id", 1),
        "nature_contrat": jeanne_initial.get("nature_contrat", "CDI"),
        "duree_essai_jours": jeanne_initial.get("duree_essai_jours", 0),
        "indice": jeanne_initial.get("indice", ""),
        "valeur_point": jeanne_initial.get("valeur_point", 0.0),
        "secteur": jeanne_initial.get("secteur", "PRIVE"),
        "mode_paiement": jeanne_initial.get("mode_paiement", "Chèque"),
        "rib": jeanne_initial.get("rib", ""),
        "code_banque": jeanne_initial.get("code_banque", ""),
        "code_guichet": jeanne_initial.get("code_guichet", ""),
        "compte_num": jeanne_initial.get("compte_num", ""),
        "cle_rib": jeanne_initial.get("cle_rib", ""),
        "banque": jeanne_initial.get("banque", ""),
        "nom_guichet": jeanne_initial.get("nom_guichet", ""),
        "bic": jeanne_initial.get("bic", ""),
        "categorie_prof": jeanne_initial.get("categorie_prof", "M1"),
        "poste": jeanne_initial.get("poste", ""),
        "solde_conge_initial": jeanne_initial.get("solde_conge_initial", 0.0),
        "type_sortie": jeanne_initial.get("type_sortie", "L"),
        "groupe_preavis": jeanne_initial.get("groupe_preavis", 1),
        "jours_preavis_deja_faits": jeanne_initial.get("jours_preavis_deja_faits", 0),
        "avantage_vehicule": jeanne_initial.get("avantage_vehicule", 0.0),
        "avantage_logement": jeanne_initial.get("avantage_logement", 0.0),
        "avantage_telephone": jeanne_initial.get("avantage_telephone", 0.0),
        "avantage_autres": jeanne_initial.get("avantage_autres", 0.0)
    }
    
    response = requests.put('http://localhost:8000/workers/2032', json=update_data)
    if response.status_code == 200:
        print('     ✅ Modification envoyée avec succès')
    else:
        print(f'     ❌ Erreur modification: {response.status_code}')
        print(f'     Détails: {response.text}')

    # Vérification immédiate
    print('\n   Vérification immédiate après modification:')
    response = requests.get('http://localhost:8000/workers/2032')
    if response.status_code == 200:
        jeanne_apres = response.json()
        etablissement_apres = jeanne_apres.get("etablissement", "VIDE")
        departement_apres = jeanne_apres.get("departement", "VIDE")
        
        print(f'     Établissement: "{etablissement_apres}"')
        print(f'     Département: "{departement_apres}"')
        
        if etablissement_apres == "TEST_ETABLISSEMENT" and departement_apres == "TEST_DEPARTEMENT":
            print('     ✅ PERSISTANCE OK - Modification immédiatement visible')
        else:
            print('     ❌ DÉFAUT PERSISTANCE - Modification non sauvegardée')
    else:
        print(f'     ❌ Erreur vérification: {response.status_code}')

    print('\n' + '=' * 80)

    # 2. Test de persistance après délai
    print('2️⃣ TEST DE PERSISTANCE - Vérification après délai (simulation cache)')
    print('-' * 60)
    
    print('   Attente de 2 secondes (simulation accès différé)...')
    time.sleep(2)
    
    response = requests.get('http://localhost:8000/workers/2032')
    if response.status_code == 200:
        jeanne_delai = response.json()
        etablissement_delai = jeanne_delai.get("etablissement", "VIDE")
        departement_delai = jeanne_delai.get("departement", "VIDE")
        
        print(f'   Établissement après délai: "{etablissement_delai}"')
        print(f'   Département après délai: "{departement_delai}"')
        
        if etablissement_delai == "TEST_ETABLISSEMENT" and departement_delai == "TEST_DEPARTEMENT":
            print('   ✅ PERSISTANCE STABLE - Données conservées après délai')
        else:
            print('   ❌ DÉFAUT CACHE - Données modifiées ou perdues après délai')
    else:
        print(f'   ❌ Erreur vérification délai: {response.status_code}')

    print('\n' + '=' * 80)

    # 3. Test de cohérence entre endpoints
    print('3️⃣ TEST DE COHÉRENCE - Comparaison entre différents endpoints')
    print('-' * 60)
    
    # Endpoint individuel
    response1 = requests.get('http://localhost:8000/workers/2032')
    # Endpoint liste
    response2 = requests.get('http://localhost:8000/workers?employer_id=2')
    
    if response1.status_code == 200 and response2.status_code == 200:
        jeanne_individuel = response1.json()
        workers_liste = response2.json()
        jeanne_liste = None
        
        for worker in workers_liste:
            if worker['id'] == 2032:
                jeanne_liste = worker
                break
        
        if jeanne_liste:
            etab_individuel = jeanne_individuel.get("etablissement", "VIDE")
            etab_liste = jeanne_liste.get("etablissement", "VIDE")
            dept_individuel = jeanne_individuel.get("departement", "VIDE")
            dept_liste = jeanne_liste.get("departement", "VIDE")
            
            print(f'   Endpoint individuel - Établissement: "{etab_individuel}"')
            print(f'   Endpoint liste - Établissement: "{etab_liste}"')
            print(f'   Endpoint individuel - Département: "{dept_individuel}"')
            print(f'   Endpoint liste - Département: "{dept_liste}"')
            
            if etab_individuel == etab_liste and dept_individuel == dept_liste:
                print('   ✅ COHÉRENCE OK - Données identiques entre endpoints')
            else:
                print('   ❌ INCOHÉRENCE CRITIQUE - Données différentes entre endpoints')
        else:
            print('   ❌ Jeanne non trouvée dans la liste')
    else:
        print(f'   ❌ Erreur endpoints: {response1.status_code}, {response2.status_code}')

    print('\n' + '=' * 80)

    # 4. Test de synchronisation avec le moteur de paie
    print('4️⃣ TEST MOTEUR DE PAIE - Cohérence avec le filtrage')
    print('-' * 60)
    
    # Test avec les nouvelles valeurs
    params = {
        'employer_id': 2,
        'period': '2025-01',
        'etablissement': 'TEST_ETABLISSEMENT',
        'departement': 'TEST_DEPARTEMENT'
    }
    
    print(f'   Test filtrage avec: {params}')
    response = requests.get('http://localhost:8000/payroll/bulk-preview', params=params)
    if response.status_code == 200:
        bulletins = response.json()
        print(f'   Résultat: {len(bulletins)} bulletin(s)')
        
        if len(bulletins) > 0:
            for bulletin in bulletins:
                print(f'     - {bulletin["worker"]["prenom"]} {bulletin["worker"]["nom"]}')
            print('   ✅ MOTEUR SYNCHRONISÉ - Filtrage fonctionne avec nouvelles données')
        else:
            print('   ❌ MOTEUR DÉSYNCHRONISÉ - Filtrage ne trouve pas les nouvelles données')
    else:
        print(f'   ❌ Erreur moteur paie: {response.status_code}')

    print('\n' + '=' * 80)

    # 5. Restauration de l'état initial
    print('5️⃣ RESTAURATION - Remise en état initial')
    print('-' * 60)
    
    restore_data = update_data.copy()
    restore_data["etablissement"] = jeanne_initial.get("etablissement", "Mandroso Achat")
    restore_data["departement"] = jeanne_initial.get("departement", "AZER")
    
    response = requests.put('http://localhost:8000/workers/2032', json=restore_data)
    if response.status_code == 200:
        print('   ✅ État initial restauré')
    else:
        print(f'   ❌ Erreur restauration: {response.status_code}')

    print('\n' + '=' * 80)
    print('🎯 DIAGNOSTIC TERMINÉ - Analysez les résultats pour identifier les défauts')

if __name__ == "__main__":
    diagnostic_persistance_critique()