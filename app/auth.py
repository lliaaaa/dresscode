from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from .models import User, UserActivity
from . import db

bp = Blueprint("auth", __name__, url_prefix="/auth")

@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"].lower()
        password = request.form["password"]
        password2 = request.form["password2"]

        if password != password2:
            flash("Passwords do not match!", "danger")
            return redirect(url_for("auth.register"))

        if User.query.filter_by(email=email).first():
            flash("Email already exists.", "warning")
            return redirect(url_for("auth.register"))

        user = User(email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash("Registration successful! Please login.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].lower()
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session["user_id"] = user.id
            session["role"] = user.role
            # Log login activity
            activity = UserActivity(user_id=user.id, action='login')
            db.session.add(activity)
            db.session.commit()
            return redirect(url_for("main.dashboard"))

        flash("Invalid email or password", "danger")

    return render_template("login.html")


@bp.route("/logout")
def logout():
    # Log logout activity before clearing session
    if 'user_id' in session:
        activity = UserActivity(user_id=session['user_id'], action='logout')
        db.session.add(activity)
        db.session.commit()
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for("auth.login"))
