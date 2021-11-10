
from sqlalchemy import (
    Table,
    Integer,
    String, 
    Column,
    Enum,
    ForeignKey
)

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import CheckConstraint


Base = declarative_base()

course_membership = Table('course_membership', Base.metadata, 
    Column('user_id', Integer(), ForeignKey("user.id")),
    Column('course_id', Integer(), ForeignKey("course.id"))
)

class User(Base):
    __tablename__ = "user"

    id  = Column(Integer(), autoincrement=True, primary_key=True)
    role = Column(Enum("student", "teacher"), nullable=False)
    email = Column(String(255), nullable=False)
    password = Column(String(45), nullable=False)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)

class Course(Base):
    __tablename__ = "course"
    __table_args__ = (
        CheckConstraint('student_counter <= 5'),
    )

    id  = Column(Integer(), autoincrement=True, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(String(255), nullable=False)
    hours_to_complete = Column(Integer(), nullable=False)
    educational_material = Column(String(255), nullable=False)
    student_counter = Column(Integer(), nullable=False)

    users = relationship("User", secondary=course_membership, backref="courses")

class Request(Base):
    __tablename__ = "request"

    id  = Column(Integer(), autoincrement=True, primary_key=True)
    student_id = Column(Integer(), ForeignKey("user.id"))
    teacher_id = Column(Integer(), ForeignKey("user.id"))
    course_id = Column(Integer(), ForeignKey("course.id"))