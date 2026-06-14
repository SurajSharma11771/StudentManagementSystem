import sqlite3

conn = sqlite3.connect("data/students.db")
cursor = conn.cursor()

columns = [
    ("email", "TEXT"),
    ("phone", "TEXT"),
    ("address", "TEXT"),
    ("dob", "TEXT"),
    ("course", "TEXT"),
    ("semester", "TEXT"),
    ("photo", "TEXT"),
    ("created_at", "TIMESTAMP")
]

for name, dtype in columns:
    try:
        cursor.execute(f"ALTER TABLE students ADD COLUMN {name} {dtype}")
        print(f"Added: {name}")
    except sqlite3.OperationalError:
        print(f"Already exists: {name}")

conn.commit()
conn.close()

print("Migration Complete!")