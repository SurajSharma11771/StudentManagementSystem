from app.db import connect, is_postgres

conn = connect()
cursor = conn.cursor()

tables = ["students", "users", "attendance", "marks", "fees"]

for table in tables:
    try:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN organization_id INTEGER")
        print(f"Added organization_id to {table}")
    except Exception as e:
        print(f"{table}: organization_id already exists")

# first organization id nikalo
cursor.execute("SELECT id FROM organizations LIMIT 1")
org = cursor.fetchone()

if org:
    org_id = org[0]

    for table in tables:
        try:
            cursor.execute(
                f"UPDATE {table} SET organization_id = %s WHERE organization_id IS NULL"
                if is_postgres()
                else f"UPDATE {table} SET organization_id = ? WHERE organization_id IS NULL",
                (org_id,)
            )
            print(f"Updated NULL organization_id in {table}")
        except Exception as e:
            print(f"Skipped {table}:", e)

conn.commit()
conn.close()

print("Organization column fix complete.")