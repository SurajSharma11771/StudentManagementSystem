from app.controllers import student_controller as sc
from app.database_sqlite import init_db

init_db()

while True:
    print("\n===== Student Management System =====")
    print("1. Add Student")
    print("2. View Students")
    print("3. Delete Student")
    print("4. Search Student")
    print("5. Update Student")
    print("6. Exit")

    choice = input("Enter choice: ")

    if choice == "1":
        sc.add()

    elif choice == "2":
        sc.view()

    elif choice == "3":
        sc.delete()

    elif choice == "4":
        sc.search()

    elif choice == "5":
        sc.update()

    elif choice == "6":
        print("Exiting...")
        break

    else:
        print("Invalid choice!")