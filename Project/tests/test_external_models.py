import json
from unittest import TestCase
from project.db.models import User, Course, Request
from project.external_models import UserData, UserToCreate, CourseData, CourseToCreate, RequestData, RequestToCreate

class TestUserData(TestCase):
    def setUp(self):
        self.usr = User(
                id=1,
                role='student',
                email='name@mail.com',
                password='1234',
                first_name='name',
                last_name='last name'
            )
        
        self.courses = [Course(
                id=1,
                name="course name",
                description="course description",
                hours_to_complete=5,
                educational_material="material",
                student_counter=2
        )]

        self.usr_data = UserData(self.usr, self.courses)

    def test_usr_to_json(self):
        jsn = self.usr_data.toJSON()
        jsn_str = '{"id": 1, "role": "student", "email": "name@mail.com", "password": "1234", "first_name": "name", "last_name": "last name", "courses": [{"id": 1, "name": "course name", "description": "course description", "hours_to_complete": 5, "educational_material": "material", "student_counter": 2}]}'

        self.assertIsNotNone(jsn)
        self.assertEqual(jsn, jsn_str)

class TestUserToCreate(TestCase):
    def setUp(self):
        self.usr_data = json.loads('{"role": "student", "email": "name@mail.com", "password": "1234", "first_name": "name", "last_name": "last name"}')
        self.wrong_usr_data = json.loads('{"role": 1, "email": "name@.com", "password": 1, "first_name": 2, "last_name": 3}')
        self.usr_to_create = UserToCreate()

    def test_check(self):
        self.assertTrue(UserToCreate.check(self.usr_data))

    def test_load(self):
        self.assertEqual(self.usr_to_create.load(json.dumps(self.usr_data)), self.usr_data)
    
    def test_load_false(self):
        self.assertFalse(self.usr_to_create.load(json.dumps(self.wrong_usr_data)))

class TestCourseData(TestCase):
    def setUp(self):
        self.course = Course(
                id=1,
                name="course name",
                description="course description",
                hours_to_complete=5,
                educational_material="material",
                student_counter=2
        )
        
        self.users = [User(
                id=1,
                role='student',
                email='name@mail.com',
                password='1234',
                first_name='name',
                last_name='last name'
        )]

        self.course_data = CourseData(self.course, self.users)

    def test_course_to_json(self):
        jsn = self.course_data.toJSON()
        jsn_str = '{"id": 1, "name": "course name", "description": "course description", "hours_to_complete": 5, "educational_material": "material", "student_counter": 2, "users": [{"id": 1, "role": "student", "email": "name@mail.com", "password": "1234", "first_name": "name", "last_name": "last name"}]}'

        self.assertIsNotNone(jsn)
        self.assertEqual(jsn, jsn_str)

class TestCourseToCreate(TestCase):
    def setUp(self):
        self.course_data = json.loads('{"name": "course name", "description": "course description", "hours_to_complete": 5, "educational_material": "material", "student_counter": 0}')
        self.wrong_course_data = json.loads('{"name": 1, "description": 2, "hours_to_complete": 5, "educational_material": 3, "student_counter": 0}')
        self.course_to_create = CourseToCreate()

    def test_check(self):
        self.assertTrue(CourseToCreate.check(self.course_data))

    def test_load(self):
        self.assertEqual(self.course_to_create.load(json.dumps(self.course_data)), self.course_data)
    
    def test_load_false(self):
        self.assertFalse(self.course_to_create.load(json.dumps(self.wrong_course_data)))

class TestRequestData(TestCase):
    def setUp(self):
        self.request = Request(
                id=1,
                student_id=1,
                teacher_id=1,
                course_id=1
            )

        self.request_data = RequestData(self.request)

    def test_request_to_json(self):
        jsn = self.request_data.toJSON()
        jsn_str = '{"id": 1, "student_id": 1, "teacher_id": 1, "course_id": 1}'

        self.assertIsNotNone(jsn)
        self.assertEqual(jsn, jsn_str)

class TestRequestToCreate(TestCase):
    def setUp(self):
        self.request_data = json.loads('{"student_id": 1, "teacher_id": 0, "course_id": 1}')
        self.wrong_request_data = json.loads('{"student_id": "asd", "teacher_id": 0, "course_id": 1}')
        self.request_to_create = RequestToCreate()

    def test_check(self):
        self.assertTrue(RequestToCreate.check(self.request_data))

    def test_load(self):
        self.assertEqual(self.request_to_create.load(json.dumps(self.request_data)), self.request_data)
    
    def test_load_false(self):
        self.assertFalse(self.request_to_create.load(json.dumps(self.wrong_request_data)))
