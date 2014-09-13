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