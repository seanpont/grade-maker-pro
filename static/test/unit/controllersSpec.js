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

  beforeEach(module('graderControllers'));

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

  // ===== SIGN IN ======================================================================

  describe('SignInCtrl', function () {

    beforeEach(function () {
      $httpBackend.expectPOST('/api/auth', { email: 'seanpont@gmail.com'}).respond({});
      ctrl = $controller('SignInCtrl', {$scope: scope});
    });

    it('should sign the user in when provided email and password', function () {
      scope.signIn();
      expect(scope.error).toBeDefined();
      scope.email = user.email;
      scope.signIn();
      $httpBackend.flush();
      expect(location.)
    });
  });

  describe('SignInCtrl', function() {
    beforeEach(function() {
      $httpBackend.expectPOST('/api/user', {email: user.email, name: user.name}).respond({});
      ctrl = $controller('SignInCtrl', {$scope: scope});
    });

    it('creates a user when commanded thusly', function() {
      // TODO: implement test
    });
  })

});
