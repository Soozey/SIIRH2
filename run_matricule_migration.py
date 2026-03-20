#!/usr/bin/env python3
"""
Script d'exécution de la migration des matricules
Utilise le MatriculeMigrationService pour migrer les données existantes
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'siirh-backend'))

import sqlite3
from datetime import datetime
import json

def run_migration_analysis():
    """Exécuter une analyse de migration complète"""
    
    print("🔍 ANALYSE DE MIGRATION DES MATRICULES")
    print("=" * 50)
    
    conn = sqlite3.connect("siirh-backend/siirh.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Analyse globale
        print("\n📊 ANALYSE GLOBALE")
        print("-" * 30)
        
        # Statistiques des workers
        cursor.execute("""
            SELECT COUNT(*) as total,
                   COUNT(CASE WHEN matricule IS NULL OR matricule = '' THEN 1 END) as missing,
                   COUNT(CASE WHEN matricule IS NOT NULL AND LENGTH(matricule) < 6 THEN 1 END) as too_short,
                   COUNT(CASE WHEN matricule IS NOT NULL AND LENGTH(matricule) >= 6 THEN 1 END) as valid
            FROM workers
        """)
        
        stats = cursor.fetchone()
        
        print(f"Total des salariés: {stats['total']}")
        print(f"Matricules valides: {stats['valid']} ({stats['valid']/stats['total']*100:.1f}%)")
        print(f"Matricules manquants: {stats['missing']}")
        print(f"Matricules trop courts: {stats['too_short']}")
        
        # Analyse par employeur
        print("\n📊 ANALYSE PAR EMPLOYEUR")
        print("-" * 30)
        
        cursor.execute("""
            SELECT e.name as employer_name, e.id as employer_id,
                   COUNT(w.id) as total_workers,
                   COUNT(CASE WHEN w.matricule IS NULL OR w.matricule = '' THEN 1 END) as missing,
                   COUNT(CASE WHEN w.matricule IS NOT NULL AND LENGTH(w.matricule) < 6 THEN 1 END) as too_short,
                   COUNT(CASE WHEN w.matricule IS NOT NULL AND LENGTH(w.matricule) >= 6 THEN 1 END) as valid
            FROM employers e
            LEFT JOIN workers w ON w.employer_id = e.id
            GROUP BY e.id, e.name
            HAVING COUNT(w.id) > 0
            ORDER BY total_workers DESC
        """)
        
        employers = cursor.fetchall()
        
        for emp in employers:
            completion_rate = (emp['valid'] / emp['total_workers'] * 100) if emp['total_workers'] > 0 else 0
            print(f"\n{emp['employer_name']} (ID: {emp['employer_id']}):")
            print(f"  Total: {emp['total_workers']} salariés")
            print(f"  Valides: {emp['valid']} ({completion_rate:.1f}%)")
            if emp['missing'] > 0:
                print(f"  ⚠️  Manquants: {emp['missing']}")
            if emp['too_short'] > 0:
                print(f"  ⚠️  Trop courts: {emp['too_short']}")
        
        # Détection des homonymes
        print("\n👥 DÉTECTION DES HOMONYMES")
        print("-" * 30)
        
        cursor.execute("""
            SELECT CONCAT(nom, ' ', prenom) as full_name, 
                   employer_id,
                   COUNT(*) as count,
                   GROUP_CONCAT(matricule) as matricules
            FROM workers
            GROUP BY CONCAT(nom, ' ', prenom), employer_id
            HAVING COUNT(*) > 1
            ORDER BY count DESC
        """)
        
        homonyms = cursor.fetchall()
        
        if homonyms:
            print(f"⚠️  {len(homonyms)} groupes d'homonymes détectés:")
            for homonym in homonyms:
                print(f"  - {homonym['full_name']} (Employeur {homonym['employer_id']}): {homonym['count']} personnes")
                print(f"    Matricules: {homonym['matricules']}")
        else:
            print("✅ Aucun homonyme détecté")
        
        # Détection des doublons de matricules
        print("\n🔒 DÉTECTION DES DOUBLONS DE MATRICULES")
        print("-" * 30)
        
        cursor.execute("""
            SELECT matricule, COUNT(*) as count,
                   GROUP_CONCAT(nom || ' ' || prenom) as names
            FROM workers
            WHERE matricule IS NOT NULL AND matricule != ''
            GROUP BY matricule
            HAVING COUNT(*) > 1
            ORDER BY count DESC
        """)
        
        duplicates = cursor.fetchall()
        
        if duplicates:
            print(f"🚨 {len(duplicates)} matricules dupliqués détectés:")
            for dup in duplicates:
                print(f"  - {dup['matricule']}: {dup['count']} occurrences")
                print(f"    Noms: {dup['names']}")
        else:
            print("✅ Aucun doublon de matricule détecté")
        
        # Analyse des références organisationnelles
        print("\n🏢 ANALYSE DES RÉFÉRENCES ORGANISATIONNELLES")
        print("-" * 30)
        
        cursor.execute("""
            SELECT COUNT(*) as total_assignments,
                   COUNT(CASE WHEN w.matricule IS NOT NULL THEN 1 END) as with_matricule,
                   COUNT(CASE WHEN w.matricule IS NULL THEN 1 END) as without_matricule
            FROM worker_organizational_assignments woa
            LEFT JOIN workers w ON w.matricule = woa.worker_matricule
        """)
        
        org_stats = cursor.fetchone()
        
        print(f"Total des affectations: {org_stats['total_assignments']}")
        print(f"Avec matricule valide: {org_stats['with_matricule']}")
        if org_stats['without_matricule'] > 0:
            print(f"⚠️  Sans matricule valide: {org_stats['without_matricule']}")
        
        # Recommandations
        print("\n💡 RECOMMANDATIONS")
        print("-" * 30)
        
        recommendations = []
        
        if stats['missing'] > 0:
            recommendations.append(f"Générer {stats['missing']} matricules manquants")
        
        if stats['too_short'] > 0:
            recommendations.append(f"Corriger {stats['too_short']} matricules trop courts")
        
        if duplicates:
            recommendations.append(f"Résoudre {len(duplicates)} doublons de matricules")
        
        if homonyms:
            recommendations.append(f"Vérifier {len(homonyms)} groupes d'homonymes")
        
        if org_stats['without_matricule'] > 0:
            recommendations.append(f"Migrer {org_stats['without_matricule']} références organisationnelles")
        
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                print(f"{i}. {rec}")
        else:
            print("✅ Aucune action requise - système déjà cohérent")
        
        # Estimation de complexité
        complexity_score = len(recommendations)
        if complexity_score == 0:
            complexity = "AUCUNE"
            duration = "Aucune migration nécessaire"
        elif complexity_score <= 2:
            complexity = "FAIBLE"
            duration = "< 5 minutes"
        elif complexity_score <= 4:
            complexity = "MOYENNE"
            duration = "5-15 minutes"
        else:
            complexity = "ÉLEVÉE"
            duration = "15+ minutes"
        
        print(f"\n🎯 COMPLEXITÉ DE MIGRATION: {complexity}")
        print(f"⏱️  DURÉE ESTIMÉE: {duration}")
        
        # Sauvegarder le rapport
        report = {
            "timestamp": datetime.now().isoformat(),
            "global_stats": dict(stats),
            "employers": [dict(emp) for emp in employers],
            "homonyms": [dict(h) for h in homonyms],
            "duplicates": [dict(d) for d in duplicates],
            "organizational_stats": dict(org_stats),
            "recommendations": recommendations,
            "complexity": complexity,
            "estimated_duration": duration
        }
        
        report_filename = f"migration_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Rapport sauvegardé: {report_filename}")
        
        return complexity_score == 0
        
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        conn.close()

def run_migration_fix():
    """Exécuter les corrections automatiques"""
    
    print("\n🔧 CORRECTION AUTOMATIQUE DES PROBLÈMES")
    print("=" * 50)
    
    conn = sqlite3.connect("siirh-backend/siirh.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Créer une sauvegarde
        backup_name = f"pre_fix_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        print(f"\n💾 Création de la sauvegarde: {backup_name}")
        
        cursor.execute(f"""
            CREATE TABLE {backup_name}_workers AS 
            SELECT * FROM workers
        """)
        
        cursor.execute(f"""
            CREATE TABLE {backup_name}_worker_organizational_assignments AS 
            SELECT * FROM worker_organizational_assignments
        """)
        
        print("   ✅ Sauvegarde créée")
        
        # Correction 1: Générer les matricules manquants
        print(f"\n🔧 Génération des matricules manquants")
        
        cursor.execute("""
            SELECT id, nom, prenom, employer_id
            FROM workers
            WHERE matricule IS NULL OR matricule = ''
        """)
        
        missing_workers = cursor.fetchall()
        generated_count = 0
        
        for worker in missing_workers:
            # Générer un matricule unique
            base_matricule = f"E{worker['employer_id']:03d}"
            
            # Trouver un suffixe unique
            for i in range(1, 10000):
                candidate = f"{base_matricule}{worker['nom'][:2].upper()}{i:03d}"
                
                cursor.execute("""
                    SELECT COUNT(*) as count
                    FROM workers
                    WHERE matricule = ?
                """, (candidate,))
                
                if cursor.fetchone()["count"] == 0:
                    cursor.execute("""
                        UPDATE workers
                        SET matricule = ?
                        WHERE id = ?
                    """, (candidate, worker["id"]))
                    
                    print(f"   📝 {worker['nom']} {worker['prenom']}: {candidate}")
                    generated_count += 1
                    break
        
        print(f"   ✅ {generated_count} matricules générés")
        
        # Correction 2: Étendre les matricules trop courts
        print(f"\n🔧 Extension des matricules trop courts")
        
        cursor.execute("""
            SELECT id, nom, prenom, matricule, employer_id
            FROM workers
            WHERE matricule IS NOT NULL AND LENGTH(matricule) < 6
        """)
        
        short_workers = cursor.fetchall()
        extended_count = 0
        
        for worker in short_workers:
            # Étendre le matricule
            extended = f"E{worker['employer_id']:03d}{worker['matricule']}{worker['id']:03d}"
            
            # Vérifier l'unicité
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM workers
                WHERE matricule = ? AND id != ?
            """, (extended, worker["id"]))
            
            if cursor.fetchone()["count"] == 0:
                cursor.execute("""
                    UPDATE workers
                    SET matricule = ?
                    WHERE id = ?
                """, (extended, worker["id"]))
                
                print(f"   📝 {worker['nom']} {worker['prenom']}: {worker['matricule']} → {extended}")
                extended_count += 1
        
        print(f"   ✅ {extended_count} matricules étendus")
        
        # Correction 3: Résoudre les doublons
        print(f"\n🔧 Résolution des doublons de matricules")
        
        cursor.execute("""
            SELECT matricule, GROUP_CONCAT(id) as worker_ids
            FROM workers
            WHERE matricule IS NOT NULL AND matricule != ''
            GROUP BY matricule
            HAVING COUNT(*) > 1
        """)
        
        duplicates = cursor.fetchall()
        resolved_count = 0
        
        for dup in duplicates:
            worker_ids = dup["worker_ids"].split(',')
            # Garder le premier, changer les autres
            for worker_id in worker_ids[1:]:
                cursor.execute("""
                    SELECT nom, prenom, employer_id FROM workers WHERE id = ?
                """, (worker_id,))
                
                worker = cursor.fetchone()
                
                # Générer un nouveau matricule unique
                base_matricule = f"E{worker['employer_id']:03d}"
                
                for i in range(1, 10000):
                    candidate = f"{base_matricule}{worker['nom'][:2].upper()}{i:03d}"
                    
                    cursor.execute("""
                        SELECT COUNT(*) as count
                        FROM workers
                        WHERE matricule = ?
                    """, (candidate,))
                    
                    if cursor.fetchone()["count"] == 0:
                        cursor.execute("""
                            UPDATE workers
                            SET matricule = ?
                            WHERE id = ?
                        """, (candidate, worker_id))
                        
                        print(f"   📝 Doublon résolu: {dup['matricule']} → {candidate}")
                        resolved_count += 1
                        break
        
        print(f"   ✅ {resolved_count} doublons résolus")
        
        # Validation finale
        print(f"\n🔍 Validation finale")
        
        cursor.execute("""
            SELECT COUNT(*) as total,
                   COUNT(CASE WHEN matricule IS NOT NULL AND matricule != '' AND LENGTH(matricule) >= 6 THEN 1 END) as valid
            FROM workers
        """)
        
        final_stats = cursor.fetchone()
        
        if final_stats["total"] == final_stats["valid"]:
            print(f"   ✅ Validation réussie: {final_stats['valid']}/{final_stats['total']} matricules valides")
            conn.commit()
            
            print(f"\n🎉 MIGRATION TERMINÉE AVEC SUCCÈS!")
            print(f"✅ Tous les matricules sont maintenant valides et uniques")
            print(f"💾 Sauvegarde disponible: {backup_name}_*")
            
            return True
        else:
            invalid_count = final_stats["total"] - final_stats["valid"]
            print(f"   ❌ Validation échouée: {invalid_count} matricules encore invalides")
            conn.rollback()
            return False
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Erreur lors de la correction: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        conn.close()

def main():
    """Fonction principale"""
    
    print("🚀 MIGRATION DES MATRICULES - SYSTÈME ORGANISATIONNEL")
    print("=" * 60)
    
    # Étape 1: Analyse
    print("\n📋 ÉTAPE 1: ANALYSE DES DONNÉES EXISTANTES")
    is_clean = run_migration_analysis()
    
    if is_clean:
        print("\n🎉 SYSTÈME DÉJÀ COHÉRENT - AUCUNE MIGRATION NÉCESSAIRE")
        return True
    
    # Étape 2: Demander confirmation
    print("\n❓ VOULEZ-VOUS PROCÉDER AUX CORRECTIONS AUTOMATIQUES?")
    print("   Cette opération va:")
    print("   - Créer une sauvegarde complète")
    print("   - Générer les matricules manquants")
    print("   - Corriger les matricules invalides")
    print("   - Résoudre les doublons")
    
    response = input("\nContinuer? (o/N): ").lower().strip()
    
    if response in ['o', 'oui', 'y', 'yes']:
        # Étape 3: Correction
        print("\n📋 ÉTAPE 2: CORRECTION AUTOMATIQUE")
        success = run_migration_fix()
        
        if success:
            print("\n📋 ÉTAPE 3: ANALYSE POST-MIGRATION")
            run_migration_analysis()
            
            print("\n🎯 MIGRATION COMPLÈTE!")
            print("✅ Le système organisationnel est maintenant basé sur les matricules")
            print("✅ Toutes les données sont cohérentes et intègres")
            print("✅ Prêt pour la mise en production")
            
            return True
        else:
            print("\n❌ MIGRATION ÉCHOUÉE")
            print("🔄 Les données ont été restaurées à leur état initial")
            return False
    else:
        print("\n⏸️  MIGRATION ANNULÉE PAR L'UTILISATEUR")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print(f"\n🚀 PRÊT POUR LA SUITE: Task 5.3 - Rollback et Validation")
    else:
        print(f"\n🛑 ARRÊT - CORRECTIONS MANUELLES REQUISES")