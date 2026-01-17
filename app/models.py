from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)

    created_students = db.relationship("Student", backref="creator", lazy=True)
    logged_violations = db.relationship("Violation", backref="admin", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Flask-Login expects get_id() to return a string
    def get_id(self):
        return str(self.user_id)

    # Role checks
    def is_admin(self):
        return self.role == "admin"

    def is_guard(self):
        return self.role == "guard"

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"


# ------------------ Student Table ------------------
class Student(db.Model):
    __tablename__ = "students"

    student_id = db.Column(db.String(20), primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    program = db.Column(db.String(50), nullable=False)
    year_level = db.Column(db.String(10), nullable=False)

    created_by = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=True)
    violations = db.relationship("Violation", backref="student", lazy=True)

    def __repr__(self):
        return f"<Student {self.student_id} - {self.first_name} {self.last_name}>"

# ------------------ Violation Table ------------------
class Violation(db.Model):
    __tablename__ = "violations"

    violation_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), db.ForeignKey("students.student_id"), nullable=False)
    violation_type = db.Column(db.String(200), nullable=False)
    reason = db.Column(db.String(500), nullable=True)   # ✅ add reason
    violation_date = db.Column(db.DateTime, default=datetime.utcnow)
    admin_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)

    def __repr__(self):
        return f"<Violation {self.violation_type} Student={self.student_id} ByUser={self.admin_id}>"
