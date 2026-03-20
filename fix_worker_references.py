#!/usr/bin/env python3
"""
Script pour corriger toutes les références à des IDs de travailleurs inexistants dans le frontend.
"""

import os
import re

def fix_worker_references():
    """Corrige les références à des IDs de travailleurs inexistants"""
    
    # IDs existants dans la base de données
    existing_ids = [2007, 2022, 2032, 2042]
    default_id = 2022  # ID par défaut à utiliser
    
    fixes_made = []
    
    # Fichiers à vérifier et corriger
    files_to_check = [
        "siirh-frontend/src/pages/HeuresSupplementairesPageHS.tsx",
        "siirh-frontend/src/pages/Absences.tsx",
        "siirh-frontend/src/pages/LeavePermissionManagement.tsx",
        "siirh-frontend/src/components/PrimesManagerModal.tsx"
    ]
    
    for file_path in files_to_check:
        if not os.path.exists(file_path):
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Pattern pour useState avec des IDs de travailleurs
            # Remplacer useState<number>(ID_INEXISTANT) par useState<number>(ID_EXISTANT)
            patterns_to_fix = [
                (r'useState<number>\(2\)', f'useState<number>({default_id})'),
                (r'useState<number>\(40\)', f'useState<number>({default_id})'),  # Si 40 était un ID de travailleur
                (r'worker_id:\s*2[^0-9]', f'worker_id: {default_id}'),
                (r'workerIdHS.*=.*2[^0-9]', f'workerIdHS = {default_id}'),
            ]
            
            for pattern, replacement in patterns_to_fix:
                if re.search(pattern, content):
                    content = re.sub(pattern, replacement, content)
                    fixes_made.append(f"Fixed pattern '{pattern}' in {file_path}")
            
            # Sauvegarder si des changements ont été faits
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ Updated {file_path}")
            else:
                print(f"✓ No changes needed in {file_path}")
                
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
    
    return fixes_made

def main():
    print("🔧 Fixing worker ID references...")
    print("=" * 50)
    
    fixes = fix_worker_references()
    
    if fixes:
        print(f"\n✅ Made {len(fixes)} fixes:")
        for fix in fixes:
            print(f"  - {fix}")
        print("\n🔄 Please restart the frontend to clear any cached values:")
        print("   1. Stop the frontend (Ctrl+C)")
        print("   2. Clear browser cache (F12 > Application > Storage > Clear)")
        print("   3. Restart with 'npm run dev'")
    else:
        print("\n✅ No fixes needed - all references are correct!")
        print("\n💡 If you're still seeing 404 errors:")
        print("   1. Clear browser cache (F12 > Application > Storage > Clear)")
        print("   2. Hard refresh the page (Ctrl+Shift+R)")
        print("   3. Check browser console for any remaining errors")

if __name__ == "__main__":
    main()