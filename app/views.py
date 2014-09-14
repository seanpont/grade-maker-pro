# -*- coding: utf-8 -*-
"""
views.py

URL route handlers

Note that any handler params must match the URL route params.
For example the *say_hello* handler, handling the URL route '/hello/<username>',
  must be passed *username* as the argument.

"""
import datetime
import json
import urllib
from string import Template
from functools import wraps
from collections import defaultdict

import logging
import webapp2

from google.appengine.api import users as google_users
from google.appengine.api import mail
from google.appengine.ext import ndb
from google.appengine.api import images
from google.appengine.ext import blobstore
from google.appengine.ext import ndb
from google.appengine.ext.webapp.blobstore_handlers import BlobstoreUploadHandler, BlobstoreDownloadHandler

from lib.gaesessions import get_current_session
from lib.itsdangerous import TimestampSigner, BadData
from lib.secret_keys import TIMESTAMP_SIGNER_KEY
from lib.router import route

import models
from utils import *


datetime_handler = lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) else None

timestamper = TimestampSigner(TIMESTAMP_SIGNER_KEY)


class BaseHandler(webapp2.RequestHandler):

    # noinspection PyAttributeOutsideInit
    def initialize(self, request, response):
        super(BaseHandler, self).initialize(request, response)
        self.session = get_current_session()
        user_key = self.session.get('user_key')
        self.user = user_key and ndb.Key(urlsafe=user_key).get()

    def write(self, data):
        if isinstance(data, ndb.Model):
            data = models.to_dict(data)
        json_txt = ")]}',\n" + json.dumps(data, default=datetime_handler)
        self.response.headers['Content-Type'] = 'application/json; charset=UTF-8'
        self.response.write(json_txt)

    def params(self, *args):
        """get request parameter(s)"""
        if len(args) == 1:
            return self.request.get(args[0])
        return (self.request.get(arg) for arg in args)

    def data(self):
        _ = self.request.body  # if not called, body_file is empty
        return json.load(self.request.body_file)

    def datum(self, *args):
        data = self.data()
        if len(args) == 1:
            return data.get(args[0])
        return [data.get(arg) for arg in args]

    def check(self, condition, message='', code=400):
        if not condition:
            logging.info(message)
            self.abort(code, message)


class AuthorizedHandler(BaseHandler):
    def initialize(self, request, response):
        super(AuthorizedHandler, self).initialize(request, response)
        self.check(self.user, code=401)


# ===== AUTHENTICATION ==========================================================================


def send_welcome_email(name, email, url, token):
    mail.send_mail(
        sender="GradeMakerPro Support <seanpont@gmail.com>",
        to=Template("${name} <${email}>").substitute(name=name, email=email),
        subject="Your account has been approved",
        body=Template("""
${name},

Welcome to GradeMaker Pro! Here is your verification code:

${token}

Alternatively, you may click the link below to sign in to your account.
This link is valid for 30 minutes.

${url}?token=${token}

Thanks,
The GradeMaker Pro Team
""").substitute(name=name, email=email, url=url, token=token))


@route('/api/auth')
class AuthHandler(BaseHandler):

    def post(self):
        self.check(not self.user, "user already signed in!")
        name, email = self.datum('name', 'email')
        self.check(email, "email required!")
        email = email.lower()
        user = models.Teacher.get_by_email(email)
        if user:
            name = user.name
        else:
            self.check(name, 'name required')
            models.Teacher.get_or_create(name, email)
        token = timestamper.sign(email)
        send_welcome_email(name, email, self.request.url, token)
        self.response.set_cookie('verify', 'true')

    def get(self):
        self.verify(self.params('token'))
        self.redirect('/')

    # noinspection PyAttributeOutsideInit
    def verify(self, token):
        if self.user:
            return
        self.check(token, "auth token required")
        try:
            email = timestamper.unsign(token, max_age=60*30)
            self.user = models.Teacher.get_by_email(email)
            self.check(self.user)
            self.session['user_key'] = self.user.key.urlsafe()
            self.response.delete_cookie('verify')
        except BadData:
            self.abort(401)


@route('/api/auth/verify')
class VerifyHandler(AuthHandler):
    def post(self):
        self.verify(self.datum('token'))
        self.write(self.user)


@route('/api/auth/google')
class GoogleSignIn(BaseHandler):
    def get(self):
        if self.user:
            return self.redirect('/')
        google_user = google_users.get_current_user()
        if not google_user:
            return self.redirect(google_users.create_login_url(self.request.url))
        user = models.Teacher.get_or_create(google_user.nickname(), google_user.email())
        self.session['user_key'] = user.key.urlsafe()
        return self.redirect('/')


@route('/api/user')
class UserHandler(BaseHandler):
    def get(self):
        self.check(self.user, 'user has not signed in', 404)
        self.write(self.user)


@route('/api/blobstore/(.*)')
class Blobstore(BlobstoreDownloadHandler):
    def get(self, resource):
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource) or self.abort(404)
        self.send_blob(blob_info)


@route('/api/sign-out')
class SignOut(BaseHandler):
    def post(self):
        self.session.terminate()

# ===== CLASSES ===============================================================

@route('/api/classroom')
class ClassHandler(AuthorizedHandler):
    def get(self):
        self.write(self.user.get_classrooms())

    def post(self):
        name = self.datum('name')
        self.check(name)
        classroom = models.Classroom.create(name, self.user)
        self.write(classroom)



# ===== ADMIN ========================================================


@route('/api/perform-migrations')
class AdminMigration(AuthorizedHandler):
    # noinspection PyMethodMayBeStatic
    def get(self):
        models.perform_migrations()


