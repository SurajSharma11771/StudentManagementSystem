from app.db import connect
from app.database_sqlite import q

ORG_ID = 1

conn = connect()
cursor = conn.cursor()

for table in ["attendance", "marks", "fees"]:
    cursor.execute(
        q(f"""
            DELETE FROM {table}
            WHERE organization_id=?
            AND roll NOT IN (
                SELECT roll FROM students WHERE organization_id=?
            )
        """),
        (ORG_ID, ORG_ID)
    )

    print(f"{table} cleaned")

conn.commit()
conn.close()

print("Orphan records cleanup done")