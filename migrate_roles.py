import sqlite3

DB_PATH = "data/students.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'staff'")
    print("✅ Role column added successfully.")
except sqlite3.OperationalError as e:
    print("ℹ️", e)

conn.commit()

# Existing admin user ko admin role do
cursor.execute(
    "UPDATE users SET role='admin' WHERE username='admin'"
)

conn.commit()
conn.close()

print("✅ Admin role assigned.")