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

    describe('SignInCtrl', function () {
        var scope, ctrl, $httpBackend, Data;

        var creds = {
            email: 'seanpont@gmail.com',
            password: 'asdf1234'
        }

        var user = {
            name: "Sean Pont",
            email: "seanpont@gmail.com",
            classrooms: [1, 2, 3]
        }

        beforeEach(inject(function (_$httpBackend_, $rootScope, $controller, _Data_) {
            $httpBackend = _$httpBackend_;
            $httpBackend.expectPOST('/api/user', creds).respond(user);

            scope = $rootScope.$new();
            ctrl = $controller('SignInCtrl', {$scope: scope});
            Data = _Data_;
        }));


        it('should sign the user in when provided email and password', function () {
            expect(Data.user).toBeUndefined();
            scope.email = creds.email;
            scope.password = creds.password;
            scope.signIn();
            $httpBackend.flush();
            expect(Data.user).toEqualData(user);
        });
    });


//    describe('PhoneDetailCtrl', function () {
//        var scope, $httpBackend, ctrl,
//            xyzPhoneData = function () {
//                return {
//                    name: 'phone xyz',
//                    images: ['image/url1.png', 'image/url2.png']
//                }
//            };
//
//
//        beforeEach(inject(function (_$httpBackend_, $rootScope, $routeParams, $controller) {
//            $httpBackend = _$httpBackend_;
//            $httpBackend.expectGET('phones/xyz.json').respond(xyzPhoneData());
//
//            $routeParams.phoneId = 'xyz';
//            scope = $rootScope.$new();
//            ctrl = $controller('PhoneDetailCtrl', {$scope: scope});
//        }));
//
//
//        it('should fetch phone detail', function () {
//            expect(scope.phone).toEqualData({});
//            $httpBackend.flush();
//
//            expect(scope.phone).toEqualData(xyzPhoneData());
//        });
//    });
});
