from app import create_app, db, bcrypt #adding bcrypt for passwords

app = create_app()

with app.app_context():
    # Import models inside the app context to avoid circular imports
    from app.models import User, Course, Enrollment

    # OPTIONAL: Reset the database (comment these out if you don’t want to wipe data)
    db.drop_all()
    db.create_all()

    # Add test users
    # student = User(username='sally', password='pass123', role='student')
    # teacher = User(username='tony', password='teach123', role='teacher')
    # admin = User(username='admin1', password='admin123', role='admin')

    #hashed test users
    hashed_pw_sally = bcrypt.generate_password_hash('pass123').decode('utf-8')
    student = User(username='sally', password=hashed_pw_sally, role='student')
    hashed_pw_tony = bcrypt.generate_password_hash('teach123').decode('utf-8')
    teacher = User(username='tony', password=hashed_pw_tony, role='teacher')
    hashed_pw_admin = bcrypt.generate_password_hash('admin123').decode('utf-8')
    admin = User(username='admin1', password=hashed_pw_admin, role='admin')
    db.session.add_all([student, teacher, admin])
    db.session.commit()

    #test courses
    course1 = Course(name="CSE 120", capacity=160, teacher_id=teacher.id, time="MW 4:30-5:45 PM")
    course2 = Course(name="CSE 165", capacity=90, teacher_id=teacher.id, time="TR 11:00 12:15 PM")
    db.session.add_all([course1, course2])
    db.session.commit()

    #test enrollments
    enrolled1 = Enrollment(course_id=course1.id, user_id=student.id, grade="A")
    enrolled2 = Enrollment(course_id=course2.id, user_id=student.id, grade="B")
    db.session.add_all([enrolled1, enrolled2])
    db.session.commit()

    print("Database tables created and test users added!")