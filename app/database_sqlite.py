import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = "data/students.db"


def connect():
    return sqlite3.connect(DB_PATH)


def init_db():
    os.makedirs("data", exist_ok=True)

    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
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

    conn.commit()
    conn.close()
    create_users_table()
    
def create_users_table():
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()
    
def add_student(name, roll):
    conn = connect()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO students (name, roll) VALUES (?, ?)", (name, roll))
        conn.commit()
        print("Student added successfully!")
    except:
        print("Student already exists!")
    finally:
        conn.close()

def add_user(username, password):
    conn = connect()
    cursor = conn.cursor()

    hashed_password = generate_password_hash(password)

    try:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hashed_password)
        )

        conn.commit()

    except sqlite3.IntegrityError:
        print("Username already exists.")

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

    cursor.execute("DELETE FROM students WHERE roll=?", (roll,))
    conn.commit()

    if cursor.rowcount == 0:
        print("Student not found!")
    else:
        print("Student deleted!")

    conn.close()


def search_student(roll):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("SELECT name, roll FROM students WHERE roll=?", (roll,))
    data = cursor.fetchone()

    conn.close()

    if data:
        print(f"Found → Name: {data[0]}, Roll: {data[1]}")
    else:
        print("Student not found!")


def update_student(roll, name):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("UPDATE students SET name=? WHERE roll=?", (name, roll))
    conn.commit()

    if cursor.rowcount == 0:
        print("Student not found!")
    else:
        print("Student updated!")

    conn.close()

def verify_user(username, password):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
    "SELECT username, password, role FROM users WHERE username=?",
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

    cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()

    conn.close()

def update_user_role(user_id, role):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE users SET role=? WHERE id=?",
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

    SELECT name,roll

    FROM students

    ORDER BY id DESC

    LIMIT 5

    """)

    students = cursor.fetchall()

    conn.close()

    return students


def get_student_by_roll(roll):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM students
        WHERE roll=?
    """, (roll,))

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
    photo
):

    conn = connect()

    cursor = conn.cursor()

    cursor.execute("""
    UPDATE students

    SET

    email=?,
    phone=?,
    address=?,
    dob=?,
    course=?,
    semester=?,
    photo=?

    WHERE roll=?

    """,(

        email,
        phone,
        address,
        dob,
        course,
        semester,
        photo,
        roll

    ))

    conn.commit()

    conn.close()