'use strict';

/* Controllers */


var graderControllers = angular.module('graderControllers', [
  'ngRoute', 'ui.bootstrap', 'graderServices', 'graderDirectives']);

graderControllers.controller('HomeCtrl', function () {
});

var utils = {
  sum: function (items) {
    var s = 0;
    angular.forEach(items, function (item) {
      s += item
    });
    return s;
  },

  collect: function (items, func) {
    var c = [];
    angular.forEach(items, function (item) {
      c = c.concat(func(item) || []);
    });
    return c;
  }
};

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

    $scope.filter = {
      students: null
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

    Classroom.query(function (classrooms) {
      $scope.classrooms = classrooms;
      $scope.classroomsLoaded = true;
    });

    $scope.createClassroom = {
      show: false,
      error: null,
      create: function () {
        var name = $scope.createClassroom.name;
        if (!name) {
          $scope.createClassroom.error = 'Please include a name (like "7th grade Math Spring 2013")'
          return;
        }
        $scope.createClassroom.inProgress = true;
        new Classroom({name: name}).$save(
          function (classroom) {
            classroom.loaded = true;
            $scope.classrooms.push(classroom);
            $scope.createClassroom.cancel();
            $scope.displayClassroom(classroom);
          },
          function (response) {
            $scope.createClassroom.inProgress = false;
            $scope.createClassroom.error = response.data;
          }
        );
      },
      cancel: function () {
        $scope.createClassroom.show = false;
        $scope.createClassroom.name = null;
        $scope.createClassroom.inProgress = false;
        $scope.createClassroom.error = null;
      }
    };

    $scope.displayClassroom = function (classroom) {
      if (!classroom.loaded) {
        classroom.$get({ id: classroom.id }, function (classroom) {
          classroom.loaded = true;
          $scope.classroom = classroom;
        });
      } else {
        $scope.classroom = classroom;
      }
    };

    // ----- STUDENTS -----------------------------------------------------------------

    $scope.addStudent = {
      name: null,
      error: null,
      submit: function () {
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
          $scope.addStudent.inProgress = false;
          students = null; // expire type-ahead cache
        }, function (response) {
          $scope.addStudent.error = response.data;
          $scope.addStudent.inProgress = false;
        });
      },
      typeahead: function () {
        // Collect students from all classrooms, then filter out those from
        var studentsInClassroom = $scope.classroom.students.map(function(student) {
          return student.id
        });
        return $scope.classrooms.map(function (c) {
          return c.students || [];
        }).reduce(function (a, b) {
          return a.concat(b)
        }).filter(function (student) {
          return student && studentsInClassroom.indexOf(student.id) == -1;
        }).map(function (student) {
          return student.name
        });
      }
    };

    var students = null;
    $scope.students = function () {
      if (!students) {
        students = Student.query();
      }
      return students;
    };

    // ----- ASSIGNMENTS -----------------------------------------------------------------

    $scope.addAssignment = {
      show: false,
      submit: function () {
        var classroom = $scope.classroom,
          category = $scope.addAssignment.category,
          dueDate = $scope.addAssignment.dueDate,
          points = $scope.addAssignment.points;

        if (!category || !dueDate || !points) {
          $scope.addAssignment.error = "Please include a category, due date, and total points";
          return;
        }
        $scope.addAssignment.inProgress = true;
        var assignment = new Assignment({ category: category, due_date: dueDate, points: points});
        assignment.$save({classroom_id: classroom.id},
          function (assignment) {
            classroom.assignments.push(assignment);
            if (!classroom.grade_weights[assignment.category]) {
              classroom.grade_weights[assignment.category] = 100;
            }
            $scope.addAssignment.category = null;
            $scope.addAssignment.dueDate = new Date();
            $scope.addAssignment.points = null;
            $scope.addAssignment.inProgress = false;
          }, function (response) {
            $scope.addAssignment.error = response.data;
            $scope.addAssignment.inProgress = false;
          });
      }
    };

    // ----- GRADES -----------------------------------------------------------------

    $scope.updateAssignment = function (assignment) {
      Assignment.save({classroom_id: $scope.classroom.id, assignment_id: assignment.id}, assignment)
    };

    $scope.gradeFor = function (classroom, student) {
      var points = [0, 0];
      angular.forEach(classroom.assignments, function (assignment) {
        var grade = assignment.grades[student.id];
        if ((typeof grade !== 'undefined' && grade != '')) {
          var weight = classroom.grade_weights[assignment.category];
          points[0] += parseFloat(grade) * weight;
          points[1] += assignment.points * weight;
        }
      });
      return points;
    };

    $scope.asRatio = function (grade) {
      return grade[0] + ' / ' + grade[1]
    };

    $scope.asPercent = function (grade) {
      return (grade[0] * 100 / (grade[1] || 1)).toPrecision(3) + '%'
    };

    $scope.categories = function () {
      var categories = [];
      angular.forEach($scope.classrooms, function (classroom) {
        categories = categories.concat(Object.keys(classroom.grade_weights));
      });
      return categories;
    };

    var sum = function (items) {
      var s = 0;
      angular.forEach(items, function (item) {
        s += item
      })
      return s;
    };

    $scope.categoryWeightPercent = function (category) {
      var weight = $scope.classroom.grade_weights[category];
      var total = sum($scope.classroom.grade_weights);
      return $scope.asPercent([weight, total])
    };

    $scope.keys = function (obj) {
      return obj ? Object.keys(obj) : '';
    };


  }
]);
