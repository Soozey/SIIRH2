"""
Vérifier les données de Jeanne pour comprendre le problème d'affichage
"""
import sqlite3
import json

def check_jeanne():
    conn = sqlite3.connect('siirh-backend/siirh.db')
    cursor = conn.cursor()
    
    print("=" * 70)
    print("VÉRIFICATION DES DONNÉES DE JEANNE")
    print("=" * 70)
    
    # Trouver Jeanne
    cursor.execute("""
        SELECT id, nom, prenom, employer_id, 
               etablissement, departement, service, unite,
               etablissement_id, departement_id, service_id, unite_id
        FROM workers 
        WHERE nom LIKE '%Jeanne%' OR prenom LIKE '%Jeanne%'
    """)
    
    workers = cursor.fetchall()
    
    if not workers:
        print("❌ Aucun travailleur trouvé avec 'Jeanne'")
        conn.close()
        return
    
    for worker in workers:
        print(f"\n📋 Travailleur trouvé:")
        print(f"   ID: {worker[0]}")
        print(f"   Nom: {worker[1]} {worker[2]}")
        print(f"   Employer ID: {worker[3]}")
        print(f"\n   Structures (texte):")
        print(f"   - Établissement: {worker[4]}")
        print(f"   - Département: {worker[5]}")
        print(f"   - Service: {worker[6]}")
        print(f"   - Unité: {worker[7]}")
        print(f"\n   Structures (IDs):")
        print(f"   - Établissement ID: {worker[8]}")
        print(f"   - Département ID: {worker[9]}")
        print(f"   - Service ID: {worker[10]}")
        print(f"   - Unité ID: {worker[11]}")
        
        # Vérifier si les IDs sont NULL
        if worker[8] is None and worker[9] is None and worker[10] is None and worker[11] is None:
            print(f"\n   ⚠️ PROBLÈME DÉTECTÉ: Tous les IDs sont NULL!")
            print(f"   C'est pourquoi toutes les structures sont visibles.")
            
            # Proposer une correction
            print(f"\n   💡 Solution: Assigner des IDs de structures valides")
    
    conn.close()

if __name__ == "__main__":
    check_jeanne()
