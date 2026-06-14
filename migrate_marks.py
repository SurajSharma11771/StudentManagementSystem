import sqlite3

conn = sqlite3.connect("data/students.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS marks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    roll INTEGER NOT NULL,
    subject TEXT NOT NULL,
    internal INTEGER NOT NULL,
    external INTEGER NOT NULL,
    total INTEGER NOT NULL
)
""")

conn.commit()
conn.close()

print("Marks table created successfully!")