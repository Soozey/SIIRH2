#!/usr/bin/env python3
"""
Démonstration interactive du système de suppression
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def demo_suppression_process():
    """Démonstration du processus de suppression"""
    
    print("🎯 DÉMONSTRATION DU SYSTÈME DE SUPPRESSION")
    print("=" * 50)
    print("Cette démonstration vous montre comment fonctionne le système de suppression")
    print("dans l'interface utilisateur.\n")
    
    # 1. Créer une structure de démonstration
    print("1️⃣ Création d'une structure de démonstration...")
    
    try:
        # Créer un employeur de test
        employer_data = {
            "raison_sociale": "Demo Suppression Company",
            "adresse": "123 Demo Street",
            "email": "demo@suppression.com",
            "type_regime_id": 1
        }
        
        response = requests.post(f"{BASE_URL}/employers/", json=employer_data)
        if response.status_code == 200:
            employer = response.json()
            employer_id = employer["id"]
            print(f"   ✅ Employeur créé: {employer['raison_sociale']} (ID: {employer_id})")
        else:
            print(f"   ❌ Erreur création employeur: {response.status_code}")
            return
        
        # Créer des structures organisationnelles
        structures = [
            {
                "name": "Établissement Demo",
                "code": "DEMO",
                "level": "etablissement",
                "parent_id": None,
                "description": "Établissement pour démonstration"
            },
            {
                "name": "Département Vide",
                "code": "DEPT_VIDE",
                "level": "departement",
                "parent_id": None,  # Sera mis à jour
                "description": "Département vide pour test de suppression simple"
            },
            {
                "name": "Département Occupé",
                "code": "DEPT_OCC",
                "level": "departement", 
                "parent_id": None,  # Sera mis à jour
                "description": "Département avec sous-structures"
            }
        ]
        
        created_structures = []
        
        for i, struct_data in enumerate(structures):
            struct_data["employer_id"] = employer_id
            
            response = requests.post(f"{BASE_URL}/organizational-structure/create", json=struct_data)
            if response.status_code == 200:
                structure = response.json()
                created_structures.append(structure)
                print(f"   ✅ {structure['name']} créé (ID: {structure['id']})")
                
                # Mettre à jour les parent_id pour les départements
                if i > 0:
                    structures[i]["parent_id"] = created_structures[0]["id"]
            else:
                print(f"   ❌ Erreur création {struct_data['name']}: {response.status_code}")
        
        # Créer un service dans le département occupé
        if len(created_structures) >= 3:
            service_data = {
                "employer_id": employer_id,
                "parent_id": created_structures[2]["id"],  # Département Occupé
                "level": "service",
                "code": "SRV_TEST",
                "name": "Service Test",
                "description": "Service pour démonstration"
            }
            
            response = requests.post(f"{BASE_URL}/organizational-structure/create", json=service_data)
            if response.status_code == 200:
                service = response.json()
                created_structures.append(service)
                print(f"   ✅ {service['name']} créé (ID: {service['id']})")
        
    except Exception as e:
        print(f"   ❌ Erreur lors de la création: {e}")
        return
    
    # 2. Démonstration des vérifications de contraintes
    print(f"\n2️⃣ Démonstration des vérifications de contraintes...")
    
    for structure in created_structures:
        try:
            print(f"\n   📋 Analyse de: {structure['name']} ({structure['level']})")
            
            # Vérifier les contraintes de suppression
            response = requests.get(f"{BASE_URL}/organizational-structure/{structure['id']}/can-delete")
            if response.status_code == 200:
                constraints = response.json()
                
                print(f"      - Peut être supprimé: {'✅ OUI' if constraints['can_delete'] else '❌ NON'}")
                print(f"      - Salariés directs: {constraints['direct_workers_count']}")
                print(f"      - Sous-structures: {constraints['children_count']}")
                print(f"      - Salariés descendants: {constraints['descendant_workers_count']}")
                
                if not constraints['can_delete']:
                    print(f"      - Raison: {constraints['reason']}")
                    
                    # Afficher les détails des contraintes
                    if constraints['children']:
                        print(f"      - Sous-structures:")
                        for child in constraints['children']:
                            print(f"        • {child['name']} ({child['level']})")
                    
                    if constraints['workers']:
                        print(f"      - Salariés:")
                        for worker in constraints['workers']:
                            print(f"        • {worker['prenom']} {worker['nom']} ({worker['matricule']})")
                
                # Simuler l'indicateur visuel
                if constraints['can_delete']:
                    print(f"      🟢 Indicateur: ✓ Supprimable")
                else:
                    print(f"      🟠 Indicateur: ⚠ Occupée")
                    
            else:
                print(f"      ❌ Erreur vérification: {response.status_code}")
                
        except Exception as e:
            print(f"      ❌ Erreur: {e}")
    
    # 3. Démonstration de suppression
    print(f"\n3️⃣ Démonstration de suppression...")
    
    # Trouver une structure supprimable
    supprimable = None
    for structure in created_structures:
        try:
            response = requests.get(f"{BASE_URL}/organizational-structure/{structure['id']}/can-delete")
            if response.status_code == 200:
                constraints = response.json()
                if constraints['can_delete']:
                    supprimable = structure
                    break
        except:
            continue
    
    if supprimable:
        print(f"\n   🎯 Test de suppression simple: {supprimable['name']}")
        
        try:
            response = requests.delete(f"{BASE_URL}/organizational-structure/{supprimable['id']}")
            if response.status_code == 200:
                print(f"      ✅ Suppression réussie!")
                print(f"      📝 Dans l'interface: Modal de confirmation → Clic sur 'Supprimer'")
            else:
                print(f"      ❌ Erreur suppression: {response.status_code}")
        except Exception as e:
            print(f"      ❌ Erreur: {e}")
    
    # Test de suppression forcée
    non_supprimable = None
    for structure in created_structures:
        if structure != supprimable:
            try:
                response = requests.get(f"{BASE_URL}/organizational-structure/{structure['id']}/can-delete")
                if response.status_code == 200:
                    constraints = response.json()
                    if not constraints['can_delete']:
                        non_supprimable = structure
                        break
            except:
                continue
    
    if non_supprimable:
        print(f"\n   🎯 Test de suppression forcée: {non_supprimable['name']}")
        
        try:
            # D'abord montrer le blocage
            response = requests.delete(f"{BASE_URL}/organizational-structure/{non_supprimable['id']}")
            if response.status_code == 400:
                print(f"      ⚠️ Suppression bloquée (normal): {response.json()['detail']}")
                print(f"      📝 Dans l'interface: Modal d'avertissement avec détails")
            
            # Puis montrer la suppression forcée
            response = requests.delete(f"{BASE_URL}/organizational-structure/{non_supprimable['id']}?force=true")
            if response.status_code == 200:
                print(f"      ✅ Suppression forcée réussie!")
                print(f"      📝 Dans l'interface: Confirmation → 'Forcer la suppression'")
            else:
                print(f"      ❌ Erreur suppression forcée: {response.status_code}")
                
        except Exception as e:
            print(f"      ❌ Erreur: {e}")
    
    # 4. Résumé de l'utilisation
    print(f"\n4️⃣ RÉSUMÉ - Comment utiliser dans l'interface:")
    print("=" * 50)
    print("📍 ÉTAPES À SUIVRE:")
    print("   1. Aller dans Organisation → 'Gestion Hiérarchique avec Suppression'")
    print("   2. Cliquer sur une structure dans l'arbre pour la sélectionner")
    print("   3. Cliquer sur le bouton rouge '🗑️ Supprimer'")
    print("   4. Suivre les instructions du modal qui s'ouvre")
    print()
    print("🚦 INDICATEURS VISUELS:")
    print("   🟢 ✓ Supprimable = Structure vide, suppression directe")
    print("   🟠 ⚠ Occupée = Contient des éléments, options avancées")
    print()
    print("⚙️ OPTIONS DE SUPPRESSION:")
    print("   • Suppression simple: Pour structures vides")
    print("   • Suppression forcée: Réassigne automatiquement les éléments")
    print("   • Annulation: Retour sans modification")
    print()
    print("🛡️ SÉCURITÉS:")
    print("   • Vérification automatique des contraintes")
    print("   • Informations détaillées sur l'impact")
    print("   • Confirmations multiples pour éviter les erreurs")
    print("   • Réassignation intelligente des éléments")

if __name__ == "__main__":
    demo_suppression_process()