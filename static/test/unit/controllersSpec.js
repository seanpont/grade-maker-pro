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

  // ===== SignInCtrl ======================================================================

  describe('SignInCtrl', function () {

    it('should verify the user in when provided email', function () {
      $httpBackend.expectPOST('/api/auth', { email: 'seanpont@gmail.com'}).respond({});
      ctrl = $controller('SignInCtrl', {$scope: scope});
      scope.signIn();
      scope.authenticate();
      expect(scope.error).toBeDefined();
      scope.email = user.email;
      scope.authenticate();
      $httpBackend.flush();
      expect($location.path()).toBe('/verify')
    });

    it('creates a user when commanded thusly', function() {
      $httpBackend.expectPOST('/api/auth', {email: user.email, name: user.name}).respond({});
      ctrl = $controller('SignInCtrl', {$scope: scope});
      scope.signUp();
      scope.email = user.email;
      scope.authenticate();
      expect(scope.error).toBeDefined();
      scope.name = user.name;
      scope.authenticate();
      $httpBackend.flush();
      expect($location.path()).toBe('/verify');
    });
  });

  // ===== VerifyCtrl ======================================================================

  describe('VerifyCtrl', function() {

    it('should verify the code', function() {
      $httpBackend.expectPOST('/api/auth/verify', {token: 123456}).respond(user);
      ctrl = $controller('VerifyCtrl', {$scope: scope});
      scope.verify();
      expect(scope.error).toBeDefined();
      scope.token = 123456;
      scope.verify();
      $httpBackend.flush();
      expect(Data.user).toEqualData(user);
      expect($location.path()).toBe('/hallway');
    });
  });

});
