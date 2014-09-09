'use strict';

/* Controllers */


var graderControllers = angular.module('graderControllers', [
  'ngRoute', 'ui.bootstrap', 'graderServices']);

graderControllers.controller('HomeCtrl', function() {});

graderControllers.controller('SignInCtrl', ['$scope', '$http', '$modal', '$routeParams',
  function ($scope, $http, $modal, $routeParams) {

    $scope.signingIn = false;
    $scope.error = $routeParams.error || '';

    $scope.signIn = function () {
      console.log('signIn')
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

graderControllers.controller('SignInCtrl', ['$scope', '$http', '$modal', '$routeParams',
  function ($scope, $http, $modal, $routeParams) {

  }
]);


graderControllers.controller('HallwayCtrl', ['$scope', 'Grader',
  function ($scope, Grader) {

  }
]);
