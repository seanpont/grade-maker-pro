'use strict';

/* Controllers */

var graderControllers = angular.module('graderControllers', []);


graderControllers.controller('HomeCtrl', ['$scope', '$location', '$http', 'Data',
    function($scope, $location, $http, Data) {
        $http.get('/api/user').
            success(function(data) {
                Data.user = data;
                $location.url('/hallway')
            }).
            error(function() {
                $location.url('/sign-in')
            });
    }
]);

graderControllers.controller('SignInCtrl', ['$scope', '$http', '$routeParams', '$location', 'Data',
    function ($scope, $http, $routeParams, $location, Data) {

        $scope.error = $routeParams.error || '';

        $scope.signIn = function() {
            if (!$scope.email || !$scope.password) {
                $scope.error = 'Email and password required';
                return;
            }
            $http.post('/api/auth', {email: $scope.email, password: $scope.password}).
                success(function(data) {
                    Data.user = data;
                    $location.url('/hallway')
                }).
                error(function() {
                    $scope.error = "Email or password invalid";
                });
        };

        $scope.clearError = function() {
            $scope.error = null;
        }
    }
]);

graderControllers.controller('HallwayCtrl', ['$scope', 'Grader',
    function ($scope, Grader) {

    }
]);
