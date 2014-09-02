import webapp2
from lib import router

app = webapp2.WSGIApplication(router.collect('app.views'), debug=True)




 






