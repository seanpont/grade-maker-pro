import unittest

from google.appengine.ext import testbed

import logging

from app import models
from app import views


class UnitTest(unittest.TestCase):

    def setUp(self):
        # Testbed stubs
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_blobstore_stub()
        self.testbed.init_mail_stub()
        self.mail_stub = self.testbed.get_stub(testbed.MAIL_SERVICE_NAME)
        self.testbed.init_memcache_stub()

    def tearDown(self):
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
        views.send_welcome_email("Sean Pont", "seanpont@gmail.com", "/api/auth?token=abc123")
        messages = self.mail_stub.get_sent_messages(to='seanpont@gmail.com')
        self.assertEqual(1, len(messages))
        self.assertEqual('Sean Pont <seanpont@gmail.com>', messages[0].to)