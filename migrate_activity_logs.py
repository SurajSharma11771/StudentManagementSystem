from app.db import connect
from app.database_sqlite import q, is_postgres

conn = connect()
cursor = conn.cursor()

if is_postgres():
    id_type = "SERIAL PRIMARY KEY"
else:
    id_type = "INTEGER PRIMARY KEY AUTOINCREMENT"

cursor.execute(f"""
CREATE TABLE IF NOT EXISTS activity_logs (
    id {id_type},
    username TEXT,
    action TEXT NOT NULL,
    organization_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()
conn.close()

print("Activity logs table created successfully!")