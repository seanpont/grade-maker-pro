'use strict';

/* Controllers */


var graderControllers = angular.module('graderControllers', [
  'ngRoute', 'ui.bootstrap', 'graderServices']);

graderControllers.controller('HomeCtrl', function () {
});

// ===== SIGN IN ======================================================================

graderControllers.controller('SignInCtrl', ['$scope', '$http', '$routeParams', '$location',
  function ($scope, $http, $routeParams, $location) {

    $scope.newUser = true;
    $scope.error = $routeParams.error || '';
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

graderControllers.controller('SchoolCtrl', ['$scope', 'Classroom',
  function ($scope, Classroom) {
    $scope.show = {};

    $scope.selected = function (name) {
      return $scope.show[name] ? 'selected' : '';
    }

    // ----- CLASSROOMS --------------------------------------------------------------

    $scope.classrooms = Classroom.query(function () {
      console.log('Classrooms: ')
      console.log($scope.classrooms);
    });

    $scope.createClassroom = {};
    $scope.createClassroom.create = function () {
      if (!$scope.createClassroom.name) {
        $scope.createClassroom.error = 'Please include a name (like "7th grade Math Spring 2013")'
        return;
      }
      $scope.createClassroom.inProgress = true;
      new Classroom({name: $scope.createClassroom.name}).$save(
        function (classroom) {
          console.log("Classroom created!");
          console.log(classroom);
          $scope.classrooms.push(classroom);
          $scope.createClassroom.inProgress = false;
          $scope.createClassroom.name = null;
          $scope.createClassroom.error = null;
          $scope.show.createClassroom = false;
        },
        function(response) {
          console.log("Could not create classroom")
          console.log(response);
          $scope.createClassroom.inProgress = false;
          $scope.createClassroom.error = response.data;
        }
      );
    }
  }
]);
