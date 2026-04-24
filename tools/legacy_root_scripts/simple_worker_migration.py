#!/usr/bin/env python3
"""
Migration simplifiée des assignations organisationnelles des salariés
Met à jour seulement les champs organisationnels
"""

import requests
import json

BACKEND_URL = "http://localhost:8000"

def get_id_to_name_mapping():
    """Récupère le mapping ID → Nom des structures"""
    try:
        employer_id = 1
        response = requests.get(f"{BACKEND_URL}/organizational-structure/{employer_id}/tree")
        
        if response.status_code != 200:
            return None
        
        tree_data = response.json()
        id_to_name = {}
        
        def extract_mapping(nodes):
            for node in nodes:
                id_to_name[str(node['id'])] = node['name']
                if node.get('children'):
                    extract_mapping(node['children'])
        
        if tree_data.get('tree'):
            extract_mapping(tree_data['tree'])
        
        return id_to_name
    except:
        return None

def migrate_worker_simple(worker_id, new_assignments):
    """Met à jour un salarié avec les nouvelles assignations"""
    try:
        # 1. Récupérer les données actuelles du salarié
        response = requests.get(f"{BACKEND_URL}/workers/{worker_id}")
        if response.status_code != 200:
            return False, f"Impossible de récupérer le salarié {worker_id}"
        
        worker_data = response.json()
        
        # 2. Préparer les données complètes avec les nouvelles assignations
        update_data = {
            'employer_id': worker_data.get('employer_id'),
            'matricule': worker_data.get('matricule', ''),
            'nom': worker_data.get('nom', ''),
            'prenom': worker_data.get('prenom', ''),
            'sexe': worker_data.get('sexe'),
            'situation_familiale': worker_data.get('situation_familiale'),
            'date_naissance': worker_data.get('date_naissance'),
            'adresse': worker_data.get('adresse', ''),
            'telephone': worker_data.get('telephone'),
            'email': worker_data.get('email'),
            'cin': worker_data.get('cin'),
            'cin_delivre_le': worker_data.get('cin_delivre_le'),
            'cin_lieu': worker_data.get('cin_lieu'),
            'cnaps_num': worker_data.get('cnaps_num'),
            'nombre_enfant': worker_data.get('nombre_enfant', 0),
            'date_embauche': worker_data.get('date_embauche'),
            'type_regime_id': worker_data.get('type_regime_id', 1),
            'salaire_base': worker_data.get('salaire_base', 0.0),
            'salaire_horaire': worker_data.get('salaire_horaire', 0.0),
            'vhm': worker_data.get('vhm', 173.33),
            'horaire_hebdo': worker_data.get('horaire_hebdo', 40.0),
            'nature_contrat': worker_data.get('nature_contrat', 'CDI'),
            'duree_essai_jours': worker_data.get('duree_essai_jours', 0),
            'date_fin_essai': worker_data.get('date_fin_essai'),
            'etablissement': new_assignments.get('etablissement', worker_data.get('etablissement', '')),
            'departement': new_assignments.get('departement', worker_data.get('departement', '')),
            'service': new_assignments.get('service', worker_data.get('service', '')),
            'unite': new_assignments.get('unite', worker_data.get('unite', '')),
            'indice': worker_data.get('indice'),
            'valeur_point': worker_data.get('valeur_point', 0.0),
            'secteur': worker_data.get('secteur'),
            'mode_paiement': worker_data.get('mode_paiement', 'Virement'),
            'rib': worker_data.get('rib'),
            'code_banque': worker_data.get('code_banque'),
            'code_guichet': worker_data.get('code_guichet'),
            'compte_num': worker_data.get('compte_num'),
            'cle_rib': worker_data.get('cle_rib'),
            'banque': worker_data.get('banque'),
            'nom_guichet': worker_data.get('nom_guichet'),
            'bic': worker_data.get('bic'),
            'categorie_prof': worker_data.get('categorie_prof'),
            'poste': worker_data.get('poste'),
            'solde_conge_initial': worker_data.get('solde_conge_initial', 0.0),
            'date_debauche': worker_data.get('date_debauche'),
            'type_sortie': worker_data.get('type_sortie'),
            'groupe_preavis': worker_data.get('groupe_preavis'),
            'jours_preavis_deja_faits': worker_data.get('jours_preavis_deja_faits', 0),
            'avantage_vehicule': worker_data.get('avantage_vehicule', 0.0),
            'avantage_logement': worker_data.get('avantage_logement', 0.0),
            'avantage_telephone': worker_data.get('avantage_telephone', 0.0),
            'avantage_autres': worker_data.get('avantage_autres', 0.0),
            'taux_sal_cnaps_override': worker_data.get('taux_sal_cnaps_override'),
            'taux_sal_smie_override': worker_data.get('taux_sal_smie_override')
        }
        
        # 3. Mettre à jour
        response = requests.put(f"{BACKEND_URL}/workers/{worker_id}", json=update_data)
        
        if response.status_code == 200:
            return True, "Succès"
        else:
            return False, f"Erreur HTTP {response.status_code}: {response.text}"
        
    except Exception as e:
        return False, f"Exception: {str(e)}"

def main():
    """Fonction principale"""
    print("🚀 Migration Simplifiée des Assignations")
    print("=" * 60)
    
    # 1. Récupérer le mapping
    print("🔍 Récupération du mapping ID → Nom...")
    id_to_name = get_id_to_name_mapping()
    
    if not id_to_name:
        print("❌ Impossible de récupérer le mapping")
        return
    
    print("✅ Mapping récupéré:")
    for id_val, name in id_to_name.items():
        print(f"   {id_val} → {name}")
    
    # 2. Récupérer les salariés
    print("\n👥 Récupération des salariés...")
    response = requests.get(f"{BACKEND_URL}/workers")
    if response.status_code != 200:
        print("❌ Impossible de récupérer les salariés")
        return
    
    workers = response.json()
    employer_workers = [w for w in workers if w.get('employer_id') == 1]
    
    print(f"✅ {len(employer_workers)} salarié(s) trouvé(s)")
    
    # 3. Migrer chaque salarié
    print("\n🔄 Migration en cours...")
    
    for worker in employer_workers:
        worker_id = worker['id']
        worker_name = f"{worker.get('prenom', '')} {worker.get('nom', '')}"
        
        # Préparer les nouvelles assignations
        new_assignments = {}
        changes = []
        
        # Mapper chaque champ organisationnel
        for field in ['etablissement', 'departement', 'service', 'unite']:
            old_value = worker.get(field, '')
            if old_value and old_value in id_to_name:
                new_assignments[field] = id_to_name[old_value]
                changes.append(f"{field}: {old_value} → {new_assignments[field]}")
        
        if changes:
            print(f"\n   👤 {worker_name}:")
            for change in changes:
                print(f"      - {change}")
            
            # Effectuer la migration
            success, message = migrate_worker_simple(worker_id, new_assignments)
            
            if success:
                print(f"      ✅ Migration réussie")
            else:
                print(f"      ❌ Erreur: {message}")
        else:
            print(f"\n   ➡️ {worker_name}: Aucune migration nécessaire")
    
    # 4. Test final
    print(f"\n🧪 Test du filtrage...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/payroll/bulk-preview", {
            'params': {
                'employer_id': 1,
                'period': '2024-12',
                'etablissement': 'SIRAMA'
            }
        })
        
        if response.status_code == 200:
            bulletins = response.json()
            print(f"✅ Test réussi: {len(bulletins)} bulletin(s) avec filtre SIRAMA")
            
            if len(bulletins) > 0:
                print("🎉 LE FILTRAGE FONCTIONNE MAINTENANT!")
            else:
                print("⚠️ Aucun bulletin trouvé - vérifiez la période ou les données")
        else:
            print(f"❌ Test échoué: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur test: {e}")

if __name__ == "__main__":
    main()