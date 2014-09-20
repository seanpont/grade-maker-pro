'use strict';

/* Controllers */


var graderControllers = angular.module('graderControllers', [
  'ngRoute', 'ui.bootstrap', 'graderServices']);

graderControllers.controller('HomeCtrl', function () {
});

// ===== SIGN IN ======================================================================

graderControllers.controller('SignInCtrl', ['$scope', '$http', '$location',
  function ($scope, $http, $location) {

    $scope.newUser = true;
    $scope.error = null;
    $scope.clearError = function () {
      $scope.error = null;
    };
    $scope.signIn = function () {
      $scope.newUser = false;
    };
    $scope.signUp = function () {
      $scope.newUser = true;
    };
    $scope.authenticate = function () {

      // VALIDATION
      if ($scope.newUser) {
        if (!$scope.email || !$scope.name) {
          $scope.error = 'Name and Email required';
          return;
        }
      } else {
        if (!$scope.email) {
          $scope.error = 'Email required';
          return;
        }
      }

      $http.post('/api/auth', {name: $scope.name, email: $scope.email}).
        success(function () {
          $location.url('/verify');
        }).
        error(function (msg) {
          $scope.error = msg;
        });
    };
  }
]);

// ===== VERIFY ======================================================================

graderControllers.controller('VerifyCtrl', ['$scope', '$http', '$location', '$cookies', '$rootScope',
  function ($scope, $http, $location, $cookies, $rootScope) {
    $scope.verify = function () {
      if (!$scope.token) {
        $scope.error = "Verification code required";
        return;
      }
      $http.post('/api/auth/verify', {token: $scope.token}).
        success(function (data) {
          $rootScope.user = data;
          $location.url('/school');
        }).
        error(function () {
          $scope.error = 'Verification code invalid or expired';
        });
    };

    $scope.signIn = function () {
      delete $cookies.verify;
      $location.url('/sign-in')
    }
  }
]);

// ===== SCHOOL ======================================================================

graderControllers.controller('SchoolCtrl', ['$scope', '$http', 'Classroom', 'Student', 'Assignment',
  function ($scope, $http, Classroom, Student, Assignment) {
    $scope.show = {
      classrooms: false,
      classroom: false,
      addStudent: false,
      addAssignment: false
    };

    $scope.collectNames = function (students) {
      var names = [];
      angular.forEach(students, function (student) {
        names.push(student != null ? student.name : '');
      });
      return names;
    };

    $scope.selectedIf = function (bool) {
      return bool ? 'selected' : '';
    };

    // ----- CLASSROOMS --------------------------------------------------------------

    $scope.classrooms = Classroom.query();

    $scope.createClassroom = {};
    $scope.createClassroom.create = function () {
      if (!$scope.createClassroom.name) {
        $scope.createClassroom.error = 'Please include a name (like "7th grade Math Spring 2013")'
        return;
      }
      $scope.createClassroom.inProgress = true;
      new Classroom({name: $scope.createClassroom.name}).$save(
        function (classroom) {
          $scope.classrooms.push(classroom);
          $scope.createClassroom.inProgress = false;
          $scope.createClassroom.name = null;
          $scope.createClassroom.error = null;
          $scope.show.createClassroom = false;
        },
        function (response) {
          $scope.createClassroom.inProgress = false;
          $scope.createClassroom.error = response.data;
        }
      );
    };

    $scope.displayClassroom = function (classroom) {
      classroom.$get({ id: classroom.id });
      $scope.classroom = classroom;
      $scope.show.classroom = true;
    };

    $scope.addStudent = {};
    $scope.addStudent.submit = function () {
      if (!$scope.addStudent.name) {
        $scope.addStudent.error = "Name required";
        return;
      }
      $scope.addStudent.inProgress = true;

      Student.save({
        name: $scope.addStudent.name,
        classroom_id: $scope.classroom.id
      }, function (student) {
        $scope.classroom.students.push(student);
        $scope.addStudent.name = null;
        $scope.show.addStudent = false;
        $scope.addStudent.inProgress = false;
        students = null; // expire type-ahead cache
      }, function (response) {
        $scope.addStudent.error = response.data;
        $scope.addStudent.inProgress = false;
      });
    };

    var students = null;
    $scope.students = function () {
      if (!students) {
        students = Student.query();
      }
      return students;
    };

    $scope.addAssignment = {};
    $scope.addAssignment.submit = function () {
      var classroom = $scope.classroom;
      if (!$scope.addAssignment.name || !$scope.addAssignment.dueDate || !$scope.addAssignment.points) {
        $scope.addAssignment.error = "Please include a name, due date, and total points";
        return;
      }
      $scope.addAssignment.inProgress = true;
      var assignment = new Assignment({
        name: $scope.addAssignment.name,
        due_date: $scope.addAssignment.dueDate,
        points: $scope.addAssignment.points,
        classroom_id: classroom.id
      });
      assignment.$save(function (assignment) {
        classroom.assignments.push(assignment);
        $scope.addAssignment.name = null;
        $scope.addAssignment.dueDate = null;
        $scope.addAssignment.points = null;
        $scope.addAssignment.inProgress = false;
      }, function (response) {
        $scope.addAssignment.error = response.data;
        $scope.addAssignment.inProgress = false;
      });
    };

    $scope.updateAssignment = function (assignment) {
      Assignment.save({classroom_id: $scope.classroom.id, assignment_id: assignment.id}, assignment)
    }

  }
]);
