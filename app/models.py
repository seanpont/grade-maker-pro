"""
models.py

App Engine datastore models

"""

from google.appengine.ext import ndb

from utils import *


def to_dict(model):
    assert isinstance(model, ndb.Model)
    model_dict = model.to_dict()
    model_dict['id'] = model.key.id()
    return model_dict


def domain_of(email):
    return email.lower().split('@')[1]


School = 'School'


class Student(ndb.Model):
    # parent = School
    name = ndb.StringProperty(required=True)
    created_at = ndb.DateTimeProperty(auto_now_add=True)
    updated_at = ndb.DateTimeProperty(auto_now=True)

    # noinspection PyUnresolvedReferences
    def to_dict(self):
        student = super(Student, self).to_dict()
        name_parts = self.name.split(' ')
        student['last_name'] = name_parts[min(len(name_parts), 1)]
        return student

    @classmethod
    def key_for(cls, school_key, student_id):
        """ @:rtype ndb.Key """
        return ndb.Key(School, school_key.id(), Student, student_id)

    @classmethod
    def name_to_key(cls, school_key, name):
        """ @:rtype ndb.Key """
        return cls.key_for(school_key, name.lower())

    @classmethod
    @ndb.transactional()
    def upsert(cls, school_key, name):
        student = cls.name_to_key(school_key, name).get()
        if not student:
            student = Student(parent=school_key, id=name.lower(), name=name).put().get()
        return student


class GradeWeight(ndb.Model):
    category = ndb.StringProperty(required=True)
    weight = ndb.FloatProperty(required=True, default=100)


class Classroom(ndb.Model):
    # parent = School
    name = ndb.StringProperty(required=True)
    students = ndb.KeyProperty(kind=Student, repeated=True)
    grade_weights = ndb.StructuredProperty(GradeWeight, repeated=True)
    created_at = ndb.DateTimeProperty(auto_now_add=True)
    updated_at = ndb.DateTimeProperty(auto_now=True)

    def to_dict(self):
        classroom = super(Classroom, self).to_dict()
        classroom['grade_weights'] = {gw.category: gw.weight for gw in self.grade_weights} or {}
        return classroom

    def upsert_grade_weight(self, category):
        if category not in [gw.category for gw in self.grade_weights]:
            self.grade_weights.append(GradeWeight(category=category))
            self.put()


    @classmethod
    def by_id(cls, school_key, classroom_id):
        return cls.get_by_id(int(classroom_id), parent=school_key)

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
            return True
        return False


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

    def to_dict(self):
        return {'name': self.name, 'email': self.email}

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
    category = ndb.StringProperty(required=True)
    due_date = ndb.DateProperty(required=True)
    points = ndb.IntegerProperty(required=True)
    grades = ndb.StructuredProperty(Grade, repeated=True)
    created_at = ndb.DateTimeProperty(auto_now_add=True)
    updated_at = ndb.DateTimeProperty(auto_now=True)

    def to_dict(self):
        assignment = super(Assignment, self).to_dict()
        assignment['grades'] = {grade.student_key.id(): grade.points for grade in self.grades}
        return assignment

    # noinspection PyTypeChecker
    def upsert_grade(self, student_key, points):
        for grade in self.grades:
            if grade.student_key == student_key:
                grade.points = points
                return
        self.grades.append(Grade(student_key=student_key, points=points))

    def delete_grade(self, student_key):
        find_and_remove(self.grades, lambda grade: grade.student_key == student_key)

    @classmethod
    def by_id(cls, school_key, classroom_id, assignment_id):
        """ @:rtype Assignment """
        return ndb.Key(School, school_key.id(), Classroom, classroom_id, Assignment, assignment_id).get()

    @classmethod
    def create(cls, classroom, category, due_date, points):
        return Assignment(parent=classroom.key, category=category, due_date=due_date,
                          points=points).put().get()


def perform_migrations():
    pass