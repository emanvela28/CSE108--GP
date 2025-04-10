from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from .models import User, Course, Enrollment
from .forms import LoginForm
from . import db, login_manager, bcrypt

main = Blueprint('main', __name__)

# Needed by Flask-Login to load user session
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@main.route('/')
def home():
    return redirect(url_for('main.login'))

@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        # if user and user.password == form.password.data:  # For demo only! Use hashed passwords in production
        if user and bcrypt.check_password_hash(user.password, form.password.data): #changed password to use bcrypt
            login_user(user)
            flash('Logged in successfully!', 'success')
            if user.role == 'student':
                return redirect(url_for('main.student_dashboard'))
            elif user.role == 'teacher':
                return redirect(url_for('main.teacher_dashboard'))
            elif user.role == 'admin':
                return redirect(url_for('main.admin_dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html', form=form)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))


@main.route('/student')
@login_required
def student_dashboard():
    if current_user.role != 'student':
        flash("Access denied.", "danger")
        return redirect(url_for('main.login'))

    all_courses = Course.query.all()
    enrolled_course_ids = [e.course_id for e in current_user.enrollments]
    return render_template(
        'student_dashboard.html',
        all_courses=all_courses,
        enrolled_course_ids=enrolled_course_ids
    )



@main.route('/teacher')
@login_required
def teacher_dashboard():
    if current_user.role != 'teacher':
        flash("Access denied.", "danger")
        return redirect(url_for('main.login'))

    courses = Course.query.filter_by(teacher_id=current_user.id).all()

    # Add enrollment count for display
    for course in courses:
        course.enrollment_count = len(course.enrollments)

    return render_template('teacher_dashboard.html', courses=courses)

@main.route('/admin')
@login_required
def admin_dashboard():
    return render_template('admin_dashboard.html')

@main.route('/course/<int:course_id>')
@login_required
def course_details(course_id):
    course = Course.query.get(course_id)
    if not course or course.teacher_id != current_user.id:
        flash("Course not found or access denied.", "danger")
        return redirect(url_for('main.teacher_dashboard'))

    enrolled_students = [enrollment.student for enrollment in course.enrollments]

    return render_template(
        'course_details.html',
        course=course,
        teacher=current_user,
        students=enrolled_students
    )


@main.route('/all-classes')
@login_required
def all_classes():
    if current_user.role != 'student':
        flash("Access denied.", "danger")
        return redirect(url_for('main.login'))

    courses = Course.query.all()
    return render_template('all_classes.html', courses=courses)


@main.route('/enroll/<int:course_id>', methods=['POST'])
@login_required
def enroll(course_id):
    if current_user.role != 'student':
        return redirect(url_for('main.login'))

    course = Course.query.get(course_id)
    if not course or len(course.enrollments) >= course.capacity:
        flash("Course full or not found.")
        return redirect(url_for('main.student_dashboard'))

    # Avoid duplicate enrollment
    existing = Enrollment.query.filter_by(user_id=current_user.id, course_id=course.id).first()
    if not existing:
        db.session.add(Enrollment(user_id=current_user.id, course_id=course.id))
        db.session.commit()
        flash("Enrolled successfully!")
    return redirect(url_for('main.student_dashboard'))


@main.route('/drop/<int:course_id>', methods=['POST'])
@login_required
def drop(course_id):
    if current_user.role != 'student':
        return redirect(url_for('main.login'))

    enrollment = Enrollment.query.filter_by(user_id=current_user.id, course_id=course_id).first()
    if enrollment:
        db.session.delete(enrollment)
        db.session.commit()
        flash("Dropped course.")
    return redirect(url_for('main.student_dashboard'))
