"""
Vérification finale de la correction du modal optimisé
"""
import os
import json
from datetime import datetime

def check_file_exists(filepath):
    """Vérifier qu'un fichier existe"""
    return os.path.exists(filepath)

def check_file_content(filepath, search_text):
    """Vérifier qu'un fichier contient un texte spécifique"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            return search_text in content
    except:
        return False

def main():
    print("=" * 80)
    print("VÉRIFICATION FINALE - MODAL OPTIMISÉ")
    print("=" * 80)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    results = {
        "files_checked": 0,
        "files_ok": 0,
        "files_missing": [],
        "content_checks": 0,
        "content_ok": 0,
        "content_issues": []
    }
    
    # 1. Vérifier les fichiers principaux
    print("1️⃣ Vérification des fichiers principaux")
    print()
    
    files_to_check = [
        ("siirh-frontend/src/components/OrganizationalFilterModalOptimized.tsx", "Composant modal optimisé"),
        ("siirh-frontend/src/pages/PayrollRun.tsx", "Page PayrollRun"),
    ]
    
    for filepath, description in files_to_check:
        results["files_checked"] += 1
        if check_file_exists(filepath):
            print(f"   ✅ {description}")
            print(f"      Fichier: {filepath}")
            results["files_ok"] += 1
        else:
            print(f"   ❌ {description} - MANQUANT")
            print(f"      Fichier: {filepath}")
            results["files_missing"].append(filepath)
    
    print()
    
    # 2. Vérifier la correction de l'erreur de syntaxe
    print("2️⃣ Vérification de la correction de l'erreur de syntaxe")
    print()
    
    modal_file = "siirh-frontend/src/components/OrganizationalFilterModalOptimized.tsx"
    
    # Vérifier que la correction est présente
    results["content_checks"] += 1
    if check_file_content(modal_file, "activeFiltersCount > 1 ? 's' : ''"):
        print("   ✅ Correction de la syntaxe appliquée")
        print("      Code: activeFiltersCount > 1 ? 's' : ''")
        results["content_ok"] += 1
    else:
        print("   ❌ Correction de la syntaxe NON trouvée")
        results["content_issues"].append("Syntaxe non corrigée dans le modal")
    
    # Vérifier que l'ancienne erreur n'est plus présente
    results["content_checks"] += 1
    if not check_file_content(modal_file, "activeFiltersCount > 1 ? s' : ''"):
        print("   ✅ Ancienne erreur supprimée")
        print("      Ancienne erreur: activeFiltersCount > 1 ? s' : ''")
        results["content_ok"] += 1
    else:
        print("   ❌ Ancienne erreur TOUJOURS présente")
        results["content_issues"].append("Ancienne erreur toujours dans le code")
    
    print()
    
    # 3. Vérifier la configuration React Query
    print("3️⃣ Vérification de la configuration React Query")
    print()
    
    react_query_checks = [
        ("enabled: isOpen", "Query employeurs avec enabled"),
        ("staleTime: 5 * 60 * 1000", "Cache de 5 minutes"),
        ("retry: false", "Pas de retry automatique"),
        ("enabled: isOpen && !!selectedEmployerId && useFilters", "Query établissements conditionnelle"),
    ]
    
    for search_text, description in react_query_checks:
        results["content_checks"] += 1
        if check_file_content(modal_file, search_text):
            print(f"   ✅ {description}")
            results["content_ok"] += 1
        else:
            print(f"   ⚠️  {description} - NON trouvé")
            results["content_issues"].append(description)
    
    print()
    
    # 4. Vérifier l'intégration dans PayrollRun
    print("4️⃣ Vérification de l'intégration dans PayrollRun")
    print()
    
    payroll_file = "siirh-frontend/src/pages/PayrollRun.tsx"
    
    integration_checks = [
        ("OrganizationalFilterModalOptimized", "Import du modal optimisé"),
        ("isBulkPrintModalOpen", "État du modal d'impression"),
        ("isJournalPreviewModalOpen", "État du modal d'aperçu"),
        ("isJournalExportModalOpen", "État du modal d'export"),
        ("handleBulkPrintConfirm", "Callback d'impression"),
        ("handleJournalPreviewConfirm", "Callback d'aperçu"),
        ("handleJournalExportConfirm", "Callback d'export"),
    ]
    
    for search_text, description in integration_checks:
        results["content_checks"] += 1
        if check_file_content(payroll_file, search_text):
            print(f"   ✅ {description}")
            results["content_ok"] += 1
        else:
            print(f"   ❌ {description} - NON trouvé")
            results["content_issues"].append(description)
    
    print()
    
    # 5. Vérifier les fichiers de documentation
    print("5️⃣ Vérification de la documentation")
    print()
    
    doc_files = [
        ("CORRECTION_ERREUR_500_MODAL_OPTIMISE.md", "Documentation de la correction"),
        ("GUIDE_RAPIDE_TEST_MODAL.md", "Guide de test rapide"),
        ("LIVRAISON_FINALE_MODAL_OPTIMISE.md", "Document de livraison"),
        ("test_modal_frontend_fix.py", "Script de test du modal"),
        ("diagnose_500_error.py", "Script de diagnostic"),
    ]
    
    for filepath, description in doc_files:
        results["files_checked"] += 1
        if check_file_exists(filepath):
            print(f"   ✅ {description}")
            results["files_ok"] += 1
        else:
            print(f"   ⚠️  {description} - MANQUANT")
            results["files_missing"].append(filepath)
    
    print()
    
    # Résumé
    print("=" * 80)
    print("RÉSUMÉ DE LA VÉRIFICATION")
    print("=" * 80)
    print()
    
    print(f"📁 Fichiers vérifiés: {results['files_checked']}")
    print(f"   ✅ OK: {results['files_ok']}")
    if results['files_missing']:
        print(f"   ❌ Manquants: {len(results['files_missing'])}")
        for f in results['files_missing']:
            print(f"      - {f}")
    print()
    
    print(f"📝 Vérifications de contenu: {results['content_checks']}")
    print(f"   ✅ OK: {results['content_ok']}")
    if results['content_issues']:
        print(f"   ⚠️  Problèmes: {len(results['content_issues'])}")
        for issue in results['content_issues']:
            print(f"      - {issue}")
    print()
    
    # Verdict final
    print("=" * 80)
    
    all_files_ok = results['files_ok'] == results['files_checked']
    all_content_ok = results['content_ok'] == results['content_checks']
    
    if all_files_ok and all_content_ok:
        print("✅ VÉRIFICATION RÉUSSIE!")
        print()
        print("Tous les fichiers sont présents et les corrections sont appliquées.")
        print()
        print("🚀 Le modal optimisé est prêt à être testé!")
        print()
        print("Prochaines étapes:")
        print("1. Redémarrer le serveur frontend si nécessaire")
        print("2. Ouvrir http://localhost:5173/payroll")
        print("3. Cliquer sur 'Imprimer tous les bulletins'")
        print("4. Vérifier que le modal s'ouvre sans erreur 500")
        print("5. Tester le filtrage en cascade")
        print()
        print("Pour tester les endpoints backend:")
        print("   python test_modal_frontend_fix.py")
    else:
        print("⚠️  VÉRIFICATION INCOMPLÈTE")
        print()
        if not all_files_ok:
            print(f"❌ {len(results['files_missing'])} fichier(s) manquant(s)")
        if not all_content_ok:
            print(f"⚠️  {len(results['content_issues'])} problème(s) de contenu")
        print()
        print("Vérifier les détails ci-dessus et corriger les problèmes.")
    
    print("=" * 80)
    
    # Sauvegarder le rapport
    report = {
        "date": datetime.now().isoformat(),
        "results": results,
        "verdict": "SUCCESS" if (all_files_ok and all_content_ok) else "INCOMPLETE"
    }
    
    with open("verification_finale_modal_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print()
    print("📊 Rapport sauvegardé: verification_finale_modal_report.json")
    print()
    
    return 0 if (all_files_ok and all_content_ok) else 1

if __name__ == "__main__":
    exit(main())
