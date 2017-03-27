import unittest

from playhouse.test_utils import test_database
from peewee import *
from datetime import datetime

from app import app
from models import Todo


TEST_DB = SqliteDatabase(':memory:')
TEST_DB.connect()
TEST_DB.create_tables([Todo, ], safe=True)


#  Test data


class TodoModelTestCase(unittest.TestCase):
    def test_create_todo(self):
        pass


class UserModelTestCase(unittest.TestCase):
    def test_create_user(self):
        pass


class ViewTestCase(unittest.TestCase):
    # Executed prior to each test
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.test_client()


class TodoViewsTestCase(ViewTestCase):
    def test_todo_create(self):
        pass


if __name__ == '__main__':
    unittest.main()
