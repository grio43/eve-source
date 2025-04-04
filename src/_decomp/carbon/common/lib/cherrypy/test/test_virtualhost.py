#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\lib\cherrypy\test\test_virtualhost.py
import os
curdir = os.path.join(os.getcwd(), os.path.dirname(__file__))
import cherrypy
from cherrypy.test import helper

class VirtualHostTest(helper.CPWebCase):

    def setup_server():

        class Root:

            def index(self):
                return 'Hello, world'

            index.exposed = True

            def dom4(self):
                return 'Under construction'

            dom4.exposed = True

            def method(self, value):
                return 'You sent %s' % repr(value)

            method.exposed = True

        class VHost:

            def __init__(self, sitename):
                self.sitename = sitename

            def index(self):
                return 'Welcome to %s' % self.sitename

            index.exposed = True

            def vmethod(self, value):
                return 'You sent %s' % repr(value)

            vmethod.exposed = True

            def url(self):
                return cherrypy.url('nextpage')

            url.exposed = True
            static = cherrypy.tools.staticdir.handler(section='/static', dir=curdir)

        root = Root()
        root.mydom2 = VHost('Domain 2')
        root.mydom3 = VHost('Domain 3')
        hostmap = {'www.mydom2.com': '/mydom2',
         'www.mydom3.com': '/mydom3',
         'www.mydom4.com': '/dom4'}
        cherrypy.tree.mount(root, config={'/': {'request.dispatch': cherrypy.dispatch.VirtualHost(**hostmap)},
         '/mydom2/static2': {'tools.staticdir.on': True,
                             'tools.staticdir.root': curdir,
                             'tools.staticdir.dir': 'static',
                             'tools.staticdir.index': 'index.html'}})

    setup_server = staticmethod(setup_server)

    def testVirtualHost(self):
        self.getPage('/', [('Host', 'www.mydom1.com')])
        self.assertBody('Hello, world')
        self.getPage('/mydom2/', [('Host', 'www.mydom1.com')])
        self.assertBody('Welcome to Domain 2')
        self.getPage('/', [('Host', 'www.mydom2.com')])
        self.assertBody('Welcome to Domain 2')
        self.getPage('/', [('Host', 'www.mydom3.com')])
        self.assertBody('Welcome to Domain 3')
        self.getPage('/', [('Host', 'www.mydom4.com')])
        self.assertBody('Under construction')
        self.getPage('/method?value=root')
        self.assertBody("You sent u'root'")
        self.getPage('/vmethod?value=dom2+GET', [('Host', 'www.mydom2.com')])
        self.assertBody("You sent u'dom2 GET'")
        self.getPage('/vmethod', [('Host', 'www.mydom3.com')], method='POST', body='value=dom3+POST')
        self.assertBody("You sent u'dom3 POST'")
        self.getPage('/vmethod/pos', [('Host', 'www.mydom3.com')])
        self.assertBody("You sent 'pos'")
        self.getPage('/url', [('Host', 'www.mydom2.com')])
        self.assertBody('%s://www.mydom2.com/nextpage' % self.scheme)

    def test_VHost_plus_Static(self):
        self.getPage('/static/style.css', [('Host', 'www.mydom2.com')])
        self.assertStatus('200 OK')
        self.assertHeader('Content-Type', 'text/css;charset=utf-8')
        self.getPage('/static2/dirback.jpg', [('Host', 'www.mydom2.com')])
        self.assertStatus('200 OK')
        self.assertHeader('Content-Type', 'image/jpeg')
        self.getPage('/static2/', [('Host', 'www.mydom2.com')])
        self.assertStatus('200 OK')
        self.assertBody('Hello, world\r\n')
        self.getPage('/static2', [('Host', 'www.mydom2.com')])
        self.assertStatus(301)
