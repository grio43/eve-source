#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\lib\cherrypy\test\test_wsgiapps.py
from cherrypy.test import helper

class WSGIGraftTests(helper.CPWebCase):

    def setup_server():
        import os
        curdir = os.path.join(os.getcwd(), os.path.dirname(__file__))
        import cherrypy

        def test_app(environ, start_response):
            status = '200 OK'
            response_headers = [('Content-type', 'text/plain')]
            start_response(status, response_headers)
            output = ['Hello, world!\n', 'This is a wsgi app running within CherryPy!\n\n']
            keys = list(environ.keys())
            keys.sort()
            for k in keys:
                output.append('%s: %s\n' % (k, environ[k]))

            return output

        def test_empty_string_app(environ, start_response):
            status = '200 OK'
            response_headers = [('Content-type', 'text/plain')]
            start_response(status, response_headers)
            return ['Hello',
             '',
             ' ',
             '',
             'world']

        class WSGIResponse(object):

            def __init__(self, appresults):
                self.appresults = appresults
                self.iter = iter(appresults)

            def __iter__(self):
                return self

            def next(self):
                return self.iter.next()

            def close(self):
                if hasattr(self.appresults, 'close'):
                    self.appresults.close()

        class ReversingMiddleware(object):

            def __init__(self, app):
                self.app = app

            def __call__(self, environ, start_response):
                results = app(environ, start_response)

                class Reverser(WSGIResponse):

                    def next(this):
                        line = list(this.iter.next())
                        line.reverse()
                        return ''.join(line)

                return Reverser(results)

        class Root:

            def index(self):
                return "I'm a regular CherryPy page handler!"

            index.exposed = True

        cherrypy.tree.mount(Root())
        cherrypy.tree.graft(test_app, '/hosted/app1')
        cherrypy.tree.graft(test_empty_string_app, '/hosted/app3')
        app = cherrypy.Application(Root(), script_name=None)
        cherrypy.tree.graft(ReversingMiddleware(app), '/hosted/app2')

    setup_server = staticmethod(setup_server)
    wsgi_output = 'Hello, world!\nThis is a wsgi app running within CherryPy!'

    def test_01_standard_app(self):
        self.getPage('/')
        self.assertBody("I'm a regular CherryPy page handler!")

    def test_04_pure_wsgi(self):
        import cherrypy
        if not cherrypy.server.using_wsgi:
            return self.skip('skipped (not using WSGI)... ')
        self.getPage('/hosted/app1')
        self.assertHeader('Content-Type', 'text/plain')
        self.assertInBody(self.wsgi_output)

    def test_05_wrapped_cp_app(self):
        import cherrypy
        if not cherrypy.server.using_wsgi:
            return self.skip('skipped (not using WSGI)... ')
        self.getPage('/hosted/app2/')
        body = list("I'm a regular CherryPy page handler!")
        body.reverse()
        body = ''.join(body)
        self.assertInBody(body)

    def test_06_empty_string_app(self):
        import cherrypy
        if not cherrypy.server.using_wsgi:
            return self.skip('skipped (not using WSGI)... ')
        self.getPage('/hosted/app3')
        self.assertHeader('Content-Type', 'text/plain')
        self.assertInBody('Hello world')
