#!/usr/bin/env python3
"""
Correction définitive de l'affectation de Jeanne et identification des processus destructifs
"""

import requests
import json
import time

def correction_definitive_jeanne():
    print('🔧 CORRECTION DÉFINITIVE - Jeanne RAFARAVAVY')
    print('=' * 60)

    # 1. État initial de Jeanne
    print('1️⃣ ÉTAT INITIAL de Jeanne:')
    response = requests.get('http://localhost:8000/workers/2032')
    if response.status_code == 200:
        jeanne_initial = response.json()
        print(f'   Établissement: "{jeanne_initial.get("etablissement", "VIDE")}"')
        print(f'   Département: "{jeanne_initial.get("departement", "VIDE")}"')
    else:
        print(f'   ❌ Erreur: {response.status_code}')
        return

    print()

    # 2. Correction vers "Mandroso Achat"
    print('2️⃣ CORRECTION vers "Mandroso Achat":')
    
    # Préparer les données complètes avec correction
    update_data = {
        "employer_id": jeanne_initial["employer_id"],
        "matricule": jeanne_initial["matricule"],
        "nom": jeanne_initial["nom"],
        "prenom": jeanne_initial["prenom"],
        "salaire_base": jeanne_initial["salaire_base"],
        "salaire_horaire": jeanne_initial["salaire_horaire"],
        "vhm": jeanne_initial["vhm"],
        "horaire_hebdo": jeanne_initial["horaire_hebdo"],
        
        # CORRECTION DÉFINITIVE
        "etablissement": "Mandroso Achat",  # CORRECTION
        "departement": "AZER",              # MAINTENU
        "service": jeanne_initial.get("service", ""),
        "unite": jeanne_initial.get("unite", ""),
        
        # Tous les autres champs obligatoires
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
        print('   ✅ Correction appliquée avec succès')
    else:
        print(f'   ❌ Erreur correction: {response.status_code}')
        print(f'   Détails: {response.text}')
        return

    # Vérification immédiate
    response = requests.get('http://localhost:8000/workers/2032')
    if response.status_code == 200:
        jeanne_corrigee = response.json()
        print(f'   Vérification: "{jeanne_corrigee.get("etablissement", "VIDE")}" / "{jeanne_corrigee.get("departement", "VIDE")}"')
    
    print()

    # 3. Test du filtrage avec la correction
    print('3️⃣ TEST FILTRAGE avec correction:')
    params = {
        'employer_id': 2,
        'period': '2025-01',
        'etablissement': 'Mandroso Achat',
        'departement': 'AZER'
    }
    
    response = requests.get('http://localhost:8000/payroll/bulk-preview', params=params)
    if response.status_code == 200:
        bulletins = response.json()
        print(f'   Résultat: {len(bulletins)} bulletin(s)')
        
        jeanne_trouvee = False
        for bulletin in bulletins:
            print(f'     - {bulletin["worker"]["prenom"]} {bulletin["worker"]["nom"]}')
            if bulletin["worker"]["prenom"] == "Jeanne":
                jeanne_trouvee = True
        
        if jeanne_trouvee:
            print('   ✅ Jeanne trouvée dans les résultats!')
        else:
            print('   ❌ Jeanne MANQUANTE dans les résultats!')
    else:
        print(f'   ❌ Erreur filtrage: {response.status_code}')

    print()

    # 4. Surveillance des processus destructifs
    print('4️⃣ SURVEILLANCE - Identification des processus destructifs')
    print('   Surveillance pendant 10 secondes...')
    
    for i in range(5):  # 5 vérifications sur 10 secondes
        time.sleep(2)
        print(f'   Vérification {i+1}/5:')
        
        response = requests.get('http://localhost:8000/workers/2032')
        if response.status_code == 200:
            jeanne_check = response.json()
            etab_check = jeanne_check.get("etablissement", "VIDE")
            
            print(f'     Établissement: "{etab_check}"')
            
            if etab_check != "Mandroso Achat":
                print(f'     🚨 PROCESSUS DESTRUCTIF DÉTECTÉ!')
                print(f'     Changement: "Mandroso Achat" → "{etab_check}"')
                print(f'     Moment: {i*2 + 2} secondes après correction')
                break
        else:
            print(f'     ❌ Erreur vérification: {response.status_code}')
    else:
        print('   ✅ Aucun processus destructif détecté pendant la surveillance')

    print()

    # 5. Test de déclenchement de synchronisation
    print('5️⃣ TEST DÉCLENCHEMENT SYNCHRONISATION - Identifier le coupable')
    
    # État avant synchronisation
    response = requests.get('http://localhost:8000/workers/2032')
    if response.status_code == 200:
        jeanne_avant_sync = response.json()
        etab_avant = jeanne_avant_sync.get("etablissement", "VIDE")
        print(f'   Avant synchronisation: "{etab_avant}"')
    
    # Déclencher la synchronisation
    print('   Déclenchement synchronisation...')
    response = requests.post('http://localhost:8000/organizational-structure/2/sync-workers')
    if response.status_code == 200:
        result = response.json()
        print(f'   Synchronisation: {result["total_updated"]} modification(s)')
    else:
        print(f'   ❌ Erreur sync: {response.status_code}')
    
    # État après synchronisation
    response = requests.get('http://localhost:8000/workers/2032')
    if response.status_code == 200:
        jeanne_apres_sync = response.json()
        etab_apres = jeanne_apres_sync.get("etablissement", "VIDE")
        print(f'   Après synchronisation: "{etab_apres}"')
        
        if etab_avant != etab_apres:
            print(f'   🚨 COUPABLE IDENTIFIÉ: La synchronisation modifie les données!')
            print(f'   Changement: "{etab_avant}" → "{etab_apres}"')
        else:
            print('   ✅ Synchronisation sécurisée - Données préservées')

    print()

    # 6. Test final du workflow utilisateur
    print('6️⃣ TEST FINAL - Workflow utilisateur complet')
    
    # S'assurer que Jeanne est sur "Mandroso Achat"
    if etab_apres != "Mandroso Achat":
        print('   Correction finale de Jeanne...')
        response = requests.put('http://localhost:8000/workers/2032', json=update_data)
        if response.status_code == 200:
            print('   ✅ Jeanne remise sur "Mandroso Achat"')
    
    # Test final du filtrage
    params = {
        'employer_id': 2,
        'period': '2025-01',
        'etablissement': 'Mandroso Achat',
        'departement': 'AZER'
    }
    
    response = requests.get('http://localhost:8000/payroll/bulk-preview', params=params)
    if response.status_code == 200:
        bulletins = response.json()
        print(f'   Test final: {len(bulletins)} bulletin(s) avec "Mandroso Achat" + "AZER"')
        
        jeanne_dans_resultats = any(
            b["worker"]["prenom"] == "Jeanne" 
            for b in bulletins
        )
        
        if jeanne_dans_resultats:
            print('   ✅ PROBLÈME RÉSOLU: Jeanne apparaît dans les résultats!')
        else:
            print('   ❌ PROBLÈME PERSISTE: Jeanne manquante dans les résultats')
    else:
        print(f'   ❌ Erreur test final: {response.status_code}')

    print()
    print('🎯 DIAGNOSTIC TERMINÉ')

if __name__ == "__main__":
    correction_definitive_jeanne()