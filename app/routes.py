from flask import Blueprint, render_template
from .decorators import login_required, role_required
from .models import User
from flask import session, request, redirect, url_for, flash
from .models import db, Student, Violation

bp = Blueprint("main", __name__)

@bp.route("/")
def index():
    return render_template("home.html")

@bp.route('/admin', methods=['GET'])
def admin_dashboard():
    query = Violation.query

    search = request.args.get('search')
    if search:
        query = query.filter(
            Violation.student_name.ilike(f"%{search}%")
        )

    course = request.args.get('course')
    if course:
        query = query.filter_by(course=course)

    year = request.args.get('year')
    if year:
        query = query.filter_by(year_level=year)

    violations = query.all()
    return render_template(
        "dashboard.html",
        violations=violations,
        students=Student.query.all()
    )

# ---------------- ADD STUDENT ----------------
@bp.route("/students/add", methods=["POST"])
@login_required
def add_student():
    student = Student(
        student_id=request.form["student_id"],
        first_name=request.form["first_name"],
        last_name=request.form["last_name"],
        program=request.form["program"],
        year_level=request.form["year_level"],
        created_by=current_user.user_id
    )
    db.session.add(student)
    db.session.commit()
    return redirect(url_for("bp.admin_dashboard"))

# ---------------- BULK ADD STUDENTS ----------------
@bp.route("/students/bulk-add", methods=["POST"])
@login_required
def bulk_add_students():
    file = request.files["csv_file"]
    stream = io.StringIO(file.stream.read().decode("UTF8"))
    reader = csv.DictReader(stream)

    for row in reader:
        student = Student(
            student_id=row["student_id"],
            first_name=row["first_name"],
            last_name=row["last_name"],
            program=row["program"],
            year_level=row["year_level"],
            created_by=current_user.user_id
        )
        db.session.add(student)

    db.session.commit()
    return redirect(url_for("bp.admin_dashboard"))

# ---------------- ADD VIOLATION ----------------
@bp.route("/violations/add", methods=["POST"])
@login_required
def add_violation():
    violation = Violation(
        student_id=request.form["student_id"],
        violation_type=request.form["violation_type"],
        reason=request.form.get("reason"),
        violation_date=datetime.utcnow(),
        admin_id=current_user.user_id
    )
    db.session.add(violation)
    db.session.commit()
    return redirect(url_for("bp.admin_dashboard"))

# ---------------- DELETE VIOLATION ----------------
@bp.route("/violations/delete/<int:violation_id>", methods=["POST"])
@login_required
def delete_violation(violation_id):
    violation = Violation.query.get_or_404(violation_id)
    db.session.delete(violation)
    db.session.commit()
    return redirect(url_for("bp.admin_dashboard"))

# ---------------- CLEAR ALL VIOLATIONS ----------------
@bp.route("/violations/clear", methods=["POST"])
@login_required
def clear_violations():
    Violation.query.delete()
    db.session.commit()
    return redirect(url_for("bp.admin_dashboard"))
