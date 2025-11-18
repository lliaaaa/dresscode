from flask import Blueprint, render_template
from .decorators import login_required, role_required

bp = Blueprint("main", __name__)

@bp.route("/")
def index():
    return render_template("home.html")

@bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

@bp.route("/admin")
@login_required
@role_required("admin")
def admin_area():
    return render_template("admin/admin.html")
