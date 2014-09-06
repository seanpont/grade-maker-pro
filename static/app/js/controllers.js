'use strict';

/* Controllers */

var graderControllers = angular.module('graderControllers', []);

graderControllers.controller('SignInCtrl', ['$scope', '$http', '$routeParams', 'Data',
    function ($scope, $http, $routeParams, Data) {

        if ($routeParams.error) {
            $scope.error = $routeParams.error;
        }

        $scope.signIn = function() {
            if (!$scope.email || !$scope.password) {
                $scope.error = 'Email and password required';
                return;
            }
            $http.post('/api/user', {email: $scope.email, password: $scope.password}).
                success(function(data) {
                    console.log("auth success!");
                    console.log(data);
                    Data.user = data;
                }).
                error(function() {
                    $scope.error = "Email or password invalid";
                });
        }

        $scope.clearError = function() {
            $scope.error = null;
        }
    }
]);

graderControllers.controller('HallwayCtrl', ['$scope', 'Grader',
    function ($scope, Grader) {

    }
]);
