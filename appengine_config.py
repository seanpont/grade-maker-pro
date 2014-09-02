"""
App Engine config

"""

def webapp_add_wsgi_middleware(app):
    from google.appengine.ext.appstats import recording
    app = recording.appstats_wsgi_middleware(app)

    from lib.secret_keys import SESSION_KEY
    from lib.gaesessions import SessionMiddleware
    app = SessionMiddleware(app, cookie_key=SESSION_KEY)

    return app
