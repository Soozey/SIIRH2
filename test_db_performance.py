"""
Test de performance de la base de données
"""
import time
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+psycopg2://postgres:tantely123@127.0.0.1:5432/db_siirh_app"

def test_db_performance():
    print("=" * 60)
    print("TEST DE PERFORMANCE DE LA BASE DE DONNÉES")
    print("=" * 60)
    
    # Test 1: Connexion
    print("\n1. Test de connexion")
    start = time.time()
    engine = create_engine(DATABASE_URL, pool_pre_ping=True, echo=False)
    elapsed = (time.time() - start) * 1000
    print(f"   Création engine: {elapsed:.2f}ms")
    
    # Test 2: Première requête
    print("\n2. Première requête")
    start = time.time()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    result = db.execute(text("SELECT 1"))
    elapsed = (time.time() - start) * 1000
    print(f"   SELECT 1: {elapsed:.2f}ms")
    db.close()
    
    # Test 3: Requêtes répétées
    print("\n3. Requêtes répétées (10x)")
    times = []
    for i in range(10):
        db = SessionLocal()
        start = time.time()
        result = db.execute(text("SELECT COUNT(*) FROM organizational_nodes"))
        elapsed = (time.time() - start) * 1000
        times.append(elapsed)
        db.close()
    
    avg = sum(times) / len(times)
    print(f"   Moyenne: {avg:.2f}ms")
    print(f"   Min: {min(times):.2f}ms")
    print(f"   Max: {max(times):.2f}ms")
    
    # Test 4: Requête complexe
    print("\n4. Requête complexe (arbre organisationnel)")
    db = SessionLocal()
    start = time.time()
    result = db.execute(text("""
        SELECT * FROM organizational_nodes 
        WHERE employer_id = 1 AND is_active = true
        ORDER BY level, sort_order, name
    """))
    rows = result.fetchall()
    elapsed = (time.time() - start) * 1000
    print(f"   Temps: {elapsed:.2f}ms")
    print(f"   Lignes: {len(rows)}")
    db.close()
    
    # Test 5: Connexion avec pool_pre_ping=False
    print("\n5. Test sans pool_pre_ping")
    engine2 = create_engine(DATABASE_URL, pool_pre_ping=False, echo=False)
    SessionLocal2 = sessionmaker(autocommit=False, autoflush=False, bind=engine2)
    
    times = []
    for i in range(10):
        db = SessionLocal2()
        start = time.time()
        result = db.execute(text("SELECT COUNT(*) FROM organizational_nodes"))
        elapsed = (time.time() - start) * 1000
        times.append(elapsed)
        db.close()
    
    avg = sum(times) / len(times)
    print(f"   Moyenne: {avg:.2f}ms")
    print(f"   Min: {min(times):.2f}ms")
    print(f"   Max: {max(times):.2f}ms")
    
    print("\n" + "=" * 60)
    print("TESTS TERMINÉS")
    print("=" * 60)

if __name__ == "__main__":
    test_db_performance()
