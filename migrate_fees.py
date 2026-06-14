import sqlite3

conn = sqlite3.connect("data/students.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS fees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    roll INTEGER NOT NULL,
    total_fee INTEGER NOT NULL,
    paid_amount INTEGER NOT NULL,
    pending_amount INTEGER NOT NULL,
    payment_date TEXT NOT NULL
)
""")

conn.commit()
conn.close()

print("Fees table created successfully!")