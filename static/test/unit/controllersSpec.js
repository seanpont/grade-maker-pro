'use strict';

/* jasmine specs for controllers go here */
describe('GraderApp controllers', function () {

    beforeEach(function () {
        this.addMatchers({
            toEqualData: function (expected) {
                return angular.equals(this.actual, expected);
            }
        });
    });

    beforeEach(module('graderApp'));
    beforeEach(module('graderServices'));

    var creds = {
        email: 'seanpont@gmail.com',
        password: 'asdf1234'
    };

    var user = {
        name: "Sean Pont",
        email: "seanpont@gmail.com",
        classrooms: [1, 2, 3]
    };

    var scope, ctrl, $controller, $location, $httpBackend, Data;

    beforeEach(inject(function (_$httpBackend_, $rootScope, _$location_, _$controller_, _Data_) {
        $httpBackend = _$httpBackend_;
        $location = _$location_;
        $controller = _$controller_;
        scope = $rootScope.$new();
        Data = _Data_;
    }));

    // ===== HOME =======================================================

    describe('HomeCtrl', function () {

        beforeEach(function() {
            $httpBackend.expectGET('/api/user').respond(user);
            ctrl = $controller('HomeCtrl', {$scope: scope});
        });

        it('should go to the hallway when the user is signed in', function () {
            $httpBackend.flush();
            expect(Data.user).toEqualData(user);
            expect($location.path()).toBe('/hallway')
        });
    });

    describe('HomeCtrl', function () {

        beforeEach(function () {
            $httpBackend.expectGET('/api/user').respond(404, {});
            ctrl = $controller('HomeCtrl', {$scope: scope});
        });

        it('should go to the hallway when the user is signed in', function () {
            $httpBackend.flush();
            expect(Data.user).toBeUndefined();
            expect($location.path()).toBe('/sign-in')
        });
    });

    // ===== SIGN IN ======================================================================

    describe('SignInCtrl', function () {

        beforeEach(function () {
            $httpBackend.expectPOST('/api/auth', creds).respond(user);
            ctrl = $controller('SignInCtrl', {$scope: scope});
        });

        it('should sign the user in when provided email and password', function () {
            expect(Data.user).toBeUndefined();
            scope.email = creds.email;
            scope.password = creds.password;
            scope.signIn();
            $httpBackend.flush();
            expect(Data.user).toEqualData(user);
            expect($location.path()).toBe('/hallway')
        });
    });

});
