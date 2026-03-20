"""
Test si le frontend est accessible
"""
import requests

def test_frontend():
    print("Test du frontend...")
    
    ports = [5173, 5174, 5175]
    
    for port in ports:
        try:
            url = f"http://localhost:{port}"
            print(f"\nTest de {url}...")
            response = requests.get(url, timeout=2)
            print(f"✅ Frontend accessible sur le port {port}")
            print(f"   Status: {response.status_code}")
            return True
        except requests.exceptions.ConnectionError:
            print(f"❌ Port {port} non accessible")
        except requests.exceptions.Timeout:
            print(f"⚠️ Port {port} timeout")
        except Exception as e:
            print(f"❌ Port {port} erreur: {e}")
    
    print("\n❌ Frontend non accessible sur aucun port")
    return False

if __name__ == "__main__":
    test_frontend()
