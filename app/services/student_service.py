from app.database import load_data, save_data
from app.models.student import Student


def add_student(name, roll):
    data = load_data()

    # duplicate check
    for s in data:
        if s["roll"] == roll:
            print("Student already exists!")
            return

    student = Student(name, roll)
    data.append(student.to_dict())

    save_data(data)
    print("Student added successfully!")


def view_students():
    data = load_data()

    if not data:
        print("No students found!")
        return

    for s in data:
        print(f"Name: {s['name']}, Roll: {s['roll']}")


def delete_student(roll):
    data = load_data()

    new_data = [s for s in data if s["roll"] != roll]

    if len(data) == len(new_data):
        print("Student not found!")
        return

    save_data(new_data)
    print("Student deleted!")


def search_student(roll):
    data = load_data()

    for s in data:
        if s["roll"] == roll:
            print(f"Found → Name: {s['name']}, Roll: {s['roll']}")
            return

    print("Student not found!")


def update_student(roll, new_name):
    data = load_data()

    for s in data:
        if s["roll"] == roll:
            s["name"] = new_name
            save_data(data)
            print("Student updated!")
            return

    print("Student not found!")