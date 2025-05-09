from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from .models import User, Topic, Post, Reply, Vote
from .forms import LoginForm, RegisterForm
from . import db, login_manager, bcrypt

main = Blueprint('main', __name__)

# ------------------------------
# USER SESSION & AUTHENTICATION
# ------------------------------
@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)

        db.session.add(user)
        db.session.commit()
        flash("Your account has been created! You are now able to log in.", 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', title='Register', form=form)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@main.route('/')
@main.route('/home')
@main.route('/topics')
@login_required
def topics_index():
    all_topics = Topic.query.order_by(Topic.name).all()
    return render_template('topics_index.html', title='Forum Topics', topics = all_topics)

@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('main.topics_index'))

        else:
            flash('Login unsuccessful, please check username or password.', 'danger')
    return render_template('login.html', title='Login', form=form)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('main.login'))

@main.route('/topic/<topic_slug>')
@login_required
def topic_page(topic_slug):
    topic = Topic.query.filter_by(slug=topic_slug).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts_pagination = Post.query


    return f"Temp page for topic: {topic.name} (slug: {topic_slug}). Pending posts flow"