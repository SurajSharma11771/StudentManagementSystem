from app.database_sqlite import (
    add_student,
    get_students,
    delete_student,
    search_student,
    update_student
)


def add():
    name = input("Enter name: ")
    roll = int(input("Enter roll: "))
    add_student(name, roll)


def view():
    students = get_students()

    if not students:
        print("No students found!")
        return

    for s in students:
        print(f"Name: {s[0]}, Roll: {s[1]}")


def delete():
    roll = int(input("Enter roll: "))
    delete_student(roll)


def search():
    roll = int(input("Enter roll: "))
    search_student(roll)


def update():
    roll = int(input("Enter roll: "))
    name = input("Enter new name: ")
    update_student(roll, name)