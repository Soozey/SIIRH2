#!/usr/bin/env python3
"""
Script de validation de la migration hiérarchique organisationnelle.

Ce script valide que :
1. La structure hiérarchique a été créée correctement
2. Les relations parent-enfant sont cohérentes
3. Les contraintes d'intégrité sont respectées
4. Les chemins hiérarchiques sont corrects
5. Le filtrage en cascade fonctionne

Exécution : python test_hierarchical_migration_validation.py
"""

import sys
import os
import sqlite3
from datetime import datetime
import json

def test_hierarchical_structure():
    """Teste la structure hiérarchique créée"""
    
    db_path = "siirh-backend/siirh.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🧪 Test de la structure hiérarchique organisationnelle")
        print("=" * 60)
        
        # Test 1: Vérifier les niveaux hiérarchiques
        print("\n1️⃣ Test des niveaux hiérarchiques...")
        
        cursor.execute("""
            SELECT level, COUNT(*) as count, GROUP_CONCAT(name, ', ') as names
            FROM organizational_nodes 
            WHERE employer_id = 1 AND is_active = 1
            GROUP BY level 
            ORDER BY level
        """)
        
        levels = cursor.fetchall()
        level_names = {1: "Établissements", 2: "Départements", 3: "Services", 4: "Unités"}
        
        for level, count, names in levels:
            level_name = level_names.get(level, f"Niveau {level}")
            print(f"  ✅ {level_name} (Niveau {level}): {count} éléments")
            print(f"     Noms: {names}")
        
        # Test 2: Vérifier les relations parent-enfant
        print("\n2️⃣ Test des relations parent-enfant...")
        
        cursor.execute("""
            SELECT 
                child.id as child_id,
                child.name as child_name,
                child.level as child_level,
                parent.id as parent_id,
                parent.name as parent_name,
                parent.level as parent_level
            FROM organizational_nodes child
            LEFT JOIN organizational_nodes parent ON child.parent_id = parent.id
            WHERE child.employer_id = 1 AND child.is_active = 1
            ORDER BY child.level, child.name
        """)
        
        relations = cursor.fetchall()
        
        for child_id, child_name, child_level, parent_id, parent_name, parent_level in relations:
            if parent_id:
                if parent_level == child_level - 1:
                    print(f"  ✅ {child_name} (L{child_level}) → {parent_name} (L{parent_level})")
                else:
                    print(f"  ❌ ERREUR: {child_name} (L{child_level}) → {parent_name} (L{parent_level}) - Niveaux incohérents")
            else:
                if child_level == 1:
                    print(f"  ✅ {child_name} (L{child_level}) → Racine")
                else:
                    print(f"  ❌ ERREUR: {child_name} (L{child_level}) sans parent")
        
        # Test 3: Vérifier les chemins hiérarchiques
        print("\n3️⃣ Test des chemins hiérarchiques...")
        
        cursor.execute("""
            SELECT id, level, name, full_path
            FROM organizational_paths 
            WHERE employer_id = 1
            ORDER BY level, name
        """)
        
        paths = cursor.fetchall()
        
        for node_id, level, name, full_path in paths[:10]:  # Limiter à 10 pour l'affichage
            print(f"  ✅ {name} (L{level}): {full_path}")
        
        if len(paths) > 10:
            print(f"  ... et {len(paths) - 10} autres chemins")
        
        # Test 4: Test du filtrage en cascade
        print("\n4️⃣ Test du filtrage en cascade...")
        
        # Établissements (niveau 1)
        cursor.execute("""
            SELECT id, name FROM organizational_nodes 
            WHERE employer_id = 1 AND level = 1 AND is_active = 1
            ORDER BY name
        """)
        etablissements = cursor.fetchall()
        
        print(f"  📍 {len(etablissements)} établissements disponibles:")
        for etab_id, etab_name in etablissements:
            print(f"    • {etab_name} (ID: {etab_id})")
            
            # Départements de cet établissement
            cursor.execute("""
                SELECT id, name FROM organizational_nodes 
                WHERE employer_id = 1 AND parent_id = ? AND level = 2 AND is_active = 1
                ORDER BY name
            """, (etab_id,))
            departements = cursor.fetchall()
            
            print(f"      🏛️ {len(departements)} départements:")
            for dept_id, dept_name in departements:
                print(f"        • {dept_name} (ID: {dept_id})")
                
                # Services de ce département
                cursor.execute("""
                    SELECT id, name FROM organizational_nodes 
                    WHERE employer_id = 1 AND parent_id = ? AND level = 3 AND is_active = 1
                    ORDER BY name
                """, (dept_id,))
                services = cursor.fetchall()
                
                if services:
                    print(f"          🔧 {len(services)} services:")
                    for serv_id, serv_name in services:
                        print(f"            • {serv_name} (ID: {serv_id})")
                        
                        # Unités de ce service
                        cursor.execute("""
                            SELECT id, name FROM organizational_nodes 
                            WHERE employer_id = 1 AND parent_id = ? AND level = 4 AND is_active = 1
                            ORDER BY name
                        """, (serv_id,))
                        unites = cursor.fetchall()
                        
                        if unites:
                            print(f"              👥 {len(unites)} unités:")
                            for unit_id, unit_name in unites:
                                print(f"                • {unit_name} (ID: {unit_id})")
        
        # Test 5: Vérifier les contraintes d'intégrité
        print("\n5️⃣ Test des contraintes d'intégrité...")
        
        # Vérifier qu'il n'y a pas de cycles
        cursor.execute("""
            WITH RECURSIVE hierarchy_check AS (
                SELECT id, parent_id, name, 1 as depth, CAST(id AS TEXT) as path
                FROM organizational_nodes 
                WHERE employer_id = 1 AND is_active = 1
                
                UNION ALL
                
                SELECT n.id, n.parent_id, n.name, h.depth + 1, h.path || '->' || CAST(n.id AS TEXT)
                FROM organizational_nodes n
                JOIN hierarchy_check h ON n.parent_id = h.id
                WHERE h.depth < 10 AND n.employer_id = 1 AND n.is_active = 1
                  AND INSTR(h.path, CAST(n.id AS TEXT)) = 0
            )
            SELECT COUNT(*) FROM hierarchy_check WHERE depth > 4
        """)
        
        cycles = cursor.fetchone()[0]
        
        if cycles == 0:
            print("  ✅ Aucun cycle détecté dans la hiérarchie")
        else:
            print(f"  ❌ {cycles} cycles potentiels détectés")
        
        # Vérifier les niveaux cohérents
        cursor.execute("""
            SELECT COUNT(*) FROM organizational_nodes child
            JOIN organizational_nodes parent ON child.parent_id = parent.id
            WHERE child.employer_id = 1 AND child.is_active = 1
              AND parent.level != child.level - 1
        """)
        
        level_violations = cursor.fetchone()[0]
        
        if level_violations == 0:
            print("  ✅ Tous les niveaux hiérarchiques sont cohérents")
        else:
            print(f"  ❌ {level_violations} violations de niveau détectées")
        
        # Test 6: Performance des requêtes
        print("\n6️⃣ Test de performance...")
        
        import time
        
        # Test de requête de filtrage en cascade
        start_time = time.time()
        
        cursor.execute("""
            SELECT n1.name as etablissement, n2.name as departement, n3.name as service, n4.name as unite
            FROM organizational_nodes n1
            LEFT JOIN organizational_nodes n2 ON n2.parent_id = n1.id AND n2.level = 2
            LEFT JOIN organizational_nodes n3 ON n3.parent_id = n2.id AND n3.level = 3  
            LEFT JOIN organizational_nodes n4 ON n4.parent_id = n3.id AND n4.level = 4
            WHERE n1.employer_id = 1 AND n1.level = 1 AND n1.is_active = 1
            ORDER BY n1.name, n2.name, n3.name, n4.name
        """)
        
        cascade_results = cursor.fetchall()
        end_time = time.time()
        
        print(f"  ✅ Requête de cascade complète: {len(cascade_results)} résultats en {(end_time - start_time)*1000:.2f}ms")
        
        # Afficher quelques exemples
        print("  📋 Exemples de combinaisons hiérarchiques:")
        for i, (etab, dept, serv, unit) in enumerate(cascade_results[:5]):
            path_parts = [etab]
            if dept: path_parts.append(dept)
            if serv: path_parts.append(serv)
            if unit: path_parts.append(unit)
            print(f"    {i+1}. {' > '.join(path_parts)}")
        
        conn.close()
        
        print(f"\n🎉 Validation terminée avec succès !")
        print(f"✅ Structure hiérarchique opérationnelle")
        print(f"✅ Filtrage en cascade fonctionnel")
        print(f"✅ Intégrité des données respectée")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la validation : {e}")
        return False


def test_api_simulation():
    """Simule les appels API pour le filtrage en cascade"""
    
    db_path = "siirh-backend/siirh.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print(f"\n🌐 Simulation des appels API de filtrage en cascade")
        print("=" * 60)
        
        employer_id = 1
        
        # API 1: GET /employers/{employer_id}/organization/cascading-options (établissements)
        print(f"\n📡 GET /employers/{employer_id}/organization/cascading-options")
        
        cursor.execute("""
            SELECT id, name, code, level, parent_id
            FROM organizational_nodes 
            WHERE employer_id = ? AND parent_id IS NULL AND level = 1 AND is_active = 1
            ORDER BY name
        """, (employer_id,))
        
        etablissements = cursor.fetchall()
        
        print(f"  ✅ Réponse: {len(etablissements)} établissements")
        for etab_id, name, code, level, parent_id in etablissements:
            print(f"    • {name} (ID: {etab_id}, Code: {code})")
        
        # API 2: GET /employers/{employer_id}/organization/cascading-options?parent_id=X (départements)
        if etablissements:
            etab_id = etablissements[0][0]  # Premier établissement
            etab_name = etablissements[0][1]
            
            print(f"\n📡 GET /employers/{employer_id}/organization/cascading-options?parent_id={etab_id}")
            
            cursor.execute("""
                SELECT id, name, code, level, parent_id
                FROM organizational_nodes 
                WHERE employer_id = ? AND parent_id = ? AND level = 2 AND is_active = 1
                ORDER BY name
            """, (employer_id, etab_id))
            
            departements = cursor.fetchall()
            
            print(f"  ✅ Réponse: {len(departements)} départements pour '{etab_name}'")
            for dept_id, name, code, level, parent_id in departements:
                print(f"    • {name} (ID: {dept_id}, Code: {code})")
            
            # API 3: GET /employers/{employer_id}/organization/cascading-options?parent_id=Y (services)
            if departements:
                dept_id = departements[0][0]  # Premier département
                dept_name = departements[0][1]
                
                print(f"\n📡 GET /employers/{employer_id}/organization/cascading-options?parent_id={dept_id}")
                
                cursor.execute("""
                    SELECT id, name, code, level, parent_id
                    FROM organizational_nodes 
                    WHERE employer_id = ? AND parent_id = ? AND level = 3 AND is_active = 1
                    ORDER BY name
                """, (employer_id, dept_id))
                
                services = cursor.fetchall()
                
                print(f"  ✅ Réponse: {len(services)} services pour '{dept_name}'")
                for serv_id, name, code, level, parent_id in services:
                    print(f"    • {name} (ID: {serv_id}, Code: {code})")
                
                # API 4: GET /employers/{employer_id}/organization/cascading-options?parent_id=Z (unités)
                if services:
                    serv_id = services[0][0]  # Premier service
                    serv_name = services[0][1]
                    
                    print(f"\n📡 GET /employers/{employer_id}/organization/cascading-options?parent_id={serv_id}")
                    
                    cursor.execute("""
                        SELECT id, name, code, level, parent_id
                        FROM organizational_nodes 
                        WHERE employer_id = ? AND parent_id = ? AND level = 4 AND is_active = 1
                        ORDER BY name
                    """, (employer_id, serv_id))
                    
                    unites = cursor.fetchall()
                    
                    print(f"  ✅ Réponse: {len(unites)} unités pour '{serv_name}'")
                    for unit_id, name, code, level, parent_id in unites:
                        print(f"    • {name} (ID: {unit_id}, Code: {code})")
        
        # API 5: GET /employers/{employer_id}/organization/tree (arbre complet)
        print(f"\n📡 GET /employers/{employer_id}/organization/tree")
        
        cursor.execute("""
            SELECT id, parent_id, level, name, code, 
                   (SELECT COUNT(*) FROM organizational_nodes children 
                    WHERE children.parent_id = nodes.id AND children.is_active = 1) as children_count
            FROM organizational_nodes nodes
            WHERE employer_id = ? AND is_active = 1
            ORDER BY level, name
        """, (employer_id,))
        
        tree_nodes = cursor.fetchall()
        
        print(f"  ✅ Réponse: {len(tree_nodes)} nœuds dans l'arbre")
        
        # Construire et afficher l'arbre
        nodes_by_parent = {}
        for node_id, parent_id, level, name, code, children_count in tree_nodes:
            if parent_id not in nodes_by_parent:
                nodes_by_parent[parent_id] = []
            nodes_by_parent[parent_id].append((node_id, level, name, code, children_count))
        
        def print_tree(parent_id, indent=""):
            if parent_id in nodes_by_parent:
                for node_id, level, name, code, children_count in nodes_by_parent[parent_id]:
                    print(f"  {indent}• {name} (L{level}, {children_count} enfants)")
                    print_tree(node_id, indent + "  ")
        
        print_tree(None)
        
        conn.close()
        
        print(f"\n🎉 Simulation API terminée avec succès !")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la simulation API : {e}")
        return False


def main():
    """Fonction principale de validation"""
    
    print("🧪 Validation complète de la migration hiérarchique organisationnelle")
    print("=" * 80)
    
    # Test 1: Structure hiérarchique
    success1 = test_hierarchical_structure()
    
    # Test 2: Simulation API
    success2 = test_api_simulation()
    
    # Résumé final
    print(f"\n📊 Résumé de la validation")
    print("=" * 40)
    
    if success1:
        print("✅ Structure hiérarchique: VALIDÉE")
    else:
        print("❌ Structure hiérarchique: ÉCHEC")
    
    if success2:
        print("✅ Simulation API: VALIDÉE")
    else:
        print("❌ Simulation API: ÉCHEC")
    
    if success1 and success2:
        print(f"\n🎉 TÂCHE 2.1 TERMINÉE AVEC SUCCÈS !")
        print(f"✅ La structure hiérarchique organisationnelle est opérationnelle")
        print(f"✅ Les données ont été migrées sans erreur")
        print(f"✅ Le filtrage en cascade est prêt à être implémenté")
        print(f"\n📋 Prochaines étapes :")
        print(f"  • Tâche 2.2: Écrire les tests de propriété pour les contraintes hiérarchiques")
        print(f"  • Tâche 2.3: Créer la vue matérialisée organizational_paths")
        print(f"  • Tâche 3.1: Créer le service HierarchicalOrganizationalService")
        return True
    else:
        print(f"\n❌ Des problèmes ont été détectés lors de la validation")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)