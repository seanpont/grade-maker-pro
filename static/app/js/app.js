'use strict';

/* App Module */

var graderApp = angular.module('graderApp', [
    'ngRoute',
    'graderControllers',
    'graderServices',
    'graderAnimations',
    'graderFilters'
]);

graderApp.config(['$routeProvider',
    function ($routeProvider) {
        $routeProvider.
            when('/', {
                templateUrl: 'partials/home.html',
                controller: 'HomeCtrl'
            }).
            when('/sign-in', {
                templateUrl: 'partials/sign-in.html',
                controller: 'SignInCtrl'
            }).
            when('/hallway', {
                templateUrl: 'partials/hallway.html',
                controller: 'HallwayCtrl'
            }).
            otherwise({
                redirectTo: '/sign-in'
            });
    }]);

graderApp.factory("Data", function() {return {}});