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
        courses = entry.courses
    session.close()
    return entry

def delete_entry_by_uid(model_class, uid):
    session = Session()

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
