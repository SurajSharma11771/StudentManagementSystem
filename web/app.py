from flask import Flask, render_template, request, redirect, session, send_file, jsonify
from openpyxl import Workbook
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
    update_student_profile,
    mark_attendance,
    get_attendance,
    attendance_summary,
    add_marks,
    get_marks,
    marks_summary,
    add_fee,
    get_fees,
    fees_summary,
    get_student_by_roll
)
from web.auth import (
    login_user,
    is_logged_in,
    is_admin,
    logout_user
)
import os
from werkzeug.utils import secure_filename
from PIL import Image


from io import BytesIO
from flask import send_file
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

app = Flask(__name__)
UPLOAD_FOLDER = "web/static/uploads/students"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.secret_key = "mysecretkey"
API_KEY = "student-erp-secret-key"

init_db()

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def api_key_required():
    key = request.headers.get("X-API-KEY")

    if key != API_KEY:
        return False

    return True

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

@app.route("/attendance")
def attendance_page():
    if not is_logged_in():
        return redirect("/login")

    students = get_students()
    attendance = get_attendance()
    summary = attendance_summary()

    return render_template(
        "attendance.html",
        students=students,
        attendance=attendance,
        summary=summary
    )

@app.route("/marks")
def marks_page():
    if not is_logged_in():
        return redirect("/login")

    students = get_students()
    marks = get_marks()
    summary = marks_summary()

    return render_template(
        "marks.html",
        students=students,
        marks=marks,
        summary=summary
    )

@app.route("/fees")
def fees_page():
    if not is_logged_in():
        return redirect("/login")

    students = get_students()
    fees = get_fees()
    summary = fees_summary()

    return render_template(
        "fees.html",
        students=students,
        fees=fees,
        summary=summary
    )


@app.route("/fees/add", methods=["POST"])
def fees_add():
    if not is_logged_in():
        return redirect("/login")

    roll = int(request.form["roll"])
    total_fee = int(request.form["total_fee"])
    paid_amount = int(request.form["paid_amount"])
    payment_date = request.form["payment_date"]

    add_fee(roll, total_fee, paid_amount, payment_date)

    return redirect("/fees")

@app.route("/marks/add", methods=["POST"])
def marks_add():
    if not is_logged_in():
        return redirect("/login")

    roll = int(request.form["roll"])
    subject = request.form["subject"]
    internal = int(request.form["internal"])
    external = int(request.form["external"])

    add_marks(roll, subject, internal, external)

    return redirect("/marks")


@app.route("/attendance/mark", methods=["POST"])
def attendance_mark():
    if not is_logged_in():
        return redirect("/login")

    roll = int(request.form["roll"])
    date = request.form["date"]
    status = request.form["status"]

    mark_attendance(roll, date, status)

    return redirect("/attendance")

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

@app.route("/student/photo/<int:roll>", methods=["POST"])
def upload_student_photo(roll):
    if not is_logged_in():
        return redirect("/login")

    student = get_student_by_roll(roll)

    if student is None:
        return "Student Not Found", 404

    if "photo" not in request.files:
        return redirect(f"/student/{roll}")

    photo = request.files["photo"]

    if photo.filename == "":
        return redirect(f"/student/{roll}")

    if photo and allowed_file(photo.filename):
        ext = photo.filename.rsplit(".", 1)[1].lower()
        filename = secure_filename(f"student_{roll}.{ext}")

        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)

        image = Image.open(photo)
        image = image.resize((300, 300))
        image.save(filepath)

        update_student_profile(
            roll,
            student[3],
            student[4],
            student[5],
            student[6],
            student[7],
            student[8],
            filename
        )

    return redirect(f"/student/{roll}")

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

@app.route("/reports/students/pdf")
def student_report_pdf():
    if not is_logged_in():
        return redirect("/login")

    students = get_students()

    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    content = []

    content.append(Paragraph("Student Profile Report", styles["Title"]))
    content.append(Spacer(1, 12))

    table_data = [[
        "Name", "Roll", "Email", "Phone", "Course", "Semester"
    ]]

    for s in students:
        student = get_student_by_roll(s[1])

        if student is None:
            continue

        table_data.append([
            str(student[1]),
            str(student[2]),
            str(student[3] or "-"),
            str(student[4] or "-"),
            str(student[7] or "-"),
            str(student[8] or "-")
        ])

    table = Table(table_data)

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
    ]))

    content.append(table)

    doc.build(content)

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="students_report.pdf",
        mimetype="application/pdf"
    )

@app.route("/reports/students/excel")
def student_report_excel():
    if not is_logged_in():
        return redirect("/login")

    students = get_students()

    wb = Workbook()
    ws = wb.active
    ws.title = "Students"

    ws.append(["Name", "Roll", "Email", "Phone", "Course", "Semester"])

    for s in students:
        student = get_student_by_roll(s[1])

        if student is None:
            continue

        ws.append([
            student[1],
            student[2],
            student[3] or "-",
            student[4] or "-",
            student[7] or "-",
            student[8] or "-"
        ])

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="students_report.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@app.route("/reports/attendance/pdf")
def attendance_report_pdf():
    if not is_logged_in():
        return redirect("/login")

    attendance = get_attendance()

    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    content = []

    content.append(Paragraph("Attendance Report", styles["Title"]))
    content.append(Spacer(1, 12))

    table_data = [[
        "Student",
        "Roll",
        "Date",
        "Status"
    ]]

    for a in attendance:
        table_data.append([
            str(a[1] or "-"),
            str(a[2]),
            str(a[3]),
            str(a[4])
        ])

    table = Table(table_data)

    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BACKGROUND', (0,1), (-1,-1), colors.beige),
    ]))

    content.append(table)

    doc.build(content)

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="attendance_report.pdf",
        mimetype="application/pdf"
    )

@app.route("/reports/attendance/excel")
def attendance_report_excel():
    if not is_logged_in():
        return redirect("/login")

    attendance = get_attendance()

    wb = Workbook()
    ws = wb.active
    ws.title = "Attendance"

    ws.append(["Student", "Roll", "Date", "Status"])

    for a in attendance:
        ws.append([
            a[1] or "-",
            a[2],
            a[3],
            a[4]
        ])

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="attendance_report.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@app.route("/reports/marks/pdf")
def marks_report_pdf():
    if not is_logged_in():
        return redirect("/login")

    marks = get_marks()

    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    content = []

    content.append(Paragraph("Marks Report", styles["Title"]))
    content.append(Spacer(1, 12))

    table_data = [[
        "Student",
        "Roll",
        "Subject",
        "Internal",
        "External",
        "Total"
    ]]

    for m in marks:
        table_data.append([
            str(m[1] or "-"),
            str(m[2]),
            str(m[3]),
            str(m[4]),
            str(m[5]),
            str(m[6])
        ])

    table = Table(table_data)

    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BACKGROUND', (0,1), (-1,-1), colors.beige),
    ]))

    content.append(table)

    doc.build(content)

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="marks_report.pdf",
        mimetype="application/pdf"
    )

@app.route("/reports/marks/excel")
def marks_report_excel():
    if not is_logged_in():
        return redirect("/login")

    marks = get_marks()

    wb = Workbook()
    ws = wb.active
    ws.title = "Marks"

    ws.append(["Student", "Roll", "Subject", "Internal", "External", "Total"])

    for m in marks:
        ws.append([
            m[1] or "-",
            m[2],
            m[3],
            m[4],
            m[5],
            m[6]
        ])

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="marks_report.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@app.route("/reports/fees/pdf")
def fees_report_pdf():
    if not is_logged_in():
        return redirect("/login")

    fees = get_fees()

    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    content = []

    content.append(Paragraph("Fees Report", styles["Title"]))
    content.append(Spacer(1, 12))

    table_data = [[
        "Student",
        "Roll",
        "Total Fee",
        "Paid",
        "Pending",
        "Date"
    ]]

    for f in fees:
        table_data.append([
            str(f[1] or "-"),
            str(f[2]),
            f"₹{f[3]}",
            f"₹{f[4]}",
            f"₹{f[5]}",
            str(f[6])
        ])

    table = Table(table_data)

    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BACKGROUND', (0,1), (-1,-1), colors.beige),
    ]))

    content.append(table)
    doc.build(content)
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="fees_report.pdf",
        mimetype="application/pdf"
    )


@app.route("/reports/fees/excel")
def fees_report_excel():
    if not is_logged_in():
        return redirect("/login")

    fees = get_fees()

    wb = Workbook()
    ws = wb.active
    ws.title = "Fees"

    ws.append(["Student", "Roll", "Total Fee", "Paid", "Pending", "Date"])

    for f in fees:
        ws.append([
            f[1] or "-",
            f[2],
            f[3],
            f[4],
            f[5],
            f[6]
        ])

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="fees_report.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@app.route("/api/students")
def api_students():
    if not is_logged_in():
        return jsonify({"error": "Unauthorized"}), 401

    students = get_students()

    data = []

    for s in students:
        student = get_student_by_roll(s[1])

        if student is None:
            continue

        data.append({
            "id": student[0],
            "name": student[1],
            "roll": student[2],
            "email": student[3],
            "phone": student[4],
            "address": student[5],
            "dob": student[6],
            "course": student[7],
            "semester": student[8],
            "photo": student[9],
            "created_at": student[10]
        })

    return jsonify(data)


@app.route("/api/attendance")
def api_attendance():
    if not is_logged_in():
        return jsonify({"error": "Unauthorized"}), 401

    attendance = get_attendance()

    data = []

    for a in attendance:
        data.append({
            "id": a[0],
            "student": a[1],
            "roll": a[2],
            "date": a[3],
            "status": a[4]
        })

    return jsonify(data)

@app.route("/api/marks")
def api_marks():
    if not is_logged_in():
        return jsonify({"error": "Unauthorized"}), 401

    marks = get_marks()

    data = []

    for m in marks:
        data.append({
            "id": m[0],
            "student": m[1],
            "roll": m[2],
            "subject": m[3],
            "internal": m[4],
            "external": m[5],
            "total": m[6]
        })

    return jsonify(data)

@app.route("/api/fees")
def api_fees():
    if not is_logged_in():
        return jsonify({"error": "Unauthorized"}), 401

    fees = get_fees()

    data = []

    for f in fees:
        data.append({
            "id": f[0],
            "student": f[1],
            "roll": f[2],
            "total_fee": f[3],
            "paid_amount": f[4],
            "pending_amount": f[5],
            "payment_date": f[6]
        })

    return jsonify(data)

@app.route("/api/students", methods=["POST"])
def api_add_student():
    #if not is_logged_in():
    #   return jsonify({"error": "Unauthorized"}), 401

    if not api_key_required():
        return jsonify({"error": "Invalid or missing API key"}), 401
    
    data = request.get_json()

    name = data.get("name")
    roll = data.get("roll")

    if not name or not roll:
        return jsonify({"error": "Name and roll are required"}), 400

    add_student(name, int(roll))

    return jsonify({
        "message": "Student added successfully",
        "student": {
            "name": name,
            "roll": int(roll)
        }
    }), 201

@app.route("/api/students/<int:roll>", methods=["PUT"])
def api_update_student(roll):
    data = request.get_json()
    if not api_key_required():
        return jsonify({"error": "Invalid or missing API key"}), 401
    name = data.get("name")

    if not name:
        return jsonify({"error": "Name is required"}), 400

    update_student(roll, name)

    return jsonify({
        "message": "Student updated successfully",
        "roll": roll,
        "name": name
    })

@app.route("/api/students/<int:roll>", methods=["DELETE"])
def api_delete_student(roll):
    delete_student(roll)
    if not api_key_required():
        return jsonify({"error": "Invalid or missing API key"}), 401
    return jsonify({
        "message": "Student deleted successfully",
        "roll": roll
    })



if __name__ == "__main__":
    app.run(debug=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

