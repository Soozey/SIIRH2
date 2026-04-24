#!/usr/bin/env python3
"""
Script pour supprimer les données organisationnelles d'exemple
et ne garder que celles créées par l'utilisateur
"""

import requests
import json

def clean_organizational_data():
    base_url = "http://localhost:8000"
    
    print("🧹 NETTOYAGE COMPLET DES DONNÉES ORGANISATIONNELLES D'EXEMPLE")
    print("=" * 70)
    print("SUPPRESSION DE TOUTES LES DONNÉES ORGANISATIONNELLES CRÉÉES POUR LES TESTS")
    print("=" * 70)
    
    # 1. Récupérer tous les salariés de tous les employeurs
    print("\n📋 1. Récupération de tous les salariés...")
    
    # Récupérer la liste des employeurs
    employers_response = requests.get(f"{base_url}/employers")
    if employers_response.status_code != 200:
        print("❌ Impossible de récupérer la liste des employeurs")
        return
    
    employers = employers_response.json()
    print(f"   Employeurs trouvés: {len(employers)}")
    
    total_cleaned = 0
    
    for employer in employers:
        employer_id = employer['id']
        employer_name = employer['raison_sociale']
        
        print(f"\n🏢 Traitement de {employer_name} (ID: {employer_id})")
        print("-" * 50)
        
        # Récupérer tous les salariés de cet employeur
        response = requests.get(f"{base_url}/workers?employer_id={employer_id}")
        if response.status_code == 200:
            workers = response.json()
            print(f"   📊 {len(workers)} salariés trouvés")
            
            for worker in workers:
                worker_id = worker['id']
                nom = worker['nom']
                prenom = worker['prenom']
                
                # Vérifier si ce salarié a des données organisationnelles
                has_org_data = any([
                    worker.get('etablissement'),
                    worker.get('departement'), 
                    worker.get('service'),
                    worker.get('unite')
                ])
                
                if has_org_data:
                    print(f"   🔍 {nom} {prenom} (ID: {worker_id})")
                    print(f"      Établissement: {worker.get('etablissement')}")
                    print(f"      Département: {worker.get('departement')}")
                    print(f"      Service: {worker.get('service')}")
                    print(f"      Unité: {worker.get('unite')}")
                    
                    # SUPPRIMER TOUTES LES DONNÉES ORGANISATIONNELLES
                    # Car selon l'utilisateur, il n'a créé aucune de ces données
                    update_data = {
                        "matricule": worker['matricule'],
                        "nom": worker['nom'],
                        "prenom": worker['prenom'],
                        "adresse": worker.get('adresse'),
                        "poste": worker.get('poste'),
                        "categorie_prof": worker.get('categorie_prof'),
                        "date_embauche": worker.get('date_embauche'),
                        "salaire_base": worker.get('salaire_base', 0),
                        "salaire_horaire": worker.get('salaire_horaire', 0),
                        "horaire_hebdo": worker.get('horaire_hebdo', 40),  # Champ requis
                        "cnaps_num": worker.get('cnaps_num'),
                        "secteur": worker.get('secteur'),
                        "mode_paiement": worker.get('mode_paiement'),
                        "employer_id": worker['employer_id'],
                        "type_regime_id": worker.get('type_regime_id'),
                        "vhm": worker.get('vhm'),
                        # SUPPRIMER TOUTES LES DONNÉES ORGANISATIONNELLES
                        "etablissement": None,
                        "departement": None,
                        "service": None,
                        "unite": None,
                        # Garder les autres champs intacts
                        "avantage_vehicule": worker.get('avantage_vehicule', 0),
                        "avantage_logement": worker.get('avantage_logement', 0),
                        "avantage_telephone": worker.get('avantage_telephone', 0),
                        "avantage_autres": worker.get('avantage_autres', 0),
                        "date_debauche": worker.get('date_debauche'),
                        "type_sortie": worker.get('type_sortie'),
                        "groupe_preavis": worker.get('groupe_preavis'),
                        "jours_preavis_deja_faits": worker.get('jours_preavis_deja_faits'),
                        "nature_contrat": worker.get('nature_contrat')
                    }
                    
                    # Mettre à jour le salarié
                    update_response = requests.put(
                        f"{base_url}/workers/{worker_id}",
                        json=update_data
                    )
                    
                    if update_response.status_code == 200:
                        print(f"      ✅ Toutes les données organisationnelles supprimées")
                        total_cleaned += 1
                    else:
                        print(f"      ❌ Erreur lors de la suppression: {update_response.status_code}")
                        try:
                            error_detail = update_response.json()
                            print(f"         Détail: {error_detail}")
                        except:
                            print(f"         Réponse: {update_response.text}")
                else:
                    print(f"   ℹ️  {nom} {prenom} - Aucune donnée organisationnelle")
        else:
            print(f"   ❌ Erreur lors de la récupération des salariés: {response.status_code}")
    
    print("\n" + "=" * 70)
    print("🎯 RÉSUMÉ DU NETTOYAGE COMPLET")
    print("=" * 70)
    print(f"✅ {total_cleaned} salariés nettoyés")
    print("🗑️  TOUTES les données organisationnelles d'exemple ont été supprimées")
    
    # Vérifier l'état final
    print("\n📊 État final des données organisationnelles:")
    
    for employer in employers:
        employer_id = employer['id']
        employer_name = employer['raison_sociale']
        
        response = requests.get(f"{base_url}/employers/{employer_id}/organizational-data/workers")
        if response.status_code == 200:
            org_data = response.json()
            print(f"\n{employer_name} (ID: {employer_id}):")
            print(f"  Établissements: {org_data.get('etablissements', [])}")
            print(f"  Départements: {org_data.get('departements', [])}")
            print(f"  Services: {org_data.get('services', [])}")
            print(f"  Unités: {org_data.get('unites', [])}")
            
            # Vérifier si des données existent encore
            has_any_data = any([
                org_data.get('etablissements'),
                org_data.get('departements'),
                org_data.get('services'),
                org_data.get('unites')
            ])
            
            if not has_any_data:
                print(f"  ✅ Aucune donnée organisationnelle (nettoyage réussi)")
            else:
                print(f"  ⚠️  Des données existent encore")
    
    print("\n" + "=" * 70)
    print("✅ NETTOYAGE COMPLET TERMINÉ")
    print("=" * 70)
    print("🎯 RÉSULTAT:")
    print("   • Toutes les données organisationnelles d'exemple supprimées")
    print("   • Base de données prête pour vos vraies données")
    print("   • Système de filtrage toujours fonctionnel")
    print("   • Vous pouvez maintenant créer vos propres structures")
    print("=" * 70)

if __name__ == "__main__":
    clean_organizational_data()