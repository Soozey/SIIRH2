#!/usr/bin/env python3
"""
RESTAURATION ÉTAT ORIGINAL
==========================
Restaure l'état original des données avant mes modifications de test
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
EMPLOYER_ID = 2  # Mandroso Services

def restore_original_workers():
    """Restaure l'état original des salariés"""
    print("🔄 RESTAURATION - État original des salariés")
    print("=" * 50)
    
    # État original basé sur vos données initiales
    original_workers = {
        2042: {  # Jean RAKOTO
            "etablissement": "Mandroso Achat",
            "departement": "AZER", 
            "service": "",
            "unite": ""
        },
        2007: {  # Souzzy RAKOTOBE
            "etablissement": "Mandroso Achat",
            "departement": "AZER",
            "service": "QSD",
            "unite": ""
        },
        2022: {  # HENINTSOA RAFALIMANANA
            "etablissement": "Mandroso Achat", 
            "departement": "AZER",
            "service": "QSD",
            "unite": ""
        },
        2032: {  # Jeanne RAFARAVAVY
            "etablissement": "Mandroso Formation",
            "departement": "AZER",
            "service": "",
            "unite": ""
        }
    }
    
    for worker_id, org_data in original_workers.items():
        try:
            # Récupérer les données actuelles du salarié
            response = requests.get(f"{BASE_URL}/workers/{worker_id}")
            if response.status_code != 200:
                print(f"❌ Impossible de récupérer le salarié {worker_id}")
                continue
                
            worker = response.json()
            
            # Préparer les données de mise à jour avec l'état original
            update_data = {
                "employer_id": worker.get('employer_id'),
                "matricule": worker.get('matricule'),
                "nom": worker.get('nom'),
                "prenom": worker.get('prenom'),
                "salaire_base": worker.get('salaire_base'),
                "salaire_horaire": worker.get('salaire_horaire'),
                "vhm": worker.get('vhm'),
                "horaire_hebdo": worker.get('horaire_hebdo'),
                # RESTAURER L'ÉTAT ORIGINAL
                "etablissement": org_data["etablissement"],
                "departement": org_data["departement"],
                "service": org_data["service"],
                "unite": org_data["unite"],
                # Autres champs requis
                "sexe": worker.get('sexe', ''),
                "situation_familiale": worker.get('situation_familiale', ''),
                "date_naissance": worker.get('date_naissance'),
                "lieu_naissance": worker.get('lieu_naissance', ''),
                "adresse": worker.get('adresse', ''),
                "telephone": worker.get('telephone', ''),
                "email": worker.get('email', ''),
                "cin": worker.get('cin', ''),
                "cin_delivre_le": worker.get('cin_delivre_le'),
                "cin_lieu": worker.get('cin_lieu', ''),
                "cnaps_num": worker.get('cnaps_num', ''),
                "nombre_enfant": worker.get('nombre_enfant', 0),
                "date_embauche": worker.get('date_embauche'),
                "nature_contrat": worker.get('nature_contrat', 'CDI'),
                "duree_essai_jours": worker.get('duree_essai_jours', 0),
                "date_fin_essai": worker.get('date_fin_essai'),
                "indice": worker.get('indice', ''),
                "valeur_point": worker.get('valeur_point', 0),
                "secteur": worker.get('secteur', ''),
                "mode_paiement": worker.get('mode_paiement', ''),
                "rib": worker.get('rib', ''),
                "code_banque": worker.get('code_banque', ''),
                "code_guichet": worker.get('code_guichet', ''),
                "compte_num": worker.get('compte_num', ''),
                "cle_rib": worker.get('cle_rib', ''),
                "nom_guichet": worker.get('nom_guichet', ''),
                "banque": worker.get('banque', ''),
                "bic": worker.get('bic', ''),
                "categorie_prof": worker.get('categorie_prof', ''),
                "poste": worker.get('poste', ''),
                "date_debauche": worker.get('date_debauche'),
                "type_sortie": worker.get('type_sortie', 'L'),
                "groupe_preavis": worker.get('groupe_preavis', 1),
                "jours_preavis_deja_faits": worker.get('jours_preavis_deja_faits', 0),
                "type_regime_id": worker.get('type_regime_id', 1),
                "avantage_vehicule": worker.get('avantage_vehicule', 0),
                "avantage_logement": worker.get('avantage_logement', 0),
                "avantage_telephone": worker.get('avantage_telephone', 0),
                "avantage_autres": worker.get('avantage_autres', 0),
                "taux_sal_cnaps_override": worker.get('taux_sal_cnaps_override'),
                "taux_sal_smie_override": worker.get('taux_sal_smie_override'),
                "taux_pat_cnaps_override": worker.get('taux_pat_cnaps_override'),
                "taux_pat_smie_override": worker.get('taux_pat_smie_override'),
                "taux_pat_fmfp_override": worker.get('taux_pat_fmfp_override'),
                "solde_conge_initial": worker.get('solde_conge_initial', 0)
            }
            
            # Appliquer la restauration
            response = requests.put(f"{BASE_URL}/workers/{worker_id}", json=update_data)
            if response.status_code == 200:
                print(f"✅ {worker.get('prenom', '')} {worker.get('nom', '')} restauré")
                print(f"   Établissement: '{org_data['etablissement']}'")
                print(f"   Département: '{org_data['departement']}'")
                print(f"   Service: '{org_data['service']}'")
                print(f"   Unité: '{org_data['unite']}'")
            else:
                print(f"❌ Erreur restauration {worker_id}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Exception restauration {worker_id}: {e}")

def verify_current_state():
    """Vérifie l'état actuel après restauration"""
    print("\n📊 VÉRIFICATION - État après restauration")
    print("=" * 45)
    
    try:
        response = requests.get(f"{BASE_URL}/workers")
        if response.status_code == 200:
            workers = response.json()
            mandroso_workers = [w for w in workers if w.get('employer_id') == EMPLOYER_ID]
            
            for worker in mandroso_workers:
                print(f"   ID {worker['id']}: {worker.get('prenom', '')} {worker.get('nom', '')}")
                print(f"     Établissement: '{worker.get('etablissement', '')}'")
                print(f"     Département: '{worker.get('departement', '')}'")
                print(f"     Service: '{worker.get('service', '')}'")
                print(f"     Unité: '{worker.get('unite', '')}'")
                print()
        else:
            print(f"❌ Erreur récupération workers: {response.status_code}")
    except Exception as e:
        print(f"❌ Exception vérification: {e}")

def main():
    """Restauration complète de l'état original"""
    print("🔄 RESTAURATION ÉTAT ORIGINAL")
    print("================================================================================")
    print("Objectif: Restaurer l'état original des données avant les tests de diagnostic")
    print("================================================================================")
    
    restore_original_workers()
    verify_current_state()
    
    print("✅ RESTAURATION TERMINÉE")
    print("\nVos données sont maintenant dans l'état original.")
    print("Nous pouvons maintenant analyser le vrai problème de synchronisation.")

if __name__ == "__main__":
    main()