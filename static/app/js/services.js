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
  function ($resource) {
    return $resource('/api/student/:id', {id: '@id'});
  }]);

graderServices.factory('Assignment', ['$resource',
  function ($resource) {
    return $resource('/api/assignment/:id', {id: '@assignment_id'}, {
      grade: {
        method: 'POST',
        url: '/api/assignment/:id',
        params: {id: '@assignment_id'},
        data: {classroom_id: '@classroom_id', student_id: '@student_id', grade: '@grade'}
      }
    });
  }]);




