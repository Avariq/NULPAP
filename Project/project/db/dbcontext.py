from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from project.db.models import User, Course, Request
from project.config import DB_URI

engine = create_engine(DB_URI)
engine.connect()
Session = sessionmaker(bind=engine, expire_on_commit=False)


def create_entry(model_class, *, commit=True, **kwargs):
    session = Session()
    entry = model_class(**kwargs)
    session.add(entry)
    if commit:
        session.commit()
    session.close()
    return entry


def get_entry_by_uid(model_class, uid):
    session = Session()
    entry = session.query(model_class).filter(model_class.id == uid).one_or_none()
    if entry:
        if model_class.__tablename__ == 'user':
            courses = entry.courses
        elif model_class.__tablename__ == 'course':
            users = entry.users
    session.close()
    return entry

def delete_entry_by_uid(model_class, uid):
    session = Session()

    entry = session.query(model_class).filter(model_class.id == uid).one_or_none()
    if model_class.__tablename__ == 'user':
        entry.courses = []
    elif model_class.__tablename__ == 'course':
        entry.users = []

    session.commit()
    session.query(model_class).filter(model_class.id == uid).delete()
    session.commit()

    session.close()
    return True

def get_user_by_email(email):
    session = Session()
    entry = session.query(User).filter_by(email=email).one_or_none()
    session.close()
    return entry

def update_user(user_data, user_id):
    session = Session()

    session.query(User).filter(User.id == user_id).update(user_data, synchronize_session=False)
    session.commit()
    user = get_entry_by_uid(User, user_id)
    none = user.courses
    session.close()

    return user

def get_accessible_courses(uid=None):
    session = Session()

    if uid:
        student = session.query(User).filter(User.id == uid).one_or_none()
        if student:
            return student.courses

    courses = session.query(Course).all()
    return courses

def update_course(course_data, course_id, student_count):
    session = Session()

    course_data['student_counter'] = student_count
    session.query(Course).filter(Course.id == course_id).update(course_data, synchronize_session=False)
    session.commit()
    course = get_entry_by_uid(Course, course_id)
    none = course.users
    session.close()

    return course

def add_user_to_course(course_id, user_id):
    session = Session()

    course = session.query(Course).filter(Course.id == course_id).one()
    user = session.query(User).filter(User.id == user_id).one()

    if course.student_counter < 5:
        course.users.append(user)
        course.student_counter += 1
        session.commit()
        session.close()
        return course
    session.close()
    return False

def get_teacher_id_by_course_id(course_id):
    session = Session()

    course = session.query(Course).filter(Course.id == course_id).one_or_none()
    if course:
        users = course.users
        for user in users:
            if user.role == 'teacher':
                session.close()
                return user.id
    session.close()
    return False

def get_student_requests(student_id):
    session = Session()

    requests = session.query(Request).filter(Request.student_id == student_id).all()
    session.close()

    return requests

def get_teacher_pending_requests(teacher_id):
    session = Session()

    requests = session.query(Request).filter(Request.teacher_id == teacher_id).all()
    session.close()

    return requests




