"""
Script de vérification rapide - Frontend prêt pour test
Vérifie que le frontend et le backend sont accessibles
"""
import requests
import sys
from datetime import datetime

def check_service(url, name):
    """Vérifie si un service est accessible"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"✅ {name} est accessible ({url})")
            return True
        else:
            print(f"⚠️  {name} répond mais avec code {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ {name} n'est pas accessible ({url})")
        print(f"   → Démarrer avec: cd siirh-{'frontend' if 'localhost:5173' in url else 'backend'} && {'npm run dev' if 'localhost:5173' in url else 'python start_server.py'}")
        return False
    except Exception as e:
        print(f"❌ Erreur lors de la vérification de {name}: {e}")
        return False

def main():
    print("=" * 70)
    print("🔍 VÉRIFICATION DE L'ENVIRONNEMENT DE TEST")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Vérifier le backend
    backend_ok = check_service("http://127.0.0.1:8000/docs", "Backend API")
    
    # Vérifier le frontend
    frontend_ok = check_service("http://localhost:5173", "Frontend")
    
    print("\n" + "=" * 70)
    
    if backend_ok and frontend_ok:
        print("✅ ENVIRONNEMENT PRÊT POUR LE TEST!")
        print("\n📋 PROCHAINES ÉTAPES:")
        print("   1. Ouvrir http://localhost:5173/payroll dans le navigateur")
        print("   2. Appuyer sur F12 → Console")
        print("   3. Filtrer les logs: [MODAL DEBUG]")
        print("   4. Suivre le scénario dans FIX_ISOLATION_EMPLOYEURS.md")
        print("\n⏱️  Temps estimé: 5 minutes")
        return 0
    else:
        print("⚠️  ENVIRONNEMENT NON PRÊT")
        print("\n🔧 ACTIONS REQUISES:")
        if not backend_ok:
            print("   1. Démarrer le backend:")
            print("      cd siirh-backend")
            print("      python start_server.py")
        if not frontend_ok:
            print("   2. Démarrer le frontend:")
            print("      cd siirh-frontend")
            print("      npm run dev")
        print("\n   3. Relancer ce script pour vérifier")
        return 1

if __name__ == "__main__":
    sys.exit(main())
