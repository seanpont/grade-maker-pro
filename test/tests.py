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
        # User info
        self.name = 'Sean Pont'
        self.email = 'Sean@GateAcademy.org'

    def tearDown(self):
        self.patcher.stop()
        self.testbed.deactivate()

    def test_model_teacher(self):
        me = models.Teacher.get_by_email(self.email)
        self.assertEqual(me, None)
        teacher = models.Teacher.get_or_create(self.name, self.email)
        self.assertIsNot(teacher, None)
        school = teacher.key.parent().get()
        self.assertIsNotNone(school)
        # school should have been created as well
        self.assertEqual(teacher.email, self.email.lower())

    def test_welcome_email(self):
        views.send_welcome_email(self.name, self.email, "/api/auth", "abc123")
        messages = self.mail_stub.get_sent_messages(to=self.email)
        self.assertEqual(1, len(messages))
        self.assertEqual('%s <%s>' % (self.name, self.email), messages[0].to)

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
        self.post('/api/auth', {'name': self.name, 'email': self.email})

    def sign_in(self):
        self.authorize()
        token = views.timestamper.sign(self.email)
        return self.post('/api/auth/verify', {'token': token})

    # ----- AUTH -----------------------------------------------------------------

    def test_auth_handler(self):
        response = self.app.post('/api/auth', '{"name": "%s", "email": "%s"}' % (self.name, self.email))
        self.assertEqual(response.status_int, 200)
        user = models.Teacher.get_by_email(self.email)
        self.assertIsNotNone(user)
        messages = self.mail_stub.get_sent_messages(self.email.lower())
        self.assertEqual(len(messages), 1)

    def test_verification_handler(self):
        user = self.sign_in()
        self.assertEqual(user['email'], self.email.lower())

    # ----- CLASSES -----------------------------------------------------------------

    def test_classrooms_handler(self):
        self.sign_in()
        classrooms = self.get('/api/classroom')
        self.assertEqual(len(classrooms), 0)
        classroom = self.post('/api/classroom', {'name': '7th grade math'})
        self.assertEqual(classroom['name'], '7th grade math')
        classrooms = self.get('/api/classroom')
        self.assertEqual(len(classrooms), 1)
        self.assertEqual(classrooms[0]['name'], '7th grade math')

    def test_classroom_handler(self):
        self.sign_in()
        classroom = self.post('/api/classroom', {'name': 'Phoenix'})
        self.assertIsNotNone(classroom['id'])
        classroom = self.get('/api/classroom/%s' % classroom['id'])
        self.assertIsNotNone(classroom)

