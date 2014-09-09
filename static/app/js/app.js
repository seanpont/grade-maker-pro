'use strict';

/* App Module */

var graderApp = angular.module('graderApp', [
  'ngRoute', 'graderControllers', 'graderServices'
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

graderApp.run(['$http', '$location', 'Data', function ($http, $location, Data) {
  console.log("fetching user info")
  $http.get('/api/user').
    success(function (data) {
      console.log('User is authenticated')
      Data.user = data;
      $location.url('/hallway')
    }).
    error(function () {
      console.log('user must sign in')
      $location.url('/sign-in')
    });
}]);