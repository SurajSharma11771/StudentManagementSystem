from app.db import connect, is_postgres

conn = connect()
cursor = conn.cursor()

if is_postgres():
    id_type = "SERIAL PRIMARY KEY"
    text_type = "TEXT"
    timestamp_type = "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
else:
    id_type = "INTEGER PRIMARY KEY AUTOINCREMENT"
    text_type = "TEXT"
    timestamp_type = "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"


cursor.execute(f"""
CREATE TABLE IF NOT EXISTS students (
    id {id_type},
    name {text_type} NOT NULL,
    roll INTEGER UNIQUE NOT NULL,
    email {text_type},
    phone {text_type},
    address {text_type},
    dob {text_type},
    course {text_type},
    semester {text_type},
    photo {text_type},
    created_at {timestamp_type}
)
""")

cursor.execute(f"""
CREATE TABLE IF NOT EXISTS users (
    id {id_type},
    username {text_type} UNIQUE NOT NULL,
    password {text_type} NOT NULL,
    role {text_type} DEFAULT 'staff'
)
""")

cursor.execute(f"""
CREATE TABLE IF NOT EXISTS attendance (
    id {id_type},
    roll INTEGER NOT NULL,
    date {text_type} NOT NULL,
    status {text_type} NOT NULL
)
""")

cursor.execute(f"""
CREATE TABLE IF NOT EXISTS marks (
    id {id_type},
    roll INTEGER NOT NULL,
    subject {text_type} NOT NULL,
    internal INTEGER NOT NULL,
    external INTEGER NOT NULL,
    total INTEGER NOT NULL
)
""")

cursor.execute(f"""
CREATE TABLE IF NOT EXISTS fees (
    id {id_type},
    roll INTEGER NOT NULL,
    total_fee INTEGER NOT NULL,
    paid_amount INTEGER NOT NULL,
    pending_amount INTEGER NOT NULL,
    payment_date {text_type} NOT NULL
)
""")

conn.commit()
conn.close()

print("Database tables created successfully!")
print("PostgreSQL mode:", is_postgres())
