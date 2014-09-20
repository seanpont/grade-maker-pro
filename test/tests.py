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
from app.utils import atterize
from datetime import date


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
        self.classroom_name = 'Phoenix'
        self.student_name = 'Bobby Jones'

    def tearDown(self):
        self.patcher.stop()
        self.testbed.deactivate()

    def test_model_teacher(self):
        me = models.Teacher.get_by_email(self.email)
        self.assertEqual(me, None)
        teacher = models.Teacher.upsert(self.name, self.email)
        self.assertIsNot(teacher, None)
        self.assertEqual(teacher.email, self.email.lower())

    def test_welcome_email(self):
        views.send_welcome_email(self.name, self.email, "/api/auth", "abc123")
        messages = self.mail_stub.get_sent_messages(to=self.email)
        self.assertEqual(1, len(messages))
        self.assertEqual('%s <%s>' % (self.name, self.email), messages[0].to)

    def test_model_student(self):
        teacher = models.Teacher.upsert(self.name, self.email)
        models.Classroom.create(self.classroom_name, teacher)
        school_key = teacher.key.parent()
        models.Student.upsert(school_key, "Donald Knuth")
        models.Student.upsert(school_key, "Claude E. Shannon")
        models.Student.upsert(school_key, "Edsger Dijkstra")
        models.Student.upsert(school_key, "donald knuth")
        self.assertEqual(len(models.Student.query().fetch()), 3)

    def test_model_assignment(self):
        teacher = models.Teacher.upsert(self.name, self.email)
        classroom = models.Classroom.create(self.classroom_name, teacher)
        assignment = models.Assignment.create(classroom, 'quiz', views.parse_date('2014-09-18'), 20)
        self.assertIsNotNone(assignment)
        self.assertEqual(assignment.due_date, date(2014, 9, 18))
        d = assignment.to_dict()
        self.assertEqual(d['grades'], {})
        assignments = models.Assignment.query(ancestor=classroom.key).fetch()
        self.assertEqual(len(assignments), 1)

    # ===== HANDLERS ===============================================================

    def get(self, path):
        response = self.app.get(path)
        self.assertEqual(response.status_int, 200)
        return atterize(json.loads(response.body[5:]))

    def post(self, path, body):
        response = self.app.post(path, json.dumps(body))
        self.assertEqual(response.status_int, 200)
        return atterize(response.body and json.loads(response.body[5:]))

    def authorize(self):
        self.post('/api/auth', {'name': self.name, 'email': self.email})

    def sign_in(self):
        self.authorize()
        token = views.encode_email_token(self.email)
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
        self.assertEqual(user.email, self.email.lower())

    # ----- CLASSROOMS -----------------------------------------------------------------

    def create_classroom(self):
        return self.post('/api/classroom', {'name': self.classroom_name})

    def get_classroom(self, classroom):
        return self.get('/api/classroom/%s' % classroom.id)

    def test_classrooms_handler(self):
        self.sign_in()
        classrooms = self.get('/api/classroom')
        self.assertEqual(len(classrooms), 0)
        classroom = self.create_classroom()
        self.assertEqual(classroom.name, self.classroom_name)
        classrooms = self.get('/api/classroom')
        self.assertEqual(len(classrooms), 1)
        self.assertEqual(classrooms[0].name, self.classroom_name)
        classroom = self.get_classroom(classroom)
        self.assertIsNotNone(classroom)
        self.assertEqual(classroom.students, [])
        self.assertEqual(classroom.assignments, [])

    # ----- STUDENTS -----------------------------------------------------------------

    def test_student_handler(self):
        self.sign_in()
        classroom = self.create_classroom()
        student = self.post('/api/student', {'name': self.student_name, 'classroom_id': classroom.id})
        self.assertIsNotNone(student)
        self.assertEqual(student.name, self.student_name)
        classroom = self.get_classroom(classroom)
        self.assertEqual(classroom.students[0].name, self.student_name)

    # ----- ASSIGNMENTS -----------------------------------------------------------------

    def test_assignments_handler(self):
        self.sign_in()
        classroom = self.create_classroom()
        assignment = self.post('/api/classroom/%s/assignment' % classroom.id, {
            'name': 'quiz',
            'due_date': '2014-09-15',
            'points': 20
        })
        self.assertIsNotNone(assignment)
        self.assertEqual(assignment.due_date, '2014-09-15')
        classroom = self.get_classroom(classroom)
        self.assertEqual(len(classroom.assignments), 1)
        student = self.post('/api/student', {'name': self.student_name, 'classroom_id': classroom.id})
        assignment.grades[student.id] = 18.0
        # update the assignment -- add a grade
        updated_assignment = self.post('/api/classroom/%s/assignment/%s' % (classroom.id, assignment.id), assignment)
        updated_assignment['updated_at'] = assignment.updated_at
        self.assertEqual(updated_assignment, assignment)


