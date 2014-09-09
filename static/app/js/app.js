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
      when('/hallway', {
        templateUrl: 'partials/hallway.html',
        controller: 'HallwayCtrl'
      }).
      otherwise({
        redirectTo: '/home'
      });
  }
]);

graderApp.run(['$http', '$location', '$cookies', 'Data', function ($http, $location, $cookies, Data) {
  if ($cookies.verify) {
    console.log($cookies.verify)
    $location.url('/verify')
  } else {
    $http.get('/api/user').
      success(function (data) {
        Data.user = data;
        $location.url('/hallway')
      }).
      error(function () {
        $location.url('/sign-in')
      });
  }
}]);