import json
from unittest import TestCase
from base64 import b64encode
from project.main import create_app
from project.db.models import Base, User, Course, Request
import project.db.dbcontext as dbcontex
from project.hasher import HashPassword

class BaseCase(TestCase):
    def setUp(self):
        self.client = create_app().test_client()
        self.haser = HashPassword()
        
        Base.metadata.create_all(dbcontex.engine)

        self.create_user_data = "{\"role\": \"student\", \"email\": \"Unique@mail.com\", \"password\": \"whom\", \"first_name\": \"Renner\", \"last_name\": \"Finn\"}"
        self.local_user_data = "{\"role\": \"student\", \"email\": \"mail@mail.com\", \"password\": \"whom\", \"first_name\": \"Renner\", \"last_name\": \"Finn\"}"
        self.local_user_data1 = "{\"role\": \"teacher\", \"email\": \"mail1@mail.com\", \"password\": \"whom\", \"first_name\": \"Renner\", \"last_name\": \"Finn\"}"
        self.invalid_user_data =  "{\"role\": \"invalid\", \"email\": \"Unique@mail.com\", \"password\": \"whom\", \"first_name\": \"Renner\", \"last_name\": \"Finn\"}"

        self.create_user(self.local_user_data)
        self.create_user(self.local_user_data1)

        self.create_course_data = "{\"name\": \"Some new course!.\", \"description\": \"Some new course! course description\", \"hours_to_complete\": 14, \"educational_material\": \"material\", \"student_counter\": 0}"
        self.local_course = "{\"name\": \"Some other course!.\", \"description\": \"Some other course! course description\", \"hours_to_complete\": 12, \"educational_material\": \"material\", \"student_counter\": 0}"
        self.invalid_course_data = "{\"name\": \"Some new course!.\", \"description\": \"Some new course! course description\", \"hours_to_complete\": 0, \"educational_material\": \"material\"}"

        self.create_course(self.local_course)

        self.create_request_data = "{\"student_id\": 1, \"course_id\": 1}"
        self.create_request_denied = "{\"student_id\": 2, \"course_id\": 1}"

    def tearDown(self):
        Base.metadata.drop_all(dbcontex.engine)

    def url(self, route):
        return f"http://127.0.0.1:5000{route}"

    def create_user(self, json_data):
        data = json.loads(json_data)
        data['password'] = self.haser.Hash(data['password'])
        return dbcontex.create_entry(User, **data)

    def create_course(self, json_data):
        data = json.loads(json_data)
        return dbcontex.create_entry(Course, **data)

    
    def create_auth_headers(self, username, password):
        headers = {
            'Authorization': 'Basic ' + b64encode('{0}:{1}'.format(username, password).encode()).decode()
        }
        return headers

class TestHello(BaseCase):
    def test_hello(self):
        response = self.client.get(self.url("/api/v1/hello-world-11"))
        self.assertEqual(response.data.decode('utf-8'), '<h1 style="color:maroon;">Hello world 11</h1>')


class TestCreateUser(BaseCase):
    def test_success(self):
        response = self.client.post(self.url("/user"), json=self.create_user_data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(b'"{\\"id\\": 3, \\"role\\": \\"student\\", \\"email\\": \\"Unique@mail.com\\", \\"password\\": \\"8e5efdde68f00630418521070210fb398aa5307ed3aada6d563ac745709a0525\\", \\"first_name\\": \\"Renner\\", \\"last_name\\": \\"Finn\\", \\"courses\\": []}"\n', response.data)

    def test_same_email(self):
        response = self.client.post(self.url("/user"), json=self.local_user_data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{"message":"User with such email already exists"}\n')

    def test_invalid_data(self):
        response = self.client.post(self.url("/user"), json=self.invalid_user_data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{"message":"Invalid data provided."}\n')

class TestLogin(BaseCase):
    def test_success(self):
        response = self.client.get(self.url("/user"), query_string={"email": "mail@mail.com", "password": "whom"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b'JWT Token')

    def test_not_found(self):
        response = self.client.get(self.url("/user"), query_string={"email": "mail2@mail.com", "password": "whom"})

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, b'User not found.')

    def test_invalid_data(self):
        response = self.client.get(self.url("/user"), query_string={"email": "mail@mail.com", "password": "whom1"})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'Invalid auth credentials.')

class TestGetUserById(BaseCase):
    def setUp(self):
        super().setUp()
        self.headers = self.create_auth_headers("mail@mail.com", "whom")

    def test_success(self):
        response = self.client.get(self.url(f"/user/{1}"), headers=self.headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b'"{\\"id\\": 1, \\"role\\": \\"student\\", \\"email\\": \\"mail@mail.com\\", \\"password\\": \\"8e5efdde68f00630418521070210fb398aa5307ed3aada6d563ac745709a0525\\", \\"first_name\\": \\"Renner\\", \\"last_name\\": \\"Finn\\", \\"courses\\": []}"\n')

    def test_no_auth(self):
        response = self.client.get(self.url(f"/user/{1}"))

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data, b'Unauthorized Access')

    def test_not_found(self):
        response = self.client.get(self.url(f"/user/{3}"), headers=self.headers)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, b'User not found.')

    def test_access_denied(self):
        response = self.client.get(self.url(f"/user/{2}"), headers=self.headers)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, b'Access denied.')

class TestUpdateUser(BaseCase):
    def setUp(self):
        super().setUp()
        self.headers = self.create_auth_headers("mail@mail.com", "whom")

    def test_success(self):
        response = self.client.put(self.url(f"/user/{1}"), headers=self.headers, json=self.local_user_data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b'"{\\"id\\": 1, \\"role\\": \\"student\\", \\"email\\": \\"mail@mail.com\\", \\"password\\": \\"8e5efdde68f00630418521070210fb398aa5307ed3aada6d563ac745709a0525\\", \\"first_name\\": \\"Renner\\", \\"last_name\\": \\"Finn\\", \\"courses\\": []}"\n')

    def test_no_auth(self):
        response = self.client.put(self.url(f"/user/{1}"), json=self.local_user_data)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data, b'Unauthorized Access')

    def test_not_found(self):
        response = self.client.put(self.url(f"/user/{3}"), headers=self.headers, json=self.local_user_data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, b'User not found.')

    def test_access_denied(self):
        response = self.client.put(self.url(f"/user/{2}"), headers=self.headers)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, b'Access denied.')

    def test_invalid_data(self):
        response = self.client.put(self.url(f"/user/{1}"), headers=self.headers, json=self.invalid_user_data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'Invalid data provided.')

class TestUserDelete(BaseCase):
    def setUp(self):
        super().setUp()
        self.headers = self.create_auth_headers("mail@mail.com", "whom")

    def test_success(self):
        response = self.client.delete(self.url(f"/user/{1}"), headers=self.headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b'User has been successfully deleted.')

    def test_no_auth(self):
        response = self.client.delete(self.url(f"/user/{1}"))

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data, b'Unauthorized Access')

    def test_not_found(self):
        response = self.client.delete(self.url(f"/user/{3}"), headers=self.headers)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, b'User not found.')

    def test_access_denied(self):
        response = self.client.delete(self.url(f"/user/{2}"), headers=self.headers)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, b'Access denied.')

class TestCreateCourse(BaseCase):
    def setUp(self):
        super().setUp()

        self.teacher_headers = self.create_auth_headers("mail1@mail.com", "whom")
        self.student_headers = self.create_auth_headers("mail@mail.com", "whom")

    def test_success(self):
        response = self.client.post(self.url("/course"), headers=self.teacher_headers, json=self.create_course_data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, b'"{\\"id\\": 2, \\"name\\": \\"Some new course!.\\", \\"description\\": \\"Some new course! course description\\", \\"hours_to_complete\\": 14, \\"educational_material\\": \\"material\\", \\"student_counter\\": 0, \\"users\\": []}"\n')

    def test_invalid_data(self):
        response = self.client.post(self.url("/course"), headers=self.teacher_headers, json=self.invalid_course_data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'Invalid data provided.')

    def test_no_auth(self):
        response = self.client.post(self.url("/course"), json=self.create_course_data)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data, b'Unauthorized Access')

    def test_access_denied(self):
        response = self.client.post(self.url("/course"), headers=self.student_headers, json=self.create_course_data)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, b'Access denied.')

class TestGetCourse(BaseCase):
    def setUp(self):
        super().setUp()

        self.teacher_headers = self.create_auth_headers("mail1@mail.com", "whom")
        self.student_headers = self.create_auth_headers("mail@mail.com", "whom")

    def test_success_teacher(self):
        response = self.client.get(self.url("/course"), headers=self.teacher_headers, query_string={"id": 1})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b'"{\\"id\\": 1, \\"name\\": \\"Some other course!.\\", \\"description\\": \\"Some other course! course description\\", \\"hours_to_complete\\": 12, \\"educational_material\\": \\"material\\", \\"student_counter\\": 0, \\"users\\": []}"\n')

    def test_s_student(self):
        response = self.client.get(self.url("/course"), headers=self.student_headers, query_string={"id": 1})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b'You have none courses.')

    def test_student_with_course(self):
        dbcontex.add_user_to_course(1, 1)
        response = self.client.get(self.url("/course"), headers=self.student_headers, query_string={"id": 1})

        self.assertEqual(response.status_code, 200)

    def test_no_auth(self):
        response = self.client.get(self.url("/course"), query_string={"id": 1})

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data, b'Unauthorized Access')

    def test_course_not_found(self):
        response = self.client.get(self.url("/course"), headers=self.teacher_headers, query_string={"id": 3})

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, b'Course not found.')

class TestGetCourses(BaseCase):
    def setUp(self):
        super().setUp()

        self.teacher_headers = self.create_auth_headers("mail1@mail.com", "whom")
        self.student_headers = self.create_auth_headers("mail@mail.com", "whom")

    def test_success_teacher(self):
        response = self.client.get(self.url("/courses/all"), headers=self.teacher_headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b'[["{\\"id\\": 1, \\"name\\": \\"Some other course!.\\", \\"description\\": \\"Some other course! course description\\", \\"hours_to_complete\\": 12, \\"educational_material\\": \\"material\\", \\"student_counter\\": 0, \\"users\\": []}"],200]\n')

    def test_s_student(self):
        response = self.client.get(self.url("/courses/all"), headers=self.student_headers, query_string={"id": 1})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b'[[],200]\n')

    def test_student_with_course(self):
        dbcontex.add_user_to_course(1, 1)
        response = self.client.get(self.url("/courses/all"), headers=self.student_headers, query_string={"id": 1})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b'[["{\\"id\\": 1, \\"name\\": \\"Some other course!.\\", \\"description\\": \\"Some other course! course description\\", \\"hours_to_complete\\": 12, \\"educational_material\\": \\"material\\", \\"student_counter\\": 1, \\"users\\": [{\\"id\\": 1, \\"role\\": \\"student\\", \\"email\\": \\"mail@mail.com\\", \\"password\\": \\"8e5efdde68f00630418521070210fb398aa5307ed3aada6d563ac745709a0525\\", \\"first_name\\": \\"Renner\\", \\"last_name\\": \\"Finn\\"}]}"],200]\n')

    def test_no_auth(self):
        response = self.client.get(self.url("/courses/all"))

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data, b'Unauthorized Access')

class TestUpdateCourse(BaseCase):
    def setUp(self):
        super().setUp()

        self.teacher_headers = self.create_auth_headers("mail1@mail.com", "whom")
        self.student_headers = self.create_auth_headers("mail@mail.com", "whom")

    def test_success(self):
        response = self.client.put(self.url("/course/1"), headers=self.teacher_headers, json=self.create_course_data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b'"{\\"id\\": 1, \\"name\\": \\"Some new course!.\\", \\"description\\": \\"Some new course! course description\\", \\"hours_to_complete\\": 14, \\"educational_material\\": \\"material\\", \\"student_counter\\": 0, \\"users\\": []}"\n')

    def test_invalid_data(self):
        response = self.client.put(self.url("/course/1"), headers=self.teacher_headers, json=self.invalid_course_data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'Invalid data provided.')

    def test_no_auth(self):
        response = self.client.put(self.url("/course/1"), json=self.create_course_data)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data, b'Unauthorized Access')

    def test_access_denied(self):
        response = self.client.put(self.url("/course/1"), headers=self.student_headers, json=self.create_course_data)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, b'Access denied.')

    def test_course_not_found(self):
        response = self.client.put(self.url("/course/2"), headers=self.teacher_headers, json=self.create_course_data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, b'Course not found.')

class TestDeleteCourse(BaseCase):
    def setUp(self):
        super().setUp()

        self.teacher_headers = self.create_auth_headers("mail1@mail.com", "whom")
        self.student_headers = self.create_auth_headers("mail@mail.com", "whom")

    def test_success_teacher(self):
        response = self.client.delete(self.url("/course/1"), headers=self.teacher_headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b'Course has been successfully deleted.')


    def test_no_auth(self):
        response = self.client.delete(self.url("/course/1"))

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data, b'Unauthorized Access')

    def test_access_denied(self):
        response = self.client.delete(self.url("/course/1"), headers=self.student_headers)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, b'Access denied.')

    def test_course_not_found(self):
        response = self.client.delete(self.url("/course/2"), headers=self.teacher_headers)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, b'Course not found.')

class TestAddUserToCourse(BaseCase):
    def setUp(self):
        super().setUp()

        self.teacher_headers = self.create_auth_headers("mail1@mail.com", "whom")
        self.student_headers = self.create_auth_headers("mail@mail.com", "whom")

    def test_success(self):
        response = self.client.post(self.url("/course/1/2"), headers=self.teacher_headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b'["{\\"id\\": 1, \\"name\\": \\"Some other course!.\\", \\"description\\": \\"Some other course! course description\\", \\"hours_to_complete\\": 12, \\"educational_material\\": \\"material\\", \\"student_counter\\": 1, \\"users\\": [{\\"id\\": 2, \\"role\\": \\"teacher\\", \\"email\\": \\"mail1@mail.com\\", \\"password\\": \\"8e5efdde68f00630418521070210fb398aa5307ed3aada6d563ac745709a0525\\", \\"first_name\\": \\"Renner\\", \\"last_name\\": \\"Finn\\"}]}",201]\n')

    def test_no_auth(self):
        response = self.client.post(self.url("/course/1/2"))

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data, b'Unauthorized Access')

    def test_access_denied(self):
        response = self.client.post(self.url("/course/1/2"), headers=self.student_headers)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, b'Access denied.')

    def test_course_not_found(self):
        response = self.client.post(self.url("/course/2/2"), headers=self.teacher_headers)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, b'Course not found.')
    
    def test_user_not_found(self):
        response = self.client.post(self.url("/course/1/3"), headers=self.teacher_headers)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, b'User not found.')

class TestCreateRequest(BaseCase):
    def setUp(self):
        super().setUp()

        self.teacher_headers = self.create_auth_headers("mail1@mail.com", "whom")
        self.student_headers = self.create_auth_headers("mail@mail.com", "whom")

    def test_success(self):
        dbcontex.add_user_to_course(1, 2)
        response = self.client.post(self.url("/request"), headers=self.student_headers, json=self.create_request_data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, b'"{\\"id\\": 1, \\"student_id\\": 1, \\"teacher_id\\": 2, \\"course_id\\": 1}"\n')

    def test_invalid_data(self):
        response = self.client.post(self.url("/request"), headers=self.student_headers)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'Invalid data provided.')

    def test_no_auth(self):
        response = self.client.post(self.url("/request"), json=self.create_request_data)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data, b'Unauthorized Access')

    def test_access_denied(self):
        response = self.client.post(self.url("/request"), headers=self.teacher_headers, json=self.create_request_data)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, b'Access denied.')

    def test_access_deniend1(self):
        response = self.client.post(self.url("/request"), headers=self.student_headers, json=self.create_request_denied)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, b'Access denied.')

class TestGetRequests(BaseCase):
    def setUp(self):
        super().setUp()

        self.teacher_headers = self.create_auth_headers("mail1@mail.com", "whom")
        self.student_headers = self.create_auth_headers("mail@mail.com", "whom")

        dbcontex.add_user_to_course(1, 2)
        dbcontex.create_entry(Request, **json.loads('{"student_id": 1, "course_id": 1}'))

    def test_success_teacher(self):
        response = self.client.get(self.url("/request/2"), headers=self.teacher_headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b'[]\n')

    def test_success_student(self):
        response = self.client.get(self.url("/request/1"), headers=self.student_headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b'["{\\"id\\": 1, \\"student_id\\": 1, \\"teacher_id\\": null, \\"course_id\\": 1}"]\n')

    def test_access_denied(self):
        response = self.client.get(self.url("/request/2"), headers=self.student_headers)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, b'Access denied.')

    def test_no_auth(self):
        response = self.client.get(self.url("/request/1"))

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data, b'Unauthorized Access')
