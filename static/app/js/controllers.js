'use strict';

/* Controllers */

var graderControllers = angular.module('graderControllers', []);

graderControllers.controller('SignInCtrl', ['$scope', '$http', 'Data',
    function ($scope, $http, Data) {
        $scope.signIn = function() {
            $http.post('/api/user', {email: $scope.email, password: $scope.password}).
                success(function(data, status, headers, config) {
                    console.log("auth success!");
                    console.log(data);
                    Data.user = data;
                }).
                error(function(data, status, headers, config) {
                    console.log("auth fail!");
                    console.log(data);
                    alert("Email or Password invalid");
                });
        }
    }
]);

graderControllers.controller('HallwayCtrl', ['$scope', 'Grader',
    function ($scope, Grader) {

    }
]);
