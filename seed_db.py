"""
Database Initialization and Seeding Script

Run this script to initialize the SQLite database tables and insert sample seed data:
    python seed_db.py
"""

import sqlite3
from pathlib import Path

from app.config import get_settings


def seed_database():
    settings = get_settings()
    db_url = settings.database_url

    # Resolve SQLite file path
    if db_url.startswith("sqlite:///"):
        db_path = db_url.replace("sqlite:///", "")
        if db_path.startswith("./"):
            db_path = db_path[2:]
        db_file = Path(db_path).resolve()
    else:
        db_file = Path("case_management.db").resolve()

    print(f"Connecting to SQLite database at: {db_file}")

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Enable Foreign Key enforcement
    cursor.execute("PRAGMA foreign_keys = ON;")

    schema_file = Path(__file__).parent / "sql" / "schema.sql"
    seed_file = Path(__file__).parent / "sql" / "seed.sql"

    print("Executing schema.sql...")
    with open(schema_file, "r", encoding="utf-8") as f:
        cursor.executescript(f.read())

    # Check if data already exists to avoid duplicates
    cursor.execute("SELECT COUNT(*) FROM users;")
    user_count = cursor.fetchone()[0]

    if user_count > 0:
        print(f"Database already contains {user_count} users. Clearing existing data for clean re-seed...")
        cursor.execute("DELETE FROM case_history;")
        cursor.execute("DELETE FROM cases;")
        cursor.execute("DELETE FROM users;")
        try:
            cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('users', 'cases', 'case_history');")
        except sqlite3.OperationalError:
            pass
        conn.commit()

    print("Executing seed.sql...")
    with open(seed_file, "r", encoding="utf-8") as f:
        cursor.executescript(f.read())

    conn.commit()

    # Report verification summary
    cursor.execute("SELECT COUNT(*) FROM users;")
    total_users = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM cases;")
    total_cases = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM case_history;")
    total_history = cursor.fetchone()[0]

    print("=" * 50)
    print("Database seeding completed successfully!")
    print(f"  - Users created:        {total_users}")
    print(f"  - Cases created:        {total_cases}")
    print(f"  - Case History entries: {total_history}")
    print("=" * 50)

    conn.close()


if __name__ == "__main__":
    seed_database()
