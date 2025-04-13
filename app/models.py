from . import db
from flask_login import UserMixin

# ----------------------------
# User Model
# ----------------------------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # 'student', 'teacher', 'admin'
    full_name = db.Column(db.String(100))  # or whatever length you prefer


    # Relationships
    enrollments = db.relationship('Enrollment', back_populates='student', lazy=True, cascade='all, delete-orphan')
    courses_taught = db.relationship('Course', backref='teacher', lazy=True, cascade='all, delete-orphan')

    def __str__(self):
        return self.username


# ----------------------------
# Course Model
# ----------------------------
class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    time = db.Column(db.String(100), nullable=False)

    enrollments = db.relationship('Enrollment', back_populates='course', lazy=True, cascade='all, delete-orphan')

    def __str__(self):
        return self.name


# ----------------------------
# Enrollment Model
# ----------------------------
class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    grade = db.Column(db.String(2))

    # Relationships (used in Flask-Admin and app logic)
    student = db.relationship('User', back_populates='enrollments')
    course = db.relationship('Course', back_populates='enrollments')
