#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\lib\cherrypy\tutorial\tut10_http_errors.py
import os
localDir = os.path.dirname(__file__)
curpath = os.path.normpath(os.path.join(os.getcwd(), localDir))
import cherrypy

class HTTPErrorDemo(object):
    _cp_config = {'error_page.403': os.path.join(curpath, 'custom_error.html')}

    def index(self):
        tracebacks = cherrypy.request.show_tracebacks
        if tracebacks:
            trace = 'off'
        else:
            trace = 'on'
        return '\n        <html><body>\n            <p>Toggle tracebacks <a href="toggleTracebacks">%s</a></p>\n            <p><a href="/doesNotExist">Click me; I\'m a broken link!</a></p>\n            <p><a href="/error?code=403">Use a custom error page from a file.</a></p>\n            <p>These errors are explicitly raised by the application:</p>\n            <ul>\n                <li><a href="/error?code=400">400</a></li>\n                <li><a href="/error?code=401">401</a></li>\n                <li><a href="/error?code=402">402</a></li>\n                <li><a href="/error?code=500">500</a></li>\n            </ul>\n            <p><a href="/messageArg">You can also set the response body\n            when you raise an error.</a></p>\n        </body></html>\n        ' % trace

    index.exposed = True

    def toggleTracebacks(self):
        tracebacks = cherrypy.request.show_tracebacks
        cherrypy.config.update({'request.show_tracebacks': not tracebacks})
        raise cherrypy.HTTPRedirect('/')

    toggleTracebacks.exposed = True

    def error(self, code):
        raise cherrypy.HTTPError(status=code)

    error.exposed = True

    def messageArg(self):
        message = "If you construct an HTTPError with a 'message' argument, it wil be placed on the error page (underneath the status line by default)."
        raise cherrypy.HTTPError(500, message=message)

    messageArg.exposed = True


import os.path
tutconf = os.path.join(os.path.dirname(__file__), 'tutorial.conf')
if __name__ == '__main__':
    cherrypy.quickstart(HTTPErrorDemo(), config=tutconf)
else:
    cherrypy.tree.mount(HTTPErrorDemo(), config=tutconf)
