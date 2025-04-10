from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from .models import User
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

# Placeholder dashboards
@main.route('/student')
@login_required
def student_dashboard():
    return render_template('student_dashboard.html')

@main.route('/teacher')
@login_required
def teacher_dashboard():
    return render_template('teacher_dashboard.html')

@main.route('/admin')
@login_required
def admin_dashboard():
    return render_template('admin_dashboard.html')

