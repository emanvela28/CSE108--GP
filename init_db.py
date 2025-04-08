from app import create_app, db

app = create_app()

with app.app_context():
    # Import models inside the app context to avoid circular imports
    from app.models import User, Course, Enrollment

    # OPTIONAL: Reset the database (comment these out if you don’t want to wipe data)
    db.drop_all()
    db.create_all()

    # Add test users
    student = User(username='sally', password='pass123', role='student')
    teacher = User(username='tony', password='teach123', role='teacher')
    admin = User(username='admin1', password='admin123', role='admin')

    db.session.add_all([student, teacher, admin])
    db.session.commit()

    print("Database tables created and test users added!")
