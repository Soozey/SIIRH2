#!/usr/bin/env python3
"""
Monitoring continu pour capturer l'erreur 500 en temps réel
"""

import requests
import time
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def monitor_continuously():
    """Monitoring continu des endpoints susceptibles de causer l'erreur 500"""
    
    print("🔄 MONITORING CONTINU DE L'ERREUR 500")
    print("=" * 50)
    print("Appuyez sur Ctrl+C pour arrêter")
    print(f"Démarré à: {datetime.now().strftime('%H:%M:%S')}")
    
    # Endpoints à surveiller en continu
    endpoints_to_monitor = [
        "/employers",
        "/organizational-structure/1/tree",
        "/organizational-structure/2/tree", 
        "/workers",
        "/organizational-structure/1/validate",
    ]
    
    error_count = 0
    check_count = 0
    
    try:
        while True:
            check_count += 1
            current_time = datetime.now().strftime('%H:%M:%S')
            
            print(f"\n[{current_time}] Check #{check_count}")
            
            for endpoint in endpoints_to_monitor:
                try:
                    response = requests.get(f"{BASE_URL}{endpoint}", timeout=3)
                    
                    if response.status_code == 500:
                        error_count += 1
                        print(f"🚨 ERREUR 500 CAPTURÉE!")
                        print(f"   Endpoint: {endpoint}")
                        print(f"   Time: {current_time}")
                        print(f"   Response: {response.text[:300]}")
                        print(f"   Headers: {dict(response.headers)}")
                        
                        # Sauvegarder l'erreur
                        error_data = {
                            'timestamp': current_time,
                            'endpoint': endpoint,
                            'status_code': response.status_code,
                            'response_text': response.text,
                            'headers': dict(response.headers)
                        }
                        
                        with open('error_500_captured.json', 'w') as f:
                            json.dump(error_data, f, indent=2)
                        
                        print(f"   ✅ Erreur sauvegardée dans error_500_captured.json")
                        
                    elif response.status_code >= 400:
                        print(f"   ⚠️  {endpoint}: {response.status_code}")
                    else:
                        print(f"   ✅ {endpoint}: {response.status_code}")
                        
                except requests.exceptions.Timeout:
                    print(f"   ⏱️  {endpoint}: TIMEOUT")
                except requests.exceptions.ConnectionError:
                    print(f"   🔌 {endpoint}: CONNECTION ERROR")
                except Exception as e:
                    print(f"   ❌ {endpoint}: {e}")
            
            # Attendre 5 secondes avant le prochain check
            time.sleep(5)
            
    except KeyboardInterrupt:
        print(f"\n\n📊 RÉSUMÉ DU MONITORING")
        print(f"Durée: {check_count * 5} secondes")
        print(f"Checks effectués: {check_count}")
        print(f"Erreurs 500 capturées: {error_count}")
        
        if error_count == 0:
            print("\n💡 RECOMMANDATIONS:")
            print("1. L'erreur 500 pourrait être liée à une action spécifique")
            print("2. Essayez de naviguer dans l'application pendant le monitoring")
            print("3. Vérifiez si l'erreur apparaît lors d'actions particulières:")
            print("   - Changement d'employeur")
            print("   - Ouverture de modals")
            print("   - Création/modification de structures")
            print("   - Chargement de pages spécifiques")

if __name__ == "__main__":
    monitor_continuously()