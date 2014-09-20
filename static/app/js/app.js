'use strict';

/* App Module */

var graderApp = angular.module('graderApp', [
  'ngRoute', 'ngCookies', 'graderControllers', 'graderServices', 'graderAnimations'
]);

graderApp.config(['$routeProvider',
  function ($routeProvider) {
    $routeProvider.
      when('/home', {
        templateUrl: 'partials/home.html',
        controller: 'HomeCtrl'
      }).
      when('/sign-in', {
        templateUrl: 'partials/sign-in.html',
        controller: 'SignInCtrl'
      }).
      when('/verify', {
        templateUrl: 'partials/verify.html',
        controller: 'VerifyCtrl'
      }).
      when('/school', {
        templateUrl: 'partials/school.html',
        controller: 'SchoolCtrl'
      }).
      otherwise({
        redirectTo: '/home'
      });
  }
]);

graderApp.run(['$http', '$location', '$cookies', '$rootScope',
  function ($http, $location, $cookies, $rootScope) {
    $http.get('/api/user').
      success(function (data) {
        $rootScope.user = data;
        $location.url('/school')
      }).
      error(function () {
        if ($cookies.verify) {
          $location.url('/verify')
        } else {
          $location.url('/sign-in')
        }
      });
  }]);

graderApp.directive('onlyNum', function () {
  return function (scope, element, attrs) {

    var keyCode = [8, 9, 37, 39, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 110, 190];
    element.bind("keydown", function (event) {
      if ($.inArray(event.which, keyCode) == -1) {
        scope.$apply(function () {
          scope.$eval(attrs.onlyNum);
          event.preventDefault();
        });
        event.preventDefault();
      }
    });
  };
});

