# -*- coding: utf-8 -*-
import re
import os
from binascii import b2a_hex
import logging
from collections import Iterable


class ValidationError(Exception):
    pass


def listify(item):
    return item if isinstance(item, Iterable) else (item,)


class FormValidator(object):
    """
    Validate and transform fields in a request.
    Each transformer is given the value in sequence.
    It may return the value, return a modified value,
    or raise an exception. The exceptions are collected
    and put in #errors.

    Example usage:
    class SignInForm(FormValidator):
        name = is_required
        email = is_required, is_email
        password = is_required
        favorite_color = is_optional

    class SignInHandler(Handler):
        def get(self):
            self.render_html('sign_in.html')

        def post(self):
            form = SignInForm(self)
            form.validate()
            if form.errors:
                return self.get()
            save_user(form.name, form.email, form.password, form.favorite_color)
            return self.redirect('/welcome')
    """
    def __init__(self, handler):
        self.handler = handler
        self.request = handler.request
        self.session = handler.session
        self.errors = {}
        self.clear_fields()

    @classmethod
    def csrf_token(cls, session):
        return '<input type="hidden" name="csrf_token" value="%s">' % cls.get_csrf_token(session)

    @classmethod
    def get_csrf_token(cls, session, reset=False):
        token = session.get('csrf_token')
        if not token or reset:
            token = session['csrf_token'] = b2a_hex(os.urandom(64))
        return token

    def validate(self, abort_on_failure=True):
        self.check_csrf_token()
        for name, validators in self._fields():
            value = str(jinja2.escape(self.request.get(name)))
            for validator in listify(validators):
                try:
                    value = validator(value)
                    if value is None:  # short-circuit if no value returned
                        break
                except Exception as e:
                    self.errors[name] = e.message
                    break
            self.__setattr__(name, value)
        if hasattr(self, '_req'):
            self._req()
        if self.errors and abort_on_failure:
            logging.warn('Form error: %s', self.errors)
            self.handler.abort(406)
        return self

    @classmethod
    def _fields(cls):
        return [field for field in cls.__dict__.iteritems() if not field[0].startswith('_')]

    def check_csrf_token(self):
        form_token = self.request.get('csrf_token')
        session_token = self.get_csrf_token(self.session)
        if form_token != session_token:
            logging.warn('Potential CSRF attack in progress')
            self.get_csrf_token(self.session, True)
            self.handler.abort(401)

    def clear_fields(self):
        for name, _ in self._fields():
            self.__setattr__(name, None)

    def __str__(self):
        return str({field: self.__getattribute__(field) for field, _ in self._fields()}) + " " + str(self.errors)



# ====== Validators ===================================


def is_required(arg):
    if not arg:
        raise ValidationError('Required')
    return arg


def is_optional(arg):
    return arg or None


EMAIL_REGEX = re.compile(r'^.+@[^.].*\.[a-z]{2,10}$', re.IGNORECASE)


def is_email(email):
    if email and not EMAIL_REGEX.match(email):
        raise ValidationError('Invalid')
    return email.lower()


def is_between(low, high):
    """Validates that a number is between the specified values, inclusive."""
    def validate_is_between(val):
        if not low <= val <= high:
            raise ValidationError('Invalid value')
        return val
    return validate_is_between


def is_one_of(*accepted_values):
    def validator(val):
        if not val in accepted_values:
            raise ValidationError("Value %s not in %s", val, accepted_values)
        return val
    return validator