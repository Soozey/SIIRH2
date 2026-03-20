#!/usr/bin/env python3
"""
Script pour vérifier les données organisationnelles dans la base de données
"""

import sqlite3

def check_organizational_data():
    conn = sqlite3.connect('siirh-backend/siirh.db')
    cursor = conn.cursor()

    print('=== TABLES DISPONIBLES ===')
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    for table in tables:
        print(f'Table: {table[0]}')

    print('\n=== SALARIÉS AVEC DONNÉES ORGANISATIONNELLES ===')
    cursor.execute('''
    SELECT id, matricule, nom, prenom, etablissement, departement, service, unite, employer_id
    FROM worker 
    WHERE etablissement IS NOT NULL OR departement IS NOT NULL OR service IS NOT NULL OR unite IS NOT NULL
    ORDER BY employer_id, id
    ''')

    workers = cursor.fetchall()
    print(f'Nombre de salariés avec données organisationnelles: {len(workers)}')
    print()
    
    for w in workers:
        print(f'ID: {w[0]} | Matricule: {w[1]} | {w[2]} {w[3]} | Employeur: {w[8]}')
        print(f'  Établissement: {w[4]}')
        print(f'  Département: {w[5]}')
        print(f'  Service: {w[6]}')
        print(f'  Unité: {w[7]}')
        print()

    print('=== EMPLOYEURS ===')
    cursor.execute('SELECT id, raison_sociale FROM employer ORDER BY id')
    employers = cursor.fetchall()
    for emp in employers:
        print(f'ID: {emp[0]} | {emp[1]}')

    conn.close()

if __name__ == "__main__":
    check_organizational_data()