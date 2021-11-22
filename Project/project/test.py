from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from project.db.models import User, Course, Request
from project.config import DB_URI

engine = create_engine(DB_URI)
engine.connect()

Session = sessionmaker(bind=engine, expire_on_commit=False)
session = Session()

user = session.query(User).join(User.courses).filter(User.id==10).first()
print(user.courses[0].description)

session.close()

