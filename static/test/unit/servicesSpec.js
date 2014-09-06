'use strict';

describe('service', function () {

  // load modules
    beforeEach(module('graderApp'));

    // Test service availability
    it('check the existence of User factory', inject(function (User) {
        expect(User).toBeDefined();
    }));
});
