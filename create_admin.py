from werkzeug.security import generate_password_hash
from app.database_sqlite import init_db, q
from app.db import connect

init_db()

conn = connect()
cursor = conn.cursor()

cursor.execute("DELETE FROM organizations")
cursor.execute("INSERT INTO organizations (id, name) VALUES (1, 'Default Organization')")

hashed_password = generate_password_hash("admin123")

cursor.execute(
    q("""
        UPDATE users
        SET password=?, role=?, organization_id=?
        WHERE username=?
    """),
    (hashed_password, "admin", 1, "admin")
)

conn.commit()
conn.close()

print("Admin fixed successfully!")
print("Organization ID:", 1)
print("Username: admin")
print("Password: admin123")