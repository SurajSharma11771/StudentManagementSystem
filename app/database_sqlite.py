import os
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from app.db import connect, is_postgres


def q(sql):
    if is_postgres():
        return sql.replace("?", "%s")
    return sql

def ensure_org_columns():
    conn = connect()
    cursor = conn.cursor()

    tables = ["students", "users", "attendance", "marks", "fees"]

    for table in tables:
        try:
            cursor.execute(
                f"ALTER TABLE {table} ADD COLUMN organization_id INTEGER"
            )
            conn.commit()
        except Exception:
            conn.rollback()

    try:
        cursor.execute("SELECT id FROM organizations LIMIT 1")
        org = cursor.fetchone()
    except Exception:
        conn.rollback()
        conn.close()
        return

    if org:
        org_id = org[0]

        for table in tables:
            try:
                cursor.execute(
                    q(f"UPDATE {table} SET organization_id=? WHERE organization_id IS NULL"),
                    (org_id,)
                )
                conn.commit()
            except Exception:
                conn.rollback()
    conn.close()



def ensure_user_status_column():
    conn = connect()
    cursor = conn.cursor()

    try:
        cursor.execute("ALTER TABLE users ADD COLUMN status TEXT DEFAULT 'approved'")
        conn.commit()
    except Exception:
        conn.rollback()

    conn.close()

def init_db():
    os.makedirs("data", exist_ok=True)

    conn = connect()
    cursor = conn.cursor()

    if is_postgres():
        id_type = "SERIAL PRIMARY KEY"
    else:
        id_type = "INTEGER PRIMARY KEY AUTOINCREMENT"

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS organizations (
            id {id_type},
            name TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS students (
            id {id_type},
            name TEXT NOT NULL,
            roll INTEGER NOT NULL,
            email TEXT,
            phone TEXT,
            address TEXT,
            dob TEXT,
            course TEXT,
            semester TEXT,
            photo TEXT,
            organization_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(roll, organization_id)
        )
    """)

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS users (
            id {id_type},
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'staff',
            organization_id INTEGER
        )
    """)

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS attendance (
            id {id_type},
            roll INTEGER NOT NULL,
            date TEXT NOT NULL,
            status TEXT NOT NULL,
            organization_id INTEGER
        )
    """)

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS marks (
            id {id_type},
            roll INTEGER NOT NULL,
            subject TEXT NOT NULL,
            internal INTEGER NOT NULL,
            external INTEGER NOT NULL,
            total INTEGER NOT NULL,
            organization_id INTEGER
        )
    """)

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS fees (
            id {id_type},
            roll INTEGER NOT NULL,
            total_fee INTEGER NOT NULL,
            paid_amount INTEGER NOT NULL,
            pending_amount INTEGER NOT NULL,
            payment_date TEXT NOT NULL,
            organization_id INTEGER
        )
    """)
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS activity_logs (
        id {id_type},
        username TEXT NOT NULL,
        action TEXT NOT NULL,
        organization_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

    conn.commit()
    conn.close()

    ensure_org_columns()
    ensure_user_status_column()


def add_student(
    name,
    roll,
    organization_id=None,
    email=None,
    phone=None,
    address=None,
    dob=None,
    course=None,
    semester=None,
    photo=None
):
    conn = connect()
    cursor = conn.cursor()

    try:
        cursor.execute(
            q("""
                INSERT INTO students
                (name, roll, organization_id, email, phone, address, dob, course, semester, photo)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """),
            (name, roll, organization_id, email, phone, address, dob, course, semester, photo)
        )
        conn.commit()

    except Exception as e:
        conn.rollback()
        print("Student already exists!", e)
    finally:
        conn.close()


def get_students(organization_id=None):
    conn = connect()
    cursor = conn.cursor()

    if organization_id:
        cursor.execute(
            q("""
                SELECT name, roll, email, phone, address, dob, course, semester, photo
                FROM students
                WHERE organization_id=?
                ORDER BY id DESC
            """),
            (organization_id,)
        )
    else:
        cursor.execute("""
            SELECT name, roll, email, phone, address, dob, course, semester, photo
            FROM students
            ORDER BY id DESC
        """)

    data = cursor.fetchall()

    conn.close()
    return data


def delete_student(roll, organization_id):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        q("DELETE FROM attendance WHERE roll=? AND organization_id=?"),
        (roll, organization_id)
    )

    cursor.execute(
        q("DELETE FROM marks WHERE roll=? AND organization_id=?"),
        (roll, organization_id)
    )

    cursor.execute(
        q("DELETE FROM fees WHERE roll=? AND organization_id=?"),
        (roll, organization_id)
    )

    cursor.execute(
        q("DELETE FROM students WHERE roll=? AND organization_id=?"),
        (roll, organization_id)
    )

    conn.commit()
    conn.close()


def search_student(roll):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        q("SELECT name, roll FROM students WHERE roll=?"),
        (roll,)
    )

    data = cursor.fetchone()
    conn.close()

    if data:
        print(f"Found → Name: {data[0]}, Roll: {data[1]}")
    else:
        print("Student not found!")


def update_student(roll, name, organization_id):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        q("""
            UPDATE students
            SET name=?
            WHERE roll=? AND organization_id=?
        """),
        (name, roll, organization_id)
    )

    conn.commit()
    conn.close()


def get_student_by_roll(roll, organization_id=None):
    conn = connect()
    cursor = conn.cursor()

    if organization_id:
        cursor.execute(
            q("SELECT * FROM students WHERE roll=? AND organization_id=?"),
            (roll, organization_id)
        )
    else:
        cursor.execute(
            q("SELECT * FROM students WHERE roll=?"),
            (roll,)
        )

    student = cursor.fetchone()
    conn.close()

    return student


def update_student_profile(
    roll,
    email,
    phone,
    address,
    dob,
    course,
    semester,
    photo,
    organization_id
):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
    q("""
        UPDATE students
        SET email=?,
            phone=?,
            address=?,
            dob=?,
            course=?,
            semester=?,
            photo=?
        WHERE roll=?
        AND organization_id=?
    """),
    (
        email,
        phone,
        address,
        dob,
        course,
        semester,
        photo,
        roll,
        organization_id
    )
)

    conn.commit()
    conn.close()


def add_user(
    username,
    password,
    organization_id=None,
    role="user",
    status="approved"
):
    conn = connect()
    cursor = conn.cursor()

    hashed_password = generate_password_hash(password)

    try:

        cursor.execute(
            q("""
                INSERT INTO users (
                    username,
                    password,
                    organization_id,
                    role,
                    status
                )
                VALUES (?, ?, ?, ?, ?)
            """),
            (
                username,
                hashed_password,
                organization_id,
                role,
                status
            )
        )

        conn.commit()

    except Exception as e:

        conn.rollback()

        print(
            "Username already exists.",
            e
        )

    finally:

        conn.close()


def verify_user(username, password):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        q("""
            SELECT username, password, role, organization_id, status
            FROM users
            WHERE username=?
        """),
        (username,)
    )

    row = cursor.fetchone()
    conn.close()

    if row is None:
        return None

    db_username = row[0]
    stored_password = row[1]
    role = row[2]
    organization_id = row[3]
    status = row[4]

    if status != "approved":
        return {
            "error": "pending"
        }

    if check_password_hash(stored_password, password):
        return {
            "username": db_username,
            "role": role,
            "organization_id": organization_id,
            "status": status
        }

    return None


def get_users(organization_id=None):
    conn = connect()
    cursor = conn.cursor()

    if organization_id:

        cursor.execute(
            q("""
                SELECT
                    id,
                    username,
                    role,
                    status
                FROM users
                WHERE organization_id=?
            """),
            (organization_id,)
        )

    else:

        cursor.execute("""
            SELECT
                id,
                username,
                role,
                status
            FROM users
        """)

    users = cursor.fetchall()

    conn.close()

    return users


def delete_user(user_id):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        q("DELETE FROM users WHERE id=?"),
        (user_id,)
    )

    conn.commit()
    conn.close()

def approve_user(user_id):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        q("UPDATE users SET status=? WHERE id=?"),
        ("approved", user_id)
    )

    conn.commit()
    conn.close()


def reject_user(user_id):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        q("UPDATE users SET status=? WHERE id=?"),
        ("rejected", user_id)
    )

    conn.commit()
    conn.close()

def update_user_role(user_id, role):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        q("UPDATE users SET role=? WHERE id=?"),
        (role, user_id)
    )

    conn.commit()
    conn.close()


def total_students(organization_id=None):
    conn = connect()
    cursor = conn.cursor()

    if organization_id:
        cursor.execute(
            q("SELECT COUNT(*) FROM students WHERE organization_id=?"),
            (organization_id,)
        )
    else:
        cursor.execute("SELECT COUNT(*) FROM students")

    total = cursor.fetchone()[0]

    conn.close()
    return total


def total_users(organization_id=None):
    conn = connect()
    cursor = conn.cursor()

    if organization_id:
        cursor.execute(
            q("SELECT COUNT(*) FROM users WHERE organization_id=?"),
            (organization_id,)
        )
    else:
        cursor.execute("SELECT COUNT(*) FROM users")

    total = cursor.fetchone()[0]
    conn.close()

    return total


def recent_students(organization_id=None):
    conn = connect()
    cursor = conn.cursor()

    if organization_id:
        cursor.execute(
            q("""
                SELECT name, roll
                FROM students
                WHERE organization_id=?
                ORDER BY id DESC
                LIMIT 5
            """),
            (organization_id,)
        )
    else:
        cursor.execute("""
            SELECT name, roll
            FROM students
            ORDER BY id DESC
            LIMIT 5
        """)

    students = cursor.fetchall()
    conn.close()

    return students

def mark_attendance(roll, date, status, organization_id):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        q("""
            SELECT id FROM attendance
            WHERE roll=? AND date=? AND organization_id=?
        """),
        (roll, date, organization_id)
    )

    existing = cursor.fetchone()

    if existing:
        cursor.execute(
            q("""
                UPDATE attendance
                SET status=?
                WHERE roll=? AND date=? AND organization_id=?
            """),
            (status, roll, date, organization_id)
        )
    else:
        cursor.execute(
            q("""
                INSERT INTO attendance
                (roll, date, status, organization_id)
                VALUES (?, ?, ?, ?)
            """),
            (roll, date, status, organization_id)
        )

    conn.commit()
    conn.close()

def get_attendance(organization_id):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        q("""
            SELECT attendance.id,
                   students.name,
                   attendance.roll,
                   attendance.date,
                   attendance.status
            FROM attendance
            LEFT JOIN students
                ON students.roll = attendance.roll
                AND students.organization_id = attendance.organization_id
            WHERE attendance.organization_id=?
            ORDER BY attendance.date DESC
        """),
        (organization_id,)
    )

    data = cursor.fetchall()

    conn.close()

    return data


def attendance_summary(organization_id):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        q("""
            SELECT status, COUNT(*)
            FROM attendance
            WHERE organization_id=?
            GROUP BY status
        """),
        (organization_id,)
    )

    rows = cursor.fetchall()
    
    conn.close()

    summary = {
        "Present": 0,
        "Absent": 0,
        "Leave": 0
    }

    for status, count in rows:
        summary[status] = count

    return summary


def add_marks(roll, subject, internal, external, organization_id):
    total = internal + external

    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        q("""
            INSERT INTO marks
            (roll, subject, internal, external, total, organization_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """),
        (roll, subject, internal, external, total, organization_id)
    )

    conn.commit()
    conn.close()


def get_marks(organization_id):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        q("""
            SELECT marks.id, students.name, marks.roll, marks.subject,
                   marks.internal, marks.external, marks.total
            FROM marks
            LEFT JOIN students
                ON students.roll = marks.roll
                AND students.organization_id = marks.organization_id
            WHERE marks.organization_id=?
            ORDER BY marks.id DESC
        """),
        (organization_id,)
    )

    data = cursor.fetchall()
    conn.close()
    
    return data


def marks_summary(organization_id):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        q("""
            SELECT COUNT(*), MAX(total), AVG(total)
            FROM marks
            WHERE organization_id=?
        """),
        (organization_id,)
    )

    row = cursor.fetchone()

    conn.close()

    return {
        "records": row[0] or 0,
        "highest": row[1] or 0,
        "average": round(row[2] or 0, 2)
    }


def add_fee(roll, total_fee, paid_amount, payment_date, organization_id):
    pending_amount = total_fee - paid_amount

    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        q("""
            INSERT INTO fees
            (roll, total_fee, paid_amount, pending_amount, payment_date, organization_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """),
        (roll, total_fee, paid_amount, pending_amount, payment_date, organization_id)
    )

    conn.commit()
    conn.close()


def get_fees(organization_id):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        q("""
            SELECT fees.id, students.name, fees.roll, fees.total_fee,
                   fees.paid_amount, fees.pending_amount, fees.payment_date
            FROM fees
            LEFT JOIN students
                ON students.roll = fees.roll
                AND students.organization_id = fees.organization_id
            WHERE fees.organization_id=?
            ORDER BY fees.id DESC
        """),
        (organization_id,)
    )

    data = cursor.fetchall()
    conn.close()

    return data


def fees_summary(organization_id):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        q("""
            SELECT SUM(total_fee), SUM(paid_amount), SUM(pending_amount)
            FROM fees
            WHERE organization_id=?
        """),
        (organization_id,)
    )

    row = cursor.fetchone()

    conn.close()

    return {
        "total": row[0] or 0,
        "paid": row[1] or 0,
        "pending": row[2] or 0
    }


def reset_admin_password():
    conn = connect()
    cursor = conn.cursor()

    hashed_password = generate_password_hash("admin123")

    cursor.execute(
        q("""
            INSERT INTO users (username, password, role)
            VALUES (?, ?, ?)
            ON CONFLICT (username)
            DO UPDATE SET password = EXCLUDED.password, role = EXCLUDED.role
        """),
        ("admin", hashed_password, "admin")
    )

    conn.commit()
    conn.close()

    print("Admin password reset successfully")

def admin_exists():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        q("SELECT id FROM users WHERE role=? LIMIT 1"),
        ("admin",)
    )

    admin = cursor.fetchone()

    conn.close()

    return admin is not None

def create_organization(name):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        q("INSERT INTO organizations (name) VALUES (?)"),
        (name,)
    )

    conn.commit()

    cursor.execute(
        q("SELECT id FROM organizations WHERE name=?"),
        (name,)
    )

    org = cursor.fetchone()

    conn.close()

    return org[0]


def get_user_with_org(username):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        q("SELECT id, username, role, organization_id FROM users WHERE username=?"),
        (username,)
    )

    user = cursor.fetchone()

    conn.close()

    return user


def organization_exists():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM organizations LIMIT 1")
    org = cursor.fetchone()

    conn.close()

    return org is not None

def dashboard_summary(organization_id):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        q("SELECT COUNT(*) FROM students WHERE organization_id=?"),
        (organization_id,)
    )
    students = cursor.fetchone()[0] or 0

    cursor.execute(
        q("SELECT status, COUNT(*) FROM attendance WHERE organization_id=? GROUP BY status"),
        (organization_id,)
    )
    attendance_rows = cursor.fetchall()

    attendance = {
        "Present": 0,
        "Absent": 0,
        "Leave": 0
    }

    for status, count in attendance_rows:
        attendance[status] = count

    cursor.execute(
        q("SELECT SUM(paid_amount), SUM(pending_amount) FROM fees WHERE organization_id=?"),
        (organization_id,)
    )
    fee_row = cursor.fetchone()

    fees = {
        "paid": fee_row[0] or 0,
        "pending": fee_row[1] or 0
    }

    cursor.execute(
        q("SELECT AVG(total), MAX(total) FROM marks WHERE organization_id=?"),
        (organization_id,)
    )
    marks_row = cursor.fetchone()

    marks = {
        "average": round(marks_row[0] or 0, 2),
        "highest": marks_row[1] or 0
    }

    conn.close()

    return {
        "students": students,
        "attendance": attendance,
        "fees": fees,
        "marks": marks
    }

def clear_orphan_records(organization_id):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        q("""
            DELETE FROM attendance
            WHERE organization_id=?
            AND roll NOT IN (
                SELECT roll FROM students WHERE organization_id=?
            )
        """),
        (organization_id, organization_id)
    )

    cursor.execute(
        q("""
            DELETE FROM marks
            WHERE organization_id=?
            AND roll NOT IN (
                SELECT roll FROM students WHERE organization_id=?
            )
        """),
        (organization_id, organization_id)
    )

    cursor.execute(
        q("""
            DELETE FROM fees
            WHERE organization_id=?
            AND roll NOT IN (
                SELECT roll FROM students WHERE organization_id=?
            )
        """),
        (organization_id, organization_id)
    )

    conn.commit()
    conn.close()

def add_activity_log(username, action, organization_id):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        q("""
            INSERT INTO activity_logs (username, action, organization_id)
            VALUES (?, ?, ?)
        """),
        (username, action, organization_id)
    )

    conn.commit()
    conn.close()


def get_recent_activity_logs(organization_id, limit=5):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        q("""
            SELECT username, action, created_at
            FROM activity_logs
            WHERE organization_id=?
            ORDER BY id DESC
            LIMIT ?
        """),
        (organization_id, limit)
    )

    logs = cursor.fetchall()
    conn.close()
    return logs

def change_password(username, new_password):
    conn = connect()
    cursor = conn.cursor()

    hashed_password = generate_password_hash(new_password)

    cursor.execute(
        q("""
            UPDATE users
            SET password=?
            WHERE username=?
        """),
        (hashed_password, username)
    )

    conn.commit()
    conn.close()

def check_user_password(username, password):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        q("SELECT password FROM users WHERE username=?"),
        (username,)
    )

    row = cursor.fetchone()
    conn.close()

    if row is None:
        return False

    return check_password_hash(row[0], password)

def get_students_paginated(organization_id, limit, offset):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        q("""
            SELECT name, roll, email, phone, address, dob, course, semester, photo
            FROM students
            WHERE organization_id=?
            ORDER BY id DESC
            LIMIT ? OFFSET ?
        """),
        (organization_id, limit, offset)
    )

    students = cursor.fetchall()
    conn.close()

    return students

def get_all_activity_logs(organization_id):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        q("""
            SELECT username,
                   action,
                   created_at
            FROM activity_logs
            WHERE organization_id=?
            ORDER BY id DESC
        """),
        (organization_id,)
    )

    logs = cursor.fetchall()

    conn.close()

    return logs

def update_student_full(
    roll,
    name,
    email,
    phone,
    address,
    dob,
    course,
    semester,
    organization_id
):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        q("""
            UPDATE students
            SET name=?,
                email=?,
                phone=?,
                address=?,
                dob=?,
                course=?,
                semester=?
            WHERE roll=? AND organization_id=?
        """),
        (
            name,
            email,
            phone,
            address,
            dob,
            course,
            semester,
            roll,
            organization_id
        )
    )

    conn.commit()
    conn.close()

def get_organization_by_id(org_id):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        q("SELECT id, name FROM organizations WHERE id=?"),
        (org_id,)
    )

    org = cursor.fetchone()
    conn.close()

    return org


def update_organization_name(org_id, new_name):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        q("UPDATE organizations SET name=? WHERE id=?"),
        (new_name, org_id)
    )

    conn.commit()
    conn.close() 

def get_organization_by_name(name):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        q("SELECT id, name FROM organizations WHERE name=?"),
        (name,)
    )

    org = cursor.fetchone()

    conn.close()

    return org