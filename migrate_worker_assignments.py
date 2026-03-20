#!/usr/bin/env python3
"""
Script de migration pour assigner les salariés aux nouvelles structures hiérarchiques
"""

import requests
import json

BACKEND_URL = "http://localhost:8000"

def create_id_to_name_mapping():
    """Crée un mapping des IDs vers les noms des structures"""
    print("🔍 Création du Mapping ID → Nom")
    print("=" * 50)
    
    try:
        # Récupérer l'arbre hiérarchique complet
        employer_id = 1  # Karibo Services
        response = requests.get(f"{BACKEND_URL}/organizational-structure/{employer_id}/tree")
        
        if response.status_code != 200:
            print("❌ Impossible de récupérer l'arbre hiérarchique")
            return None
        
        tree_data = response.json()
        
        # Créer le mapping récursivement
        id_to_name = {}
        
        def extract_mapping(nodes):
            for node in nodes:
                id_to_name[str(node['id'])] = node['name']
                if node.get('children'):
                    extract_mapping(node['children'])
        
        if tree_data.get('tree'):
            extract_mapping(tree_data['tree'])
        
        print("✅ Mapping créé:")
        for id_val, name in id_to_name.items():
            print(f"   ID {id_val} → {name}")
        
        return id_to_name
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None

def migrate_workers(id_to_name_mapping):
    """Migre les assignations des salariés"""
    print("\n🔄 Migration des Assignations des Salariés")
    print("=" * 50)
    
    try:
        # Récupérer tous les salariés
        response = requests.get(f"{BACKEND_URL}/workers")
        if response.status_code != 200:
            print("❌ Impossible de récupérer les salariés")
            return False
        
        workers = response.json()
        employer_workers = [w for w in workers if w.get('employer_id') == 1]
        
        if not employer_workers:
            print("⚠️ Aucun salarié trouvé")
            return False
        
        print(f"📊 {len(employer_workers)} salarié(s) à migrer:")
        
        migration_count = 0
        
        for worker in employer_workers:
            worker_id = worker['id']
            worker_name = f"{worker.get('prenom', '')} {worker.get('nom', '')}"
            
            # Préparer les nouvelles assignations
            new_assignments = {}
            changed = False
            
            # Mapper établissement
            old_etab = worker.get('etablissement', '')
            if old_etab and old_etab in id_to_name_mapping:
                new_assignments['etablissement'] = id_to_name_mapping[old_etab]
                changed = True
                print(f"   👤 {worker_name}: Établissement {old_etab} → {new_assignments['etablissement']}")
            elif old_etab and old_etab not in id_to_name_mapping and old_etab != '':
                print(f"   ⚠️ {worker_name}: Établissement {old_etab} non trouvé dans le mapping")
            
            # Mapper département
            old_dept = worker.get('departement', '')
            if old_dept and old_dept in id_to_name_mapping:
                new_assignments['departement'] = id_to_name_mapping[old_dept]
                changed = True
                print(f"   👤 {worker_name}: Département {old_dept} → {new_assignments['departement']}")
            elif old_dept and old_dept not in id_to_name_mapping and old_dept != '':
                print(f"   ⚠️ {worker_name}: Département {old_dept} non trouvé dans le mapping")
            
            # Mapper service
            old_service = worker.get('service', '')
            if old_service and old_service in id_to_name_mapping:
                new_assignments['service'] = id_to_name_mapping[old_service]
                changed = True
                print(f"   👤 {worker_name}: Service {old_service} → {new_assignments['service']}")
            elif old_service and old_service not in id_to_name_mapping and old_service != '':
                print(f"   ⚠️ {worker_name}: Service {old_service} non trouvé dans le mapping")
            
            # Mapper unité
            old_unite = worker.get('unite', '')
            if old_unite and old_unite in id_to_name_mapping:
                new_assignments['unite'] = id_to_name_mapping[old_unite]
                changed = True
                print(f"   👤 {worker_name}: Unité {old_unite} → {new_assignments['unite']}")
            elif old_unite and old_unite not in id_to_name_mapping and old_unite != '':
                print(f"   ⚠️ {worker_name}: Unité {old_unite} non trouvé dans le mapping")
            
            # Mettre à jour le salarié si des changements sont nécessaires
            if changed:
                # Préparer les données complètes du salarié avec les nouvelles assignations
                update_data = {
                    'matricule': worker.get('matricule', ''),
                    'nom': worker.get('nom', ''),
                    'prenom': worker.get('prenom', ''),
                    'adresse': worker.get('adresse', ''),
                    'nombre_enfant': worker.get('nombre_enfant', 0),
                    'type_regime_id': worker.get('type_regime_id', 1),
                    'salaire_base': worker.get('salaire_base', 0),
                    'salaire_horaire': worker.get('salaire_horaire', 0),
                    'vhm': worker.get('vhm', 0),
                    'horaire_hebdo': worker.get('horaire_hebdo', 0),
                    'etablissement': new_assignments.get('etablissement', worker.get('etablissement', '')),
                    'departement': new_assignments.get('departement', worker.get('departement', '')),
                    'service': new_assignments.get('service', worker.get('service', '')),
                    'unite': new_assignments.get('unite', worker.get('unite', ''))
                }
                
                # Mettre à jour via l'API
                response = requests.put(f"{BACKEND_URL}/workers/{worker_id}", json=update_data)
                
                if response.status_code == 200:
                    print(f"   ✅ {worker_name}: Migration réussie")
                    migration_count += 1
                else:
                    print(f"   ❌ {worker_name}: Erreur migration ({response.status_code})")
            else:
                print(f"   ➡️ {worker_name}: Aucune migration nécessaire")
        
        print(f"\n✅ Migration terminée: {migration_count} salarié(s) migré(s)")
        return migration_count > 0
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_after_migration():
    """Test le système après migration"""
    print("\n🧪 Test Après Migration")
    print("=" * 50)
    
    try:
        employer_id = 1
        period = "2024-12"
        
        # Test sans filtres
        print("📋 Test sans filtres:")
        response = requests.get(f"{BACKEND_URL}/payroll/bulk-preview", {
            'params': {
                'employer_id': employer_id,
                'period': period
            }
        })
        
        if response.status_code == 200:
            bulletins_all = response.json()
            print(f"   ✅ {len(bulletins_all)} bulletin(s) trouvé(s)")
        else:
            print(f"   ❌ Erreur: {response.status_code}")
            return False
        
        # Test avec filtre SIRAMA
        print("\n📋 Test avec filtre établissement 'SIRAMA':")
        response = requests.get(f"{BACKEND_URL}/payroll/bulk-preview", {
            'params': {
                'employer_id': employer_id,
                'period': period,
                'etablissement': 'SIRAMA'
            }
        })
        
        if response.status_code == 200:
            bulletins_filtered = response.json()
            print(f"   ✅ {len(bulletins_filtered)} bulletin(s) trouvé(s) avec filtre")
            
            if len(bulletins_filtered) > 0:
                print("   🎉 LE FILTRAGE FONCTIONNE MAINTENANT!")
                return True
            else:
                print("   ⚠️ Aucun bulletin avec filtre - vérifiez les assignations")
                return False
        else:
            print(f"   ❌ Erreur avec filtre: {response.status_code}")
            return False
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def main():
    """Fonction principale"""
    print("🚀 Migration des Assignations Organisationnelles")
    print("=" * 70)
    
    # 1. Créer le mapping
    id_to_name = create_id_to_name_mapping()
    if not id_to_name:
        print("❌ Impossible de créer le mapping")
        return
    
    # 2. Confirmer la migration
    print(f"\n⚠️ ATTENTION: Cette opération va modifier {len(id_to_name)} assignations de salariés")
    confirm = input("Voulez-vous continuer? (oui/non): ")
    
    if confirm.lower() not in ['oui', 'o', 'yes', 'y']:
        print("❌ Migration annulée")
        return
    
    # 3. Effectuer la migration
    success = migrate_workers(id_to_name)
    
    if success:
        # 4. Tester le résultat
        test_success = test_after_migration()
        
        if test_success:
            print("\n🎉 MIGRATION RÉUSSIE!")
            print("\n📋 MAINTENANT VOUS POUVEZ:")
            print("1. Aller sur /payroll")
            print("2. Cliquer sur 'Imprimer tous les bulletins'")
            print("3. Sélectionner des filtres organisationnels")
            print("4. Voir les bulletins filtrés s'afficher!")
        else:
            print("\n⚠️ Migration effectuée mais tests échoués")
            print("Vérifiez manuellement les assignations des salariés")
    else:
        print("\n❌ Migration échouée")

if __name__ == "__main__":
    main()