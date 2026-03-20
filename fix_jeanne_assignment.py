#!/usr/bin/env python3
"""
Correction de l'affectation de Jeanne selon le scénario utilisateur
"""

import requests
import json

def fix_jeanne_assignment():
    print('🔧 Correction de l\'affectation de Jeanne')
    print('=' * 45)

    # 1. Récupérer les données complètes de Jeanne
    print('1️⃣ Récupération des données de Jeanne:')
    response = requests.get('http://localhost:8000/workers/2032')
    if response.status_code == 200:
        jeanne = response.json()
        print(f'   Établissement actuel: {jeanne.get("etablissement", "N/A")}')
        print(f'   Département actuel: {jeanne.get("departement", "N/A")}')
    else:
        print(f'   ❌ Erreur: {response.status_code}')
        return

    print()

    # 2. Corriger l'affectation selon la Photo 1
    print('2️⃣ Correction vers "Mandroso Achat" + "AZER":')
    
    # Préparer les données complètes avec la correction
    update_data = {
        "employer_id": jeanne["employer_id"],
        "matricule": jeanne["matricule"],
        "nom": jeanne["nom"],
        "prenom": jeanne["prenom"],
        "salaire_base": jeanne["salaire_base"],
        "salaire_horaire": jeanne["salaire_horaire"],
        "vhm": jeanne["vhm"],
        "horaire_hebdo": jeanne["horaire_hebdo"],
        # Correction des affectations
        "etablissement": "Mandroso Achat",  # Comme dans la Photo 1
        "departement": "AZER",              # Comme dans la Photo 1
        "service": jeanne.get("service", ""),
        "unite": jeanne.get("unite", ""),
        # Autres champs obligatoires
        "sexe": jeanne.get("sexe", ""),
        "situation_familiale": jeanne.get("situation_familiale", ""),
        "adresse": jeanne.get("adresse", ""),
        "telephone": jeanne.get("telephone", ""),
        "email": jeanne.get("email", ""),
        "cin": jeanne.get("cin", ""),
        "cnaps_num": jeanne.get("cnaps_num", ""),
        "nombre_enfant": jeanne.get("nombre_enfant", 0),
        "date_embauche": jeanne.get("date_embauche", "2025-01-01"),
        "type_regime_id": jeanne.get("type_regime_id", 1),
        "nature_contrat": jeanne.get("nature_contrat", "CDI"),
        "duree_essai_jours": jeanne.get("duree_essai_jours", 0),
        "indice": jeanne.get("indice", ""),
        "valeur_point": jeanne.get("valeur_point", 0.0),
        "secteur": jeanne.get("secteur", "PRIVE"),
        "mode_paiement": jeanne.get("mode_paiement", "Chèque"),
        "rib": jeanne.get("rib", ""),
        "code_banque": jeanne.get("code_banque", ""),
        "code_guichet": jeanne.get("code_guichet", ""),
        "compte_num": jeanne.get("compte_num", ""),
        "cle_rib": jeanne.get("cle_rib", ""),
        "banque": jeanne.get("banque", ""),
        "nom_guichet": jeanne.get("nom_guichet", ""),
        "bic": jeanne.get("bic", ""),
        "categorie_prof": jeanne.get("categorie_prof", "M1"),
        "poste": jeanne.get("poste", "Femme de ménage"),
        "solde_conge_initial": jeanne.get("solde_conge_initial", 0.0),
        "type_sortie": jeanne.get("type_sortie", "L"),
        "groupe_preavis": jeanne.get("groupe_preavis", 1),
        "jours_preavis_deja_faits": jeanne.get("jours_preavis_deja_faits", 0),
        "avantage_vehicule": jeanne.get("avantage_vehicule", 0.0),
        "avantage_logement": jeanne.get("avantage_logement", 0.0),
        "avantage_telephone": jeanne.get("avantage_telephone", 0.0),
        "avantage_autres": jeanne.get("avantage_autres", 0.0)
    }
    
    response = requests.put(f'http://localhost:8000/workers/2032', json=update_data)
    if response.status_code == 200:
        print('   ✅ Affectation corrigée avec succès!')
    else:
        print(f'   ❌ Erreur: {response.status_code}')
        print(f'   Détails: {response.text}')

    print()

    # 3. Vérification de la correction
    print('3️⃣ Vérification de la correction:')
    response = requests.get('http://localhost:8000/workers/2032')
    if response.status_code == 200:
        jeanne_updated = response.json()
        print(f'   Établissement: {jeanne_updated.get("etablissement", "N/A")}')
        print(f'   Département: {jeanne_updated.get("departement", "N/A")}')
    else:
        print(f'   ❌ Erreur: {response.status_code}')

    print()

    # 4. Test du filtrage avec les valeurs corrigées
    print('4️⃣ Test du filtrage avec "Mandroso Achat" + "AZER":')
    params = {
        'employer_id': 2,
        'period': '2025-01',
        'etablissement': 'Mandroso Achat',
        'departement': 'AZER'
    }
    response = requests.get('http://localhost:8000/payroll/bulk-preview', params=params)
    if response.status_code == 200:
        bulletins = response.json()
        print(f'   ✅ {len(bulletins)} bulletin(s) trouvé(s)')
        if bulletins:
            for bulletin in bulletins:
                print(f'   - {bulletin["worker"]["prenom"]} {bulletin["worker"]["nom"]}')
        else:
            print('   ⚠️ Aucun bulletin - vérifiez les données de paie')
    else:
        print(f'   ❌ Erreur: {response.status_code}')

    print()
    print('🎉 Correction terminée!')

if __name__ == "__main__":
    fix_jeanne_assignment()