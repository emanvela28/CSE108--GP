from flask import Flask, redirect, url_for, render_template, flash
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField
from wtforms.validators import DataRequired
from wtforms.fields import SelectField

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'main.login'
bcrypt = Bcrypt()

# Secure base model view
class SecureModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == 'admin'
    
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('main.login'))

# Custom admin home
class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated or current_user.role != 'admin':
            return redirect(url_for('main.login'))

        from .models import User, Course, Enrollment
        user_count = User.query.count()
        course_count = Course.query.count()
        enrollment_count = Enrollment.query.count()

        return self.render('admin/index.html',
                           user_count=user_count,
                           course_count=course_count,
                           enrollment_count=enrollment_count)

# Admin Form
class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password')  # Optional unless creating a new user
    role = SelectField('Role', choices=[
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('admin', 'Admin')
    ])

# UserAdmin with auto password hashing
class UserAdmin(SecureModelView):
    form = UserForm
    column_exclude_list = ['password']
    column_searchable_list = ['username', 'role']
    column_filters = ['role']

    def delete_model(self, model):
        if model.role == 'teacher' and model.courses_taught:
            flash("❌ Cannot delete teacher who is assigned to courses.", "error")
            return False
        return super().delete_model(model)

    def on_model_change(self, form, model, is_created):
        raw_password = form.password.data

        # Hash password if new or changed
        if raw_password:
            if not raw_password.startswith("$2b$"):
                model.password = bcrypt.generate_password_hash(raw_password).decode('utf-8')
        else:
            # If no password was entered on edit, preserve the existing one
            if not is_created:
                existing = User.query.get(model.id)
                model.password = existing.password
            else:
                flash("⚠️ Password is required for new users.", "error")
                raise ValueError("Password cannot be empty for new users.")


# CourseAdmin with teacher name display
class CourseAdmin(SecureModelView):
    column_list = ['name', 'capacity', 'teacher_name', 'time']
    column_labels = {'teacher_name': 'Professor'}
    column_searchable_list = ['name']
    form_columns = ['name', 'capacity', 'teacher_id', 'time']

    def _teacher_name(view, context, model, name):
        return model.teacher.username if model.teacher else "N/A"

    column_formatters = {
        'teacher_name': _teacher_name
    }

# EnrollmentAdmin with AJAX search fields
class EnrollmentAdmin(SecureModelView):
    column_list = ['student.username', 'course.name', 'grade']
    column_labels = {
        'student.username': 'Student',
        'course.name': 'Course',
        'grade': 'Grade'
    }
    form_columns = ['student', 'course', 'grade']  # use relationship fields

    form_ajax_refs = {
        'student': {
            'fields': ('username',)
        },
        'course': {
            'fields': ('name',)
        }
    }



# App factory
def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'supersecretkey'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../instance/app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)

    from .routes import main
    from .models import User, Course, Enrollment
    app.register_blueprint(main)

    admin = Admin(app, name='Admin Panel', template_mode='bootstrap4', index_view=MyAdminIndexView())
    admin.add_view(UserAdmin(User, db.session))
    admin.add_view(CourseAdmin(Course, db.session))
    admin.add_view(EnrollmentAdmin(Enrollment, db.session))

    return app
