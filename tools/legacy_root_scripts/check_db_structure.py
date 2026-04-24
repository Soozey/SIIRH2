#!/usr/bin/env python3
import sqlite3

def check_database():
    try:
        conn = sqlite3.connect('siirh-backend/siirh.db')
        
        # Get all tables
        tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        print("Tables in database:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Check if employers table exists and show its structure
        if any('employers' in table for table in tables):
            print("\nEmployers table structure:")
            columns = conn.execute("PRAGMA table_info(employers)").fetchall()
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
        else:
            print("\n❌ No 'employers' table found")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_database()