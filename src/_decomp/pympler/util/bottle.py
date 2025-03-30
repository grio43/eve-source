#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\pympler\util\bottle.py
from __future__ import with_statement
__author__ = 'Marcel Hellkamp'
__version__ = '0.11.4'
__license__ = 'MIT'
if __name__ == '__main__':
    from optparse import OptionParser
    _cmd_parser = OptionParser(usage='usage: %prog [options] package.module:app')
    _opt = _cmd_parser.add_option
    _opt('--version', action='store_true', help='show version number.')
    _opt('-b', '--bind', metavar='ADDRESS', help='bind socket to ADDRESS.')
    _opt('-s', '--server', default='wsgiref', help='use SERVER as backend.')
    _opt('-p', '--plugin', action='append', help='install additional plugin/s.')
    _opt('--debug', action='store_true', help='start server in debug mode.')
    _opt('--reload', action='store_true', help='auto-reload on file changes.')
    _cmd_options, _cmd_args = _cmd_parser.parse_args()
    if _cmd_options.server and _cmd_options.server.startswith('gevent'):
        import gevent.monkey
        gevent.monkey.patch_all()
import base64, cgi, email.utils, functools, hmac, imp, itertools, mimetypes, os, re, subprocess, sys, tempfile, threading, time, urllib, warnings
from datetime import date as datedate, datetime, timedelta
from tempfile import TemporaryFile
from traceback import format_exc, print_exc
try:
    from json import dumps as json_dumps, loads as json_lds
except ImportError:
    try:
        from simplejson import dumps as json_dumps, loads as json_lds
    except ImportError:
        try:
            from django.utils.simplejson import dumps as json_dumps, loads as json_lds
        except ImportError:

            def json_dumps(data):
                raise ImportError('JSON support requires Python 2.6 or simplejson.')


            json_lds = json_dumps

py = sys.version_info
py3k = py >= (3, 0, 0)
py25 = py < (2, 6, 0)
py31 = (3, 1, 0) <= py < (3, 2, 0)

def _e():
    return sys.exc_info()[1]


try:
    _stdout, _stderr = (sys.stdout.write, sys.stderr.write)
except IOError:
    _stdout = lambda x: sys.stdout.write(x)
    _stderr = lambda x: sys.stderr.write(x)

if py3k:
    import http.client as httplib
    import _thread as thread
    from urllib.parse import urljoin, SplitResult as UrlSplitResult
    from urllib.parse import urlencode, quote as urlquote, unquote as urlunquote
    urlunquote = functools.partial(urlunquote, encoding='latin1')
    from http.cookies import SimpleCookie
    from collections import MutableMapping as DictMixin
    import pickle
    from io import BytesIO
    basestring = str
    unicode = str
    json_loads = lambda s: json_lds(touni(s))
    callable = lambda x: hasattr(x, '__call__')
    imap = map
else:
    import httplib
    import thread
    from urlparse import urljoin, SplitResult as UrlSplitResult
    from urllib import urlencode, quote as urlquote, unquote as urlunquote
    from Cookie import SimpleCookie
    from itertools import imap
    import cPickle as pickle
    from StringIO import StringIO as BytesIO
    if py25:
        msg = 'Python 2.5 support may be dropped in future versions of Bottle.'
        warnings.warn(msg, DeprecationWarning)
        from UserDict import DictMixin

        def next(it):
            return it.next()


        bytes = str
    else:
        from collections import MutableMapping as DictMixin
    json_loads = json_lds

def tob(s, enc = 'utf8'):
    if isinstance(s, unicode):
        return s.encode(enc)
    return bytes(s)


def touni(s, enc = 'utf8', err = 'strict'):
    if isinstance(s, bytes):
        return s.decode(enc, err)
    return unicode(s)


tonat = touni if py3k else tob
if py31:
    from io import TextIOWrapper

    class NCTextIOWrapper(TextIOWrapper):

        def close(self):
            pass


class FieldStorage(cgi.FieldStorage):

    def __nonzero__(self):
        return bool(self.list or self.file)

    if py3k:
        __bool__ = __nonzero__


def update_wrapper(wrapper, wrapped, *a, **ka):
    try:
        functools.update_wrapper(wrapper, wrapped, *a, **ka)
    except AttributeError:
        pass


def depr(message):
    warnings.warn(message, DeprecationWarning, stacklevel=3)


def makelist(data):
    if isinstance(data, (tuple,
     list,
     set,
     dict)):
        return list(data)
    elif data:
        return [data]
    else:
        return []


class DictProperty(object):

    def __init__(self, attr, key = None, read_only = False):
        self.attr, self.key, self.read_only = attr, key, read_only

    def __call__(self, func):
        functools.update_wrapper(self, func, updated=[])
        self.getter, self.key = func, self.key or func.__name__
        return self

    def __get__(self, obj, cls):
        if obj is None:
            return self
        key, storage = self.key, getattr(obj, self.attr)
        if key not in storage:
            storage[key] = self.getter(obj)
        return storage[key]

    def __set__(self, obj, value):
        if self.read_only:
            raise AttributeError('Read-Only property.')
        getattr(obj, self.attr)[self.key] = value

    def __delete__(self, obj):
        if self.read_only:
            raise AttributeError('Read-Only property.')
        del getattr(obj, self.attr)[self.key]


class cached_property(object):

    def __init__(self, func):
        self.func = func

    def __get__(self, obj, cls):
        if obj is None:
            return self
        value = obj.__dict__[self.func.__name__] = self.func(obj)
        return value


class lazy_attribute(object):

    def __init__(self, func):
        functools.update_wrapper(self, func, updated=[])
        self.getter = func

    def __get__(self, obj, cls):
        value = self.getter(cls)
        setattr(cls, self.__name__, value)
        return value


class BottleException(Exception):
    pass


class RouteError(BottleException):
    pass


class RouteReset(BottleException):
    pass


class RouterUnknownModeError(RouteError):
    pass


class RouteSyntaxError(RouteError):
    pass


class RouteBuildError(RouteError):
    pass


class Router(object):
    default_pattern = '[^/]+'
    default_filter = 're'
    rule_syntax = re.compile('(\\\\*)(?:(?::([a-zA-Z_][a-zA-Z_0-9]*)?()(?:#(.*?)#)?)|(?:<([a-zA-Z_][a-zA-Z_0-9]*)?(?::([a-zA-Z_]*)(?::((?:\\\\.|[^\\\\>]+)+)?)?)?>))')

    def __init__(self, strict = False):
        self.rules = {}
        self.builder = {}
        self.static = {}
        self.dynamic = []
        self.strict_order = strict
        self.filters = {'re': self.re_filter,
         'int': self.int_filter,
         'float': self.float_filter,
         'path': self.path_filter}

    def re_filter(self, conf):
        return (conf or self.default_pattern, None, None)

    def int_filter(self, conf):
        return ('-?\\d+', int, lambda x: str(int(x)))

    def float_filter(self, conf):
        return ('-?[\\d.]+', float, lambda x: str(float(x)))

    def path_filter(self, conf):
        return ('.+?', None, None)

    def add_filter(self, name, func):
        self.filters[name] = func

    def parse_rule(self, rule):
        offset, prefix = (0, '')
        for match in self.rule_syntax.finditer(rule):
            prefix += rule[offset:match.start()]
            g = match.groups()
            if len(g[0]) % 2:
                prefix += match.group(0)[len(g[0]):]
                offset = match.end()
                continue
            if prefix:
                yield (prefix, None, None)
            name, filtr, conf = g[1:4] if g[2] is not None else g[4:7]
            if not filtr:
                filtr = self.default_filter
            yield (name, filtr, conf or None)
            offset, prefix = match.end(), ''

        if offset <= len(rule) or prefix:
            yield (prefix + rule[offset:], None, None)

    def add(self, rule, method, target, name = None):
        if rule in self.rules:
            self.rules[rule][method] = target
            if name:
                self.builder[name] = self.builder[rule]
            return
        target = self.rules[rule] = {method: target}
        anons = 0
        pattern = ''
        filters = []
        builder = []
        is_static = True
        for key, mode, conf in self.parse_rule(rule):
            if mode:
                is_static = False
                mask, in_filter, out_filter = self.filters[mode](conf)
                if key:
                    pattern += '(?P<%s>%s)' % (key, mask)
                else:
                    pattern += '(?:%s)' % mask
                    key = 'anon%d' % anons
                    anons += 1
                if in_filter:
                    filters.append((key, in_filter))
                builder.append((key, out_filter or str))
            elif key:
                pattern += re.escape(key)
                builder.append((None, key))

        self.builder[rule] = builder
        if name:
            self.builder[name] = builder
        if is_static and not self.strict_order:
            self.static[self.build(rule)] = target
            return

        def fpat_sub(m):
            if len(m.group(1)) % 2:
                return m.group(0)
            return m.group(1) + '(?:'

        flat_pattern = re.sub('(\\\\*)(\\(\\?P<[^>]*>|\\((?!\\?))', fpat_sub, pattern)
        try:
            re_match = re.compile('^(%s)$' % pattern).match
        except re.error:
            raise RouteSyntaxError('Could not add Route: %s (%s)' % (rule, _e()))

        def match(path):
            url_args = re_match(path).groupdict()
            for name, wildcard_filter in filters:
                try:
                    url_args[name] = wildcard_filter(url_args[name])
                except ValueError:
                    raise HTTPError(400, 'Path has wrong format.')

            return url_args

        try:
            combined = '%s|(^%s$)' % (self.dynamic[-1][0].pattern, flat_pattern)
            self.dynamic[-1] = (re.compile(combined), self.dynamic[-1][1])
            self.dynamic[-1][1].append((match, target))
        except (AssertionError, IndexError):
            self.dynamic.append((re.compile('(^%s$)' % flat_pattern), [(match, target)]))

        return match

    def build(self, _name, *anons, **query):
        builder = self.builder.get(_name)
        if not builder:
            raise RouteBuildError('No route with that name.', _name)
        try:
            for i, value in enumerate(anons):
                query['anon%d' % i] = value

            url = ''.join([ (f(query.pop(n)) if n else f) for n, f in builder ])
            if not query:
                return url
            return url + '?' + urlencode(query)
        except KeyError:
            raise RouteBuildError('Missing URL argument: %r' % _e().args[0])

    def match(self, environ):
        path, targets, urlargs = environ['PATH_INFO'] or '/', None, {}
        if path in self.static:
            targets = self.static[path]
        else:
            for combined, rules in self.dynamic:
                match = combined.match(path)
                if not match:
                    continue
                getargs, targets = rules[match.lastindex - 1]
                urlargs = getargs(path) if getargs else {}
                break

        if not targets:
            raise HTTPError(404, 'Not found: ' + repr(environ['PATH_INFO']))
        method = environ['REQUEST_METHOD'].upper()
        if method in targets:
            return (targets[method], urlargs)
        if method == 'HEAD' and 'GET' in targets:
            return (targets['GET'], urlargs)
        if 'ANY' in targets:
            return (targets['ANY'], urlargs)
        allowed = [ verb for verb in targets if verb != 'ANY' ]
        if 'GET' in allowed and 'HEAD' not in allowed:
            allowed.append('HEAD')
        raise HTTPError(405, 'Method not allowed.', Allow=','.join(allowed))


class Route(object):

    def __init__(self, app, rule, method, callback, name = None, plugins = None, skiplist = None, **config):
        self.app = app
        self.rule = rule
        self.method = method
        self.callback = callback
        self.name = name or None
        self.plugins = plugins or []
        self.skiplist = skiplist or []
        self.config = ConfigDict(config)

    def __call__(self, *a, **ka):
        depr('Some APIs changed to return Route() instances instead of callables. Make sure to use the Route.call method and not to call Route instances directly.')
        return self.call(*a, **ka)

    @cached_property
    def call(self):
        return self._make_callback()

    def reset(self):
        self.__dict__.pop('call', None)

    def prepare(self):
        self.call

    @property
    def _context(self):
        depr('Switch to Plugin API v2 and access the Route object directly.')
        return dict(rule=self.rule, method=self.method, callback=self.callback, name=self.name, app=self.app, config=self.config, apply=self.plugins, skip=self.skiplist)

    def all_plugins(self):
        unique = set()
        for p in reversed(self.app.plugins + self.plugins):
            if True in self.skiplist:
                break
            name = getattr(p, 'name', False)
            if name and (name in self.skiplist or name in unique):
                continue
            if p in self.skiplist or type(p) in self.skiplist:
                continue
            if name:
                unique.add(name)
            yield p

    def _make_callback(self):
        callback = self.callback
        for plugin in self.all_plugins():
            try:
                if hasattr(plugin, 'apply'):
                    api = getattr(plugin, 'api', 1)
                    context = self if api > 1 else self._context
                    callback = plugin.apply(callback, context)
                else:
                    callback = plugin(callback)
            except RouteReset:
                return self._make_callback()

            if callback is not self.callback:
                update_wrapper(callback, self.callback)

        return callback

    def __repr__(self):
        return '<%s %r %r>' % (self.method, self.rule, self.callback)


class Bottle(object):

    def __init__(self, catchall = True, autojson = True):
        self.catchall = catchall
        self.resources = ResourceManager()
        self.config = ConfigDict()
        self.config.autojson = autojson
        self.routes = []
        self.router = Router()
        self.error_handler = {}
        self.plugins = []
        self.hooks = HooksPlugin()
        self.install(self.hooks)
        if self.config.autojson:
            self.install(JSONPlugin())
        self.install(TemplatePlugin())

    def mount(self, prefix, app, **options):
        if isinstance(app, basestring):
            prefix, app = app, prefix
            depr('Parameter order of Bottle.mount() changed.')
        segments = [ p for p in prefix.split('/') if p ]
        if not segments:
            raise ValueError('Empty path prefix.')
        path_depth = len(segments)

        def mountpoint_wrapper():
            try:
                request.path_shift(path_depth)
                rs = BaseResponse([], 200)

                def start_response(status, header):
                    rs.status = status
                    for name, value in header:
                        rs.add_header(name, value)

                    return rs.body.append

                body = app(request.environ, start_response)
                body = itertools.chain(rs.body, body)
                return HTTPResponse(body, rs.status_code, rs.headers)
            finally:
                request.path_shift(-path_depth)

        options.setdefault('skip', True)
        options.setdefault('method', 'ANY')
        options.setdefault('mountpoint', {'prefix': prefix,
         'target': app})
        options['callback'] = mountpoint_wrapper
        self.route(('/%s/<:re:.*>' % '/'.join(segments)), **options)
        if not prefix.endswith('/'):
            self.route(('/' + '/'.join(segments)), **options)

    def merge(self, routes):
        if isinstance(routes, Bottle):
            routes = routes.routes
        for route in routes:
            self.add_route(route)

    def install(self, plugin):
        if hasattr(plugin, 'setup'):
            plugin.setup(self)
        if not callable(plugin) and not hasattr(plugin, 'apply'):
            raise TypeError('Plugins must be callable or implement .apply()')
        self.plugins.append(plugin)
        self.reset()
        return plugin

    def uninstall(self, plugin):
        removed, remove = [], plugin
        for i, plugin in list(enumerate(self.plugins))[::-1]:
            if remove is True or remove is plugin or remove is type(plugin) or getattr(plugin, 'name', True) == remove:
                removed.append(plugin)
                del self.plugins[i]
                if hasattr(plugin, 'close'):
                    plugin.close()

        if removed:
            self.reset()
        return removed

    def run(self, **kwargs):
        run(self, **kwargs)

    def reset(self, route = None):
        global DEBUG
        if route is None:
            routes = self.routes
        elif isinstance(route, Route):
            routes = [route]
        else:
            routes = [self.routes[route]]
        for route in routes:
            route.reset()

        if DEBUG:
            for route in routes:
                route.prepare()

        self.hooks.trigger('app_reset')

    def close(self):
        for plugin in self.plugins:
            if hasattr(plugin, 'close'):
                plugin.close()

        self.stopped = True

    def match(self, environ):
        return self.router.match(environ)

    def get_url(self, routename, **kargs):
        scriptname = request.environ.get('SCRIPT_NAME', '').strip('/') + '/'
        location = self.router.build(routename, **kargs).lstrip('/')
        return urljoin(urljoin('/', scriptname), location)

    def add_route(self, route):
        self.routes.append(route)
        self.router.add(route.rule, route.method, route, name=route.name)
        if DEBUG:
            route.prepare()

    def route(self, path = None, method = 'GET', callback = None, name = None, apply = None, skip = None, **config):
        if callable(path):
            path, callback = None, path
        plugins = makelist(apply)
        skiplist = makelist(skip)

        def decorator(callback):
            if isinstance(callback, basestring):
                callback = load(callback)
            for rule in makelist(path) or yieldroutes(callback):
                for verb in makelist(method):
                    verb = verb.upper()
                    route = Route(self, rule, verb, callback, name=name, plugins=plugins, skiplist=skiplist, **config)
                    self.add_route(route)

            return callback

        if callback:
            return decorator(callback)
        return decorator

    def get(self, path = None, method = 'GET', **options):
        return self.route(path, method, **options)

    def post(self, path = None, method = 'POST', **options):
        return self.route(path, method, **options)

    def put(self, path = None, method = 'PUT', **options):
        return self.route(path, method, **options)

    def delete(self, path = None, method = 'DELETE', **options):
        return self.route(path, method, **options)

    def error(self, code = 500):

        def wrapper(handler):
            self.error_handler[int(code)] = handler
            return handler

        return wrapper

    def hook(self, name):

        def wrapper(func):
            self.hooks.add(name, func)
            return func

        return wrapper

    def handle(self, path, method = 'GET'):
        depr('This method will change semantics in 0.10. Try to avoid it.')
        if isinstance(path, dict):
            return self._handle(path)
        return self._handle({'PATH_INFO': path,
         'REQUEST_METHOD': method.upper()})

    def default_error_handler(self, res):
        return tob(template(ERROR_PAGE_TEMPLATE, e=res))

    def _handle(self, environ):
        try:
            environ['bottle.app'] = self
            request.bind(environ)
            response.bind()
            route, args = self.router.match(environ)
            environ['route.handle'] = route
            environ['bottle.route'] = route
            environ['route.url_args'] = args
            return route.call(**args)
        except HTTPResponse:
            return _e()
        except RouteReset:
            route.reset()
            return self._handle(environ)
        except (KeyboardInterrupt, SystemExit, MemoryError):
            raise
        except Exception:
            if not self.catchall:
                raise
            stacktrace = format_exc()
            environ['wsgi.errors'].write(stacktrace)
            return HTTPError(500, 'Internal Server Error', _e(), stacktrace)

    def _cast(self, out, peek = None):
        if not out:
            if 'Content-Length' not in response:
                response['Content-Length'] = 0
            return []
        if isinstance(out, (tuple, list)) and isinstance(out[0], (bytes, unicode)):
            out = out[0][0:0].join(out)
        if isinstance(out, unicode):
            out = out.encode(response.charset)
        if isinstance(out, bytes):
            if 'Content-Length' not in response:
                response['Content-Length'] = len(out)
            return [out]
        if isinstance(out, HTTPError):
            out.apply(response)
            out = self.error_handler.get(out.status_code, self.default_error_handler)(out)
            return self._cast(out)
        if isinstance(out, HTTPResponse):
            out.apply(response)
            return self._cast(out.body)
        if hasattr(out, 'read'):
            if 'wsgi.file_wrapper' in request.environ:
                return request.environ['wsgi.file_wrapper'](out)
            if hasattr(out, 'close') or not hasattr(out, '__iter__'):
                return WSGIFileWrapper(out)
        try:
            out = iter(out)
            first = next(out)
            while not first:
                first = next(out)

        except StopIteration:
            return self._cast('')
        except HTTPResponse:
            first = _e()
        except (KeyboardInterrupt, SystemExit, MemoryError):
            raise
        except Exception:
            if not self.catchall:
                raise
            first = HTTPError(500, 'Unhandled exception', _e(), format_exc())

        if isinstance(first, HTTPResponse):
            return self._cast(first)
        if isinstance(first, bytes):
            return itertools.chain([first], out)
        if isinstance(first, unicode):
            return imap(lambda x: x.encode(response.charset), itertools.chain([first], out))
        return self._cast(HTTPError(500, 'Unsupported response type: %s' % type(first)))

    def wsgi(self, environ, start_response):
        try:
            out = self._cast(self._handle(environ))
            if response._status_code in (100, 101, 204, 304) or environ['REQUEST_METHOD'] == 'HEAD':
                if hasattr(out, 'close'):
                    out.close()
                out = []
            start_response(response._status_line, response.headerlist)
            return out
        except (KeyboardInterrupt, SystemExit, MemoryError):
            raise
        except Exception:
            if not self.catchall:
                raise
            err = '<h1>Critical error while processing request: %s</h1>' % html_escape(environ.get('PATH_INFO', '/'))
            if DEBUG:
                err += '<h2>Error:</h2>\n<pre>\n%s\n</pre>\n<h2>Traceback:</h2>\n<pre>\n%s\n</pre>\n' % (html_escape(repr(_e())), html_escape(format_exc()))
            environ['wsgi.errors'].write(err)
            headers = [('Content-Type', 'text/html; charset=UTF-8')]
            start_response('500 INTERNAL SERVER ERROR', headers)
            return [tob(err)]

    def __call__(self, environ, start_response):
        return self.wsgi(environ, start_response)


class BaseRequest(object):
    __slots__ = 'environ'
    MEMFILE_MAX = 102400
    MAX_PARAMS = 100

    def __init__(self, environ = None):
        self.environ = {} if environ is None else environ
        self.environ['bottle.request'] = self

    @DictProperty('environ', 'bottle.app', read_only=True)
    def app(self):
        raise RuntimeError('This request is not connected to an application.')

    @property
    def path(self):
        return '/' + self.environ.get('PATH_INFO', '').lstrip('/')

    @property
    def method(self):
        return self.environ.get('REQUEST_METHOD', 'GET').upper()

    @DictProperty('environ', 'bottle.request.headers', read_only=True)
    def headers(self):
        return WSGIHeaderDict(self.environ)

    def get_header(self, name, default = None):
        return self.headers.get(name, default)

    @DictProperty('environ', 'bottle.request.cookies', read_only=True)
    def cookies(self):
        cookies = SimpleCookie(self.environ.get('HTTP_COOKIE', ''))
        cookies = list(cookies.values())[:self.MAX_PARAMS]
        return FormsDict(((c.key, c.value) for c in cookies))

    def get_cookie(self, key, default = None, secret = None):
        value = self.cookies.get(key)
        if secret and value:
            dec = cookie_decode(value, secret)
            if dec and dec[0] == key:
                return dec[1]
            return default
        return value or default

    @DictProperty('environ', 'bottle.request.query', read_only=True)
    def query(self):
        get = self.environ['bottle.get'] = FormsDict()
        pairs = _parse_qsl(self.environ.get('QUERY_STRING', ''))
        for key, value in pairs[:self.MAX_PARAMS]:
            get[key] = value

        return get

    @DictProperty('environ', 'bottle.request.forms', read_only=True)
    def forms(self):
        forms = FormsDict()
        for name, item in self.POST.allitems():
            if not hasattr(item, 'filename'):
                forms[name] = item

        return forms

    @DictProperty('environ', 'bottle.request.params', read_only=True)
    def params(self):
        params = FormsDict()
        for key, value in self.query.allitems():
            params[key] = value

        for key, value in self.forms.allitems():
            params[key] = value

        return params

    @DictProperty('environ', 'bottle.request.files', read_only=True)
    def files(self):
        files = FormsDict()
        for name, item in self.POST.allitems():
            if hasattr(item, 'filename'):
                files[name] = item

        return files

    @DictProperty('environ', 'bottle.request.json', read_only=True)
    def json(self):
        if 'application/json' in self.environ.get('CONTENT_TYPE', '') and 0 < self.content_length < self.MEMFILE_MAX:
            return json_loads(self.body.read(self.MEMFILE_MAX))

    @DictProperty('environ', 'bottle.request.body', read_only=True)
    def _body(self):
        maxread = max(0, self.content_length)
        stream = self.environ['wsgi.input']
        body = BytesIO() if maxread < self.MEMFILE_MAX else TemporaryFile(mode='w+b')
        while maxread > 0:
            part = stream.read(min(maxread, self.MEMFILE_MAX))
            if not part:
                break
            body.write(part)
            maxread -= len(part)

        self.environ['wsgi.input'] = body
        body.seek(0)
        return body

    @property
    def body(self):
        self._body.seek(0)
        return self._body

    GET = query

    @DictProperty('environ', 'bottle.request.post', read_only=True)
    def POST(self):
        post = FormsDict()
        if not self.content_type.startswith('multipart/'):
            maxlen = max(0, min(self.content_length, self.MEMFILE_MAX))
            pairs = _parse_qsl(tonat(self.body.read(maxlen), 'latin1'))
            for key, value in pairs[:self.MAX_PARAMS]:
                post[key] = value

            return post
        safe_env = {'QUERY_STRING': ''}
        for key in ('REQUEST_METHOD', 'CONTENT_TYPE', 'CONTENT_LENGTH'):
            if key in self.environ:
                safe_env[key] = self.environ[key]

        args = dict(fp=self.body, environ=safe_env, keep_blank_values=True)
        if py31:
            args['fp'] = NCTextIOWrapper(args['fp'], encoding='ISO-8859-1', newline='\n')
        elif py3k:
            args['encoding'] = 'ISO-8859-1'
        data = FieldStorage(**args)
        for item in (data.list or [])[:self.MAX_PARAMS]:
            post[item.name] = item if item.filename else item.value

        return post

    @property
    def COOKIES(self):
        depr('BaseRequest.COOKIES was renamed to BaseRequest.cookies (lowercase).')
        return self.cookies

    @property
    def url(self):
        return self.urlparts.geturl()

    @DictProperty('environ', 'bottle.request.urlparts', read_only=True)
    def urlparts(self):
        env = self.environ
        http = env.get('HTTP_X_FORWARDED_PROTO') or env.get('wsgi.url_scheme', 'http')
        host = env.get('HTTP_X_FORWARDED_HOST') or env.get('HTTP_HOST')
        if not host:
            host = env.get('SERVER_NAME', '127.0.0.1')
            port = env.get('SERVER_PORT')
            if port and port != ('80' if http == 'http' else '443'):
                host += ':' + port
        path = urlquote(self.fullpath)
        return UrlSplitResult(http, host, path, env.get('QUERY_STRING'), '')

    @property
    def fullpath(self):
        return urljoin(self.script_name, self.path.lstrip('/'))

    @property
    def query_string(self):
        return self.environ.get('QUERY_STRING', '')

    @property
    def script_name(self):
        script_name = self.environ.get('SCRIPT_NAME', '').strip('/')
        if script_name:
            return '/' + script_name + '/'
        return '/'

    def path_shift(self, shift = 1):
        script = self.environ.get('SCRIPT_NAME', '/')
        self['SCRIPT_NAME'], self['PATH_INFO'] = path_shift(script, self.path, shift)

    @property
    def content_length(self):
        return int(self.environ.get('CONTENT_LENGTH') or -1)

    @property
    def content_type(self):
        return self.environ.get('CONTENT_TYPE', '').lower()

    @property
    def is_xhr(self):
        requested_with = self.environ.get('HTTP_X_REQUESTED_WITH', '')
        return requested_with.lower() == 'xmlhttprequest'

    @property
    def is_ajax(self):
        return self.is_xhr

    @property
    def auth(self):
        basic = parse_auth(self.environ.get('HTTP_AUTHORIZATION', ''))
        if basic:
            return basic
        ruser = self.environ.get('REMOTE_USER')
        if ruser:
            return (ruser, None)

    @property
    def remote_route(self):
        proxy = self.environ.get('HTTP_X_FORWARDED_FOR')
        if proxy:
            return [ ip.strip() for ip in proxy.split(',') ]
        remote = self.environ.get('REMOTE_ADDR')
        if remote:
            return [remote]
        return []

    @property
    def remote_addr(self):
        route = self.remote_route
        if route:
            return route[0]

    def copy(self):
        return Request(self.environ.copy())

    def get(self, value, default = None):
        return self.environ.get(value, default)

    def __getitem__(self, key):
        return self.environ[key]

    def __delitem__(self, key):
        self[key] = ''
        del self.environ[key]

    def __iter__(self):
        return iter(self.environ)

    def __len__(self):
        return len(self.environ)

    def keys(self):
        return self.environ.keys()

    def __setitem__(self, key, value):
        if self.environ.get('bottle.request.readonly'):
            raise KeyError('The environ dictionary is read-only.')
        self.environ[key] = value
        todelete = ()
        if key == 'wsgi.input':
            todelete = ('body', 'forms', 'files', 'params', 'post', 'json')
        elif key == 'QUERY_STRING':
            todelete = ('query', 'params')
        elif key.startswith('HTTP_'):
            todelete = ('headers', 'cookies')
        for key in todelete:
            self.environ.pop('bottle.request.' + key, None)

    def __repr__(self):
        return '<%s: %s %s>' % (self.__class__.__name__, self.method, self.url)

    def __getattr__(self, name):
        try:
            var = self.environ['bottle.request.ext.%s' % name]
            if hasattr(var, '__get__'):
                return var.__get__(self)
            return var
        except KeyError:
            raise AttributeError('Attribute %r not defined.' % name)

    def __setattr__(self, name, value):
        if name == 'environ':
            return object.__setattr__(self, name, value)
        self.environ['bottle.request.ext.%s' % name] = value


def _hkey(s):
    return s.title().replace('_', '-')


class HeaderProperty(object):

    def __init__(self, name, reader = None, writer = str, default = ''):
        self.name, self.default = name, default
        self.reader, self.writer = reader, writer
        self.__doc__ = 'Current value of the %r header.' % name.title()

    def __get__(self, obj, cls):
        if obj is None:
            return self
        value = obj.headers.get(self.name, self.default)
        if self.reader:
            return self.reader(value)
        return value

    def __set__(self, obj, value):
        obj.headers[self.name] = self.writer(value)

    def __delete__(self, obj):
        del obj.headers[self.name]


class BaseResponse(object):
    default_status = 200
    default_content_type = 'text/html; charset=UTF-8'
    bad_headers = {204: set(('Content-Type',)),
     304: set(('Allow', 'Content-Encoding', 'Content-Language', 'Content-Length', 'Content-Range', 'Content-Type', 'Content-Md5', 'Last-Modified'))}

    def __init__(self, body = '', status = None, **headers):
        self._cookies = None
        self._headers = {'Content-Type': [self.default_content_type]}
        self.body = body
        self.status = status or self.default_status
        if headers:
            for name, value in headers.items():
                self[name] = value

    def copy(self):
        copy = Response()
        copy.status = self.status
        copy._headers = dict(((k, v[:]) for k, v in self._headers.items()))
        return copy

    def __iter__(self):
        return iter(self.body)

    def close(self):
        if hasattr(self.body, 'close'):
            self.body.close()

    @property
    def status_line(self):
        return self._status_line

    @property
    def status_code(self):
        return self._status_code

    def _set_status(self, status):
        if isinstance(status, int):
            code, status = status, _HTTP_STATUS_LINES.get(status)
        elif ' ' in status:
            status = status.strip()
            code = int(status.split()[0])
        else:
            raise ValueError('String status line without a reason phrase.')
        if not 100 <= code <= 999:
            raise ValueError('Status code out of range.')
        self._status_code = code
        self._status_line = str(status or '%d Unknown' % code)

    def _get_status(self):
        return self._status_line

    status = property(_get_status, _set_status, None, ' A writeable property to change the HTTP response status. It accepts\n            either a numeric code (100-999) or a string with a custom reason\n            phrase (e.g. "404 Brain not found"). Both :data:`status_line` and\n            :data:`status_code` are updated accordingly. The return value is\n            always a status string. ')
    del _get_status
    del _set_status

    @property
    def headers(self):
        hdict = HeaderDict()
        hdict.dict = self._headers
        return hdict

    def __contains__(self, name):
        return _hkey(name) in self._headers

    def __delitem__(self, name):
        del self._headers[_hkey(name)]

    def __getitem__(self, name):
        return self._headers[_hkey(name)][-1]

    def __setitem__(self, name, value):
        self._headers[_hkey(name)] = [str(value)]

    def get_header(self, name, default = None):
        return self._headers.get(_hkey(name), [default])[-1]

    def set_header(self, name, value):
        self._headers[_hkey(name)] = [str(value)]

    def add_header(self, name, value):
        self._headers.setdefault(_hkey(name), []).append(str(value))

    def iter_headers(self):
        return self.headerlist

    def wsgiheader(self):
        depr('The wsgiheader method is deprecated. See headerlist.')
        return self.headerlist

    @property
    def headerlist(self):
        out = []
        headers = self._headers.items()
        if self._status_code in self.bad_headers:
            bad_headers = self.bad_headers[self._status_code]
            headers = [ h for h in headers if h[0] not in bad_headers ]
        out += [ (name, val) for name, vals in headers for val in vals ]
        if self._cookies:
            for c in self._cookies.values():
                out.append(('Set-Cookie', c.OutputString()))

        return out

    content_type = HeaderProperty('Content-Type')
    content_length = HeaderProperty('Content-Length', reader=int)

    @property
    def charset(self):
        if 'charset=' in self.content_type:
            return self.content_type.split('charset=')[-1].split(';')[0].strip()
        return 'UTF-8'

    @property
    def COOKIES(self):
        depr('The COOKIES dict is deprecated. Use `set_cookie()` instead.')
        if not self._cookies:
            self._cookies = SimpleCookie()
        return self._cookies

    def set_cookie(self, name, value, secret = None, **options):
        if not self._cookies:
            self._cookies = SimpleCookie()
        if secret:
            value = touni(cookie_encode((name, value), secret))
        elif not isinstance(value, basestring):
            raise TypeError('Secret key missing for non-string Cookie.')
        if len(value) > 4096:
            raise ValueError('Cookie value to long.')
        self._cookies[name] = value
        for key, value in options.items():
            if key == 'max_age':
                if isinstance(value, timedelta):
                    value = value.seconds + value.days * 24 * 3600
            if key == 'expires':
                if isinstance(value, (datedate, datetime)):
                    value = value.timetuple()
                elif isinstance(value, (int, float)):
                    value = time.gmtime(value)
                value = time.strftime('%a, %d %b %Y %H:%M:%S GMT', value)
            self._cookies[name][key.replace('_', '-')] = value

    def delete_cookie(self, key, **kwargs):
        kwargs['max_age'] = -1
        kwargs['expires'] = 0
        self.set_cookie(key, '', **kwargs)

    def __repr__(self):
        out = ''
        for name, value in self.headerlist:
            out += '%s: %s\n' % (name.title(), value.strip())

        return out


_lctx = threading.local()

def local_property(name):

    def fget(self):
        try:
            return getattr(_lctx, name)
        except AttributeError:
            raise RuntimeError('Request context not initialized.')

    def fset(self, value):
        setattr(_lctx, name, value)

    def fdel(self):
        delattr(_lctx, name)

    return property(fget, fset, fdel, 'Thread-local property stored in :data:`_lctx.%s`' % name)


class LocalRequest(BaseRequest):
    bind = BaseRequest.__init__
    environ = local_property('request_environ')


class LocalResponse(BaseResponse):
    bind = BaseResponse.__init__
    _status_line = local_property('response_status_line')
    _status_code = local_property('response_status_code')
    _cookies = local_property('response_cookies')
    _headers = local_property('response_headers')
    body = local_property('response_body')


Request = BaseRequest
Response = BaseResponse

class HTTPResponse(Response, BottleException):

    def __init__(self, body = '', status = None, header = None, **headers):
        if header or 'output' in headers:
            depr('Call signature changed (for the better)')
            if header:
                headers.update(header)
            if 'output' in headers:
                body = headers.pop('output')
        super(HTTPResponse, self).__init__(body, status, **headers)

    def apply(self, response):
        response._status_code = self._status_code
        response._status_line = self._status_line
        response._headers = self._headers
        response._cookies = self._cookies
        response.body = self.body

    def _output(self, value = None):
        depr('Use HTTPResponse.body instead of HTTPResponse.output')
        if value is None:
            return self.body
        self.body = value

    output = property(_output, _output, doc='Alias for .body')


class HTTPError(HTTPResponse):
    default_status = 500

    def __init__(self, status = None, body = None, exception = None, traceback = None, header = None, **headers):
        self.exception = exception
        self.traceback = traceback
        super(HTTPError, self).__init__(body, status, header, **headers)


class PluginError(BottleException):
    pass


class JSONPlugin(object):
    name = 'json'
    api = 2

    def __init__(self, json_dumps = json_dumps):
        self.json_dumps = json_dumps

    def apply(self, callback, route):
        dumps = self.json_dumps
        if not dumps:
            return callback

        def wrapper(*a, **ka):
            rv = callback(*a, **ka)
            if isinstance(rv, dict):
                json_response = dumps(rv)
                response.content_type = 'application/json'
                return json_response
            return rv

        return wrapper


class HooksPlugin(object):
    name = 'hooks'
    api = 2
    _names = ('before_request', 'after_request', 'app_reset')

    def __init__(self):
        self.hooks = dict(((name, []) for name in self._names))
        self.app = None

    def _empty(self):
        return not (self.hooks['before_request'] or self.hooks['after_request'])

    def setup(self, app):
        self.app = app

    def add(self, name, func):
        was_empty = self._empty()
        self.hooks.setdefault(name, []).append(func)
        if self.app and was_empty and not self._empty():
            self.app.reset()

    def remove(self, name, func):
        was_empty = self._empty()
        if name in self.hooks and func in self.hooks[name]:
            self.hooks[name].remove(func)
        if self.app and not was_empty and self._empty():
            self.app.reset()

    def trigger(self, name, *a, **ka):
        hooks = self.hooks[name]
        if ka.pop('reversed', False):
            hooks = hooks[::-1]
        return [ hook(*a, **ka) for hook in hooks ]

    def apply(self, callback, route):
        if self._empty():
            return callback

        def wrapper(*a, **ka):
            self.trigger('before_request')
            rv = callback(*a, **ka)
            self.trigger('after_request', reversed=True)
            return rv

        return wrapper


class TemplatePlugin(object):
    name = 'template'
    api = 2

    def apply(self, callback, route):
        conf = route.config.get('template')
        if isinstance(conf, (tuple, list)) and len(conf) == 2:
            return view(conf[0], **conf[1])(callback)
        elif isinstance(conf, str) and 'template_opts' in route.config:
            depr('The `template_opts` parameter is deprecated.')
            return view(conf, **route.config['template_opts'])(callback)
        elif isinstance(conf, str):
            return view(conf)(callback)
        else:
            return callback


class _ImportRedirect(object):

    def __init__(self, name, impmask):
        self.name = name
        self.impmask = impmask
        self.module = sys.modules.setdefault(name, imp.new_module(name))
        self.module.__dict__.update({'__file__': __file__,
         '__path__': [],
         '__all__': [],
         '__loader__': self})
        sys.meta_path.append(self)

    def find_module(self, fullname, path = None):
        if '.' not in fullname:
            return
        packname, modname = fullname.rsplit('.', 1)
        if packname != self.name:
            return
        return self

    def load_module(self, fullname):
        if fullname in sys.modules:
            return sys.modules[fullname]
        packname, modname = fullname.rsplit('.', 1)
        realname = self.impmask % modname
        __import__(realname)
        module = sys.modules[fullname] = sys.modules[realname]
        setattr(self.module, modname, module)
        module.__loader__ = self
        return module


class MultiDict(DictMixin):

    def __init__(self, *a, **k):
        self.dict = dict(((k, [v]) for k, v in dict(*a, **k).items()))

    def __len__(self):
        return len(self.dict)

    def __iter__(self):
        return iter(self.dict)

    def __contains__(self, key):
        return key in self.dict

    def __delitem__(self, key):
        del self.dict[key]

    def __getitem__(self, key):
        return self.dict[key][-1]

    def __setitem__(self, key, value):
        self.append(key, value)

    def keys(self):
        return self.dict.keys()

    if py3k:

        def values(self):
            return (v[-1] for v in self.dict.values())

        def items(self):
            return ((k, v[-1]) for k, v in self.dict.items())

        def allitems(self):
            return ((k, v) for k, vl in self.dict.items() for v in vl)

        iterkeys = keys
        itervalues = values
        iteritems = items
        iterallitems = allitems
    else:

        def values(self):
            return [ v[-1] for v in self.dict.values() ]

        def items(self):
            return [ (k, v[-1]) for k, v in self.dict.items() ]

        def iterkeys(self):
            return self.dict.iterkeys()

        def itervalues(self):
            return (v[-1] for v in self.dict.itervalues())

        def iteritems(self):
            return ((k, v[-1]) for k, v in self.dict.iteritems())

        def iterallitems(self):
            return ((k, v) for k, vl in self.dict.iteritems() for v in vl)

        def allitems(self):
            return [ (k, v) for k, vl in self.dict.iteritems() for v in vl ]

    def get(self, key, default = None, index = -1, type = None):
        try:
            val = self.dict[key][index]
            if type:
                return type(val)
            return val
        except Exception:
            pass

        return default

    def append(self, key, value):
        self.dict.setdefault(key, []).append(value)

    def replace(self, key, value):
        self.dict[key] = [value]

    def getall(self, key):
        return self.dict.get(key) or []

    getone = get
    getlist = getall


class FormsDict(MultiDict):
    input_encoding = 'utf8'
    recode_unicode = True

    def _fix(self, s, encoding = None):
        if isinstance(s, unicode) and self.recode_unicode:
            s = s.encode('latin1')
        if isinstance(s, bytes):
            return s.decode(encoding or self.input_encoding)
        return s

    def decode(self, encoding = None):
        copy = FormsDict()
        enc = copy.input_encoding = encoding or self.input_encoding
        copy.recode_unicode = False
        for key, value in self.allitems():
            copy.append(self._fix(key, enc), self._fix(value, enc))

        return copy

    def getunicode(self, name, default = None, encoding = None):
        try:
            return self._fix(self[name], encoding)
        except (UnicodeError, KeyError):
            return default

    def __getattr__(self, name, default = unicode()):
        if name.startswith('__') and name.endswith('__'):
            return super(FormsDict, self).__getattr__(name)
        return self.getunicode(name, default=default)


class HeaderDict(MultiDict):

    def __init__(self, *a, **ka):
        self.dict = {}
        if a or ka:
            self.update(*a, **ka)

    def __contains__(self, key):
        return _hkey(key) in self.dict

    def __delitem__(self, key):
        del self.dict[_hkey(key)]

    def __getitem__(self, key):
        return self.dict[_hkey(key)][-1]

    def __setitem__(self, key, value):
        self.dict[_hkey(key)] = [str(value)]

    def append(self, key, value):
        self.dict.setdefault(_hkey(key), []).append(str(value))

    def replace(self, key, value):
        self.dict[_hkey(key)] = [str(value)]

    def getall(self, key):
        return self.dict.get(_hkey(key)) or []

    def get(self, key, default = None, index = -1):
        return MultiDict.get(self, _hkey(key), default, index)

    def filter(self, names):
        for name in [ _hkey(n) for n in names ]:
            if name in self.dict:
                del self.dict[name]


class WSGIHeaderDict(DictMixin):
    cgikeys = ('CONTENT_TYPE', 'CONTENT_LENGTH')

    def __init__(self, environ):
        self.environ = environ

    def _ekey(self, key):
        key = key.replace('-', '_').upper()
        if key in self.cgikeys:
            return key
        return 'HTTP_' + key

    def raw(self, key, default = None):
        return self.environ.get(self._ekey(key), default)

    def __getitem__(self, key):
        return tonat(self.environ[self._ekey(key)], 'latin1')

    def __setitem__(self, key, value):
        raise TypeError('%s is read-only.' % self.__class__)

    def __delitem__(self, key):
        raise TypeError('%s is read-only.' % self.__class__)

    def __iter__(self):
        for key in self.environ:
            if key[:5] == 'HTTP_':
                yield key[5:].replace('_', '-').title()
            elif key in self.cgikeys:
                yield key.replace('_', '-').title()

    def keys(self):
        return [ x for x in self ]

    def __len__(self):
        return len(self.keys())

    def __contains__(self, key):
        return self._ekey(key) in self.environ


class ConfigDict(dict):

    def __getattr__(self, key):
        if key not in self and key[0].isupper():
            self[key] = ConfigDict()
        return self.get(key)

    def __setattr__(self, key, value):
        if hasattr(dict, key):
            raise AttributeError('Read-only attribute.')
        if key in self and self[key] and isinstance(self[key], ConfigDict):
            raise AttributeError('Non-empty namespace attribute.')
        self[key] = value

    def __delattr__(self, key):
        if key in self:
            del self[key]

    def __call__(self, *a, **ka):
        for key, value in dict(*a, **ka).items():
            setattr(self, key, value)

        return self


class AppStack(list):

    def __call__(self):
        return self[-1]

    def push(self, value = None):
        if not isinstance(value, Bottle):
            value = Bottle()
        self.append(value)
        return value


class WSGIFileWrapper(object):

    def __init__(self, fp, buffer_size = 65536):
        self.fp, self.buffer_size = fp, buffer_size
        for attr in ('fileno', 'close', 'read', 'readlines', 'tell', 'seek'):
            if hasattr(fp, attr):
                setattr(self, attr, getattr(fp, attr))

    def __iter__(self):
        buff, read = self.buffer_size, self.read
        while True:
            part = read(buff)
            if not part:
                return
            yield part


class ResourceManager(object):

    def __init__(self, base = './', opener = open, cachemode = 'all'):
        self.opener = open
        self.base = base
        self.cachemode = cachemode
        self.path = []
        self.cache = {}

    def add_path(self, path, base = None, index = None, create = False):
        base = os.path.abspath(os.path.dirname(base or self.base))
        path = os.path.abspath(os.path.join(base, os.path.dirname(path)))
        path += os.sep
        if path in self.path:
            self.path.remove(path)
        if create and not os.path.isdir(path):
            os.makedirs(path)
        if index is None:
            self.path.append(path)
        else:
            self.path.insert(index, path)
        self.cache.clear()
        return os.path.exists(path)

    def __iter__(self):
        search = self.path[:]
        while search:
            path = search.pop()
            if not os.path.isdir(path):
                continue
            for name in os.listdir(path):
                full = os.path.join(path, name)
                if os.path.isdir(full):
                    search.append(full)
                else:
                    yield full

    def lookup(self, name):
        if name not in self.cache or DEBUG:
            for path in self.path:
                fpath = os.path.join(path, name)
                if os.path.isfile(fpath):
                    if self.cachemode in ('all', 'found'):
                        self.cache[name] = fpath
                    return fpath

            if self.cachemode == 'all':
                self.cache[name] = None
        return self.cache[name]

    def open(self, name, mode = 'r', *args, **kwargs):
        fname = self.lookup(name)
        if not fname:
            raise IOError('Resource %r not found.' % name)
        return self.opener(name, mode=mode, *args, **kwargs)


def abort(code = 500, text = 'Unknown Error: Application stopped.'):
    raise HTTPError(code, text)


def redirect(url, code = None):
    if code is None:
        code = 303 if request.get('SERVER_PROTOCOL') == 'HTTP/1.1' else 302
    location = urljoin(request.url, url)
    res = HTTPResponse('', status=code, Location=location)
    if response._cookies:
        res._cookies = response._cookies
    raise res


def _file_iter_range(fp, offset, bytes, maxread = 1024 * 1024):
    fp.seek(offset)
    while bytes > 0:
        part = fp.read(min(bytes, maxread))
        if not part:
            break
        bytes -= len(part)
        yield part


def static_file(filename, root, mimetype = 'auto', download = False):
    root = os.path.abspath(root) + os.sep
    filename = os.path.abspath(os.path.join(root, filename.strip('/\\')))
    headers = dict()
    if not filename.startswith(root):
        return HTTPError(403, 'Access denied.')
    if not os.path.exists(filename) or not os.path.isfile(filename):
        return HTTPError(404, 'File does not exist.')
    if not os.access(filename, os.R_OK):
        return HTTPError(403, 'You do not have permission to access this file.')
    if mimetype == 'auto':
        mimetype, encoding = mimetypes.guess_type(filename)
        if mimetype:
            headers['Content-Type'] = mimetype
        if encoding:
            headers['Content-Encoding'] = encoding
    elif mimetype:
        headers['Content-Type'] = mimetype
    if download:
        download = os.path.basename(filename if download == True else download)
        headers['Content-Disposition'] = 'attachment; filename="%s"' % download
    stats = os.stat(filename)
    headers['Content-Length'] = clen = stats.st_size
    lm = time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime(stats.st_mtime))
    headers['Last-Modified'] = lm
    ims = request.environ.get('HTTP_IF_MODIFIED_SINCE')
    if ims:
        ims = parse_date(ims.split(';')[0].strip())
    if ims is not None and ims >= int(stats.st_mtime):
        headers['Date'] = time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime())
        return HTTPResponse(status=304, **headers)
    body = '' if request.method == 'HEAD' else open(filename, 'rb')
    headers['Accept-Ranges'] = 'bytes'
    ranges = request.environ.get('HTTP_RANGE')
    if 'HTTP_RANGE' in request.environ:
        ranges = list(parse_range_header(request.environ['HTTP_RANGE'], clen))
        if not ranges:
            return HTTPError(416, 'Requested Range Not Satisfiable')
        offset, end = ranges[0]
        headers['Content-Range'] = 'bytes %d-%d/%d' % (offset, end - 1, clen)
        headers['Content-Length'] = str(end - offset)
        if body:
            body = _file_iter_range(body, offset, end - offset)
        return HTTPResponse(body, status=206, **headers)
    return HTTPResponse(body, **headers)


def debug(mode = True):
    global DEBUG
    DEBUG = bool(mode)


def parse_date(ims):
    try:
        ts = email.utils.parsedate_tz(ims)
        return time.mktime(ts[:8] + (0,)) - (ts[9] or 0) - time.timezone
    except (TypeError,
     ValueError,
     IndexError,
     OverflowError):
        return None


def parse_auth(header):
    try:
        method, data = header.split(None, 1)
        if method.lower() == 'basic':
            user, pwd = touni(base64.b64decode(tob(data))).split(':', 1)
            return (user, pwd)
    except (KeyError, ValueError):
        return


def parse_range_header(header, maxlen = 0):
    if not header or header[:6] != 'bytes=':
        return
    ranges = [ r.split('-', 1) for r in header[6:].split(',') if '-' in r ]
    for start, end in ranges:
        try:
            if not start:
                start, end = max(0, maxlen - int(end)), maxlen
            elif not end:
                start, end = int(start), maxlen
            else:
                start, end = int(start), min(int(end) + 1, maxlen)
            if 0 <= start < end <= maxlen:
                yield (start, end)
        except ValueError:
            pass


def _parse_qsl(qs):
    r = []
    for pair in qs.replace(';', '&').split('&'):
        if not pair:
            continue
        nv = pair.split('=', 1)
        if len(nv) != 2:
            nv.append('')
        key = urlunquote(nv[0].replace('+', ' '))
        value = urlunquote(nv[1].replace('+', ' '))
        r.append((key, value))

    return r


def _lscmp(a, b):
    return not sum(((0 if x == y else 1) for x, y in zip(a, b))) and len(a) == len(b)


def cookie_encode(data, key):
    msg = base64.b64encode(pickle.dumps(data, -1))
    sig = base64.b64encode(hmac.new(tob(key), msg).digest())
    return tob('!') + sig + tob('?') + msg


def cookie_decode(data, key):
    data = tob(data)
    if cookie_is_encoded(data):
        sig, msg = data.split(tob('?'), 1)
        if _lscmp(sig[1:], base64.b64encode(hmac.new(tob(key), msg).digest())):
            return pickle.loads(base64.b64decode(msg))


def cookie_is_encoded(data):
    return bool(data.startswith(tob('!')) and tob('?') in data)


def html_escape(string):
    return string.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#039;')


def html_quote(string):
    return '"%s"' % html_escape(string).replace('\n', '%#10;').replace('\r', '&#13;').replace('\t', '&#9;')


def yieldroutes(func):
    import inspect
    path = '/' + func.__name__.replace('__', '/').lstrip('/')
    spec = inspect.getargspec(func)
    argc = len(spec[0]) - len(spec[3] or [])
    path += '/:%s' * argc % tuple(spec[0][:argc])
    yield path
    for arg in spec[0][argc:]:
        path += '/:%s' % arg
        yield path


def path_shift(script_name, path_info, shift = 1):
    if shift == 0:
        return (script_name, path_info)
    pathlist = path_info.strip('/').split('/')
    scriptlist = script_name.strip('/').split('/')
    if pathlist and pathlist[0] == '':
        pathlist = []
    if scriptlist and scriptlist[0] == '':
        scriptlist = []
    if shift > 0 and shift <= len(pathlist):
        moved = pathlist[:shift]
        scriptlist = scriptlist + moved
        pathlist = pathlist[shift:]
    elif shift < 0 and shift >= -len(scriptlist):
        moved = scriptlist[shift:]
        pathlist = moved + pathlist
        scriptlist = scriptlist[:shift]
    else:
        empty = 'SCRIPT_NAME' if shift < 0 else 'PATH_INFO'
        raise AssertionError('Cannot shift. Nothing left from %s' % empty)
    new_script_name = '/' + '/'.join(scriptlist)
    new_path_info = '/' + '/'.join(pathlist)
    if path_info.endswith('/') and pathlist:
        new_path_info += '/'
    return (new_script_name, new_path_info)


def validate(**vkargs):
    depr('Use route wildcard filters instead.')

    def decorator(func):

        @functools.wraps(func)
        def wrapper(*args, **kargs):
            for key, value in vkargs.items():
                if key not in kargs:
                    abort(403, 'Missing parameter: %s' % key)
                try:
                    kargs[key] = value(kargs[key])
                except ValueError:
                    abort(403, 'Wrong parameter format for: %s' % key)

            return func(*args, **kargs)

        return wrapper

    return decorator


def auth_basic(check, realm = 'private', text = 'Access denied'):

    def decorator(func):

        def wrapper(*a, **ka):
            user, password = request.auth or (None, None)
            if user is None or not check(user, password):
                response.headers['WWW-Authenticate'] = 'Basic realm="%s"' % realm
                return HTTPError(401, text)
            return func(*a, **ka)

        return wrapper

    return decorator


def make_default_app_wrapper(name):

    @functools.wraps(getattr(Bottle, name))
    def wrapper(*a, **ka):
        return getattr(app(), name)(*a, **ka)

    return wrapper


route = make_default_app_wrapper('route')
get = make_default_app_wrapper('get')
post = make_default_app_wrapper('post')
put = make_default_app_wrapper('put')
delete = make_default_app_wrapper('delete')
error = make_default_app_wrapper('error')
mount = make_default_app_wrapper('mount')
hook = make_default_app_wrapper('hook')
install = make_default_app_wrapper('install')
uninstall = make_default_app_wrapper('uninstall')
url = make_default_app_wrapper('get_url')

class ServerAdapter(object):
    quiet = False

    def __init__(self, host = '127.0.0.1', port = 8080, **config):
        self.options = config
        self.host = host
        self.port = int(port)

    def run(self, handler):
        pass

    def __repr__(self):
        args = ', '.join([ '%s=%s' % (k, repr(v)) for k, v in self.options.items() ])
        return '%s(%s)' % (self.__class__.__name__, args)


class CGIServer(ServerAdapter):
    quiet = True

    def run(self, handler):
        from wsgiref.handlers import CGIHandler

        def fixed_environ(environ, start_response):
            environ.setdefault('PATH_INFO', '')
            return handler(environ, start_response)

        CGIHandler().run(fixed_environ)


class FlupFCGIServer(ServerAdapter):

    def run(self, handler):
        import flup.server.fcgi
        self.options.setdefault('bindAddress', (self.host, self.port))
        flup.server.fcgi.WSGIServer(handler, **self.options).run()


class WSGIRefServer(ServerAdapter):

    def run(self, handler):
        from wsgiref.simple_server import make_server, WSGIRequestHandler
        if self.quiet:

            class QuietHandler(WSGIRequestHandler):

                def log_request(*args, **kw):
                    pass

            self.options['handler_class'] = QuietHandler
        srv = make_server(self.host, self.port, handler, **self.options)
        srv.serve_forever()


class CherryPyServer(ServerAdapter):

    def run(self, handler):
        from cherrypy import wsgiserver
        server = wsgiserver.CherryPyWSGIServer((self.host, self.port), handler)
        try:
            server.start()
        finally:
            server.stop()


class WaitressServer(ServerAdapter):

    def run(self, handler):
        from waitress import serve
        serve(handler, host=self.host, port=self.port)


class PasteServer(ServerAdapter):

    def run(self, handler):
        from paste import httpserver
        if not self.quiet:
            from paste.translogger import TransLogger
            handler = TransLogger(handler)
        httpserver.serve(handler, host=self.host, port=str(self.port), **self.options)


class MeinheldServer(ServerAdapter):

    def run(self, handler):
        from meinheld import server
        server.listen((self.host, self.port))
        server.run(handler)


class FapwsServer(ServerAdapter):

    def run(self, handler):
        import fapws._evwsgi as evwsgi
        from fapws import base, config
        port = self.port
        if float(config.SERVER_IDENT[-2:]) > 0.4:
            port = str(port)
        evwsgi.start(self.host, port)
        if 'BOTTLE_CHILD' in os.environ and not self.quiet:
            _stderr('WARNING: Auto-reloading does not work with Fapws3.\n')
            _stderr('         (Fapws3 breaks python thread support)\n')
        evwsgi.set_base_module(base)

        def app(environ, start_response):
            environ['wsgi.multiprocess'] = False
            return handler(environ, start_response)

        evwsgi.wsgi_cb(('', app))
        evwsgi.run()


class TornadoServer(ServerAdapter):

    def run(self, handler):
        import tornado.wsgi, tornado.httpserver, tornado.ioloop
        container = tornado.wsgi.WSGIContainer(handler)
        server = tornado.httpserver.HTTPServer(container)
        server.listen(port=self.port)
        tornado.ioloop.IOLoop.instance().start()


class AppEngineServer(ServerAdapter):
    quiet = True

    def run(self, handler):
        from google.appengine.ext.webapp import util
        module = sys.modules.get('__main__')
        if module and not hasattr(module, 'main'):
            module.main = lambda : util.run_wsgi_app(handler)
        util.run_wsgi_app(handler)


class TwistedServer(ServerAdapter):

    def run(self, handler):
        from twisted.web import server, wsgi
        from twisted.python.threadpool import ThreadPool
        from twisted.internet import reactor
        thread_pool = ThreadPool()
        thread_pool.start()
        reactor.addSystemEventTrigger('after', 'shutdown', thread_pool.stop)
        factory = server.Site(wsgi.WSGIResource(reactor, thread_pool, handler))
        reactor.listenTCP(self.port, factory, interface=self.host)
        reactor.run()


class DieselServer(ServerAdapter):

    def run(self, handler):
        from diesel.protocols.wsgi import WSGIApplication
        app = WSGIApplication(handler, port=self.port)
        app.run()


class GeventServer(ServerAdapter):

    def run(self, handler):
        from gevent import wsgi, pywsgi, local
        if not isinstance(_lctx, local.local):
            msg = 'Bottle requires gevent.monkey.patch_all() (before import)'
            raise RuntimeError(msg)
        if not self.options.get('fast'):
            wsgi = pywsgi
        log = None if self.quiet else 'default'
        wsgi.WSGIServer((self.host, self.port), handler, log=log).serve_forever()


class GunicornServer(ServerAdapter):

    def run(self, handler):
        from gunicorn.app.base import Application
        config = {'bind': '%s:%d' % (self.host, int(self.port))}
        config.update(self.options)

        class GunicornApplication(Application):

            def init(self, parser, opts, args):
                return config

            def load(self):
                return handler

        GunicornApplication().run()


class EventletServer(ServerAdapter):

    def run(self, handler):
        from eventlet import wsgi, listen
        try:
            wsgi.server(listen((self.host, self.port)), handler, log_output=not self.quiet)
        except TypeError:
            wsgi.server(listen((self.host, self.port)), handler)


class RocketServer(ServerAdapter):

    def run(self, handler):
        from rocket import Rocket
        server = Rocket((self.host, self.port), 'wsgi', {'wsgi_app': handler})
        server.start()


class BjoernServer(ServerAdapter):

    def run(self, handler):
        from bjoern import run
        run(handler, self.host, self.port)


class AutoServer(ServerAdapter):
    adapters = [WaitressServer,
     PasteServer,
     TwistedServer,
     CherryPyServer,
     WSGIRefServer]

    def run(self, handler):
        for sa in self.adapters:
            try:
                return sa(self.host, self.port, **self.options).run(handler)
            except ImportError:
                pass


server_names = {'cgi': CGIServer,
 'flup': FlupFCGIServer,
 'wsgiref': WSGIRefServer,
 'waitress': WaitressServer,
 'cherrypy': CherryPyServer,
 'paste': PasteServer,
 'fapws3': FapwsServer,
 'tornado': TornadoServer,
 'gae': AppEngineServer,
 'twisted': TwistedServer,
 'diesel': DieselServer,
 'meinheld': MeinheldServer,
 'gunicorn': GunicornServer,
 'eventlet': EventletServer,
 'gevent': GeventServer,
 'rocket': RocketServer,
 'bjoern': BjoernServer,
 'auto': AutoServer}

def load(target, **namespace):
    module, target = target.split(':', 1) if ':' in target else (target, None)
    if module not in sys.modules:
        __import__(module)
    if not target:
        return sys.modules[module]
    if target.isalnum():
        return getattr(sys.modules[module], target)
    package_name = module.split('.')[0]
    namespace[package_name] = sys.modules[package_name]
    return eval('%s.%s' % (module, target), namespace)


def load_app(target):
    global NORUN
    NORUN, nr_old = True, NORUN
    try:
        tmp = default_app.push()
        rv = load(target)
        if callable(rv):
            return rv
        return tmp
    finally:
        default_app.remove(tmp)
        NORUN = nr_old


_debug = debug

def run(app = None, server = 'wsgiref', host = '127.0.0.1', port = 8080, interval = 1, reloader = False, quiet = False, plugins = None, debug = False, **kargs):
    if NORUN:
        return
    if reloader and not os.environ.get('BOTTLE_CHILD'):
        try:
            lockfile = None
            fd, lockfile = tempfile.mkstemp(prefix='bottle.', suffix='.lock')
            os.close(fd)
            while os.path.exists(lockfile):
                args = [sys.executable] + sys.argv
                environ = os.environ.copy()
                environ['BOTTLE_CHILD'] = 'true'
                environ['BOTTLE_LOCKFILE'] = lockfile
                p = subprocess.Popen(args, env=environ)
                while p.poll() is None:
                    os.utime(lockfile, None)
                    time.sleep(interval)

                if p.poll() != 3:
                    if os.path.exists(lockfile):
                        os.unlink(lockfile)
                    sys.exit(p.poll())

        except KeyboardInterrupt:
            pass
        finally:
            if os.path.exists(lockfile):
                os.unlink(lockfile)

        return
    try:
        _debug(debug)
        app = app or default_app()
        if isinstance(app, basestring):
            app = load_app(app)
        if not callable(app):
            raise ValueError('Application is not callable: %r' % app)
        for plugin in plugins or []:
            app.install(plugin)

        if server in server_names:
            server = server_names.get(server)
        if isinstance(server, basestring):
            server = load(server)
        if isinstance(server, type):
            server = server(host=host, port=port, **kargs)
        if not isinstance(server, ServerAdapter):
            raise ValueError('Unknown or unsupported server: %r' % server)
        server.quiet = server.quiet or quiet
        if not server.quiet:
            _stderr('Bottle v%s server starting up (using %s)...\n' % (__version__, repr(server)))
            _stderr('Listening on http://%s:%d/\n' % (server.host, server.port))
            _stderr('Hit Ctrl-C to quit.\n\n')
        if reloader:
            lockfile = os.environ.get('BOTTLE_LOCKFILE')
            bgcheck = FileCheckerThread(lockfile, interval)
            with bgcheck:
                server.run(app)
            if bgcheck.status == 'reload':
                sys.exit(3)
        else:
            server.run(app)
    except KeyboardInterrupt:
        pass
    except (SystemExit, MemoryError):
        raise
    except:
        if not reloader:
            raise
        if not getattr(server, 'quiet', quiet):
            print_exc()
        time.sleep(interval)
        sys.exit(3)


class FileCheckerThread(threading.Thread):

    def __init__(self, lockfile, interval):
        threading.Thread.__init__(self)
        self.lockfile, self.interval = lockfile, interval
        self.status = None

    def run(self):
        exists = os.path.exists
        mtime = lambda path: os.stat(path).st_mtime
        files = dict()
        for module in list(sys.modules.values()):
            path = getattr(module, '__file__', '')
            if path[-4:] in ('.pyo', '.pyc'):
                path = path[:-1]
            if path and exists(path):
                files[path] = mtime(path)

        while not self.status:
            if not exists(self.lockfile) or mtime(self.lockfile) < time.time() - self.interval - 5:
                self.status = 'error'
                thread.interrupt_main()
            for path, lmtime in list(files.items()):
                if not exists(path) or mtime(path) > lmtime:
                    self.status = 'reload'
                    thread.interrupt_main()
                    break

            time.sleep(self.interval)

    def __enter__(self):
        self.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.status:
            self.status = 'exit'
        self.join()
        return exc_type is not None and issubclass(exc_type, KeyboardInterrupt)


class TemplateError(HTTPError):

    def __init__(self, message):
        HTTPError.__init__(self, 500, message)


class BaseTemplate(object):
    extensions = ['tpl',
     'html',
     'thtml',
     'stpl']
    settings = {}
    defaults = {}

    def __init__(self, source = None, name = None, lookup = [], encoding = 'utf8', **settings):
        self.name = name
        self.source = source.read() if hasattr(source, 'read') else source
        self.filename = source.filename if hasattr(source, 'filename') else None
        self.lookup = [ os.path.abspath(x) for x in lookup ]
        self.encoding = encoding
        self.settings = self.settings.copy()
        self.settings.update(settings)
        if not self.source and self.name:
            self.filename = self.search(self.name, self.lookup)
            if not self.filename:
                raise TemplateError('Template %s not found.' % repr(name))
        if not self.source and not self.filename:
            raise TemplateError('No template specified.')
        self.prepare(**self.settings)

    @classmethod
    def search(cls, name, lookup = []):
        if not lookup:
            depr('The template lookup path list should not be empty.')
            lookup = ['.']
        if os.path.isabs(name) and os.path.isfile(name):
            depr('Absolute template path names are deprecated.')
            return os.path.abspath(name)
        for spath in lookup:
            spath = os.path.abspath(spath) + os.sep
            fname = os.path.abspath(os.path.join(spath, name))
            if not fname.startswith(spath):
                continue
            if os.path.isfile(fname):
                return fname
            for ext in cls.extensions:
                if os.path.isfile('%s.%s' % (fname, ext)):
                    return '%s.%s' % (fname, ext)

    @classmethod
    def global_config(cls, key, *args):
        if args:
            cls.settings = cls.settings.copy()
            cls.settings[key] = args[0]
        else:
            return cls.settings[key]

    def prepare(self, **options):
        raise NotImplementedError

    def render(self, *args, **kwargs):
        raise NotImplementedError


class MakoTemplate(BaseTemplate):

    def prepare(self, **options):
        from mako.template import Template
        from mako.lookup import TemplateLookup
        options.update({'input_encoding': self.encoding})
        options.setdefault('format_exceptions', bool(DEBUG))
        lookup = TemplateLookup(directories=self.lookup, **options)
        if self.source:
            self.tpl = Template(self.source, lookup=lookup, **options)
        else:
            self.tpl = Template(uri=self.name, filename=self.filename, lookup=lookup, **options)

    def render(self, *args, **kwargs):
        for dictarg in args:
            kwargs.update(dictarg)

        _defaults = self.defaults.copy()
        _defaults.update(kwargs)
        return self.tpl.render(**_defaults)


class CheetahTemplate(BaseTemplate):

    def prepare(self, **options):
        from Cheetah.Template import Template
        self.context = threading.local()
        self.context.vars = {}
        options['searchList'] = [self.context.vars]
        if self.source:
            self.tpl = Template(source=self.source, **options)
        else:
            self.tpl = Template(file=self.filename, **options)

    def render(self, *args, **kwargs):
        for dictarg in args:
            kwargs.update(dictarg)

        self.context.vars.update(self.defaults)
        self.context.vars.update(kwargs)
        out = str(self.tpl)
        self.context.vars.clear()
        return out


class Jinja2Template(BaseTemplate):

    def prepare(self, filters = None, tests = None, **kwargs):
        from jinja2 import Environment, FunctionLoader
        if 'prefix' in kwargs:
            raise RuntimeError('The keyword argument `prefix` has been removed. Use the full jinja2 environment name line_statement_prefix instead.')
        self.env = Environment(loader=FunctionLoader(self.loader), **kwargs)
        if filters:
            self.env.filters.update(filters)
        if tests:
            self.env.tests.update(tests)
        if self.source:
            self.tpl = self.env.from_string(self.source)
        else:
            self.tpl = self.env.get_template(self.filename)

    def render(self, *args, **kwargs):
        for dictarg in args:
            kwargs.update(dictarg)

        _defaults = self.defaults.copy()
        _defaults.update(kwargs)
        return self.tpl.render(**_defaults)

    def loader(self, name):
        fname = self.search(name, self.lookup)
        if not fname:
            return
        with open(fname, 'rb') as f:
            return f.read().decode(self.encoding)


class SimpleTALTemplate(BaseTemplate):

    def prepare(self, **options):
        depr('The SimpleTAL template handler is deprecated and will be removed in 0.12')
        from simpletal import simpleTAL
        if self.source:
            self.tpl = simpleTAL.compileHTMLTemplate(self.source)
        else:
            with open(self.filename, 'rb') as fp:
                self.tpl = simpleTAL.compileHTMLTemplate(tonat(fp.read()))

    def render(self, *args, **kwargs):
        from simpletal import simpleTALES
        for dictarg in args:
            kwargs.update(dictarg)

        context = simpleTALES.Context()
        for k, v in self.defaults.items():
            context.addGlobal(k, v)

        for k, v in kwargs.items():
            context.addGlobal(k, v)

        output = StringIO()
        self.tpl.expand(context, output)
        return output.getvalue()


class SimpleTemplate(BaseTemplate):
    blocks = ('if', 'elif', 'else', 'try', 'except', 'finally', 'for', 'while', 'with', 'def', 'class')
    dedent_blocks = ('elif', 'else', 'except', 'finally')

    @lazy_attribute
    def re_pytokens(cls):
        return re.compile('\n            (\'\'(?!\')|""(?!")|\'{6}|"{6}    # Empty strings (all 4 types)\n             |\'(?:[^\\\\\']|\\\\.)+?\'          # Single quotes (\')\n             |"(?:[^\\\\"]|\\\\.)+?"          # Double quotes (")\n             |\'{3}(?:[^\\\\]|\\\\.|\\n)+?\'{3}  # Triple-quoted strings (\')\n             |"{3}(?:[^\\\\]|\\\\.|\\n)+?"{3}  # Triple-quoted strings (")\n             |\\#.*                        # Comments\n            )', re.VERBOSE)

    def prepare(self, escape_func = html_escape, noescape = False, **kwargs):
        self.cache = {}
        enc = self.encoding
        self._str = lambda x: touni(x, enc)
        self._escape = lambda x: escape_func(touni(x, enc))
        if noescape:
            self._str, self._escape = self._escape, self._str

    @classmethod
    def split_comment(cls, code):
        if '#' not in code:
            return code
        subf = lambda m: ('' if m.group(0)[0] == '#' else m.group(0))
        return re.sub(cls.re_pytokens, subf, code)

    @cached_property
    def co(self):
        return compile(self.code, self.filename or '<string>', 'exec')

    @cached_property
    def code(self):
        stack = []
        lineno = 0
        ptrbuffer = []
        codebuffer = []
        multiline = dedent = oneline = False
        template = self.source or open(self.filename, 'rb').read()

        def yield_tokens(line):
            for i, part in enumerate(re.split('\\{\\{(.*?)\\}\\}', line)):
                if i % 2:
                    if part.startswith('!'):
                        yield ('RAW', part[1:])
                    else:
                        yield ('CMD', part)
                else:
                    yield ('TXT', part)

        def flush():
            if not ptrbuffer:
                return
            cline = ''
            for line in ptrbuffer:
                for token, value in line:
                    if token == 'TXT':
                        cline += repr(value)
                    elif token == 'RAW':
                        cline += '_str(%s)' % value
                    elif token == 'CMD':
                        cline += '_escape(%s)' % value
                    cline += ', '

                cline = cline[:-2] + '\\\n'

            cline = cline[:-2]
            if cline[:-1].endswith('\\\\\\\\\\n'):
                cline = cline[:-7] + cline[-1]
            cline = '_printlist([' + cline + '])'
            del ptrbuffer[:]
            code(cline)

        def code(stmt):
            for line in stmt.splitlines():
                codebuffer.append('  ' * len(stack) + line.strip())

        for line in template.splitlines(True):
            lineno += 1
            line = touni(line, self.encoding)
            sline = line.lstrip()
            if lineno <= 2:
                m = re.match('%\\s*#.*coding[:=]\\s*([-\\w.]+)', sline)
                if m:
                    self.encoding = m.group(1)
                if m:
                    line = line.replace('coding', 'coding (removed)')
            if sline and sline[0] == '%' and sline[:2] != '%%':
                line = line.split('%', 1)[1].lstrip()
                cline = self.split_comment(line).strip()
                cmd = re.split('[^a-zA-Z0-9_]', cline)[0]
                flush()
                if cmd in self.blocks or multiline:
                    cmd = multiline or cmd
                    dedent = cmd in self.dedent_blocks
                    if dedent and not oneline and not multiline:
                        cmd = stack.pop()
                    code(line)
                    oneline = not cline.endswith(':')
                    multiline = cmd if cline.endswith('\\') else False
                    if not oneline and not multiline:
                        stack.append(cmd)
                elif cmd == 'end' and stack:
                    code('#end(%s) %s' % (stack.pop(), line.strip()[3:]))
                elif cmd == 'include':
                    p = cline.split(None, 2)[1:]
                    if len(p) == 2:
                        code('_=_include(%s, _stdout, %s)' % (repr(p[0]), p[1]))
                    elif p:
                        code('_=_include(%s, _stdout)' % repr(p[0]))
                    else:
                        code('_printlist(_base)')
                elif cmd == 'rebase':
                    p = cline.split(None, 2)[1:]
                    if len(p) == 2:
                        code("globals()['_rebase']=(%s, dict(%s))" % (repr(p[0]), p[1]))
                    elif p:
                        code("globals()['_rebase']=(%s, {})" % repr(p[0]))
                else:
                    code(line)
            else:
                if line.strip().startswith('%%'):
                    line = line.replace('%%', '%', 1)
                ptrbuffer.append(yield_tokens(line))

        flush()
        return '\n'.join(codebuffer) + '\n'

    def subtemplate(self, _name, _stdout, *args, **kwargs):
        for dictarg in args:
            kwargs.update(dictarg)

        if _name not in self.cache:
            self.cache[_name] = self.__class__(name=_name, lookup=self.lookup)
        return self.cache[_name].execute(_stdout, kwargs)

    def execute(self, _stdout, *args, **kwargs):
        for dictarg in args:
            kwargs.update(dictarg)

        env = self.defaults.copy()
        env.update({'_stdout': _stdout,
         '_printlist': _stdout.extend,
         '_include': self.subtemplate,
         '_str': self._str,
         '_escape': self._escape,
         'get': env.get,
         'setdefault': env.setdefault,
         'defined': env.__contains__})
        env.update(kwargs)
        eval(self.co, env)
        if '_rebase' in env:
            subtpl, rargs = env['_rebase']
            rargs['_base'] = _stdout[:]
            del _stdout[:]
            return self.subtemplate(subtpl, _stdout, rargs)
        return env

    def render(self, *args, **kwargs):
        for dictarg in args:
            kwargs.update(dictarg)

        stdout = []
        self.execute(stdout, kwargs)
        return ''.join(stdout)


def template(*args, **kwargs):
    tpl = args[0] if args else None
    adapter = kwargs.pop('template_adapter', SimpleTemplate)
    lookup = kwargs.pop('template_lookup', TEMPLATE_PATH)
    tplid = (id(lookup), tpl)
    if tplid not in TEMPLATES or DEBUG:
        settings = kwargs.pop('template_settings', {})
        if isinstance(tpl, adapter):
            TEMPLATES[tplid] = tpl
            if settings:
                TEMPLATES[tplid].prepare(**settings)
        elif '\n' in tpl or '{' in tpl or '%' in tpl or '$' in tpl:
            TEMPLATES[tplid] = adapter(source=tpl, lookup=lookup, **settings)
        else:
            TEMPLATES[tplid] = adapter(name=tpl, lookup=lookup, **settings)
    if not TEMPLATES[tplid]:
        abort(500, 'Template (%s) not found' % tpl)
    for dictarg in args[1:]:
        kwargs.update(dictarg)

    return TEMPLATES[tplid].render(kwargs)


mako_template = functools.partial(template, template_adapter=MakoTemplate)
cheetah_template = functools.partial(template, template_adapter=CheetahTemplate)
jinja2_template = functools.partial(template, template_adapter=Jinja2Template)
simpletal_template = functools.partial(template, template_adapter=SimpleTALTemplate)

def view(tpl_name, **defaults):

    def decorator(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            if isinstance(result, (dict, DictMixin)):
                tplvars = defaults.copy()
                tplvars.update(result)
                return template(tpl_name, **tplvars)
            return result

        return wrapper

    return decorator


mako_view = functools.partial(view, template_adapter=MakoTemplate)
cheetah_view = functools.partial(view, template_adapter=CheetahTemplate)
jinja2_view = functools.partial(view, template_adapter=Jinja2Template)
simpletal_view = functools.partial(view, template_adapter=SimpleTALTemplate)
TEMPLATE_PATH = ['./', './views/']
TEMPLATES = {}
DEBUG = False
NORUN = False
HTTP_CODES = httplib.responses
HTTP_CODES[418] = "I'm a teapot"
HTTP_CODES[428] = 'Precondition Required'
HTTP_CODES[429] = 'Too Many Requests'
HTTP_CODES[431] = 'Request Header Fields Too Large'
HTTP_CODES[511] = 'Network Authentication Required'
_HTTP_STATUS_LINES = dict(((k, '%d %s' % (k, v)) for k, v in HTTP_CODES.items()))
ERROR_PAGE_TEMPLATE = '\n%%try:\n    %%from %s import DEBUG, HTTP_CODES, request, touni\n    <!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">\n    <html>\n        <head>\n            <title>Error: {{e.status}}</title>\n            <style type="text/css">\n              html {background-color: #eee; font-family: sans;}\n              body {background-color: #fff; border: 1px solid #ddd;\n                    padding: 15px; margin: 15px;}\n              pre {background-color: #eee; border: 1px solid #ddd; padding: 5px;}\n            </style>\n        </head>\n        <body>\n            <h1>Error: {{e.status}}</h1>\n            <p>Sorry, the requested URL <tt>{{repr(request.url)}}</tt>\n               caused an error:</p>\n            <pre>{{e.body}}</pre>\n            %%if DEBUG and e.exception:\n              <h2>Exception:</h2>\n              <pre>{{repr(e.exception)}}</pre>\n            %%end\n            %%if DEBUG and e.traceback:\n              <h2>Traceback:</h2>\n              <pre>{{e.traceback}}</pre>\n            %%end\n        </body>\n    </html>\n%%except ImportError:\n    <b>ImportError:</b> Could not generate the error page. Please add bottle to\n    the import path.\n%%end\n' % __name__
request = LocalRequest()
response = LocalResponse()
local = threading.local()
app = default_app = AppStack()
app.push()
ext = _ImportRedirect('bottle.ext' if __name__ == '__main__' else __name__ + '.ext', 'bottle_%s').module
if __name__ == '__main__':
    opt, args, parser = (_cmd_options, _cmd_args, _cmd_parser)
    if opt.version:
        _stdout('Bottle %s\n' % __version__)
        sys.exit(0)
    if not args:
        parser.print_help()
        _stderr('\nError: No application specified.\n')
        sys.exit(1)
    sys.path.insert(0, '.')
    sys.modules.setdefault('bottle', sys.modules['__main__'])
    host, port = (opt.bind or 'localhost', 8080)
    if ':' in host:
        host, port = host.rsplit(':', 1)
    run(args[0], host=host, port=port, server=opt.server, reloader=opt.reload, plugins=opt.plugin, debug=opt.debug)
