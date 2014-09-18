# -*- coding: utf-8 -*-
"""
views.py

URL route handlers

Note that any handler params must match the URL route params.
For example the *say_hello* handler, handling the URL route '/hello/<username>',
  must be passed *username* as the argument.

"""
from datetime import date, datetime
import json
import urllib
from string import Template
import base64
from functools import wraps
from collections import defaultdict, Iterable

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


datetime_handler = lambda obj: obj.isoformat() if isinstance(obj, datetime) or isinstance(obj, date) else None

timestamper = TimestampSigner(TIMESTAMP_SIGNER_KEY)


class BaseHandler(webapp2.RequestHandler):
    # noinspection PyAttributeOutsideInit
    def initialize(self, request, response):
        super(BaseHandler, self).initialize(request, response)
        self.session = get_current_session()
        user_key = self.session.get('user_key')
        self.user = user_key and ndb.Key(urlsafe=user_key).get()
        self.school_key = self.user and self.user.key.parent()

    def write(self, data):
        if isinstance(data, ndb.Model):
            data = models.to_dict(data)
        elif isinstance(data, list) and len(data) > 0 and isinstance(data[0], ndb.Model):
            data = [models.to_dict(m) for m in data]
        json_txt = ")]}',\n" + json.dumps(data, default=datetime_handler)
        logging.info(self.request.path + ' response: ' + json_txt)
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

    def check(self, condition, code=400, message=''):
        if not condition:
            logging.info(message)
            self.abort(code, message)


class AuthorizedHandler(BaseHandler):
    def initialize(self, request, response):
        super(AuthorizedHandler, self).initialize(request, response)
        self.check(self.user, 401)


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


def encode_email_token(email):
    return base64.urlsafe_b64encode(timestamper.sign(email))


def decode_email_token(token):
    return timestamper.unsign(base64.urlsafe_b64decode(str(token)), max_age=60 * 30)


@route('/api/auth')
class AuthHandler(BaseHandler):
    def post(self):
        self.check(not self.user, 400, "user already signed in!")
        name, email = self.datum('name', 'email')
        self.check(email, 400, "email required!")
        email = email.lower()
        user = models.Teacher.get_by_email(email)
        if user:
            name = user.name
        else:
            self.check(name, 400, 'name required')
            models.Teacher.upsert(name, email)
        token = encode_email_token(email)
        send_welcome_email(name, email, self.request.url, token)
        self.response.set_cookie('verify', 'true')

    def get(self):
        self.verify(self.params('token'))
        self.redirect('/')

    # noinspection PyAttributeOutsideInit
    def verify(self, token):
        if self.user:
            return
        self.check(token, 400, "auth token required")
        try:
            email = decode_email_token(token)
            self.user = models.Teacher.get_by_email(email)
            self.check(self.user)
            self.session['user_key'] = self.user.key.urlsafe()
            self.response.delete_cookie('verify')
        except BadData:
            self.abort(401)


@route('/api/auth/verify/?')
class VerifyHandler(AuthHandler):
    def post(self):
        self.verify(self.datum('token'))
        self.write(self.user)


@route('/api/auth/google/?')
class GoogleSignIn(BaseHandler):
    def get(self):
        if self.user:
            return self.redirect('/')
        google_user = google_users.get_current_user()
        if not google_user:
            return self.redirect(google_users.create_login_url(self.request.url))
        user = models.Teacher.upsert(google_user.nickname(), google_user.email())
        self.session['user_key'] = user.key.urlsafe()
        return self.redirect('/')


@route('/api/user/?')
class UserHandler(BaseHandler):
    def get(self):
        self.check(self.user, 404, 'user has not signed in')
        self.write(self.user)


@route('/api/blobstore/(.*)/?')
class Blobstore(BlobstoreDownloadHandler):
    def get(self, resource):
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource) or self.abort(404)
        self.send_blob(blob_info)


@route('/api/sign-out/?')
class SignOut(BaseHandler):
    def post(self):
        self.session.terminate()


# ===== CLASSROOM ===============================================================


@route('/api/classroom/?')
class ClassroomsHandler(AuthorizedHandler):
    def get(self):
        self.write(self.user.get_classrooms())

    def post(self):
        name = self.datum('name')
        self.check(name)
        classroom = models.Classroom.create(name, self.user)
        self.write(classroom)


@route('/api/classroom/(\d+)/?')
class ClassroomHandler(AuthorizedHandler):
    def get(self, classroom_id):
        classroom = models.Classroom.by_id(self.school_key, classroom_id)
        self.check(classroom, 404)
        students = ndb.get_multi(classroom.students)
        assignments = models.Assignment.query(ancestor=classroom.key)
        response = models.to_dict(classroom)
        response['students'] = [models.to_dict(student) for student in students]
        response['assignments'] = [models.to_dict(assignment) for assignment in assignments]
        self.write(response)


# ===== STUDENT ===============================================================

@route('/api/student/?')
class StudentHandler(AuthorizedHandler):
    def get(self):
        """ Returns all the students in the school """
        students = models.Student.query(ancestor=self.school_key).fetch()
        self.write(students)

    def post(self):
        """
        Requires a name and a classroom id.
        First searches for the student by name.
        If found, checks if the student is already in the classroom
        If not in class, adds it to classroom.
        If already in classroom, reports error.
        If student does not exist, creates student and adds it to classroom.
        """
        name, classroom_id = self.datum('name', 'classroom_id')
        student = models.Student.upsert(self.school_key, name)
        success = models.Classroom.assign_student(self.school_key, classroom_id, student)
        self.check(success, 406, "Student already in classroom")
        self.write(student)


# ===== ASSIGNMENT ===============================================================

@route('/api/assignment/?')
class AssignmentHandler(AuthorizedHandler):
    def post(self):
        name, due_date, points, classroom_id = self.datum('name', 'due_date', 'points', 'classroom_id')
        self.check(name and due_date and points and classroom_id,
                   message='name, due_date, points, and classroom_id required')
        classroom = models.Classroom.by_id(self.school_key, classroom_id)
        self.check(classroom, 404, "Classroom not found")
        assignment = models.Assignment.create(classroom, name, due_date, points)
        self.write(assignment)



# ===== ADMIN ========================================================


@route('/api/perform-migrations/?')
class AdminMigration(AuthorizedHandler):
    # noinspection PyMethodMayBeStatic
    def get(self):
        models.perform_migrations()


