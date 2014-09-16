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

    it('creates a user when commanded thusly', function () {
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

  describe('VerifyCtrl', function () {

    it('should verify the code', function () {
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

  describe('SchoolCtrl', function () {

    it('should be able to create a classroom', function () {
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

    var classroom = {
      name: 'Phoenix',
      id: 1234
    };

    var inflatedClassroom = {
      name: 'Phoenix',
      id: 1234,
      students: [
        {name: 'Bobby', id: 2345},
        {name: 'Jimmy', id: 3456}
      ],
      assignments: [
        {name: 'Quiz1',
          total_points: 100,
          grades: {
            2345: 88,
            3456: 93
          }
        }
      ]
    };

    it('should be able to display a classroom', function () {
      $httpBackend.expectGET('/api/classroom').respond([classroom])
      ctrl = $controller('SchoolCtrl', {$scope: scope});
      $httpBackend.flush();
      expect(scope.classrooms[0].id).toBe(classroom.id);

      $httpBackend.expectGET('/api/classroom/' + classroom.id).respond(inflatedClassroom);
      scope.displayClassroom(scope.classrooms[0]);
      $httpBackend.flush();
      expect(scope.classroom).toEqualData(inflatedClassroom);
      expect(scope.show.classroom).toBe(true);
      var assignment = scope.classroom.assignments[0];
      var student1 = scope.classroom.students[0];
      var student2 = scope.classroom.students[1];
      expect(assignment.grades[student1.id]).toBe(88);
      expect(assignment.grades[student2.id]).toBe(93);
    });

    var student = {
      id: 49194,
      name: 'Jeremy'
    };

    it('should be able to create a student', function() {
      $httpBackend.whenGET('/api/classroom').respond([classroom]);
      $httpBackend.whenGET('/api/classroom/' + classroom.id).respond(inflatedClassroom);
      ctrl = $controller('SchoolCtrl', {$scope: scope});
      $httpBackend.flush();
      scope.displayClassroom(scope.classrooms[0]);
      $httpBackend.flush();

      scope.createStudent.create();
      expect(scope.createStudent.error).toBeDefined();
      scope.createStudent.name = student.name;
      scope.createStudent.create();
      $httpBackend.expectPOST('/api/student', {
        name: 'Jeremy', classroom_id: classroom.id
        }).respond(student);
      $httpBackend.flush();
      expect(scope.classroom.students.length).toBe(3);





    });


  })


});
