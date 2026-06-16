from app.db import connect, is_postgres, placeholder

conn = connect()
print("Database connected successfully!")

if is_postgres():
    print("Using PostgreSQL")
else:
    print("Using SQLite")

print("Placeholder:", placeholder())

conn.close()