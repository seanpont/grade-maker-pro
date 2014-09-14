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
  beforeEach(module('ngCookies'));

  var user = {
    name: "Sean Pont",
    email: "seanpont@gmail.com",
    classrooms: [1, 2, 3]
  };

  var scope, ctrl, $controller, $location, $httpBackend, $cookies;

  beforeEach(inject(function (_$httpBackend_, $rootScope, _$location_, _$controller_, _$cookies_) {
    $httpBackend = _$httpBackend_;
    $location = _$location_;
    $controller = _$controller_;
    scope = $rootScope.$new();
    $cookies = _$cookies_;
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
      ctrl = $controller('VerifyCtrl', {$scope: scope, $cookies: $cookies});
      scope.verify();
      expect(scope.error).toBeDefined();
      scope.token = 123456;
      scope.verify();
      $httpBackend.flush();
      expect(scope.user).toEqualData(user);
      expect($location.path()).toBe('/school');
    });
  });

  // ===== SchoolCtrl ======================================================================

  describe('SchoolCtrl', function() {

    it('should be able to create a classroom', function() {
      $httpBackend.expectGET('/api/classroom').respond([]);
      ctrl = $controller('SchoolCtrl', {$scope: scope});
      $httpBackend.flush();
      expect(scope.classrooms.length).toBe(0);

      // error case
      scope.createClassroom.create();
      expect(scope.createClassroom.error).toMatch("Please.*");

      // happy case: Math!
      scope.createClassroom.name = "Math";
      $httpBackend.expectPOST('/api/classroom', {name: 'Math'}).
        respond({name: 'Math', students: []});
      scope.createClassroom.create();
      $httpBackend.flush();
      expect(scope.classrooms.length).toBe(1);




    });



  })


});
