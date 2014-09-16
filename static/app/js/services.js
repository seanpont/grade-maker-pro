'use strict';

/* Services */

var graderServices = angular.module('graderServices', ['ngResource']);

graderServices.factory('User', ['$resource',
  function ($resource) {
    return $resource('/api/user');
  }]);

graderServices.factory('Classroom', ['$resource',
  function ($resource) {
    return $resource('/api/classroom/:id', {id: '@id'});
  }]);

graderServices.factory('Student', ['$resource',
  function($resource) {
    return $resource('/api/student/:id', {id: '@id'}, {
        find: {method: "GET", url: '/api/student/find'}
      }
    );
  }]);





