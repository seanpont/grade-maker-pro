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

graderApp.value("Data", function() {return {}});