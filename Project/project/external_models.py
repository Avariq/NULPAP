import json
import re


class UserData:
    def __init__(self, usr, courses=[]):
        self.id = usr.id
        self.role = usr.role
        self.email = usr.email
        self.password = usr.password
        self.first_name = usr.first_name
        self.last_name = usr.last_name
        self.courses = list()

        for i in courses:
            self.courses.append({'id' : i.id, 'name' : i.name, 'description' : i.description,
                                 'hours_to_complete' : i.hours_to_complete,
                                 'educational_material' : i.educational_material, 'student_counter' : i.student_counter})

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__)


class UserToCreate:

    def __init__(self):
        self.role = None
        self.email = None
        self.password = None
        self.first_name = None
        self.last_name = None

    def load(self, json_data):
        user_data = json.loads(json_data)
        if self.check(user_data):
            self.role = user_data['role']
            self.email = user_data['email']
            self.password = user_data['password']
            self.first_name = user_data['first_name']
            self.last_name = user_data['last_name']

            return self.__dict__
        return False

    @staticmethod
    def check(user_data):
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if user_data['role'] not in ['teacher', 'student']:
            return False
        if not re.fullmatch(regex, user_data['email']):
            return False
        if len(user_data['password']) > 16:
            return False
        if type(user_data['role']) != str or type(user_data['password']) != str\
                or type(user_data['first_name']) != str or type(user_data['last_name']) != str:
            return False

        return True

class CourseToCreate:

    def __init__(self, ):
        self.name = ''
        self.description = ''
        self.hours_to_complete = 0
        self.educational_material = ''
        self.student_counter = 0

    def load(self, json_data):
        course_data = json.loads(json_data)
        if self.check(course_data):
            self.name = course_data['name']
            self.description = course_data['description']
            self.hours_to_complete = course_data['hours_to_complete']
            self.educational_material = course_data['educational_material']

            return self.__dict__
        return False

    @staticmethod
    def check(course_data):
        if type(course_data['name']) != str:
            return False
        if type(course_data['description']) != str:
            return False
        if type(course_data['hours_to_complete']) != int:
            return False
        if type(course_data['educational_material']) != str:
            return False
        if course_data['hours_to_complete'] < 1:
            return False
        return True


class CourseData:
    def __init__(self, course, users=[]):
        self.id = course.id
        self.name = course.name
        self.description = course.description
        self.hours_to_complete = course.hours_to_complete
        self.educational_material = course.educational_material
        self.student_counter = course.student_counter
        self.users = list()

        for user in users:
            self.users.append({
                'id': user.id, 'role': user.role, 'email': user.email,
                'password': user.password,
                'first_name': user.first_name, 'last_name': user.last_name
            })

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__)


class RequestToCreate:

    def __init__(self):
        self.student_id = 0
        self.teacher_id = 0
        self.course_id = 0

    def load(self, json_data):
        request_data = json.loads(json_data)
        if self.check(request_data):
            self.student_id = request_data['student_id']
            self.course_id = request_data['course_id']

            return self.__dict__
        return False

    @staticmethod
    def check(request_data):
        if type(request_data['student_id']) != int or request_data['student_id'] < 1:
            return False
        if type(request_data['course_id']) != int or request_data['course_id'] < 1:
            return False
        return True

class RequestData:
    def __init__(self, request):
        self.id = request.id
        self.student_id = request.student_id
        self.teacher_id = request.teacher_id
        self.course_id = request.course_id

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__)


