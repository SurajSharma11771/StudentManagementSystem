from flask import Flask, render_template, request, redirect, session
from app.database_sqlite import (
    init_db,
    add_student,
    get_students,
    delete_student,
    update_student,
    get_users,
    add_user,
    delete_user,
    update_user_role,
    total_students,
    total_users,
    recent_students,
    get_student_by_roll,
    update_student_profile
)
from web.auth import (
    login_user,
    is_logged_in,
    is_admin,
    logout_user
)
app = Flask(__name__)
app.secret_key = "mysecretkey"

init_db()


# 🔐 LOGIN PAGE
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if login_user(username, password):
            return redirect("/")
        else:
            return "Invalid Credentials"

    return render_template("login.html")


# 🔐 LOGOUT
@app.route("/logout")
def logout():
    logout_user()
    return redirect("/login")


# 🏠 HOME (PROTECTED)
@app.route("/")
def home():
    if not is_logged_in():
        return redirect("/login")

    students = get_students()
    student_count = total_students()
    user_count = total_users()
    recent = recent_students()
    return render_template(

    "index.html",

    students=students,

    total=len(students),

    query="",

    student_count=student_count,

    user_count=user_count,

    recent=recent

    )

@app.route("/add", methods=["POST"])
def add():
    if not is_logged_in():
        return redirect("/login")

    name = request.form["name"]
    roll = int(request.form["roll"])
    add_student(name, roll)
    return redirect("/")


@app.route("/delete/<int:roll>")
def delete(roll):

    if not is_logged_in():
        return redirect("/login")

    if not is_admin():
        return "⛔ Access Denied", 403

    delete_student(roll)
    return redirect("/")


@app.route("/update", methods=["POST"])
def update():
    if not is_logged_in():
        return redirect("/login")

    roll = request.form.get("roll", "").strip()

    if not roll:
        return "Roll number missing", 400

    name = request.form["name"]

    update_student(int(roll), name)

    return redirect("/")

@app.route("/search", methods=["GET"])
def search():
    if not is_logged_in():
        return redirect("/login")

    query = request.args.get("q", "")

    students = get_students()

    # 🔍 filter logic
    filtered = [
        s for s in students
        if query.lower() in s[0].lower() or query in str(s[1])
    ]

    return render_template("index.html", students=filtered, total=len(students), query=query)

@app.route("/student/<int:roll>")
def student_profile(roll):

    if not is_logged_in():
        return redirect("/login")

    student = get_student_by_roll(roll)

    if student is None:
        return "Student Not Found", 404

    return render_template(
        "student_profile.html",
        student=student
    )


@app.route("/users")
def users():

    if not is_logged_in():
        return redirect("/login")

    if not is_admin():
        return "Access Denied", 403

    users = get_users()

    return render_template("users.html", users=users)

@app.route("/add_user", methods=["POST"])
def add_new_user():

    if not is_logged_in():
        return redirect("/login")

    if not is_admin():
        return "Access Denied", 403

    username = request.form["username"]
    password = request.form["password"]
    role = request.form["role"]

    add_user(username, password)

    # Role update
    users = get_users()

    for user in users:
        if user[1] == username:
            update_user_role(user[0], role)
            break

    return redirect("/users")

@app.route("/delete_user/<int:user_id>")
def remove_user(user_id):

    if not is_logged_in():
        return redirect("/login")

    if not is_admin():
        return "Access Denied", 403

    delete_user(user_id)

    return redirect("/users")

if __name__ == "__main__":
    app.run(debug=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)