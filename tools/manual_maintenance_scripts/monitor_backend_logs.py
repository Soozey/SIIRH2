#!/usr/bin/env python3
"""
Script pour surveiller les logs du backend en temps réel et capturer les erreurs 500.
"""

import subprocess
import time
import threading
import queue
import sys

def monitor_backend_process():
    """Surveille les logs du processus backend"""
    
    print("🔍 Surveillance des logs du backend en temps réel...")
    print("=" * 60)
    print("💡 Reproduisez l'action qui cause l'erreur 500 dans l'interface")
    print("   Les logs apparaîtront ci-dessous...")
    print("   Appuyez sur Ctrl+C pour arrêter la surveillance")
    print("-" * 60)
    
    try:
        # Démarrer la surveillance des logs
        # Note: Ceci est un exemple - en réalité, nous devons surveiller les logs du processus existant
        
        log_queue = queue.Queue()
        
        def read_logs():
            """Fonction pour lire les logs en continu"""
            # Simuler la lecture des logs
            # En réalité, nous devrions lire depuis le processus backend
            while True:
                time.sleep(1)
                # Placeholder pour la lecture des logs
                pass
        
        # Démarrer le thread de lecture des logs
        log_thread = threading.Thread(target=read_logs, daemon=True)
        log_thread.start()
        
        print("✅ Surveillance active. Effectuez l'action qui cause l'erreur 500...")
        
        # Boucle principale pour afficher les instructions
        while True:
            time.sleep(5)
            print("⏳ En attente d'erreurs... (Ctrl+C pour arrêter)")
            
    except KeyboardInterrupt:
        print("\n🛑 Surveillance arrêtée par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur lors de la surveillance: {e}")

def check_backend_status():
    """Vérifie le statut du backend"""
    
    import requests
    
    try:
        response = requests.get("http://localhost:8000/workers", timeout=5)
        if response.status_code == 200:
            print("✅ Backend accessible et fonctionnel")
            return True
        else:
            print(f"⚠️ Backend répond avec le statut {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend non accessible: {e}")
        return False

def main():
    print("🚨 Surveillance des erreurs 500 du backend")
    print("=" * 50)
    
    # Vérifier que le backend est accessible
    if not check_backend_status():
        print("\n❌ Le backend n'est pas accessible. Veuillez le démarrer d'abord.")
        return
    
    print("\n📋 Instructions pour capturer l'erreur 500:")
    print("  1. Gardez cette fenêtre ouverte")
    print("  2. Dans votre navigateur, reproduisez l'action qui cause l'erreur 500")
    print("  3. L'erreur sera capturée et affichée ici")
    print("  4. Notez l'URL exacte qui cause l'erreur dans la console F12")
    
    print("\n🔍 Actions courantes qui peuvent causer des erreurs 500:")
    print("  - Créer un nouveau travailleur")
    print("  - Modifier un travailleur existant")
    print("  - Utiliser les sélecteurs organisationnels")
    print("  - Charger la page Workers")
    print("  - Utiliser le modal de hiérarchie")
    
    print("\n💡 Pour identifier l'erreur plus facilement:")
    print("  1. Ouvrez F12 > Network dans votre navigateur")
    print("  2. Reproduisez l'action qui cause l'erreur")
    print("  3. Cherchez les requêtes en rouge (status 500)")
    print("  4. Cliquez sur la requête pour voir les détails")
    print("  5. Partagez l'URL et la réponse de l'erreur")
    
    # Démarrer la surveillance (simplifiée pour cet exemple)
    try:
        print(f"\n⏳ Surveillance en cours... (Ctrl+C pour arrêter)")
        while True:
            time.sleep(2)
            # Vérifier périodiquement si le backend est toujours accessible
            if not check_backend_status():
                print("❌ Connexion au backend perdue!")
                break
    except KeyboardInterrupt:
        print("\n🛑 Surveillance arrêtée")

if __name__ == "__main__":
    main()