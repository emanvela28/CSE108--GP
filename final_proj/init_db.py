from app import create_app, db, bcrypt #adding bcrypt for passwords
import re

app = create_app()

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'\s+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')

with app.app_context():

    from app.models import User, Topic, Post, Reply, Vote

    db.drop_all()
    db.create_all()


    #hashed test users
    hashed_pw_sally = bcrypt.generate_password_hash('pass123').decode('utf-8')
    student = User(username='sally', password=hashed_pw_sally, role='student')

    hashed_pw_tony = bcrypt.generate_password_hash('teach123').decode('utf-8')
    moderator_mike = User(username='moderator', password=hashed_pw_mike, role='moderator')

    hashed_pw_admin = bcrypt.generate_password_hash('admin123').decode('utf-8')
    admin_user = User(username='admin1', password=hashed_pw_admin, role='admin')

    db.session.add_all([student, moderator_mike, admin_user])
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