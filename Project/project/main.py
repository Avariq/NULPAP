from flask import Flask, jsonify, request, Response
from json import dump, dumps
import db.dbcontext as dbcontext
from db.models import User, Course, Request
from project.external_models import UserData, UserToCreate, CourseToCreate, CourseData, RequestToCreate, RequestData
from hasher import HashPassword


def get_decorator(errors=(Exception, ), default_value=''):

    def decorator(func):

        def new_func(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except errors as e:
                print("Got error! ", repr(e))
                return default_value

        return new_func

    return decorator

def create_app():
    app = Flask(__name__)

    Hasher256 = HashPassword()

    @app.route("/api/v1/hello-world-11", methods=['GET'])
    def hello():
        return '<h1 style="color:maroon;">Hello world 11</h1>'

    @app.route("/user/<int:user_id>", methods=['GET'])
    def get_user_by_id(user_id):
        user = dbcontext.get_entry_by_uid(User, user_id)
        if user:
            return jsonify(UserData(user, user.courses).toJSON()), 200
        return Response("User not found.", status=404)

    @app.route("/user", methods=['POST'])
    def create_user():
        user_data = UserToCreate().load(request.json)
        if user_data:
            user_data['password'] = Hasher256.Hash(user_data['password'])
            user = dbcontext.create_entry(User, **user_data)
            return jsonify(UserData(user).toJSON()), 201
        return Response("Invalid data provided.", status=400)

    @app.route("/user", methods=['GET'])
    def login():
        email = request.args.get('email')
        password = Hasher256.Hash(request.args.get('password'))
        user = dbcontext.get_user_by_email(email)
        if user:
            if password == user.password:
                return Response("JWT Token", status=200)
            return Response("Invalid auth credentials.", status=400)
        return Response("User not found.", status=404)

    @app.route("/user/<int:user_id>", methods=['PUT'])
    def update_user(user_id):
        user = dbcontext.get_entry_by_uid(User, user_id)
        if user:
            user_data = UserToCreate().load(request.json)
            if user_data:
                updated_user = dbcontext.update_user(user_data, user_id)
                return jsonify(UserData(updated_user, updated_user.courses).toJSON()), 200
            return Response("Invalid data provided.", status=400)
        return Response("User not found.", status=404)

    @app.route("/user/<int:user_id>", methods=['DELETE'])
    def delete_user(user_id):
        user = dbcontext.get_entry_by_uid(User, user_id)
        if user:
            if dbcontext.delete_entry_by_uid(User, user_id):
                return Response("User has been successfully deleted.", status=200)
            return Response("Unexpected error occurred.", status=500)
        return Response("User not found.", status=404)

    @app.route("/course", methods=['POST'])
    def create_course():
        course_data = CourseToCreate().load(request.json)

        if course_data:
            course = dbcontext.create_entry(Course, **course_data)
            return jsonify(CourseData(course).toJSON()), 201
        return Response("Invalid data provided.", status=400)

    @app.route("/course", methods=['GET'])
    def get_course():
        c_id = request.args.get('id')
        course = dbcontext.get_entry_by_uid(Course, c_id)
        if course:
            return jsonify(CourseData(course, course.users).toJSON()), 200
        return Response("Course not found.", status=404)

    @app.route("/courses/all", methods=['GET'])
    def get_courses():
        role = request.args.get('role')
        result = []
        if role:
            if role == 'student':
                student_id = request.args.get('id')
                courses = dbcontext.get_accessible_courses(student_id)
                for course in courses:
                    result.append(CourseData(course, course.users).toJSON())
            else:
                courses = dbcontext.get_accessible_courses()
                for course in courses:
                    result.append(CourseData(course, course.users).toJSON())
        else:
            return Response("Invalid data provided.", status=400)

        return jsonify(result, 200)

    @app.route("/course/<int:course_id>", methods=['PUT'])
    def update_course(course_id):
        course = dbcontext.get_entry_by_uid(Course, course_id)
        if course:
            course_data = CourseToCreate().load(request.json)
            if course_data:
                updated_course = dbcontext.update_course(course_data, course_id, course.student_counter)
                return jsonify(CourseData(updated_course, updated_course.users).toJSON()), 200
            return Response("Invalid data provided.", status=400)
        return Response("User not found.", status=404)

    @app.route("/course/<int:course_id>", methods=['DELETE'])
    def delete_course(course_id):
        course = dbcontext.get_entry_by_uid(Course, course_id)
        if course:
            if dbcontext.delete_entry_by_uid(Course, course_id):
                return Response("Course has been successfully deleted.", status=200)
            return Response("Unexpected error occurred.", status=500)
        return Response("Course not found.", status=404)

    @app.route("/course/<int:course_id>/<int:user_id>", methods=['POST'])
    def add_user_to_course(course_id, user_id):
        course = dbcontext.get_entry_by_uid(Course, course_id)
        if course:
            user = dbcontext.get_entry_by_uid(User, user_id)
            if user:
                edited_course = dbcontext.add_user_to_course(course_id, user_id)
                if edited_course:
                    return jsonify(CourseData(edited_course, edited_course.users).toJSON(), 201)
                return Response("The course has no place to spare", 400)
            return Response("User not found.", status=404)
        return Response("Course not found.", status=404)

    @app.route("/request", methods=['POST'])
    def create_request():
        request_data = RequestToCreate().load(request.json)
        if request_data:
            course_id = request_data['course_id']
            teacher_id = dbcontext.get_teacher_id_by_course_id(course_id)
            if teacher_id:
                request_data['teacher_id'] = teacher_id
                req = dbcontext.create_entry(Request, **request_data)
                return jsonify(RequestData(req).toJSON()), 201
        return Response("Invalid data provided.", status=400)

    @app.route('/request/<int:user_id>/<string:role>', methods=['GET'])
    def get_all_requests(user_id, role):
        if role == 'student':
            requests = dbcontext.get_student_requests(user_id)
        elif role == 'teacher':
            requests = dbcontext.get_teacher_pending_requests(user_id)
        else:
            return Response("Invalid data provided.", status=400)

        result = []
        for req in requests:
            result.append(RequestData(req).toJSON())
        return jsonify(result), 200

    @app.route("/request/<int:request_id>/<int:user_id>/<string:role>", methods=['DELETE'])
    def delete_request(request_id, user_id, role):
        req = dbcontext.get_entry_by_uid(Request, request_id)
        if req:
            if role == 'student':
                if req.student_id == user_id:
                    if dbcontext.delete_entry_by_uid(Request, request_id):
                        return Response("Request has been successfully deleted.", status=200)
                    return Response("Unexpected error occurred.", status=500)
                return Response("Access denied.", status=403)
            elif role == 'teacher':
                if req.teacher_id == user_id:
                    if dbcontext.delete_entry_by_uid(Request, request_id):
                        return Response("Request has been successfully deleted.", status=200)
                    return Response("Unexpected error occurred.", status=500)
                return Response("Access denied.", status=403)
        return Response("Request not found.", status=404)










    return app
