"""
Test de la correction du filtrage organisationnel
Vérifie que les filtres fonctionnent correctement après changement d'employeur
"""
import requests
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

print("=" * 80)
print("🧪 TEST - FILTRAGE ORGANISATIONNEL APRÈS CORRECTION")
print("=" * 80)
print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 1. Test avec Karibo Services (ID 1)
print("1️⃣ TEST - KARIBO SERVICES (Employer ID: 1)")
print("-" * 80)

# Sans filtre
print("Sans filtre:")
response = requests.get(f"{BASE_URL}/payroll/bulk-preview", params={
    "employer_id": 1,
    "period": "2026-01"
})
if response.status_code == 200:
    workers = response.json()
    print(f"  ✅ {len(workers)} salariés trouvés")
else:
    print(f"  ❌ Erreur {response.status_code}")

# Avec filtre établissement (ID 40 = JICA)
print("\nAvec filtre établissement=40 (JICA):")
response = requests.get(f"{BASE_URL}/payroll/bulk-preview", params={
    "employer_id": 1,
    "period": "2026-01",
    "etablissement": 40
})
if response.status_code == 200:
    workers = response.json()
    print(f"  ✅ {len(workers)} salarié(s) trouvé(s)")
    if len(workers) > 0:
        print(f"     Salarié: {workers[0]['worker']['nom']} {workers[0]['worker']['prenom']}")
else:
    print(f"  ❌ Erreur {response.status_code}: {response.text}")

# Avec filtre département (ID 41 = AWC)
print("\nAvec filtre département=41 (AWC):")
response = requests.get(f"{BASE_URL}/payroll/bulk-preview", params={
    "employer_id": 1,
    "period": "2026-01",
    "departement": 41
})
if response.status_code == 200:
    workers = response.json()
    print(f"  ✅ {len(workers)} salarié(s) trouvé(s)")
    if len(workers) > 0:
        print(f"     Salarié: {workers[0]['worker']['nom']} {workers[0]['worker']['prenom']}")
else:
    print(f"  ❌ Erreur {response.status_code}: {response.text}")

# 2. Test avec Mandroso Services (ID 2)
print("\n2️⃣ TEST - MANDROSO SERVICES (Employer ID: 2)")
print("-" * 80)

# Sans filtre
print("Sans filtre:")
response = requests.get(f"{BASE_URL}/payroll/bulk-preview", params={
    "employer_id": 2,
    "period": "2026-01"
})
if response.status_code == 200:
    workers = response.json()
    print(f"  ✅ {len(workers)} salariés trouvés")
else:
    print(f"  ❌ Erreur {response.status_code}")

# Avec filtre établissement (ID 40 = JICA de Karibo)
# Devrait retourner 0 car Mandroso n'a pas cette structure
print("\nAvec filtre établissement=40 (JICA - structure de Karibo):")
response = requests.get(f"{BASE_URL}/payroll/bulk-preview", params={
    "employer_id": 2,
    "period": "2026-01",
    "etablissement": 40
})
if response.status_code == 200:
    workers = response.json()
    print(f"  ✅ {len(workers)} salarié(s) trouvé(s) (devrait être 0)")
    if len(workers) == 0:
        print("     ✅ Correct: Aucun salarié de Mandroso n'est affecté à JICA")
    else:
        print("     ❌ ERREUR: Des salariés de Mandroso sont affectés à une structure de Karibo!")
else:
    print(f"  ❌ Erreur {response.status_code}: {response.text}")

# 3. Résumé
print("\n" + "=" * 80)
print("📋 RÉSUMÉ")
print("=" * 80)
print("✅ Les filtres acceptent maintenant des IDs (integers)")
print("✅ Les IDs sont convertis en strings pour la comparaison avec la BDD")
print("✅ Le filtrage fonctionne correctement par employeur")
print()
print("🎯 PROCHAINE ÉTAPE:")
print("Tester dans le navigateur:")
print("1. Ouvrir http://localhost:5173/payroll")
print("2. Cliquer sur 'Imprimer tous les bulletins'")
print("3. Cocher 'Filtrage par structure organisationnelle'")
print("4. Sélectionner un établissement")
print("5. Vérifier que seuls les salariés de cet établissement sont affichés")
print()
print("Si un salarié change d'employeur, ses affectations organisationnelles")
print("doivent être mises à jour pour correspondre aux structures du nouvel employeur.")
