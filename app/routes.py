from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from .models import User, Course, Enrollment
from .forms import LoginForm
from . import db, login_manager, bcrypt

main = Blueprint('main', __name__)

# ------------------------------
# USER SESSION & AUTHENTICATION
# ------------------------------

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
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Logged in successfully!', 'success')

            # Redirect based on role
            role_redirects = {
                'student': 'main.student_dashboard',
                'teacher': 'main.teacher_dashboard',
                'admin': 'admin.index'
            }
            return redirect(url_for(role_redirects.get(user.role, 'main.login')))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html', form=form)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('main.login'))


# ------------------------------
# STUDENT ROUTES
# ------------------------------

@main.route('/student')
@login_required
def student_dashboard():
    if current_user.role != 'student':
        flash("Access denied.", "danger")
        return redirect(url_for('main.login'))

    all_courses = Course.query.all()
    enrolled_course_ids = [e.course_id for e in current_user.enrollments]

    # 👇 Extract first name from full_name
    first_name = current_user.full_name.split()[0]

    return render_template(
        'student_dashboard.html',
        all_courses=all_courses,
        enrolled_course_ids=enrolled_course_ids,
        first_name=first_name
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
        flash("Access denied.", "danger")
        return redirect(url_for('main.login'))

    course = Course.query.get_or_404(course_id)
    if len(course.enrollments) >= course.capacity:
        flash("Course is full.", "error")
        return redirect(url_for('main.student_dashboard'))

    existing = Enrollment.query.filter_by(user_id=current_user.id, course_id=course.id).first()
    if not existing:
        db.session.add(Enrollment(user_id=current_user.id, course_id=course.id))
        db.session.commit()
        flash("Enrolled successfully!", "success")
    else:
        flash("You are already enrolled in this course.", "warning")

    return redirect(url_for('main.student_dashboard'))

@main.route('/drop/<int:course_id>', methods=['POST'])
@login_required
def drop(course_id):
    if current_user.role != 'student':
        flash("Access denied.", "danger")
        return redirect(url_for('main.login'))

    enrollment = Enrollment.query.filter_by(user_id=current_user.id, course_id=course_id).first()
    if enrollment:
        db.session.delete(enrollment)
        db.session.commit()
        flash("Dropped course successfully.", "success")
    else:
        flash("You are not enrolled in this course.", "error")

    return redirect(url_for('main.student_dashboard'))


# ------------------------------
# TEACHER ROUTES
# ------------------------------

@main.route('/teacher')
@login_required
def teacher_dashboard():
    if current_user.role != 'teacher':
        flash("Access denied.", "danger")
        return redirect(url_for('main.login'))

    courses = Course.query.filter_by(teacher_id=current_user.id).all()

    for course in courses:
        course.enrollment_count = len(course.enrollments)

    # Extract last name from full_name
    last_name = current_user.full_name.split()[-1]
    greeting = f"Welcome, Dr. {last_name}!"

    return render_template('teacher_dashboard.html', courses=courses, greeting=greeting)


# adjusted course details
@main.route('/course/<int:course_id>')
@login_required
def course_details(course_id):
    if current_user.role != 'teacher':
        flash("Access denied.", "danger")
        return redirect(url_for('main.login'))

    course = Course.query.get_or_404(course_id)

    if course.teacher_id != current_user.id:
        flash("You do not have permission to view details for this course.", "danger")
        return redirect(url_for('main.teacher_dashboard'))

    enrollments = Enrollment.query.filter_by(course_id=course.id).all()

    return render_template(
        'course_details.html',
        course=course,
        teacher=current_user,
        enrollments=enrollments
    )

# added new route for changing grades
@main.route('/edit_grade/<int:enrollment_id>', methods=['POST'])
@login_required
def edit_grade(enrollment_id):
    if current_user.role != 'teacher':
        flash("Access denied.", "danger")
        return redirect(url_for('main.login'))

    enrollment = Enrollment.query.get_or_404(enrollment_id)
    course = enrollment.course

    if course.teacher_id != current_user.id:
        flash("You do not have permission to edit grades for this course.", "danger")
        return redirect(url_for('main.teacher_dashboard'))

    new_grade = request.form.get('grade')

    enrollment.grade = new_grade
    try:
        db.session.commit()
        flash(f"Grade updated successfully for {enrollment.student.username}.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error updating grade: {str(e)}", "danger")

    return redirect(url_for('main.course_details', course_id=course.id))