import unittest
import base64
import json

from playhouse.test_utils import test_database
from peewee import *
from datetime import datetime

from app import app
from models import User, Todo


TEST_DB = SqliteDatabase(':memory:')
TEST_DB.connect()
TEST_DB.create_tables([User, Todo], safe=True)


#  Test data
USER_DATA = {
    'username': 'test_user',
    'email': 'test@example.com',
    'password': 'test',
    'verify_password': 'test'
}
BAD_USER_DATA = {
    'username': 'test_user',
    'email': 'test@example.com',
    'password': 'test',
    'verify_password': 'testing'
}


class TodoModelTestCase(unittest.TestCase):
    def test_create_todo(self):
        with test_database(TEST_DB, (Todo,)):
            Todo.create(name="Test your code using unittests")
            self.assertEqual(Todo.select().count(), 1)


class UserModelTestCase(unittest.TestCase):
    @staticmethod
    def create_users(count=2):
        for i in range(count):
            User.create_user(
                username='test_user{}'.format(i),
                email='test_{}@example.com'.format(i),
                password='password'
            )

    def test_create_user(self):
        with test_database(TEST_DB, (User,)):
            self.create_users()
            self.assertEqual(User.select().count(), 2)
            self.assertNotEqual(
                User.select().get().password,
                'password'
            )

    def test_create_duplicate_user_username(self):
        with test_database(TEST_DB, (User,)):
            self.create_users()
            with self.assertRaises(Exception):
                User.create_user(
                    username='test_user1',
                    email='testing@example.com',
                    password='password'
                )

    def test_create_duplicate_user_email(self):
        with test_database(TEST_DB, (User,)):
            self.create_users()
            with self.assertRaises(Exception):
                User.create_user(
                    username='test_user',
                    email='test_1@example.com',
                    password='password'
                )


class ViewTestCase(unittest.TestCase):
    # Executed prior to each test
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.test_client()


class AppViewsTestCase(ViewTestCase):
    def test_homepage_401(self):
        rv = self.app.get('/')
        self.assertEqual(rv.status_code, 401)

    def test_homepage_200(self):
        with test_database(TEST_DB, (User,)):
            UserModelTestCase.create_users(1)
            user = User.get(User.id==1)
            basic_header = {
                'Authorization': 'Basic ' + base64.b64encode(
                    bytes(user.username + ':' + 'password', 'ascii')
                ).decode('ascii')
            }
            rv = self.app.get('/api/v1/users/token', headers=basic_header)
            self.assertEqual(rv.status_code, 200)

            token = json.loads(rv.get_data(as_text=True))['token']


class UserResourceTestCase(ViewTestCase):
    def test_create_user_resource(self):
        with test_database(TEST_DB, (User,)):
            rv = self.app.post('/api/v1/users', data=USER_DATA)
            self.assertEqual(rv.status_code, 201)

    def test_bad_create_user_resource(self):
        with test_database(TEST_DB, (User,)):
            rv = self.app.post('/api/v1/users', data=BAD_USER_DATA)
            self.assertEqual(rv.status_code, 400)


class TodoResourceTestCase(ViewTestCase):
    @staticmethod
    def create_todos():
        Todo.create(name="Todo Number 1")
        Todo.create(name="Todo Number 2")

    def test_create_todo_resource(self):
        with test_database(TEST_DB, (Todo,)):
            rv = self.app.post('/api/v1/todos', data={'name': 'Wash your car'})
            self.assertEqual(rv.status_code, 201)

    def test_get_empty_todos_list(self):
        with test_database(TEST_DB, (Todo,)):
            rv = self.app.get('/api/v1/todos')
            self.assertEqual(rv.status_code, 200)
            self.assertIn('{"todos": []}', rv.get_data(as_text=True))

    def test_get_todos_list(self):
        with test_database(TEST_DB, (Todo,)):
            self.create_todos()
            rv = self.app.get('/api/v1/todos')
            self.assertEqual(rv.status_code, 200)
            self.assertIn('Todo Number 1', rv.get_data(as_text=True))
            self.assertIn('Todo Number 2', rv.get_data(as_text=True))

    def test_get_single_todo(self):
        with test_database(TEST_DB, (Todo,)):
            self.create_todos()
            rv = self.app.get('/api/v1/todos/1')
            self.assertEqual(rv.status_code, 200)
            self.assertIn('Todo Number 1', rv.get_data(as_text=True))

    def test_get_single_todo_fail(self):
        rv = self.app.get('/api/v1/todos/1')
        self.assertEqual(rv.status_code, 404)
        self.assertRaises(Todo.DoesNotExist)

    def test_update_todo(self):
        with test_database(TEST_DB, (Todo,)):
            self.create_todos()
            rv = self.app.put('/api/v1/todos/1',
                data={'name': 'Todo Number One'})
            self.assertEqual(rv.status_code, 200)
            self.assertIn('Todo Number One', rv.get_data(as_text=True))

    def test_delete_todo(self):
        with test_database(TEST_DB, (Todo,)):
            self.create_todos()
            rv = self.app.delete('/api/v1/todos/1')
            self.assertEqual(rv.status_code, 204)
            self.assertNotIn('Todo Number 1', rv.get_data(as_text=True))


class AuthTestCase(ViewTestCase):
    def test_get_auth_token_locked(self):
        with test_database(TEST_DB, (User,)):
            rv = self.app.get('/api/v1/users/token')
            self.assertEqual(rv.status_code, 401)

    def test_get_auth_token_200(self):
        with test_database(TEST_DB, (User,)):
            UserModelTestCase.create_users(1)
            user = User.get(User.id==1)
            headers={
                'Authorization': 'Basic ' + base64.b64encode(
                    bytes(user.username + ':' + 'password', 'ascii')
                ).decode('ascii')
            }
            rv = self.app.get('/api/v1/users/token', headers=headers)
            self.assertEqual(rv.status_code, 200)


if __name__ == '__main__':
    unittest.main()
