from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from random import randint

from project.db.models import User, Course, Request
from project.config import DB_URI

engine = create_engine(DB_URI)
engine.connect()

session = Session(engine)

users = []
courses = []
requests = []

def generate_users():
    id = 1

    students = [
        "Adela Lynn",
        "Tamsin Finley",
        "Bo Woodard",
        "Amaan Kelley",
        "Amal Marsh",
    ]

    teachers = [
        "Nelly Mcdonald",
        "Giacomo Riley",
        "Ho Henson",
        "Catriona Williams",
        "Eloisa Paterson"
    ]

    for student in students:
        users.append(
            User(
                id=id,
                role="student",
                email=f"{student.split()[0]}@mail.com",
                password=f"{student.split()[1]}",
                first_name=f"{student.split()[0]}",
                last_name=f"{student.split()[1]}"
            )
        )

        id += 1

    for teacher in teachers:
        users.append(
            User(
                id=id,
                role="teacher",
                email=f"{teacher.split()[0]}@mail.com",
                password=f"{teacher.split()[1]}",
                first_name=f"{teacher.split()[0]}",
                last_name=f"{teacher.split()[1]}"
            )
        )

        id += 1

def generate_courses():
    course_id = 1
    names = ["Civil and Environmental Engineering.", "Mechanical Engineering.", "Materials Science and Engineering.", "Architecture"]

    for name in names:
        counter = randint(1, 5)
        course = Course(
                id=course_id,
                name=name,
                description=f"{name} course description",
                hours_to_complete=randint(1, 100),
                educational_material="material",
                student_counter=counter
        )

        courses.append(course)
        course_id += 1

def generate_requests():
    for i in range(0, 5):
        requests.append(
            Request(
                id=i+1,
                student_id=users[i].id,
                teacher_id=users[randint(5, 9)].id,
                course_id=courses[randint(0, 3)].id
            )
        )

generate_users()
session.add_all(users)
session.commit()

generate_courses()
session.add_all(courses)
session.commit()

for course in courses:
    course.users.append(users[randint(5, 9)])
    for i in range(course.student_counter):
        course.users.append(users[randint(0, 4)])
session.commit()

generate_requests()
session.add_all(requests)
session.commit()