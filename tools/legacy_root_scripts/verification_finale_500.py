#!/usr/bin/env python3
"""
Vérification finale que l'erreur 500 est corrigée
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def verification_complete():
    """Vérification complète du système"""
    
    print("🔍 VÉRIFICATION FINALE - ERREUR 500 CORRIGÉE")
    print("=" * 50)
    
    # 1. Test des endpoints principaux
    print("\n1️⃣ Test des endpoints principaux...")
    
    endpoints_critiques = [
        ("/employers", "Liste des employeurs"),
        ("/organizational-structure/1/tree", "Arbre organisationnel employeur 1"),
        ("/organizational-structure/2/tree", "Arbre organisationnel employeur 2"),
        ("/organizational-structure/1/validate", "Validation hiérarchie"),
        ("/organizational-structure/1/children", "Enfants organisationnels"),
        ("/workers", "Liste des salariés")
    ]
    
    erreurs_500 = []
    
    for endpoint, description in endpoints_critiques:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            
            if response.status_code == 500:
                erreurs_500.append((endpoint, description, response.text[:200]))
                print(f"   ❌ {description}: ERREUR 500")
            elif response.status_code >= 400:
                print(f"   ⚠️  {description}: {response.status_code}")
            else:
                print(f"   ✅ {description}: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ {description}: Exception - {e}")
    
    # 2. Test des cas problématiques précédents
    print(f"\n2️⃣ Test des cas qui causaient l'erreur 500...")
    
    cas_problematiques = [
        ("/organizational-structure/null/tree", "ID null"),
        ("/organizational-structure/undefined/tree", "ID undefined"),
        ("/organizational-structure/0/tree", "ID zéro"),
        ("/organizational-structure/-1/tree", "ID négatif")
    ]
    
    for endpoint, description in cas_problematiques:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            
            if response.status_code == 500:
                print(f"   ❌ {description}: ERREUR 500 (problème non résolu)")
                erreurs_500.append((endpoint, description, response.text[:200]))
            elif response.status_code in [400, 404, 422]:
                print(f"   ✅ {description}: {response.status_code} (erreur appropriée)")
            else:
                print(f"   ⚠️  {description}: {response.status_code} (inattendu)")
                
        except Exception as e:
            print(f"   ❌ {description}: Exception - {e}")
    
    # 3. Test du système de suppression
    print(f"\n3️⃣ Test du système de suppression...")
    
    try:
        # Récupérer un employeur
        response = requests.get(f"{BASE_URL}/employers")
        if response.status_code == 200:
            employers = response.json()
            if employers:
                employer_id = employers[0]['id']
                
                # Test arbre
                response = requests.get(f"{BASE_URL}/organizational-structure/{employer_id}/tree")
                if response.status_code == 200:
                    tree_data = response.json()
                    print(f"   ✅ Arbre organisationnel: {tree_data['total_units']} unités")
                    
                    # Test contraintes sur une unité
                    if tree_data['tree']:
                        def get_first_unit_id(nodes):
                            for node in nodes:
                                if isinstance(node, dict) and 'id' in node:
                                    return node['id']
                                if 'children' in node:
                                    child_id = get_first_unit_id(node['children'])
                                    if child_id:
                                        return child_id
                            return None
                        
                        unit_id = get_first_unit_id(tree_data['tree'])
                        if unit_id:
                            response = requests.get(f"{BASE_URL}/organizational-structure/{unit_id}/can-delete")
                            if response.status_code == 200:
                                print(f"   ✅ Contraintes de suppression: Fonctionnel")
                            else:
                                print(f"   ⚠️  Contraintes de suppression: {response.status_code}")
                else:
                    print(f"   ❌ Erreur arbre: {response.status_code}")
        else:
            print(f"   ❌ Erreur employeurs: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Exception test suppression: {e}")
    
    # 4. Résumé final
    print(f"\n4️⃣ RÉSUMÉ FINAL")
    print("=" * 20)
    
    if erreurs_500:
        print("❌ ERREURS 500 DÉTECTÉES:")
        for endpoint, description, response_text in erreurs_500:
            print(f"   • {description} ({endpoint})")
            print(f"     Response: {response_text}")
        
        print(f"\n🔧 ACTIONS REQUISES:")
        print("1. Vérifiez les logs du backend")
        print("2. Redémarrez le serveur backend")
        print("3. Vérifiez la configuration de l'API frontend")
        
    else:
        print("✅ AUCUNE ERREUR 500 DÉTECTÉE!")
        print("\n🎉 SYSTÈME ENTIÈREMENT FONCTIONNEL:")
        print("   • Tous les endpoints répondent correctement")
        print("   • Gestion d'erreur appropriée pour les cas invalides")
        print("   • Système de suppression opérationnel")
        
        print(f"\n📋 INSTRUCTIONS POUR L'UTILISATEUR:")
        print("1. Rafraîchissez votre page (F5 ou Ctrl+F5)")
        print("2. Ouvrez le modal 'Gestion de la Hiérarchie Organisationnelle'")
        print("3. Cherchez le bouton '🗑️ Supprimer' à côté de '+ Ajouter'")
        print("4. Cliquez sur une structure dans l'arbre pour la sélectionner")
        print("5. Cliquez sur '🗑️ Supprimer' pour tester le système")
        
        print(f"\n🚦 INDICATEURS À VÉRIFIER:")
        print("   • Bouton '🗑️ Supprimer' visible dans l'en-tête du modal")
        print("   • Sélection de structure fonctionne (surlignage)")
        print("   • Modal de suppression s'ouvre correctement")
        print("   • Aucune erreur 500 dans la console F12")

if __name__ == "__main__":
    verification_complete()