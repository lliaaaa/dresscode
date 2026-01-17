from flask import Blueprint, render_template, redirect, url_for, request, abort, jsonify
from flask_login import login_required, current_user, login_user, logout_user
from .models import db, User, Student, Violation
from datetime import datetime

bp = Blueprint("main", __name__)

@bp.route('/')
def index():
    return render_template("home.html")

# ---------------- Login/Logout ----------------
@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("main.dashboard"))
    return render_template("login.html")

@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.login"))

# ---------------- Dashboard ----------------
@bp.route("/dashboard")
@login_required
def dashboard():
    if current_user.is_admin():
        total_students = Student.query.count()
        total_violations = Violation.query.count()
        recent_violations = Violation.query.order_by(Violation.violation_date.desc()).limit(5).all()
        students = Student.query.all()
        return render_template("dashboard.html",
                               total_students=total_students,
                               total_violations=total_violations,
                               recent_violations=recent_violations,
                               students=students)
    elif current_user.is_guard():
        return redirect(url_for("main.add_violation"))
    else:
        abort(403)

# ---------------- Student CRUD (Admin + Guard Add Student) ----------------
@bp.route("/students")
@login_required
def student_list():
    if not current_user.is_admin():
        abort(403)
    students = Student.query.all()
    return render_template("student_list.html", students=students)

@bp.route("/add_student", methods=["GET", "POST"])
@login_required
def add_student():
    if not (current_user.is_admin() or current_user.is_guard()):
        abort(403)
    if request.method == "POST":
        student_id = request.form['student_id']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        program = request.form['program']
        year_level = request.form['year_level']

        student = Student(student_id=student_id,
                          first_name=first_name,
                          last_name=last_name,
                          program=program,
                          year_level=year_level,
                          created_by=current_user.user_id)
        db.session.add(student)
        db.session.commit()
        return redirect(url_for("main.student_list"))
    return render_template("add_student.html")

@bp.route("/edit_student/<student_id>", methods=["GET", "POST"])
@login_required
def edit_student(student_id):
    if not current_user.is_admin():
        abort(403)
    student = Student.query.get_or_404(student_id)
    if request.method == "POST":
        student.first_name = request.form['first_name']
        student.last_name = request.form['last_name']
        student.program = request.form['program']
        student.year_level = request.form['year_level']
        db.session.commit()
        return redirect(url_for("main.student_list"))
    return render_template("edit_student.html", student=student)

@bp.route("/delete_student/<student_id>")
@login_required
def delete_student(student_id):
    if not current_user.is_admin():
        abort(403)
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    return redirect(url_for("main.student_list"))

# ---------------- Add Violation (Guard) ----------------
@bp.route("/add_violation", methods=["GET", "POST"])
@login_required
def add_violation():
    if not current_user.is_guard():
        abort(403)

    student = None
    student_id = request.args.get('student_id')
    if student_id:
        student = Student.query.filter_by(student_id=student_id).first()

    if request.method == "POST":
        student_id = request.form['student_id']
        violation_type = request.form['violation_type']
        reason = request.form['reason']

        violation = Violation(student_id=student_id,
                              violation_type=violation_type,
                              reason=reason,
                              admin_id=current_user.user_id,
                              violation_date=datetime.utcnow())
        db.session.add(violation)
        db.session.commit()
        return redirect(url_for("main.add_violation", student_id=student_id))

    return render_template("add_violation.html", student=student)

# ---------------- Add Student AJAX ----------------
@bp.route("/add_student_ajax", methods=["POST"])
@login_required
def add_student_ajax():
    if not (current_user.is_admin() or current_user.is_guard()):
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    data = request.get_json()
    student_id = data.get('student_id')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    program = data.get('program')
    year_level = data.get('year_level')

    if not all([student_id, first_name, last_name, program, year_level]):
        return jsonify({"success": False, "message": "All fields are required"}), 400

    if Student.query.filter_by(student_id=student_id).first():
        return jsonify({"success": False, "message": "Student ID already exists"}), 400

    student = Student(student_id=student_id,
                      first_name=first_name,
                      last_name=last_name,
                      program=program,
                      year_level=year_level,
                      created_by=current_user.user_id)
    db.session.add(student)
    db.session.commit()

    return jsonify({"success": True, "message": "Student added successfully"})

# ---------------- View Violations ----------------
@bp.route("/violations")
@login_required
def view_violations():
    violations = Violation.query.order_by(Violation.violation_date.desc()).all()
    return render_template("violations.html", violations=violations)
