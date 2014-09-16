"""
models.py

App Engine datastore models

"""

from google.appengine.ext import ndb


def to_dict(model):
    assert isinstance(model, ndb.Model)
    d = model.to_dict()
    d['id'] = model.key.id()
    return d


def domain_of(email):
    return email.lower().split('@')[1]


School = 'School'


class Student(ndb.Model):
    # parent = School
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty()
    created_at = ndb.DateTimeProperty(auto_now_add=True)
    updated_at = ndb.DateTimeProperty(auto_now=True)

    @classmethod
    def name_to_key(cls, school_key, name):
        return ndb.Key(School, school_key.id(), Student, name.lower())

    @classmethod
    @ndb.transactional()
    def upsert(cls, school_key, name):
        student = cls.name_to_key(school_key, name).get()
        if not student:
            student = Student(parent=school_key, name=name).put().get()
        return student


class Classroom(ndb.Model):
    # parent = School
    name = ndb.StringProperty(required=True)
    students = ndb.KeyProperty(kind=Student, repeated=True)
    created_at = ndb.DateTimeProperty(auto_now_add=True)
    updated_at = ndb.DateTimeProperty(auto_now=True)

    @classmethod
    @ndb.transactional()
    def create(cls, name, teacher):
        classroom_key = Classroom(parent=teacher.key.parent(), name=name).put()
        teacher.classroomAccess.append(ClassroomAccess(classroom=classroom_key, access=True))
        teacher.put()
        return classroom_key.get()

    @classmethod
    @ndb.transactional()
    def assign_student(cls, school_key, classroom_id, student):
        classroom = cls.get_by_id(int(classroom_id), parent=school_key)
        if not student.key in classroom.students:
            classroom.students.append(student.key)
            classroom.put()


class ClassroomAccess(ndb.Model):
    classroom = ndb.KeyProperty(kind=Classroom, required=True)
    access = ndb.BooleanProperty(required=True)  # True = teacher, False = Observer


class Teacher(ndb.Model):
    # parent = School
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)
    classroomAccess = ndb.StructuredProperty(ClassroomAccess, repeated=True)
    created_at = ndb.DateTimeProperty(auto_now_add=True)
    updated_at = ndb.DateTimeProperty(auto_now=True)

    @classmethod
    def key_for(cls, email):
        return ndb.Key(School, domain_of(email), Teacher, email.lower())

    @classmethod
    def get_by_email(cls, email):
        return cls.key_for(email).get()

    @classmethod
    @ndb.transactional()
    def upsert(cls, name, email):
        email = email.lower()
        teacher = cls.key_for(email).get()
        if not teacher:
            school_key = ndb.Key(School, domain_of(email))
            teacher = Teacher(parent=school_key, id=email, name=name, email=email).put().get()
        return teacher

    def get_classrooms(self):
        return ndb.get_multi([access.classroom for access in self.classroomAccess])


class Grade(ndb.Model):
    # parent = Assignment
    student_key = ndb.KeyProperty(kind=Student, required=True)
    points = ndb.FloatProperty(required=True)


class Assignment(ndb.Model):
    # parent = Classroom
    name = ndb.StringProperty(required=True)
    total_points = ndb.IntegerProperty(required=True)
    grades = ndb.StructuredProperty(Grade, repeated=True)
    created_at = ndb.DateTimeProperty(auto_now_add=True)
    updated_at = ndb.DateTimeProperty(auto_now=True)


def perform_migrations():
    pass