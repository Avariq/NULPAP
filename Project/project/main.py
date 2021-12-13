from flask import Flask, jsonify, request, Response
from sqlalchemy.orm import session
from flask_sqlalchemy import SQLAlchemy
from json import dump, dumps
import project.db.dbcontext as dbcontext
from project.db.models import User, Course, Request
from project.external_models import UserData, UserToCreate, CourseToCreate, CourseData, RequestToCreate, RequestData
from project.hasher import HashPassword
from project.config import DB_URI
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

def create_app():
    app = Flask(__name__)
    auth = HTTPBasicAuth()
    app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db = SQLAlchemy(app)
    db.create_all()
    db.session.commit()

    Hasher256 = HashPassword()

    @auth.verify_password
    def verify_password(username, password):
        user = db.session.query(User).filter_by(email=username).first()
        password = Hasher256.Hash(password)
        if user != None and user.password == password:
            return username

    def get_current_user():
        return db.session.query(User).filter_by(email=auth.current_user()).first()

    @app.route("/api/v1/hello-world-11", methods=['GET'])
    def hello():
        return '<h1 style="color:maroon;">Hello world 11</h1>', 200

    @app.route("/user", methods=['POST'])
    def create_user():
        # "{\"role\": \"student\", \"email\": \"Unique@mail.com\", \"password\": \"whom\", \"first_name\": \"Renner\", \"last_name\": \"Finn\"}"
        user_data = UserToCreate().load(request.json)
        if not user_data:
             return jsonify(message="Invalid data provided."), 400

        if_exists = dbcontext.get_user_by_email(user_data["email"])
        if not if_exists:
            user_data['password'] = Hasher256.Hash(user_data['password'])
            user = dbcontext.create_entry(User, **user_data)
            return jsonify(UserData(user).toJSON()), 201
        return jsonify(message="User with such email already exists"), 400

    @app.route("/user", methods=['GET'])
    def login():
        # http://127.0.0.1:88/user?email=Unique@mail.com&password=whom
        email = request.args.get('email')
        password = Hasher256.Hash(request.args.get('password'))
        user = dbcontext.get_user_by_email(email)
        if user:
            if password == user.password:
                return Response("JWT Token", status=200)
            return Response("Invalid auth credentials.", status=400)
        return Response("User not found.", status=404)

    @app.route("/user/<int:user_id>", methods=['GET'])
    @auth.login_required
    def get_user_by_id(user_id):
        user = dbcontext.get_entry_by_uid(User, user_id)
        current_user = get_current_user()
        if user:
            if current_user.email == user.email:
                return jsonify(UserData(user, user.courses).toJSON()), 200
            return Response("Access denied.", status=403)
        return Response("User not found.", status=404)

    @app.route("/user/<int:user_id>", methods=['PUT'])
    @auth.login_required
    def update_user(user_id):
        # "{\"role\": \"student\", \"email\": \"Unique@mail.com\", \"password\": \"whoom\", \"first_name\": \"Renner\", \"last_name\": \"Finn\"}"
        user = dbcontext.get_entry_by_uid(User, user_id)
        current_user = get_current_user()
        if user:
            if current_user.email == user.email:
                user_data = UserToCreate().load(request.json)
                if user_data:
                    user_data['password'] = Hasher256.Hash(user_data['password'])
                    updated_user = dbcontext.update_user(user_data, user_id)
                    return jsonify(UserData(updated_user, updated_user.courses).toJSON()), 200
                return Response("Invalid data provided.", status=400)
            return Response("Access denied.", status=403)
        return Response("User not found.", status=404)

    @app.route("/user/<int:user_id>", methods=['DELETE'])
    @auth.login_required
    def delete_user(user_id):
        user = dbcontext.get_entry_by_uid(User, user_id)
        current_user = get_current_user()
        if user:
            if current_user.email == user.email:
                if dbcontext.delete_entry_by_uid(User, user_id):
                    return Response("User has been successfully deleted.", status=200)
                return Response("Unexpected error occurred.", status=500)
            return Response("Access denied.", status=403)
        return Response("User not found.", status=404)

    @app.route("/course", methods=['POST'])
    @auth.login_required
    def create_course():
        current_user = get_current_user()
        if current_user.role == "teacher":
            # "{\"name\": \"Some new course!.\", \"description\": \"Some new course! course description\", \"hours_to_complete\": 14, \"educational_material\": \"material\"}"
            course_data = CourseToCreate().load(request.json)

            if course_data:
                course = dbcontext.create_entry(Course, **course_data)
                return jsonify(CourseData(course).toJSON()), 201
            return Response("Invalid data provided.", status=400)
        else:
            return Response("Access denied.", status=403)

    @app.route("/course", methods=['GET'])
    @auth.login_required
    def get_course():
        # http://127.0.0.1:88/course?id=1
        current_user = get_current_user()
        c_id = request.args.get('id')
        current_course = dbcontext.get_entry_by_uid(Course, c_id)
        if current_course:
            if current_user.role == "teacher":
                return jsonify(CourseData(current_course, current_course.users).toJSON()), 200
            elif current_user.role == "student":
                student_id = current_user.id
                courses = dbcontext.get_accessible_courses(student_id)
                for i in courses:
                    course = CourseData(i, i.users)
                    if course.id == c_id:
                        return jsonify(CourseData(current_course, current_course.users).toJSON()), 200
                return Response("You have none courses.", status=200)
        return Response("Course not found.", status=404)

    @app.route("/courses/all", methods=['GET'])
    @auth.login_required
    def get_courses():
        # http://127.0.0.1:88/courses/all
        current_user = get_current_user()
        result = []
        if current_user.role == "teacher":
            courses = dbcontext.get_accessible_courses()
            for course in courses:
                result.append(CourseData(course, course.users).toJSON())
        else:
            student_id = current_user.id
            courses = dbcontext.get_accessible_courses(student_id)
            for course in courses:
                result.append(CourseData(course, course.users).toJSON())
        return jsonify(result, 200)

    @app.route("/course/<int:course_id>", methods=['PUT'])
    @auth.login_required
    def update_course(course_id):
        # "{\"name\": \"Some new course!.\", \"description\": \"Some new course! course edited description\", \"hours_to_complete\": 14, \"educational_material\": \"material\"}"
        current_user = get_current_user()
        course = dbcontext.get_entry_by_uid(Course, course_id)
        if course:
            if current_user.role == "teacher":
                course_data = CourseToCreate().load(request.json)
                if course_data:
                    updated_course = dbcontext.update_course(course_data, course_id, course.student_counter)
                    return jsonify(CourseData(updated_course, updated_course.users).toJSON()), 200
                return Response("Invalid data provided.", status=400)
            else:
                return Response("Access denied.", status=403)
        return Response("Course not found.", status=404)

    @app.route("/course/<int:course_id>", methods=['DELETE'])
    @auth.login_required
    def delete_course(course_id):
        current_user = get_current_user()
        course = dbcontext.get_entry_by_uid(Course, course_id)
        if course:
            if current_user.role == "teacher":
                if dbcontext.delete_entry_by_uid(Course, course_id):
                    return Response("Course has been successfully deleted.", status=200)
            return Response("Access denied.", status=403)
        return Response("Course not found.", status=404)

    @app.route("/course/<int:course_id>/<int:user_id>", methods=['POST'])
    @auth.login_required
    def add_user_to_course(course_id, user_id):
        current_user = get_current_user()
        course = dbcontext.get_entry_by_uid(Course, course_id)
        if current_user.role == "teacher":
            if course:
                user = dbcontext.get_entry_by_uid(User, user_id)
                if user:
                    edited_course = dbcontext.add_user_to_course(course_id, user_id)
                    if edited_course:
                        return jsonify(CourseData(edited_course, edited_course.users).toJSON(), 201)
                    return Response("The course has no place to spare", 400)
                return Response("User not found.", status=404)
            return Response("Course not found.", status=404)
        return Response("Access denied.", status=403)

    @app.route("/request", methods=['POST'])
    @auth.login_required
    def create_request():
        # "{\"student_id\": 4, \"course_id\": 2}"
        current_user = get_current_user()
        if request.json is None: return Response("Invalid data provided.", status=400)

        request_data = RequestToCreate().load(request.json)
        if request_data['student_id'] != current_user.id:
            return Response("Access denied.", status=403)
        user = dbcontext.get_entry_by_uid(User, request_data['student_id'])
        if current_user.role == "student":
            if user:
                if user.role == "student":
                    course_id = request_data['course_id']
                    teacher_id = dbcontext.get_teacher_id_by_course_id(course_id)
                    if teacher_id:
                        request_data['teacher_id'] = teacher_id
                        req = dbcontext.create_entry(Request, **request_data)
                        return jsonify(RequestData(req).toJSON()), 201
                return Response("Access denied.", status=403)
            return jsonify(message="Student not found"), 404
        return Response("Access denied.", status=403)

    @app.route('/request/<int:user_id>', methods=['GET'])
    @auth.login_required
    def get_all_requests(user_id):
        current_user = get_current_user()
        if current_user.role == 'student':
            if user_id != current_user.id:
                return Response("Access denied.", status=403)
            requests = dbcontext.get_student_requests(current_user.id)
        elif current_user.role == 'teacher':
            requests = dbcontext.get_teacher_pending_requests(user_id)
        result = []
        for req in requests:
            result.append(RequestData(req).toJSON())
        return jsonify(result), 200

    @app.route("/request/<int:request_id>/<int:user_id>", methods=['DELETE'])
    @auth.login_required
    def delete_request(request_id, user_id):
        current_user = get_current_user()
        req = dbcontext.get_entry_by_uid(Request, request_id)
        course_id = req.course_id
        student_id = req.student_id
        if req:
            if current_user.role == 'student':
                if req.student_id == user_id and current_user.id == user_id:
                    if dbcontext.delete_entry_by_uid(Request, request_id):
                        return Response("Request has been successfully deleted.", status=200)
                    return Response("Unexpected error occurred.", status=500)
                return Response("Access denied.", status=403)
            elif current_user.role == 'teacher':
                if req.teacher_id == user_id:
                    if dbcontext.delete_entry_by_uid(Request, request_id):
                        dbcontext.add_user_to_course(course_id, student_id)
                        return Response("Request has been successfully deleted.", status=200)
                    return Response("Unexpected error occurred.", status=500)
                return Response("Access denied.", status=403)
        return Response("Request not found.", status=404)


    return app


if __name__ == "__main__":
    app = create_app()
    app.run()