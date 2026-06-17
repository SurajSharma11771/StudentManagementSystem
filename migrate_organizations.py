from app.db import connect
from app.database_sqlite import q

conn = connect()
cursor = conn.cursor()

try:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS organizations (
            id SERIAL PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
except Exception:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS organizations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

columns = [
    ("users", "organization_id"),
    ("students", "organization_id"),
    ("attendance", "organization_id"),
    ("marks", "organization_id"),
    ("fees", "organization_id")
]

for table, column in columns:
    try:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} INTEGER")
        print(f"Added {column} to {table}")
    except Exception as e:
        print(f"{table}.{column} already exists or skipped")

conn.commit()
conn.close()

print("Organization migration complete")