import unittest

from google.appengine.ext import testbed

import logging

from app import models


class UnitTest(unittest.TestCase):

    def setUp(self):
        # Testbed stubs
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_blobstore_stub()
        self.testbed.init_mail_stub()
        self.testbed.init_memcache_stub()

    def tearDown(self):
        self.testbed.deactivate()

    def test_model_teacher(self):
        name, email, password = 'Sean Pont', 'seanpont@gmail.com', 'abcd1234'
        me = models.Teacher.get_by_email(email)
        self.assertEqual(me, None)
        teacher_key = models.Teacher.create(name, email, password)
        self.assertIsNot(teacher_key, None)
        persisted = teacher_key.get()
        assert isinstance(persisted, models.Teacher)
        self.assertEqual(persisted.email, email)
        self.assertTrue(persisted.check_password(password))
        self.assertFalse(persisted.check_password(password+'a'))