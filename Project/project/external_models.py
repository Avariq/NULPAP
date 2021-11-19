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
            try:
                self.role = user_data['role']
                self.email = user_data['email']
                self.password = user_data['password']
                self.first_name = user_data['first_name']
                self.last_name = user_data['last_name']

                return self.__dict__
            except KeyError:
                return None
        return False

    @staticmethod
    def check(user_data):
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if user_data['role'] not in ['teacher', 'student']:
            return False
        if not re.fullmatch(regex, user_data['email']):
            return False
        if len(user_data['password']) > 64:
            return False

        return True

class CourseToCreate:

    def __init__(self):
        self.name = ''
        self.description = ''
        self.hours_to_complete = 0
        self.educational_material = ''

    def load(self, json_data):
        course_data = json.loads(json_data)
        if self.check(course_data):
            try:
                self.name = course_data['name']
                self.description = course_data['description']
                self.hours_to_complete = course_data['hours_to_complete']
                self.educational_material = course_data['educational_material']

                return self.__dict__
            except KeyError:
                return None
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








