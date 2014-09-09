"""
models.py

App Engine datastore models

"""

import logging
from google.appengine.ext import ndb


class Student(ndb.Model):
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)
    created_at = ndb.DateTimeProperty(auto_now_add=True)
    updated_at = ndb.DateTimeProperty(auto_now=True)


class Classroom(ndb.Model):
    name = ndb.StringProperty(required=True)
    students = ndb.KeyProperty(kind=Student, repeated=True)
    created_at = ndb.DateTimeProperty(auto_now_add=True)
    updated_at = ndb.DateTimeProperty(auto_now=True)


class ClassroomAccess(ndb.Model):
    classroom = ndb.KeyProperty(kind=Classroom, required=True)
    access = ndb.BooleanProperty(required=True)  # True = teacher, False = Observer


class Teacher(ndb.Model):
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)
    classrooms = ndb.StructuredProperty(ClassroomAccess, repeated=True)
    created_at = ndb.DateTimeProperty(auto_now_add=True)
    updated_at = ndb.DateTimeProperty(auto_now=True)

    @classmethod
    def get_by_email(cls, email):
        return cls.query(cls.email == email).get()

    @classmethod
    def create(cls, name, email):
        return Teacher(name=name, email=email).put()


class Grade(ndb.Model):
    student = ndb.KeyProperty(kind=Student, required=True)
    points = ndb.FloatProperty(required=True)


class Assignment(ndb.Model):
    # parent = Classroom
    name = ndb.StringProperty(required=True)
    total_points = ndb.IntegerProperty(required=True)
    grades = ndb.StructuredProperty(Grade, repeated=True)
    classroom = ndb.KeyProperty(required=True, kind=Classroom)
    created_at = ndb.DateTimeProperty(auto_now_add=True)
    updated_at = ndb.DateTimeProperty(auto_now=True)


def perform_migrations():
    pass