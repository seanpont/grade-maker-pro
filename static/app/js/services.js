'use strict';

/* Services */

var graderServices = angular.module('graderServices', ['ngResource']);

graderServices.factory('User', ['$resource',
  function ($resource) {
    return $resource('/api/user');
  }]);

graderServices.factory('Classroom', ['$resource',
  function ($resource) {
    return $resource('/api/classroom/:key', {key: '@key'});
  }]);






