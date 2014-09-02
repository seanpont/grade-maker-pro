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

    def test_groups(self):
        pass
