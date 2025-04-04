#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\lib\cherrypy\test\test_caching.py
import datetime
import gzip
from itertools import count
import os
curdir = os.path.join(os.getcwd(), os.path.dirname(__file__))
import sys
import threading
import time
import urllib
import cherrypy
from cherrypy._cpcompat import next, ntob, quote, xrange
from cherrypy.lib import httputil
gif_bytes = ntob('GIF89a\x01\x00\x01\x00\x82\x00\x01\x99"\x1e\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x02\x03\x02\x08\t\x00;')
from cherrypy.test import helper

class CacheTest(helper.CPWebCase):

    def setup_server():

        class Root:
            _cp_config = {'tools.caching.on': True}

            def __init__(self):
                self.counter = 0
                self.control_counter = 0
                self.longlock = threading.Lock()

            def index(self):
                self.counter += 1
                msg = 'visit #%s' % self.counter
                return msg

            index.exposed = True

            def control(self):
                self.control_counter += 1
                return 'visit #%s' % self.control_counter

            control.exposed = True

            def a_gif(self):
                cherrypy.response.headers['Last-Modified'] = httputil.HTTPDate()
                return gif_bytes

            a_gif.exposed = True

            def long_process(self, seconds = '1'):
                try:
                    self.longlock.acquire()
                    time.sleep(float(seconds))
                finally:
                    self.longlock.release()

                return 'success!'

            long_process.exposed = True

            def clear_cache(self, path):
                cherrypy._cache.store[cherrypy.request.base + path].clear()

            clear_cache.exposed = True

        class VaryHeaderCachingServer(object):
            _cp_config = {'tools.caching.on': True,
             'tools.response_headers.on': True,
             'tools.response_headers.headers': [('Vary', 'Our-Varying-Header')]}

            def __init__(self):
                self.counter = count(1)

            def index(self):
                return 'visit #%s' % next(self.counter)

            index.exposed = True

        class UnCached(object):
            _cp_config = {'tools.expires.on': True,
             'tools.expires.secs': 60,
             'tools.staticdir.on': True,
             'tools.staticdir.dir': 'static',
             'tools.staticdir.root': curdir}

            def force(self):
                cherrypy.response.headers['Etag'] = 'bibbitybobbityboo'
                self._cp_config['tools.expires.force'] = True
                self._cp_config['tools.expires.secs'] = 0
                return 'being forceful'

            force.exposed = True
            force._cp_config = {'tools.expires.secs': 0}

            def dynamic(self):
                cherrypy.response.headers['Etag'] = 'bibbitybobbityboo'
                cherrypy.response.headers['Cache-Control'] = 'private'
                return 'D-d-d-dynamic!'

            dynamic.exposed = True

            def cacheable(self):
                cherrypy.response.headers['Etag'] = 'bibbitybobbityboo'
                return "Hi, I'm cacheable."

            cacheable.exposed = True

            def specific(self):
                cherrypy.response.headers['Etag'] = 'need_this_to_make_me_cacheable'
                return 'I am being specific'

            specific.exposed = True
            specific._cp_config = {'tools.expires.secs': 86400}

            class Foo(object):
                pass

            def wrongtype(self):
                cherrypy.response.headers['Etag'] = 'need_this_to_make_me_cacheable'
                return 'Woops'

            wrongtype.exposed = True
            wrongtype._cp_config = {'tools.expires.secs': Foo()}

        cherrypy.tree.mount(Root())
        cherrypy.tree.mount(UnCached(), '/expires')
        cherrypy.tree.mount(VaryHeaderCachingServer(), '/varying_headers')
        cherrypy.config.update({'tools.gzip.on': True})

    setup_server = staticmethod(setup_server)

    def testCaching(self):
        elapsed = 0.0
        for trial in range(10):
            self.getPage('/')
            self.assertBody('visit #1')
            if trial != 0:
                age = int(self.assertHeader('Age'))
                self.assert_(age >= elapsed)
                elapsed = age

        self.getPage('/', method='POST')
        self.assertBody('visit #2')
        self.assertHeader('Vary', 'Accept-Encoding')
        self.getPage('/', method='GET')
        self.assertBody('visit #3')
        self.getPage('/', method='GET')
        self.assertBody('visit #3')
        self.getPage('/', method='DELETE')
        self.assertBody('visit #4')
        self.getPage('/', method='GET', headers=[('Accept-Encoding', 'gzip')])
        self.assertHeader('Content-Encoding', 'gzip')
        self.assertHeader('Vary')
        self.assertEqual(cherrypy.lib.encoding.decompress(self.body), ntob('visit #5'))
        self.getPage('/', method='GET', headers=[('Accept-Encoding', 'gzip')])
        self.assertHeader('Content-Encoding', 'gzip')
        self.assertEqual(cherrypy.lib.encoding.decompress(self.body), ntob('visit #5'))
        self.getPage('/', method='GET')
        self.assertNoHeader('Content-Encoding')
        self.assertBody('visit #6')

    def testVaryHeader(self):
        self.getPage('/varying_headers/')
        self.assertStatus('200 OK')
        self.assertHeaderItemValue('Vary', 'Our-Varying-Header')
        self.assertBody('visit #1')
        self.getPage('/varying_headers/', headers=[('Our-Varying-Header', 'request 2')])
        self.assertStatus('200 OK')
        self.assertBody('visit #2')
        self.getPage('/varying_headers/', headers=[('Our-Varying-Header', 'request 2')])
        self.assertStatus('200 OK')
        self.assertBody('visit #2')
        self.getPage('/varying_headers/')
        self.assertStatus('200 OK')
        self.assertBody('visit #1')

    def testExpiresTool(self):
        self.getPage('/expires/specific')
        self.assertStatus('200 OK')
        self.assertHeader('Expires')
        self.getPage('/expires/wrongtype')
        self.assertStatus(500)
        self.assertInBody('TypeError')
        self.getPage('/expires/index.html')
        self.assertStatus('200 OK')
        self.assertNoHeader('Pragma')
        self.assertNoHeader('Cache-Control')
        self.assertHeader('Expires')
        self.getPage('/expires/cacheable')
        self.assertStatus('200 OK')
        self.assertNoHeader('Pragma')
        self.assertNoHeader('Cache-Control')
        self.assertHeader('Expires')
        self.getPage('/expires/dynamic')
        self.assertBody('D-d-d-dynamic!')
        self.assertHeader('Cache-Control', 'private')
        self.assertHeader('Expires')
        self.getPage('/expires/force')
        self.assertStatus('200 OK')
        self.assertHeader('Pragma', 'no-cache')
        if cherrypy.server.protocol_version == 'HTTP/1.1':
            self.assertHeader('Cache-Control', 'no-cache, must-revalidate')
        self.assertHeader('Expires', 'Sun, 28 Jan 2007 00:00:00 GMT')
        self.getPage('/expires/index.html')
        self.assertStatus('200 OK')
        self.assertHeader('Pragma', 'no-cache')
        if cherrypy.server.protocol_version == 'HTTP/1.1':
            self.assertHeader('Cache-Control', 'no-cache, must-revalidate')
        self.assertHeader('Expires', 'Sun, 28 Jan 2007 00:00:00 GMT')
        self.getPage('/expires/cacheable')
        self.assertStatus('200 OK')
        self.assertHeader('Pragma', 'no-cache')
        if cherrypy.server.protocol_version == 'HTTP/1.1':
            self.assertHeader('Cache-Control', 'no-cache, must-revalidate')
        self.assertHeader('Expires', 'Sun, 28 Jan 2007 00:00:00 GMT')
        self.getPage('/expires/dynamic')
        self.assertBody('D-d-d-dynamic!')
        self.assertHeader('Pragma', 'no-cache')
        if cherrypy.server.protocol_version == 'HTTP/1.1':
            self.assertHeader('Cache-Control', 'no-cache, must-revalidate')
        self.assertHeader('Expires', 'Sun, 28 Jan 2007 00:00:00 GMT')

    def testLastModified(self):
        self.getPage('/a.gif')
        self.assertStatus(200)
        self.assertBody(gif_bytes)
        lm1 = self.assertHeader('Last-Modified')
        self.getPage('/a.gif')
        self.assertStatus(200)
        self.assertBody(gif_bytes)
        self.assertHeader('Age')
        lm2 = self.assertHeader('Last-Modified')
        self.assertEqual(lm1, lm2)
        self.getPage('/a.gif', [('If-Modified-Since', lm1)])
        self.assertStatus(304)
        self.assertNoHeader('Last-Modified')
        if not getattr(cherrypy.server, 'using_apache', False):
            self.assertHeader('Age')

    def test_antistampede(self):
        SECONDS = 4
        self.getPage('/long_process?seconds=%d' % SECONDS)
        self.assertBody('success!')
        self.getPage('/clear_cache?path=' + quote('/long_process?seconds=%d' % SECONDS, safe=''))
        self.assertStatus(200)
        sys.stdout.write('prepped... ')
        sys.stdout.flush()
        start = datetime.datetime.now()

        def run():
            self.getPage('/long_process?seconds=%d' % SECONDS)
            self.assertBody('success!')

        ts = [ threading.Thread(target=run) for i in xrange(100) ]
        for t in ts:
            t.start()

        for t in ts:
            t.join()

        self.assertEqualDates(start, datetime.datetime.now(), seconds=SECONDS + 1.1)

    def test_cache_control(self):
        self.getPage('/control')
        self.assertBody('visit #1')
        self.getPage('/control')
        self.assertBody('visit #1')
        self.getPage('/control', headers=[('Cache-Control', 'no-cache')])
        self.assertBody('visit #2')
        self.getPage('/control')
        self.assertBody('visit #2')
        self.getPage('/control', headers=[('Pragma', 'no-cache')])
        self.assertBody('visit #3')
        self.getPage('/control')
        self.assertBody('visit #3')
        time.sleep(1)
        self.getPage('/control', headers=[('Cache-Control', 'max-age=0')])
        self.assertBody('visit #4')
        self.getPage('/control')
        self.assertBody('visit #4')
