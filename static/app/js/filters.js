'use strict';

/* Filters */

angular.module('graderFilters', []).filter('checkmark', function () {
    return function (input) {
        return input ? '\u2713' : '\u2718';
    };
});
