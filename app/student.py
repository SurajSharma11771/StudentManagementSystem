from app.database import load_data, save_data


def add_student(name, roll):
    data = load_data()

    # 🔥 duplicate roll check
    for s in data:
        if s["roll"] == roll:
            print("Student with this roll already exists!")
            return

    data.append({
        "name": name,
        "roll": roll
    })

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


# 🔍 NEW FEATURE: Search Student
def search_student(roll):
    data = load_data()

    for s in data:
        if s["roll"] == roll:
            print(f"Found → Name: {s['name']}, Roll: {s['roll']}")
            return

    print("Student not found!")


# ✏️ NEW FEATURE: Update Student
def update_student(roll, new_name):
    data = load_data()

    for s in data:
        if s["roll"] == roll:
            s["name"] = new_name
            save_data(data)
            print("Student updated successfully!")
            return

    print("Student not found!")