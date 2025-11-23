"""Reset database by dropping all tables and recreating them.

WARNING: This will delete ALL data in the database!
Use only for development/hackathon purposes.
"""

from sqlalchemy import create_engine, text
from app.config.settings import settings

def reset_database():
    """Drop all tables and reset the database."""
    engine = create_engine(str(settings.DATABASE_URL))
    
    print("⚠️  WARNING: This will DELETE ALL DATA in the database!")
    print(f"Database: {str(settings.DATABASE_URL).split('@')[1] if '@' in str(settings.DATABASE_URL) else settings.DATABASE_URL}")
    
    with engine.connect() as conn:
        # Drop all tables and types
        print("\n🗑️  Dropping all tables and types...")
        
        # Drop tables in order (respecting foreign keys)
        tables = ['items', 'invoices', 'payments', 'session_users', 'sessions', 'users', 'alembic_version']
        for table in tables:
            try:
                conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
                print(f"  ✓ Dropped table: {table}")
            except Exception as e:
                print(f"  ⚠ Could not drop {table}: {e}")
        
        # Drop custom types
        types = ['session_status']
        for type_name in types:
            try:
                conn.execute(text(f"DROP TYPE IF EXISTS {type_name} CASCADE"))
                print(f"  ✓ Dropped type: {type_name}")
            except Exception as e:
                print(f"  ⚠ Could not drop type {type_name}: {e}")
        
        conn.commit()
    
    print("\n✅ Database reset complete!")
    print("\nNext steps:")
    print("  1. Run migrations: make upgrade")
    print("  2. Seed fake data: uv run python -m scripts.make_fake_data")

if __name__ == "__main__":
    reset_database()

