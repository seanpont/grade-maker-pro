import unittest

from google.appengine.ext import testbed

import logging

import webapp2
import webtest
from app import models
from app import views
from lib import router
import mock
import json


class UnitTest(unittest.TestCase):

    # noinspection PyMethodOverriding
    def setUp(self):
        # Testbed stubs
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_blobstore_stub()
        self.testbed.init_mail_stub()
        self.mail_stub = self.testbed.get_stub(testbed.MAIL_SERVICE_NAME)
        self.testbed.init_memcache_stub()
        self.app = webtest.TestApp(webapp2.WSGIApplication(router.ROUTES))
        self.patcher = mock.patch('app.views.get_current_session')
        get_current_session = self.patcher.start()
        get_current_session.return_value = {}

    def tearDown(self):
        self.patcher.stop()
        self.testbed.deactivate()

    def test_model_teacher(self):
        name, email = 'Sean Pont', 'seanpont@gmail.com'
        me = models.Teacher.get_by_email(email)
        self.assertEqual(me, None)
        teacher_key = models.Teacher.create(name, email)
        self.assertIsNot(teacher_key, None)
        persisted = teacher_key.get()
        assert isinstance(persisted, models.Teacher)
        self.assertEqual(persisted.email, email)

    def test_welcome_email(self):
        views.send_welcome_email("Sean Pont", "seanpont@gmail.com", "/api/auth", "abc123")
        messages = self.mail_stub.get_sent_messages(to='seanpont@gmail.com')
        self.assertEqual(1, len(messages))
        self.assertEqual('Sean Pont <seanpont@gmail.com>', messages[0].to)

    # ===== HANDLERS ===============================================================

    def get(self, path):
        response = self.app.get(path)
        self.assertEqual(response.status_int, 200)
        return json.loads(response.body[5:])

    def post(self, path, body):
        response = self.app.post(path, json.dumps(body))
        self.assertEqual(response.status_int, 200)
        return response.body and json.loads(response.body[5:])

    def authorize(self):
        self.post('/api/auth', {'name': 'Sean', 'email': 'seanpont@gmail.com'})

    def sign_in(self):
        self.authorize()
        user = models.Teacher.get_by_email('seanpont@gmail.com')
        token = views.timestamper.sign(str(user.key.id()))
        return self.post('/api/auth/verify', {'token': token})

    # ----- AUTH -----------------------------------------------------------------

    def test_auth_handler(self):
        response = self.app.post('/api/auth', '{"name": "Sean", "email": "seanpont@gmail.com"}')
        self.assertEqual(response.status_int, 200)
        self.assertIsNotNone(models.Teacher.get_by_email('seanpont@gmail.com'))
        messages = self.mail_stub.get_sent_messages('seanpont@gmail.com')
        self.assertEqual(len(messages), 1)

    def test_verification_handler(self):
        user = self.sign_in()
        self.assertEqual(user['email'], 'seanpont@gmail.com')

    # ----- CLASSES -----------------------------------------------------------------

    def test_classes_handler(self):
        self.sign_in()
        classes = self.get('/api/classroom')
        self.assertEqual(len(classes), 0)

