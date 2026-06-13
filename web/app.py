from flask import Flask, render_template, request, redirect, session
from app.database_sqlite import init_db, add_student, get_students, delete_student, update_student
from web.auth import login_user, is_logged_in, logout_user

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
    return render_template("index.html", students=students, total=len(students), query="")

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

    delete_student(roll)
    return redirect("/")


@app.route("/update", methods=["POST"])
def update():
    if not is_logged_in():
        return redirect("/login")

    roll = int(request.form["roll"])
    name = request.form["name"]
    update_student(roll, name)
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

if __name__ == "__main__":
    app.run(debug=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)