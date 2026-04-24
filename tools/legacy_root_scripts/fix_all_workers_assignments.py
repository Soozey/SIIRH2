#!/usr/bin/env python3
"""
Correction définitive des affectations de tous les salariés
"""

import requests
import json

def fix_all_workers_assignments():
    print('🔧 CORRECTION DÉFINITIVE des affectations')
    print('=' * 50)

    # 1. Récupérer tous les salariés
    print('1️⃣ Récupération de tous les salariés:')
    response = requests.get('http://localhost:8000/workers?employer_id=2')
    if response.status_code != 200:
        print(f'   ❌ Erreur: {response.status_code}')
        return
    
    workers = response.json()
    print(f'   {len(workers)} salariés trouvés')

    # 2. Corriger chaque salarié individuellement
    print('2️⃣ Correction de chaque salarié:')
    
    for worker in workers:
        worker_id = worker['id']
        worker_name = f"{worker['prenom']} {worker['nom']}"
        
        print(f'   Correction de {worker_name} (ID: {worker_id}):')
        
        # Récupérer les données complètes
        response = requests.get(f'http://localhost:8000/workers/{worker_id}')
        if response.status_code != 200:
            print(f'     ❌ Erreur récupération: {response.status_code}')
            continue
        
        worker_data = response.json()
        
        # Préparer les données avec la correction
        update_data = {
            "employer_id": worker_data["employer_id"],
            "matricule": worker_data["matricule"],
            "nom": worker_data["nom"],
            "prenom": worker_data["prenom"],
            "salaire_base": worker_data["salaire_base"],
            "salaire_horaire": worker_data["salaire_horaire"],
            "vhm": worker_data["vhm"],
            "horaire_hebdo": worker_data["horaire_hebdo"],
            
            # CORRECTION: Mettre tout le monde sur "Mandroso Achat"
            "etablissement": "Mandroso Achat",
            "departement": "AZER",
            "service": worker_data.get("service", ""),
            "unite": worker_data.get("unite", ""),
            
            # Autres champs obligatoires
            "sexe": worker_data.get("sexe", ""),
            "situation_familiale": worker_data.get("situation_familiale", ""),
            "adresse": worker_data.get("adresse", ""),
            "telephone": worker_data.get("telephone", ""),
            "email": worker_data.get("email", ""),
            "cin": worker_data.get("cin", ""),
            "cnaps_num": worker_data.get("cnaps_num", ""),
            "nombre_enfant": worker_data.get("nombre_enfant", 0),
            "date_embauche": worker_data.get("date_embauche", "2025-01-01"),
            "type_regime_id": worker_data.get("type_regime_id", 1),
            "nature_contrat": worker_data.get("nature_contrat", "CDI"),
            "duree_essai_jours": worker_data.get("duree_essai_jours", 0),
            "indice": worker_data.get("indice", ""),
            "valeur_point": worker_data.get("valeur_point", 0.0),
            "secteur": worker_data.get("secteur", "PRIVE"),
            "mode_paiement": worker_data.get("mode_paiement", "Chèque"),
            "rib": worker_data.get("rib", ""),
            "code_banque": worker_data.get("code_banque", ""),
            "code_guichet": worker_data.get("code_guichet", ""),
            "compte_num": worker_data.get("compte_num", ""),
            "cle_rib": worker_data.get("cle_rib", ""),
            "banque": worker_data.get("banque", ""),
            "nom_guichet": worker_data.get("nom_guichet", ""),
            "bic": worker_data.get("bic", ""),
            "categorie_prof": worker_data.get("categorie_prof", "M1"),
            "poste": worker_data.get("poste", ""),
            "solde_conge_initial": worker_data.get("solde_conge_initial", 0.0),
            "type_sortie": worker_data.get("type_sortie", "L"),
            "groupe_preavis": worker_data.get("groupe_preavis", 1),
            "jours_preavis_deja_faits": worker_data.get("jours_preavis_deja_faits", 0),
            "avantage_vehicule": worker_data.get("avantage_vehicule", 0.0),
            "avantage_logement": worker_data.get("avantage_logement", 0.0),
            "avantage_telephone": worker_data.get("avantage_telephone", 0.0),
            "avantage_autres": worker_data.get("avantage_autres", 0.0)
        }
        
        # Appliquer la correction
        response = requests.put(f'http://localhost:8000/workers/{worker_id}', json=update_data)
        if response.status_code == 200:
            print(f'     ✅ Corrigé: "Mandroso Formation" → "Mandroso Achat"')
        else:
            print(f'     ❌ Erreur correction: {response.status_code}')

    print()

    # 3. Vérification des corrections
    print('3️⃣ Vérification des corrections:')
    response = requests.get('http://localhost:8000/workers?employer_id=2')
    if response.status_code == 200:
        workers_updated = response.json()
        for worker in workers_updated:
            print(f'   {worker["prenom"]} {worker["nom"]}: {worker.get("etablissement", "N/A")}')
    
    print()

    # 4. Test du filtrage après correction
    print('4️⃣ Test du filtrage après correction:')
    params = {
        'employer_id': 2,
        'period': '2025-01',
        'etablissement': 'Mandroso Achat',
        'departement': 'AZER'
    }
    response = requests.get('http://localhost:8000/payroll/bulk-preview', params=params)
    if response.status_code == 200:
        bulletins = response.json()
        print(f'   ✅ {len(bulletins)} bulletin(s) avec "Mandroso Achat" + "AZER"')
        for bulletin in bulletins:
            print(f'     - {bulletin["worker"]["prenom"]} {bulletin["worker"]["nom"]}')
    else:
        print(f'   ❌ Erreur: {response.status_code}')

    print()
    print('🎉 CORRECTION TERMINÉE!')

if __name__ == "__main__":
    fix_all_workers_assignments()