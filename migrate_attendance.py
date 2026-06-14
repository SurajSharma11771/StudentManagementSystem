import sqlite3

conn = sqlite3.connect("data/students.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    roll INTEGER NOT NULL,
    date TEXT NOT NULL,
    status TEXT NOT NULL
)
""")

conn.commit()
conn.close()

print("Attendance table created successfully!")