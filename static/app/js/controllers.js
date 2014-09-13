'use strict';

/* Controllers */


var graderControllers = angular.module('graderControllers', [
  'ngRoute', 'ui.bootstrap', 'graderServices']);

graderControllers.controller('HomeCtrl', function() {});

// ===== SIGN IN ======================================================================

graderControllers.controller('SignInCtrl', ['$scope', '$http', '$routeParams', '$location',
  function ($scope, $http, $routeParams, $location) {

    $scope.newUser = true;
    $scope.error = $routeParams.error || '';
    $scope.clearError = function() { $scope.error = null; };

    $scope.signIn = function() {
      $scope.newUser = false;
    };

    $scope.signUp = function() {
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
    $scope.verify = function() {
      if (!$scope.token) {
        $scope.error = "Verification code required";
        return;
      }
      $http.post('/api/auth/verify', {token: $scope.token}).
        success(function(data) {
          $rootScope.user = data;
          $location.url('/school');
        }).
        error(function() {
          $scope.error = 'Verification code invalid or expired';
        });
    };

    $scope.signIn = function() {
      delete $cookies.verify;
      $location.url('/sign-in')
    }
  }
]);


graderControllers.controller('SchoolCtrl', ['$scope', 'Class',
  function ($scope, Class) {
    $scope.show = {classes: false};
    $scope.classes = [];
    $scope.showClasses = function() {
      $scope.classes = Class.query();
      $scope.show.classes = true;
    }

  }
]);
