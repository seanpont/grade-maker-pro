'use strict';

/* Services */

var graderServices = angular.module('graderServices', ['ngResource']);

graderServices.factory('User', ['$resource',
    function ($resource) {
        return $resource('/api/user');
    }]);



