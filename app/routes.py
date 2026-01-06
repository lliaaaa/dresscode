from flask import Blueprint, render_template
from .decorators import login_required, role_required
from .models import UserActivity, User
from flask import session, request, redirect, url_for, flash
from . import db

bp = Blueprint("main", __name__)

@bp.route("/")
def index():
    return render_template("home.html")

@bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

@bp.route("/activities")
@login_required
def activities():
    user_id = session['user_id']
    user_activities = UserActivity.query.filter_by(user_id=user_id).order_by(UserActivity.timestamp.desc()).all()
    return render_template("activities.html", activities=user_activities)

@bp.route("/admin", methods=["GET", "POST"])
@login_required
@role_required("admin")
def admin_area():
    if request.method == "POST":
        email = request.form["email"].lower()
        password = request.form["password"]
        role = request.form["role"]

        if User.query.filter_by(email=email).first():
            flash("Email already exists.", "warning")
        else:
            user = User(email=email, role=role)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash("User created successfully!", "success")

        return redirect(url_for("main.admin_area"))

    users = User.query.all()
    return render_template("admin/admin.html", users=users)
