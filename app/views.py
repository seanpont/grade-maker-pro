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
from functools import wraps
from collections import defaultdict

import logging
import webapp2

from google.appengine.api import users as google_users
from google.appengine.api import mail
from google.appengine.api import images
from google.appengine.ext import blobstore
from google.appengine.ext import ndb
from google.appengine.ext.webapp.blobstore_handlers import BlobstoreUploadHandler, BlobstoreDownloadHandler

from lib.gaesessions import get_current_session
from lib.itsdangerous import TimestampSigner, BadData
from lib.secret_keys import TIMESTAMP_SIGNER_KEY
from lib.router import route, url_for
from lib.formalin import *

import models
from utils import *


datetime_handler = lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) else None

timestamper = TimestampSigner(TIMESTAMP_SIGNER_KEY)


class BaseHandler(webapp2.RequestHandler):

    def initialize(self, request, response):
        super(BaseHandler, self).initialize(request, response)
        self.session = get_current_session()
        user_id = self.session.get('user_id')
        self.user = user_id and models.Users.get_by_id(user_id)

    def write(self, d):
        json_txt = ")]}',\n" + json.dumps(d, default=datetime_handler)
        self.response.headers['Content-Type'] = 'application/json; charset=UTF-8'
        self.write(json_txt)

    def params(self, *args):
        """get request parameter(s)"""
        if len(args) == 1:
            return self.request.get(args[0])
        return (self.request.get(arg) for arg in args)

    def data(self):
        logging.info('data: %s' % self.request.body)
        logging.info(dir(self.request))
        return json.load(self.request.body_file)

    def datums(self, *args):
        if len(args) == 1:
            return self.data().get(args[0])
        return [self.data().get(arg) for arg in args]

    def check(self, condition, message):
        if not condition:
            logging.info(message)
            self.abort(401, message)


def send_mail(user, subject, body, **kwargs):
    content = content_for_language(user.language)
    sender = models.SiteConfig.get().mail_sender
    subject = content[subject]
    body = jinja2.Template(content[body]).render(user=user, **kwargs)
    mail.send_mail(sender, user.email, subject, body)


# ===== AUTHENTICATION ==========================================================================

@route('/api/user')
class UserHandler(BaseHandler):

    def post(self):
        self.check(not self.user, "user already signed in!")
        email, password = self.datums('email', 'password')
        self.check(email and password, "email and password required!")
        teacher = models.Teacher.get_by_email(email)
        self.check(teacher and teacher.check_password(password), "Authentication failed: email or password invalid")
        self.session.put('user_id', teacher.key.id())
        self.write(teacher)



@route('/sign-in/google')
class GoogleSignIn(BaseHandler):
    def get(self):
        if self.user:
            self.abort(401, "User is already signed in")
        google_user = google_users.get_current_user()
        if not google_user:
            return self.redirect(google_users.create_login_url(self.request.url))
        user = models.Users.find_by_email(google_user.email())
        if not user:
            self.bad_news(content_for_language(self.language)['signIn_noUserFound'] % google_user.email())
            return self.redirect('/sign_in')
        self.session['user_id'] = user.key.id()



@route('/api/blobstore/(.*)')
class Blobstore(BlobstoreDownloadHandler):
    def get(self, resource):
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource) or self.abort(404)
        self.send_blob(blob_info)


# ===== AUTHENTICATION ========================================================


@route('/sign_in')
class SignIn(BaseHandler):
    def get(self):
        if self.user:
            return self.redirect(url_for('home'))
        self.render_html('sign_in.html',
                         email=self.session.pop('email'))

    class Form(FormValidator):
        email = is_required, is_email
        password = is_required

    def post(self):
        form = SignIn.Form(self).validate()
        logging.info('form: %s', form)
        user = models.Users.find_by_email(form.email)
        if user and user.check_password(form.password):
            self.session['user_id'] = user.key.id()
            return self.redirect('/account')
        else:
            self.bad_news(content_for_language(self.language)['signIn_badNews'])
            self.session['email'] = form.email
            self.redirect(self.request.path)


@route('/google_sign_in')
class GoogleSignIn(BaseHandler):
    def get(self):
        if self.user:
            return self.redirect(url_for('home'))
        google_user = google_users.get_current_user()
        if not google_user:
            return self.redirect(google_users.create_login_url(self.request.url))
        user = models.Users.find_by_email(google_user.email())
        if not user:
            self.bad_news(content_for_language(self.language)['signIn_noUserFound'] % google_user.email())
            return self.redirect('/sign_in')
        self.session['user_id'] = user.key.id()
        self.redirect('/')


@route('/forgot_password')
class ForgotPassword(BaseHandler):
    def get(self):
        if self.user:
            return self.redirect(url_for('account'))
        token = self.params('token')
        try:
            user_id = int(timestamper.unsign(token, 24 * 60 * 60))  # Link is valid for one day
        except BadData:
            self.bad_news("That link has expired")
            return self.redirect(url_for('sign_in'))
        user = models.Users.get_by_id(user_id) or self.abort(401)
        self.session.clear()
        self.session['user_id'] = user.key.id()
        self.redirect(url_for('account'))

    def post(self):
        """Send reset password link"""
        if self.user:
            return self.redirect(url_for('home'))
        email = self.params('email')
        user = models.Users.find_by_email(email) or self.abort(404)
        signed_user_id = timestamper.sign(str(user.key.id()))
        link = self.request.url + '?token=%s' % signed_user_id
        logging.info('forgot password link: %s', link)
        send_mail(user, 'forgotPassword_email_subject', 'forgotPassword_email_body', link=link)


@route('/sign_out')
class SignOut(BaseHandler):
    def post(self):
        self.session.terminate()
        self.redirect(url_for('home'))


@route('/admin/perform-migrations')
class AdminMigration(BaseHandler):
    def get(self):
        models.perform_migrations()
        self.redirect(url_for('home'))

