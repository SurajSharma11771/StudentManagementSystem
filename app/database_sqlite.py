import os
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from app.db import connect, is_postgres


def q(sql):
    if is_postgres():
        return sql.replace("?", "%s")
    return sql


def init_db():
    os.makedirs("data", exist_ok=True)

    conn = connect()
    cursor = conn.cursor()

    if is_postgres():
        id_type = "SERIAL PRIMARY KEY"
    else:
        id_type = "INTEGER PRIMARY KEY AUTOINCREMENT"

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS students (
            id {id_type},
            name TEXT NOT NULL,
            roll INTEGER UNIQUE NOT NULL,
            email TEXT,
            phone TEXT,
            address TEXT,
            dob TEXT,
            course TEXT,
            semester TEXT,
            photo TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS users (
            id {id_type},
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'staff'
        )
    """)

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS attendance (
            id {id_type},
            roll INTEGER NOT NULL,
            date TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS marks (
            id {id_type},
            roll INTEGER NOT NULL,
            subject TEXT NOT NULL,
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
            payment_date TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def add_student(name, roll):
    conn = connect()
    cursor = conn.cursor()

    try:
        cursor.execute(
            q("INSERT INTO students (name, roll) VALUES (?, ?)"),
            (name, roll)
        )
        conn.commit()
        print("Student added successfully!")
    except Exception as e:
        conn.rollback()
        print("Student already exists!", e)
    finally:
        conn.close()


def get_students():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("SELECT name, roll FROM students")
    data = cursor.fetchall()

    conn.close()
    return data


def delete_student(roll):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        q("DELETE FROM students WHERE roll=?"),
        (roll,)
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


def update_student(roll, name):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        q("UPDATE students SET name=? WHERE roll=?"),
        (name, roll)
    )

    conn.commit()
    conn.close()


def get_student_by_roll(roll):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        q("SELECT * FROM students WHERE roll=?"),
        (roll,)
    )

    student = cursor.fetchone()
    conn.close()

    return student


def update_student_profile(roll, email, phone, address, dob, course, semester, photo):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        q("""
            UPDATE students
            SET email=?, phone=?, address=?, dob=?, course=?, semester=?, photo=?
            WHERE roll=?
        """),
        (email, phone, address, dob, course, semester, photo, roll)
    )

    conn.commit()
    conn.close()


def add_user(username, password):
    conn = connect()
    cursor = conn.cursor()

    hashed_password = generate_password_hash(password)

    try:
        cursor.execute(
            q("INSERT INTO users (username, password) VALUES (?, ?)"),
            (username, hashed_password)
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        print("Username already exists.", e)
    finally:
        conn.close()


def verify_user(username, password):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        q("SELECT username, password, role FROM users WHERE username=?"),
        (username,)
    )

    row = cursor.fetchone()
    conn.close()

    if row is None:
        return None

    db_username = row[0]
    stored_password = row[1]
    role = row[2]

    if check_password_hash(stored_password, password):
        return {
            "username": db_username,
            "role": role
        }

    return None


def get_users():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("SELECT id, username, role FROM users")
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


def update_user_role(user_id, role):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        q("UPDATE users SET role=? WHERE id=?"),
        (role, user_id)
    )

    conn.commit()
    conn.close()


def total_students():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM students")
    total = cursor.fetchone()[0]

    conn.close()
    return total


def total_users():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users")
    total = cursor.fetchone()[0]

    conn.close()
    return total


def recent_students():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name, roll
        FROM students
        ORDER BY id DESC
        LIMIT 5
    """)

    students = cursor.fetchall()
    conn.close()

    return students


def mark_attendance(roll, date, status):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        q("SELECT id FROM attendance WHERE roll=? AND date=?"),
        (roll, date)
    )

    existing = cursor.fetchone()

    if existing:
        cursor.execute(
            q("UPDATE attendance SET status=? WHERE roll=? AND date=?"),
            (status, roll, date)
        )
    else:
        cursor.execute(
            q("INSERT INTO attendance (roll, date, status) VALUES (?, ?, ?)"),
            (roll, date, status)
        )

    conn.commit()
    conn.close()


def get_attendance():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT attendance.id, students.name, attendance.roll, attendance.date, attendance.status
        FROM attendance
        LEFT JOIN students ON students.roll = attendance.roll
        ORDER BY attendance.date DESC
    """)

    data = cursor.fetchall()
    conn.close()

    return data


def attendance_summary():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("SELECT status, COUNT(*) FROM attendance GROUP BY status")
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


def add_marks(roll, subject, internal, external):
    total = internal + external

    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        q("""
            INSERT INTO marks (roll, subject, internal, external, total)
            VALUES (?, ?, ?, ?, ?)
        """),
        (roll, subject, internal, external, total)
    )

    conn.commit()
    conn.close()


def get_marks():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT marks.id, students.name, marks.roll, marks.subject,
               marks.internal, marks.external, marks.total
        FROM marks
        LEFT JOIN students ON students.roll = marks.roll
        ORDER BY marks.id DESC
    """)

    data = cursor.fetchall()
    conn.close()

    return data


def marks_summary():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*), MAX(total), AVG(total) FROM marks")
    row = cursor.fetchone()

    conn.close()

    return {
        "records": row[0] or 0,
        "highest": row[1] or 0,
        "average": round(row[2] or 0, 2)
    }


def add_fee(roll, total_fee, paid_amount, payment_date):
    pending_amount = total_fee - paid_amount

    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        q("""
            INSERT INTO fees (roll, total_fee, paid_amount, pending_amount, payment_date)
            VALUES (?, ?, ?, ?, ?)
        """),
        (roll, total_fee, paid_amount, pending_amount, payment_date)
    )

    conn.commit()
    conn.close()


def get_fees():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT fees.id, students.name, fees.roll, fees.total_fee,
               fees.paid_amount, fees.pending_amount, fees.payment_date
        FROM fees
        LEFT JOIN students ON students.roll = fees.roll
        ORDER BY fees.id DESC
    """)

    data = cursor.fetchall()
    conn.close()

    return data


def fees_summary():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("SELECT SUM(total_fee), SUM(paid_amount), SUM(pending_amount) FROM fees")
    row = cursor.fetchone()

    conn.close()

    return {
        "total": row[0] or 0,
        "paid": row[1] or 0,
        "pending": row[2] or 0
    }