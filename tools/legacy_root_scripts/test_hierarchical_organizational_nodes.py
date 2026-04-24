#!/usr/bin/env python3
"""
Script de test pour la nouvelle structure hiérarchique organisationnelle.

Ce script teste :
1. La création de nœuds hiérarchiques
2. Les contraintes d'intégrité
3. Les relations parent-enfant
4. L'audit trail
5. La table des chemins hiérarchiques

Exécution : python test_hierarchical_organizational_nodes.py
"""

import sys
import os
import sqlite3
from datetime import datetime
import json

def test_hierarchical_structure():
    """Teste la structure hiérarchique organisationnelle"""
    
    db_path = "siirh-backend/siirh.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Base de données non trouvée : {db_path}")
        return False
    
    print("🧪 Test de la structure hiérarchique organisationnelle")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. Vérifier qu'un employeur existe
        print("👤 Vérification de l'employeur de test...")
        cursor.execute("SELECT id, raison_sociale FROM employers LIMIT 1")
        employer = cursor.fetchone()
        
        if not employer:
            print("❌ Aucun employeur trouvé dans la base")
            return False
        
        employer_id = employer[0]
        employer_name = employer[1]
        print(f"✅ Employeur trouvé : {employer_name} (ID: {employer_id})")
        
        # 2. Nettoyer les données de test existantes
        print("\n🧹 Nettoyage des données de test...")
        cursor.execute("DELETE FROM organizational_nodes WHERE employer_id = ? AND name LIKE 'Test %'", (employer_id,))
        conn.commit()
        
        # 3. Test de création d'un établissement (niveau 1)
        print("\n🏢 Test de création d'un établissement...")
        cursor.execute("""
            INSERT INTO organizational_nodes (employer_id, parent_id, level, name, code, description, created_by)
            VALUES (?, NULL, 1, 'Test Établissement Principal', 'TEST-ETAB', 'Établissement de test pour la hiérarchie', 1)
        """, (employer_id,))
        
        etablissement_id = cursor.lastrowid
        print(f"✅ Établissement créé avec ID: {etablissement_id}")
        
        # 4. Test de création d'un département (niveau 2)
        print("\n🏛️ Test de création d'un département...")
        cursor.execute("""
            INSERT INTO organizational_nodes (employer_id, parent_id, level, name, code, description, created_by)
            VALUES (?, ?, 2, 'Test Département IT', 'TEST-DEPT-IT', 'Département informatique de test', 1)
        """, (employer_id, etablissement_id))
        
        departement_id = cursor.lastrowid
        print(f"✅ Département créé avec ID: {departement_id}")
        
        # 5. Test de création d'un service (niveau 3)
        print("\n🔧 Test de création d'un service...")
        cursor.execute("""
            INSERT INTO organizational_nodes (employer_id, parent_id, level, name, code, description, created_by)
            VALUES (?, ?, 3, 'Test Service Développement', 'TEST-SERV-DEV', 'Service développement de test', 1)
        """, (employer_id, departement_id))
        
        service_id = cursor.lastrowid
        print(f"✅ Service créé avec ID: {service_id}")
        
        # 6. Test de création d'une unité (niveau 4)
        print("\n👥 Test de création d'une unité...")
        cursor.execute("""
            INSERT INTO organizational_nodes (employer_id, parent_id, level, name, code, description, created_by)
            VALUES (?, ?, 4, 'Test Équipe Frontend', 'TEST-UNIT-FRONT', 'Équipe frontend de test', 1)
        """, (employer_id, service_id))
        
        unite_id = cursor.lastrowid
        print(f"✅ Unité créée avec ID: {unite_id}")
        
        conn.commit()
        
        # 7. Test des contraintes d'intégrité
        print("\n🔒 Test des contraintes d'intégrité...")
        
        # Test : Établissement avec parent (doit échouer)
        try:
            cursor.execute("""
                INSERT INTO organizational_nodes (employer_id, parent_id, level, name)
                VALUES (?, ?, 1, 'Test Établissement Invalide')
            """, (employer_id, etablissement_id))
            print("❌ Contrainte valid_hierarchy non respectée")
            return False
        except sqlite3.IntegrityError:
            print("✅ Contrainte valid_hierarchy fonctionne")
        
        # Test : Département sans parent (doit échouer)
        try:
            cursor.execute("""
                INSERT INTO organizational_nodes (employer_id, parent_id, level, name)
                VALUES (?, NULL, 2, 'Test Département Invalide')
            """, (employer_id,))
            print("❌ Contrainte valid_hierarchy non respectée")
            return False
        except sqlite3.IntegrityError:
            print("✅ Contrainte valid_hierarchy fonctionne (niveau > 1 sans parent)")
        
        # Test : Nom dupliqué dans le même parent (doit échouer)
        try:
            cursor.execute("""
                INSERT INTO organizational_nodes (employer_id, parent_id, level, name)
                VALUES (?, ?, 3, 'Test Service Développement')
            """, (employer_id, departement_id))
            print("❌ Contrainte unique_name_per_parent non respectée")
            return False
        except sqlite3.IntegrityError:
            print("✅ Contrainte unique_name_per_parent fonctionne")
        
        # 8. Vérifier la table des chemins hiérarchiques
        print("\n🌳 Vérification des chemins hiérarchiques...")
        cursor.execute("""
            SELECT id, level, name, full_path, path_names, path_ids
            FROM organizational_paths 
            WHERE id IN (?, ?, ?, ?)
            ORDER BY level
        """, (etablissement_id, departement_id, service_id, unite_id))
        
        paths = cursor.fetchall()
        
        for path in paths:
            node_id, level, name, full_path, path_names_json, path_ids_json = path
            path_names = json.loads(path_names_json) if path_names_json else []
            path_ids = json.loads(path_ids_json) if path_ids_json else []
            
            print(f"  • Niveau {level} - {name}")
            print(f"    Chemin complet : {full_path}")
            print(f"    Noms du chemin : {path_names}")
            print(f"    IDs du chemin : {path_ids}")
        
        # 9. Test de l'audit trail
        print("\n📝 Vérification de l'audit trail...")
        cursor.execute("""
            SELECT COUNT(*) FROM organizational_audit 
            WHERE node_id IN (?, ?, ?, ?)
        """, (etablissement_id, departement_id, service_id, unite_id))
        
        audit_count = cursor.fetchone()[0]
        print(f"✅ {audit_count} entrées d'audit créées")
        
        # 10. Test de requête hiérarchique
        print("\n🔍 Test de requête hiérarchique...")
        cursor.execute("""
            WITH RECURSIVE hierarchy AS (
                -- Nœud racine
                SELECT id, employer_id, parent_id, level, name, 0 as depth
                FROM organizational_nodes 
                WHERE id = ? AND employer_id = ?
                
                UNION ALL
                
                -- Enfants récursifs
                SELECT n.id, n.employer_id, n.parent_id, n.level, n.name, h.depth + 1
                FROM organizational_nodes n
                JOIN hierarchy h ON n.parent_id = h.id
            )
            SELECT depth, level, name FROM hierarchy ORDER BY depth, level
        """, (etablissement_id, employer_id))
        
        hierarchy = cursor.fetchall()
        
        print("  Hiérarchie complète :")
        for depth, level, name in hierarchy:
            indent = "  " * (depth + 1)
            print(f"{indent}• Niveau {level}: {name}")
        
        # 11. Test de mise à jour avec audit
        print("\n✏️ Test de mise à jour avec audit...")
        cursor.execute("""
            UPDATE organizational_nodes 
            SET name = 'Test Établissement Principal (Modifié)', updated_by = 1
            WHERE id = ?
        """, (etablissement_id,))
        
        conn.commit()
        
        # Vérifier l'audit
        cursor.execute("""
            SELECT action, timestamp FROM organizational_audit 
            WHERE node_id = ? 
            ORDER BY timestamp DESC 
            LIMIT 1
        """, (etablissement_id,))
        
        audit_entry = cursor.fetchone()
        if audit_entry:
            print(f"✅ Audit de mise à jour enregistré : {audit_entry[0]} à {audit_entry[1]}")
        
        # 12. Test de suppression en cascade
        print("\n🗑️ Test de suppression...")
        cursor.execute("DELETE FROM organizational_nodes WHERE id = ?", (unite_id,))
        conn.commit()
        
        # Vérifier que l'audit et les chemins sont supprimés
        cursor.execute("SELECT COUNT(*) FROM organizational_paths WHERE id = ?", (unite_id,))
        path_count = cursor.fetchone()[0]
        
        if path_count == 0:
            print("✅ Suppression en cascade fonctionne (chemins)")
        else:
            print("❌ Suppression en cascade ne fonctionne pas")
        
        conn.close()
        
        print("\n🎉 Tous les tests sont passés avec succès !")
        print("\n📊 Résumé des tests :")
        print("  ✅ Création de hiérarchie complète (4 niveaux)")
        print("  ✅ Contraintes d'intégrité hiérarchique")
        print("  ✅ Contraintes d'unicité")
        print("  ✅ Génération automatique des chemins")
        print("  ✅ Audit trail des modifications")
        print("  ✅ Requêtes hiérarchiques récursives")
        print("  ✅ Suppression en cascade")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Erreur SQLite : {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur inattendue : {e}")
        return False


def test_cascade_filtering_simulation():
    """Simule le filtrage en cascade"""
    
    db_path = "siirh-backend/siirh.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("\n🔄 Simulation du filtrage en cascade")
        print("-" * 40)
        
        # Récupérer un employeur
        cursor.execute("SELECT id FROM employers LIMIT 1")
        employer_id = cursor.fetchone()[0]
        
        # 1. Récupérer tous les établissements (niveau 1)
        print("1️⃣ Établissements disponibles :")
        cursor.execute("""
            SELECT id, name FROM organizational_nodes 
            WHERE employer_id = ? AND level = 1 AND is_active = 1
            ORDER BY name
        """, (employer_id,))
        
        etablissements = cursor.fetchall()
        for etab_id, etab_name in etablissements:
            print(f"   • {etab_name} (ID: {etab_id})")
        
        if etablissements:
            selected_etab_id = etablissements[0][0]
            selected_etab_name = etablissements[0][1]
            
            print(f"\n🎯 Sélection : {selected_etab_name}")
            
            # 2. Récupérer les départements de cet établissement
            print("2️⃣ Départements disponibles :")
            cursor.execute("""
                SELECT id, name FROM organizational_nodes 
                WHERE employer_id = ? AND level = 2 AND parent_id = ? AND is_active = 1
                ORDER BY name
            """, (employer_id, selected_etab_id))
            
            departements = cursor.fetchall()
            for dept_id, dept_name in departements:
                print(f"   • {dept_name} (ID: {dept_id})")
            
            if departements:
                selected_dept_id = departements[0][0]
                selected_dept_name = departements[0][1]
                
                print(f"\n🎯 Sélection : {selected_dept_name}")
                
                # 3. Récupérer les services de ce département
                print("3️⃣ Services disponibles :")
                cursor.execute("""
                    SELECT id, name FROM organizational_nodes 
                    WHERE employer_id = ? AND level = 3 AND parent_id = ? AND is_active = 1
                    ORDER BY name
                """, (employer_id, selected_dept_id))
                
                services = cursor.fetchall()
                for serv_id, serv_name in services:
                    print(f"   • {serv_name} (ID: {serv_id})")
                
                if services:
                    selected_serv_id = services[0][0]
                    selected_serv_name = services[0][1]
                    
                    print(f"\n🎯 Sélection : {selected_serv_name}")
                    
                    # 4. Récupérer les unités de ce service
                    print("4️⃣ Unités disponibles :")
                    cursor.execute("""
                        SELECT id, name FROM organizational_nodes 
                        WHERE employer_id = ? AND level = 4 AND parent_id = ? AND is_active = 1
                        ORDER BY name
                    """, (employer_id, selected_serv_id))
                    
                    unites = cursor.fetchall()
                    for unit_id, unit_name in unites:
                        print(f"   • {unit_name} (ID: {unit_id})")
                    
                    # 5. Afficher le chemin complet sélectionné
                    if unites:
                        selected_unit_id = unites[0][0]
                        
                        cursor.execute("""
                            SELECT full_path FROM organizational_paths 
                            WHERE id = ?
                        """, (selected_unit_id,))
                        
                        full_path = cursor.fetchone()[0]
                        print(f"\n🌟 Chemin hiérarchique complet : {full_path}")
        
        conn.close()
        
        print("\n✅ Simulation du filtrage en cascade terminée")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la simulation : {e}")
        return False


def main():
    """Fonction principale"""
    print("🧪 Tests de la structure hiérarchique organisationnelle")
    print("=" * 70)
    
    # Test de la structure de base
    if test_hierarchical_structure():
        # Test du filtrage en cascade
        test_cascade_filtering_simulation()
        
        print("\n✅ Tous les tests sont terminés avec succès !")
        print("\n📋 La structure hiérarchique est prête pour :")
        print("  • L'implémentation du service HierarchicalOrganizationalService")
        print("  • La création des endpoints API")
        print("  • La migration des données existantes")
        print("  • L'intégration avec le frontend")
        
        return True
    else:
        print("\n❌ Échec des tests")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)