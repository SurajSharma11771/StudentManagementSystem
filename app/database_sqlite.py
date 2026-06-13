import sqlite3
import os

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
            roll INTEGER UNIQUE NOT NULL
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