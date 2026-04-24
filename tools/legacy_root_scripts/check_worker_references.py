#!/usr/bin/env python3
"""
Script pour vérifier que tous les IDs de travailleurs référencés dans le frontend existent dans la base de données.
"""

import sys
import os
import re
import requests

# Ajouter le chemin du backend
sys.path.append('./siirh-backend')

def get_existing_worker_ids():
    """Récupère les IDs des travailleurs existants depuis la base de données"""
    try:
        from siirh_backend.app.config.config import get_db
        from siirh_backend.app.models import Worker
        
        db = next(get_db())
        workers = db.query(Worker).all()
        worker_ids = [worker.id for worker in workers]
        db.close()
        return worker_ids
    except Exception as e:
        print(f"Erreur lors de la récupération des IDs depuis la DB: {e}")
        # Fallback: utiliser l'API
        try:
            response = requests.get("http://localhost:8000/workers")
            if response.status_code == 200:
                workers = response.json()
                return [worker['id'] for worker in workers]
        except Exception as api_error:
            print(f"Erreur API: {api_error}")
        return []

def scan_frontend_files():
    """Scanne les fichiers frontend pour trouver des références à des IDs de travailleurs"""
    frontend_dir = "./siirh-frontend/src"
    hardcoded_ids = []
    
    for root, dirs, files in os.walk(frontend_dir):
        for file in files:
            if file.endswith(('.tsx', '.ts')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        # Chercher des patterns comme useState<number>(ID)
                        patterns = [
                            r'useState<number>\((\d+)\)',
                            r'workerId.*=.*(\d+)',
                            r'worker_id.*=.*(\d+)',
                            r'/workers/(\d+)',
                        ]
                        
                        for pattern in patterns:
                            matches = re.findall(pattern, content)
                            for match in matches:
                                worker_id = int(match)
                                hardcoded_ids.append({
                                    'file': file_path,
                                    'id': worker_id,
                                    'pattern': pattern
                                })
                except Exception as e:
                    print(f"Erreur lors de la lecture de {file_path}: {e}")
    
    return hardcoded_ids

def main():
    print("🔍 Vérification des références aux IDs de travailleurs...")
    print("=" * 60)
    
    # Récupérer les IDs existants
    existing_ids = get_existing_worker_ids()
    print(f"📊 IDs de travailleurs existants: {existing_ids}")
    
    # Scanner les fichiers frontend
    hardcoded_refs = scan_frontend_files()
    
    if not hardcoded_refs:
        print("✅ Aucune référence codée en dur trouvée dans le frontend")
        return
    
    print(f"\n🔍 Références trouvées ({len(hardcoded_refs)}):")
    
    issues_found = False
    for ref in hardcoded_refs:
        status = "✅" if ref['id'] in existing_ids else "❌"
        if ref['id'] not in existing_ids:
            issues_found = True
        
        print(f"  {status} ID {ref['id']} dans {ref['file']}")
    
    if issues_found:
        print("\n⚠️  Des IDs de travailleurs inexistants ont été trouvés!")
        print("   Cela peut causer des erreurs 404 dans la console.")
        print("   Veuillez corriger ces références ou créer les travailleurs manquants.")
    else:
        print("\n✅ Toutes les références pointent vers des travailleurs existants!")

if __name__ == "__main__":
    main()