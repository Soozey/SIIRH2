#!/usr/bin/env python3
"""
Diagnostic de la structure hiérarchique pour comprendre les relations parent-enfant
"""

import requests
import json

BACKEND_URL = "http://localhost:8000"

def analyze_hierarchy_structure():
    """Analyse la structure hiérarchique actuelle"""
    print("🔍 Analyse de la Structure Hiérarchique")
    print("=" * 60)
    
    try:
        # Récupérer les employeurs
        response = requests.get(f"{BACKEND_URL}/employers")
        if response.status_code != 200:
            print("❌ Impossible de récupérer les employeurs")
            return
        
        employers = response.json()
        if not employers:
            print("⚠️ Aucun employeur trouvé")
            return
        
        employer_id = employers[0]['id']
        employer_name = employers[0].get('raison_sociale', f'Employeur {employer_id}')
        
        print(f"📋 Analyse pour: {employer_name} (ID: {employer_id})")
        print()
        
        # Récupérer l'arbre hiérarchique complet
        response = requests.get(f"{BACKEND_URL}/organizational-structure/{employer_id}/tree")
        if response.status_code != 200:
            print("❌ Impossible de récupérer l'arbre hiérarchique")
            return
        
        tree_data = response.json()
        
        print("🏗️ STRUCTURE HIÉRARCHIQUE COMPLÈTE:")
        print("-" * 50)
        print(json.dumps(tree_data, indent=2, ensure_ascii=False))
        
        if not tree_data.get('tree'):
            print("⚠️ Aucune structure hiérarchique trouvée")
            return
        
        # Analyser les relations parent-enfant
        print("\n📊 ANALYSE DES RELATIONS:")
        print("-" * 50)
        
        def analyze_node(node, level=0):
            indent = "  " * level
            print(f"{indent}📁 {node['name']} ({node['level']}) - ID: {node['id']}")
            
            if node.get('children'):
                print(f"{indent}   └─ {len(node['children'])} enfant(s):")
                for child in node['children']:
                    analyze_node(child, level + 1)
            else:
                print(f"{indent}   └─ Aucun enfant")
        
        for root_node in tree_data['tree']:
            analyze_node(root_node)
        
        # Test du filtrage avec les données réelles
        print("\n🧪 TEST DE FILTRAGE AVEC DONNÉES RÉELLES:")
        print("-" * 50)
        
        # Extraire le premier établissement de l'arbre
        first_establishment = None
        for node in tree_data['tree']:
            if node['level'] == 'etablissement':
                first_establishment = node
                break
        
        if first_establishment:
            etablissement_name = first_establishment['name']
            print(f"🏢 Test avec établissement: {etablissement_name}")
            
            # Tester le filtrage
            response = requests.get(f"{BACKEND_URL}/employers/{employer_id}/organizational-data/hierarchical-filtered", {
                'params': {'etablissement': etablissement_name}
            })
            
            if response.status_code == 200:
                filtered_data = response.json()
                print(f"✅ Résultat du filtrage:")
                print(f"   - Établissements: {filtered_data.get('etablissements', [])}")
                print(f"   - Départements: {filtered_data.get('departements', [])}")
                print(f"   - Services: {filtered_data.get('services', [])}")
                print(f"   - Unités: {filtered_data.get('unites', [])}")
                
                # Vérifier si le filtrage fonctionne
                expected_departments = []
                if first_establishment.get('children'):
                    for child in first_establishment['children']:
                        if child['level'] == 'departement':
                            expected_departments.append(child['name'])
                
                actual_departments = filtered_data.get('departements', [])
                
                print(f"\n🔍 VÉRIFICATION DU FILTRAGE:")
                print(f"   - Départements attendus (enfants de {etablissement_name}): {expected_departments}")
                print(f"   - Départements retournés: {actual_departments}")
                
                if set(expected_departments) == set(actual_departments):
                    print("   ✅ Le filtrage fonctionne correctement!")
                else:
                    print("   ❌ Le filtrage ne fonctionne pas comme attendu")
                    
                    # Diagnostic supplémentaire
                    print(f"\n🔧 DIAGNOSTIC:")
                    if len(actual_departments) == 0:
                        print("   - Aucun département retourné - problème de logique de filtrage")
                    elif len(actual_departments) > len(expected_departments):
                        print("   - Trop de départements retournés - filtrage trop permissif")
                    else:
                        print("   - Départements manquants - filtrage trop restrictif")
            else:
                print(f"❌ Erreur lors du test de filtrage: {response.status_code}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

def suggest_fixes():
    """Suggère des corrections basées sur l'analyse"""
    print("\n💡 SUGGESTIONS DE CORRECTION:")
    print("=" * 60)
    
    print("🔧 PROBLÈMES POSSIBLES ET SOLUTIONS:")
    print()
    print("1. 🏗️ STRUCTURE HIÉRARCHIQUE MAL FORMÉE")
    print("   - Vérifiez que les relations parent-enfant sont correctes")
    print("   - Assurez-vous que chaque niveau a bien ses enfants")
    print()
    print("2. 🔗 LOGIQUE DE FILTRAGE INCORRECTE")
    print("   - La fonction is_descendant_of pourrait avoir un bug")
    print("   - Les noms des niveaux pourraient ne pas correspondre")
    print()
    print("3. 📊 DONNÉES INCOHÉRENTES")
    print("   - Certaines unités pourraient ne pas avoir de parent_id correct")
    print("   - Les noms pourraient contenir des espaces ou caractères spéciaux")
    print()
    print("🛠️ ACTIONS RECOMMANDÉES:")
    print("1. Recréer la structure hiérarchique avec des relations claires")
    print("2. Tester le filtrage avec des données simples")
    print("3. Vérifier la cohérence des données en base")

def main():
    """Fonction principale"""
    print("🚀 Diagnostic de la Structure Hiérarchique")
    print("=" * 70)
    
    analyze_hierarchy_structure()
    suggest_fixes()

if __name__ == "__main__":
    main()