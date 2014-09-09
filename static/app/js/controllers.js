'use strict';

/* Controllers */


var graderControllers = angular.module('graderControllers', [
  'ngRoute', 'ui.bootstrap', 'graderServices']);

graderControllers.controller('HomeCtrl', function() {});

graderControllers.controller('SignInCtrl', ['$scope', '$http', '$routeParams', '$location',
  function ($scope, $http, $routeParams, $location) {

    $scope.signingIn = false;
    $scope.error = $routeParams.error || '';

    $scope.signIn = function () {
      if (!$scope.email) {
        $scope.error = 'Email required';
        return;
      }
      $http.post('/api/auth', {email: $scope.email}).
        success(function () {
          $location.url('/verify');
        }).
        error(function () {
          $scope.error = "I'm sorry, we couldn't locate your account. Would you like to create one?";
        });
    };

    $scope.createUser = function() {
      if (!$scope.email || !$scope.name) {
        $scope.error = 'Name and email required';
        return;
      }
      $http.post('/api/user', {name: $scope.name, email: $scope.email}).
        success(function() {
          $location.url('/verify');
        }).
        error(function () {
          $scope.error = "I'm sorry, but there was a problem creating your account.";
        })
    };

    $scope.clearError = function () {
      $scope.error = null;
    }
  }
]);

graderControllers.controller('VerifyCtrl', ['$scope', '$http', '$location', 'Data',
  function ($scope, $http, $location, Data) {
    $scope.verify = function() {
      if (!$scope.token) {
        $scope.error = "Verification code required";
        return;
      }
      $http.post('/api/auth/verify', {token: $scope.token}).
        success(function(data) {
          console.log(data);
          Data.user = data;
          $location.url('/hallway');
        }).
        error(function() {
          $scope.error = 'Verification code invalid or expired';
        });
    };
  }
]);


graderControllers.controller('HallwayCtrl', ['$scope', 'Grader',
  function ($scope, Grader) {

  }
]);
