#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\httplib2\__init__.py
from __future__ import generators
__author__ = 'Joe Gregorio (joe@bitworking.org)'
__copyright__ = 'Copyright 2006, Joe Gregorio'
__contributors__ = ['Thomas Broyer (t.broyer@ltgt.net)',
 'James Antill',
 'Xavier Verges Farrero',
 'Jonathan Feinberg',
 'Blair Zajac',
 'Sam Ruby',
 'Louis Nyffenegger']
__license__ = 'MIT'
__version__ = '0.9.2'
import re
import sys
import email
import email.Utils
import email.Message
import email.FeedParser
import StringIO
import gzip
import zlib
import httplib
import urlparse
import urllib
import base64
import os
import copy
import calendar
import time
import random
import errno
try:
    from hashlib import sha1 as _sha, md5 as _md5
except ImportError:
    import sha
    import md5
    _sha = sha.new
    _md5 = md5.new

import hmac
from gettext import gettext as _
import socket
try:
    from httplib2 import socks
except ImportError:
    try:
        import socks
    except (ImportError, AttributeError):
        socks = None

try:
    import ssl
    ssl_SSLError = ssl.SSLError

    def _ssl_wrap_socket(sock, key_file, cert_file, disable_validation, ca_certs):
        if disable_validation:
            cert_reqs = ssl.CERT_NONE
        else:
            cert_reqs = ssl.CERT_REQUIRED
        return ssl.wrap_socket(sock, keyfile=key_file, certfile=cert_file, cert_reqs=cert_reqs, ca_certs=ca_certs)


except (AttributeError, ImportError):
    ssl_SSLError = None

    def _ssl_wrap_socket(sock, key_file, cert_file, disable_validation, ca_certs):
        if not disable_validation:
            raise CertificateValidationUnsupported('SSL certificate validation is not supported without the ssl module installed. To avoid this error, install the ssl module, or explicity disable validation.')
        ssl_sock = socket.ssl(sock, key_file, cert_file)
        return httplib.FakeSocket(sock, ssl_sock)


if sys.version_info >= (2, 3):
    from iri2uri import iri2uri
else:

    def iri2uri(uri):
        return uri


def has_timeout(timeout):
    if hasattr(socket, '_GLOBAL_DEFAULT_TIMEOUT'):
        return timeout is not None and timeout is not socket._GLOBAL_DEFAULT_TIMEOUT
    return timeout is not None


__all__ = ['Http',
 'Response',
 'ProxyInfo',
 'HttpLib2Error',
 'RedirectMissingLocation',
 'RedirectLimit',
 'FailedToDecompressContent',
 'UnimplementedDigestAuthOptionError',
 'UnimplementedHmacDigestAuthOptionError',
 'debuglevel',
 'ProxiesUnavailableError']
debuglevel = 0
RETRIES = 2
if sys.version_info < (2, 4):

    def sorted(seq):
        seq.sort()
        return seq


def HTTPResponse__getheaders(self):
    if self.msg is None:
        raise httplib.ResponseNotReady()
    return self.msg.items()


if not hasattr(httplib.HTTPResponse, 'getheaders'):
    httplib.HTTPResponse.getheaders = HTTPResponse__getheaders

class HttpLib2Error(Exception):
    pass


class HttpLib2ErrorWithResponse(HttpLib2Error):

    def __init__(self, desc, response, content):
        self.response = response
        self.content = content
        HttpLib2Error.__init__(self, desc)


class RedirectMissingLocation(HttpLib2ErrorWithResponse):
    pass


class RedirectLimit(HttpLib2ErrorWithResponse):
    pass


class FailedToDecompressContent(HttpLib2ErrorWithResponse):
    pass


class UnimplementedDigestAuthOptionError(HttpLib2ErrorWithResponse):
    pass


class UnimplementedHmacDigestAuthOptionError(HttpLib2ErrorWithResponse):
    pass


class MalformedHeader(HttpLib2Error):
    pass


class RelativeURIError(HttpLib2Error):
    pass


class ServerNotFoundError(HttpLib2Error):
    pass


class ProxiesUnavailableError(HttpLib2Error):
    pass


class CertificateValidationUnsupported(HttpLib2Error):
    pass


class SSLHandshakeError(HttpLib2Error):
    pass


class NotSupportedOnThisPlatform(HttpLib2Error):
    pass


class CertificateHostnameMismatch(SSLHandshakeError):

    def __init__(self, desc, host, cert):
        HttpLib2Error.__init__(self, desc)
        self.host = host
        self.cert = cert


DEFAULT_MAX_REDIRECTS = 5
try:
    import ca_certs_locater
    CA_CERTS = ca_certs_locater.get()
except ImportError:
    CA_CERTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cacerts.txt')

HOP_BY_HOP = ['connection',
 'keep-alive',
 'proxy-authenticate',
 'proxy-authorization',
 'te',
 'trailers',
 'transfer-encoding',
 'upgrade']

def _get_end2end_headers(response):
    hopbyhop = list(HOP_BY_HOP)
    hopbyhop.extend([ x.strip() for x in response.get('connection', '').split(',') ])
    return [ header for header in response.keys() if header not in hopbyhop ]


URI = re.compile('^(([^:/?#]+):)?(//([^/?#]*))?([^?#]*)(\\?([^#]*))?(#(.*))?')

def parse_uri(uri):
    groups = URI.match(uri).groups()
    return (groups[1],
     groups[3],
     groups[4],
     groups[6],
     groups[8])


def urlnorm(uri):
    scheme, authority, path, query, fragment = parse_uri(uri)
    if not scheme or not authority:
        raise RelativeURIError('Only absolute URIs are allowed. uri = %s' % uri)
    authority = authority.lower()
    scheme = scheme.lower()
    if not path:
        path = '/'
    request_uri = query and '?'.join([path, query]) or path
    scheme = scheme.lower()
    defrag_uri = scheme + '://' + authority + request_uri
    return (scheme,
     authority,
     request_uri,
     defrag_uri)


re_url_scheme = re.compile('^\\w+://')
re_slash = re.compile('[?/:|]+')

def safename(filename):
    try:
        if re_url_scheme.match(filename):
            if isinstance(filename, str):
                filename = filename.decode('utf-8')
                filename = filename.encode('idna')
            else:
                filename = filename.encode('idna')
    except UnicodeError:
        pass

    if isinstance(filename, unicode):
        filename = filename.encode('utf-8')
    filemd5 = _md5(filename).hexdigest()
    filename = re_url_scheme.sub('', filename)
    filename = re_slash.sub(',', filename)
    if len(filename) > 200:
        filename = filename[:200]
    return ','.join((filename, filemd5))


NORMALIZE_SPACE = re.compile('(?:\\r\\n)?[ \\t]+')

def _normalize_headers(headers):
    return dict([ (key.lower(), NORMALIZE_SPACE.sub(value, ' ').strip()) for key, value in headers.iteritems() ])


def _parse_cache_control(headers):
    retval = {}
    if headers.has_key('cache-control'):
        parts = headers['cache-control'].split(',')
        parts_with_args = [ tuple([ x.strip().lower() for x in part.split('=', 1) ]) for part in parts if -1 != part.find('=') ]
        parts_wo_args = [ (name.strip().lower(), 1) for name in parts if -1 == name.find('=') ]
        retval = dict(parts_with_args + parts_wo_args)
    return retval


USE_WWW_AUTH_STRICT_PARSING = 0
WWW_AUTH_STRICT = re.compile('^(?:\\s*(?:,\\s*)?([^\\0-\\x1f\\x7f-\\xff()<>@,;:\\\\\\"/[\\]?={} \\t]+)\\s*=\\s*\\"?((?<=\\")(?:[^\\0-\\x08\\x0A-\\x1f\\x7f-\\xff\\\\\\"]|\\\\[\\0-\\x7f])*?(?=\\")|(?<!\\")[^\\0-\\x1f\\x7f-\\xff()<>@,;:\\\\\\"/[\\]?={} \\t]+(?!\\"))\\"?)(.*)$')
WWW_AUTH_RELAXED = re.compile('^(?:\\s*(?:,\\s*)?([^ \\t\\r\\n=]+)\\s*=\\s*\\"?((?<=\\")(?:[^\\\\\\"]|\\\\.)*?(?=\\")|(?<!\\")[^ \\t\\r\\n,]+(?!\\"))\\"?)(.*)$')
UNQUOTE_PAIRS = re.compile('\\\\(.)')

def _parse_www_authenticate(headers, headername = 'www-authenticate'):
    retval = {}
    if headers.has_key(headername):
        try:
            authenticate = headers[headername].strip()
            www_auth = USE_WWW_AUTH_STRICT_PARSING and WWW_AUTH_STRICT or WWW_AUTH_RELAXED
            while authenticate:
                if headername == 'authentication-info':
                    auth_scheme, the_rest = 'digest', authenticate
                else:
                    auth_scheme, the_rest = authenticate.split(' ', 1)
                match = www_auth.search(the_rest)
                auth_params = {}
                while match:
                    if match and len(match.groups()) == 3:
                        key, value, the_rest = match.groups()
                        auth_params[key.lower()] = UNQUOTE_PAIRS.sub('\\1', value)
                    match = www_auth.search(the_rest)

                retval[auth_scheme.lower()] = auth_params
                authenticate = the_rest.strip()

        except ValueError:
            raise MalformedHeader('WWW-Authenticate')

    return retval


def _entry_disposition(response_headers, request_headers):
    retval = 'STALE'
    cc = _parse_cache_control(request_headers)
    cc_response = _parse_cache_control(response_headers)
    if request_headers.has_key('pragma') and request_headers['pragma'].lower().find('no-cache') != -1:
        retval = 'TRANSPARENT'
        if 'cache-control' not in request_headers:
            request_headers['cache-control'] = 'no-cache'
    elif cc.has_key('no-cache'):
        retval = 'TRANSPARENT'
    elif cc_response.has_key('no-cache'):
        retval = 'STALE'
    elif cc.has_key('only-if-cached'):
        retval = 'FRESH'
    elif response_headers.has_key('date'):
        date = calendar.timegm(email.Utils.parsedate_tz(response_headers['date']))
        now = time.time()
        current_age = max(0, now - date)
        if cc_response.has_key('max-age'):
            try:
                freshness_lifetime = int(cc_response['max-age'])
            except ValueError:
                freshness_lifetime = 0

        elif response_headers.has_key('expires'):
            expires = email.Utils.parsedate_tz(response_headers['expires'])
            if None == expires:
                freshness_lifetime = 0
            else:
                freshness_lifetime = max(0, calendar.timegm(expires) - date)
        else:
            freshness_lifetime = 0
        if cc.has_key('max-age'):
            try:
                freshness_lifetime = int(cc['max-age'])
            except ValueError:
                freshness_lifetime = 0

        if cc.has_key('min-fresh'):
            try:
                min_fresh = int(cc['min-fresh'])
            except ValueError:
                min_fresh = 0

            current_age += min_fresh
        if freshness_lifetime > current_age:
            retval = 'FRESH'
    return retval


def _decompressContent(response, new_content):
    content = new_content
    try:
        encoding = response.get('content-encoding', None)
        if encoding in ('gzip', 'deflate'):
            if encoding == 'gzip':
                content = gzip.GzipFile(fileobj=StringIO.StringIO(new_content)).read()
            if encoding == 'deflate':
                content = zlib.decompress(content)
            response['content-length'] = str(len(content))
            response['-content-encoding'] = response['content-encoding']
            del response['content-encoding']
    except IOError:
        content = ''
        raise FailedToDecompressContent(_('Content purported to be compressed with %s but failed to decompress.') % response.get('content-encoding'), response, content)

    return content


def _updateCache(request_headers, response_headers, content, cache, cachekey):
    if cachekey:
        cc = _parse_cache_control(request_headers)
        cc_response = _parse_cache_control(response_headers)
        if cc.has_key('no-store') or cc_response.has_key('no-store'):
            cache.delete(cachekey)
        else:
            info = email.Message.Message()
            for key, value in response_headers.iteritems():
                if key not in ('status', 'content-encoding', 'transfer-encoding'):
                    info[key] = value

            vary = response_headers.get('vary', None)
            if vary:
                vary_headers = vary.lower().replace(' ', '').split(',')
                for header in vary_headers:
                    key = '-varied-%s' % header
                    try:
                        info[key] = request_headers[header]
                    except KeyError:
                        pass

            status = response_headers.status
            if status == 304:
                status = 200
            status_header = 'status: %d\r\n' % status
            header_str = info.as_string()
            header_str = re.sub('\r(?!\n)|(?<!\r)\n', '\r\n', header_str)
            text = ''.join([status_header, header_str, content])
            cache.set(cachekey, text)


def _cnonce():
    dig = _md5('%s:%s' % (time.ctime(), [ '0123456789'[random.randrange(0, 9)] for i in range(20) ])).hexdigest()
    return dig[:16]


def _wsse_username_token(cnonce, iso_now, password):
    return base64.b64encode(_sha('%s%s%s' % (cnonce, iso_now, password)).digest()).strip()


class Authentication(object):

    def __init__(self, credentials, host, request_uri, headers, response, content, http):
        scheme, authority, path, query, fragment = parse_uri(request_uri)
        self.path = path
        self.host = host
        self.credentials = credentials
        self.http = http

    def depth(self, request_uri):
        scheme, authority, path, query, fragment = parse_uri(request_uri)
        return request_uri[len(self.path):].count('/')

    def inscope(self, host, request_uri):
        scheme, authority, path, query, fragment = parse_uri(request_uri)
        return host == self.host and path.startswith(self.path)

    def request(self, method, request_uri, headers, content):
        pass

    def response(self, response, content):
        return False


class BasicAuthentication(Authentication):

    def __init__(self, credentials, host, request_uri, headers, response, content, http):
        Authentication.__init__(self, credentials, host, request_uri, headers, response, content, http)

    def request(self, method, request_uri, headers, content):
        headers['authorization'] = 'Basic ' + base64.b64encode('%s:%s' % self.credentials).strip()


class DigestAuthentication(Authentication):

    def __init__(self, credentials, host, request_uri, headers, response, content, http):
        Authentication.__init__(self, credentials, host, request_uri, headers, response, content, http)
        challenge = _parse_www_authenticate(response, 'www-authenticate')
        self.challenge = challenge['digest']
        qop = self.challenge.get('qop', 'auth')
        self.challenge['qop'] = 'auth' in [ x.strip() for x in qop.split() ] and 'auth' or None
        if self.challenge['qop'] is None:
            raise UnimplementedDigestAuthOptionError(_('Unsupported value for qop: %s.' % qop))
        self.challenge['algorithm'] = self.challenge.get('algorithm', 'MD5').upper()
        if self.challenge['algorithm'] != 'MD5':
            raise UnimplementedDigestAuthOptionError(_('Unsupported value for algorithm: %s.' % self.challenge['algorithm']))
        self.A1 = ''.join([self.credentials[0],
         ':',
         self.challenge['realm'],
         ':',
         self.credentials[1]])
        self.challenge['nc'] = 1

    def request(self, method, request_uri, headers, content, cnonce = None):
        H = lambda x: _md5(x).hexdigest()
        KD = lambda s, d: H('%s:%s' % (s, d))
        A2 = ''.join([method, ':', request_uri])
        self.challenge['cnonce'] = cnonce or _cnonce()
        request_digest = '"%s"' % KD(H(self.A1), '%s:%s:%s:%s:%s' % (self.challenge['nonce'],
         '%08x' % self.challenge['nc'],
         self.challenge['cnonce'],
         self.challenge['qop'],
         H(A2)))
        headers['authorization'] = 'Digest username="%s", realm="%s", nonce="%s", uri="%s", algorithm=%s, response=%s, qop=%s, nc=%08x, cnonce="%s"' % (self.credentials[0],
         self.challenge['realm'],
         self.challenge['nonce'],
         request_uri,
         self.challenge['algorithm'],
         request_digest,
         self.challenge['qop'],
         self.challenge['nc'],
         self.challenge['cnonce'])
        if self.challenge.get('opaque'):
            headers['authorization'] += ', opaque="%s"' % self.challenge['opaque']
        self.challenge['nc'] += 1

    def response(self, response, content):
        if not response.has_key('authentication-info'):
            challenge = _parse_www_authenticate(response, 'www-authenticate').get('digest', {})
            if 'true' == challenge.get('stale'):
                self.challenge['nonce'] = challenge['nonce']
                self.challenge['nc'] = 1
                return True
        else:
            updated_challenge = _parse_www_authenticate(response, 'authentication-info').get('digest', {})
            if updated_challenge.has_key('nextnonce'):
                self.challenge['nonce'] = updated_challenge['nextnonce']
                self.challenge['nc'] = 1
        return False


class HmacDigestAuthentication(Authentication):
    __author__ = 'Thomas Broyer (t.broyer@ltgt.net)'

    def __init__(self, credentials, host, request_uri, headers, response, content, http):
        Authentication.__init__(self, credentials, host, request_uri, headers, response, content, http)
        challenge = _parse_www_authenticate(response, 'www-authenticate')
        self.challenge = challenge['hmacdigest']
        self.challenge['reason'] = self.challenge.get('reason', 'unauthorized')
        if self.challenge['reason'] not in ('unauthorized', 'integrity'):
            self.challenge['reason'] = 'unauthorized'
        self.challenge['salt'] = self.challenge.get('salt', '')
        if not self.challenge.get('snonce'):
            raise UnimplementedHmacDigestAuthOptionError(_("The challenge doesn't contain a server nonce, or this one is empty."))
        self.challenge['algorithm'] = self.challenge.get('algorithm', 'HMAC-SHA-1')
        if self.challenge['algorithm'] not in ('HMAC-SHA-1', 'HMAC-MD5'):
            raise UnimplementedHmacDigestAuthOptionError(_('Unsupported value for algorithm: %s.' % self.challenge['algorithm']))
        self.challenge['pw-algorithm'] = self.challenge.get('pw-algorithm', 'SHA-1')
        if self.challenge['pw-algorithm'] not in ('SHA-1', 'MD5'):
            raise UnimplementedHmacDigestAuthOptionError(_('Unsupported value for pw-algorithm: %s.' % self.challenge['pw-algorithm']))
        if self.challenge['algorithm'] == 'HMAC-MD5':
            self.hashmod = _md5
        else:
            self.hashmod = _sha
        if self.challenge['pw-algorithm'] == 'MD5':
            self.pwhashmod = _md5
        else:
            self.pwhashmod = _sha
        self.key = ''.join([self.credentials[0],
         ':',
         self.pwhashmod.new(''.join([self.credentials[1], self.challenge['salt']])).hexdigest().lower(),
         ':',
         self.challenge['realm']])
        self.key = self.pwhashmod.new(self.key).hexdigest().lower()

    def request(self, method, request_uri, headers, content):
        keys = _get_end2end_headers(headers)
        keylist = ''.join([ '%s ' % k for k in keys ])
        headers_val = ''.join([ headers[k] for k in keys ])
        created = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        cnonce = _cnonce()
        request_digest = '%s:%s:%s:%s:%s' % (method,
         request_uri,
         cnonce,
         self.challenge['snonce'],
         headers_val)
        request_digest = hmac.new(self.key, request_digest, self.hashmod).hexdigest().lower()
        headers['authorization'] = 'HMACDigest username="%s", realm="%s", snonce="%s", cnonce="%s", uri="%s", created="%s", response="%s", headers="%s"' % (self.credentials[0],
         self.challenge['realm'],
         self.challenge['snonce'],
         cnonce,
         request_uri,
         created,
         request_digest,
         keylist)

    def response(self, response, content):
        challenge = _parse_www_authenticate(response, 'www-authenticate').get('hmacdigest', {})
        if challenge.get('reason') in ('integrity', 'stale'):
            return True
        return False


class WsseAuthentication(Authentication):

    def __init__(self, credentials, host, request_uri, headers, response, content, http):
        Authentication.__init__(self, credentials, host, request_uri, headers, response, content, http)

    def request(self, method, request_uri, headers, content):
        headers['authorization'] = 'WSSE profile="UsernameToken"'
        iso_now = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        cnonce = _cnonce()
        password_digest = _wsse_username_token(cnonce, iso_now, self.credentials[1])
        headers['X-WSSE'] = 'UsernameToken Username="%s", PasswordDigest="%s", Nonce="%s", Created="%s"' % (self.credentials[0],
         password_digest,
         cnonce,
         iso_now)


class GoogleLoginAuthentication(Authentication):

    def __init__(self, credentials, host, request_uri, headers, response, content, http):
        from urllib import urlencode
        Authentication.__init__(self, credentials, host, request_uri, headers, response, content, http)
        challenge = _parse_www_authenticate(response, 'www-authenticate')
        service = challenge['googlelogin'].get('service', 'xapi')
        if service == 'xapi' and request_uri.find('calendar') > 0:
            service = 'cl'
        auth = dict(Email=credentials[0], Passwd=credentials[1], service=service, source=headers['user-agent'])
        resp, content = self.http.request('https://www.google.com/accounts/ClientLogin', method='POST', body=urlencode(auth), headers={'Content-Type': 'application/x-www-form-urlencoded'})
        lines = content.split('\n')
        d = dict([ tuple(line.split('=', 1)) for line in lines if line ])
        if resp.status == 403:
            self.Auth = ''
        else:
            self.Auth = d['Auth']

    def request(self, method, request_uri, headers, content):
        headers['authorization'] = 'GoogleLogin Auth=' + self.Auth


AUTH_SCHEME_CLASSES = {'basic': BasicAuthentication,
 'wsse': WsseAuthentication,
 'digest': DigestAuthentication,
 'hmacdigest': HmacDigestAuthentication,
 'googlelogin': GoogleLoginAuthentication}
AUTH_SCHEME_ORDER = ['hmacdigest',
 'googlelogin',
 'digest',
 'wsse',
 'basic']

class FileCache(object):

    def __init__(self, cache, safe = safename):
        self.cache = cache
        self.safe = safe
        if not os.path.exists(cache):
            os.makedirs(self.cache)

    def get(self, key):
        retval = None
        cacheFullPath = os.path.join(self.cache, self.safe(key))
        try:
            f = file(cacheFullPath, 'rb')
            retval = f.read()
            f.close()
        except IOError:
            pass

        return retval

    def set(self, key, value):
        cacheFullPath = os.path.join(self.cache, self.safe(key))
        f = file(cacheFullPath, 'wb')
        f.write(value)
        f.close()

    def delete(self, key):
        cacheFullPath = os.path.join(self.cache, self.safe(key))
        if os.path.exists(cacheFullPath):
            os.remove(cacheFullPath)


class Credentials(object):

    def __init__(self):
        self.credentials = []

    def add(self, name, password, domain = ''):
        self.credentials.append((domain.lower(), name, password))

    def clear(self):
        self.credentials = []

    def iter(self, domain):
        for cdomain, name, password in self.credentials:
            if cdomain == '' or domain == cdomain:
                yield (name, password)


class KeyCerts(Credentials):
    pass


class AllHosts(object):
    pass


class ProxyInfo(object):
    bypass_hosts = ()

    def __init__(self, proxy_type, proxy_host, proxy_port, proxy_rdns = True, proxy_user = None, proxy_pass = None):
        self.proxy_type = proxy_type
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.proxy_rdns = proxy_rdns
        self.proxy_user = proxy_user
        self.proxy_pass = proxy_pass

    def astuple(self):
        return (self.proxy_type,
         self.proxy_host,
         self.proxy_port,
         self.proxy_rdns,
         self.proxy_user,
         self.proxy_pass)

    def isgood(self):
        return self.proxy_host != None and self.proxy_port != None

    def applies_to(self, hostname):
        return not self.bypass_host(hostname)

    def bypass_host(self, hostname):
        if self.bypass_hosts is AllHosts:
            return True
        bypass = False
        for domain in self.bypass_hosts:
            if hostname.endswith(domain):
                bypass = True

        return bypass


def proxy_info_from_environment(method = 'http'):
    if method not in ('http', 'https'):
        return
    env_var = method + '_proxy'
    url = os.environ.get(env_var, os.environ.get(env_var.upper()))
    if not url:
        return
    pi = proxy_info_from_url(url, method)
    no_proxy = os.environ.get('no_proxy', os.environ.get('NO_PROXY', ''))
    bypass_hosts = []
    if no_proxy:
        bypass_hosts = no_proxy.split(',')
    if no_proxy == '*':
        bypass_hosts = AllHosts
    pi.bypass_hosts = bypass_hosts
    return pi


def proxy_info_from_url(url, method = 'http'):
    url = urlparse.urlparse(url)
    username = None
    password = None
    port = None
    if '@' in url[1]:
        ident, host_port = url[1].split('@', 1)
        if ':' in ident:
            username, password = ident.split(':', 1)
        else:
            password = ident
    else:
        host_port = url[1]
    if ':' in host_port:
        host, port = host_port.split(':', 1)
    else:
        host = host_port
    if port:
        port = int(port)
    else:
        port = dict(https=443, http=80)[method]
    proxy_type = 3
    return ProxyInfo(proxy_type=proxy_type, proxy_host=host, proxy_port=port, proxy_user=username or None, proxy_pass=password or None)


class HTTPConnectionWithTimeout(httplib.HTTPConnection):

    def __init__(self, host, port = None, strict = None, timeout = None, proxy_info = None):
        httplib.HTTPConnection.__init__(self, host, port, strict)
        self.timeout = timeout
        self.proxy_info = proxy_info

    def connect(self):
        if self.proxy_info and socks is None:
            raise ProxiesUnavailableError('Proxy support missing but proxy use was requested!')
        msg = 'getaddrinfo returns an empty list'
        if self.proxy_info and self.proxy_info.isgood():
            use_proxy = True
            proxy_type, proxy_host, proxy_port, proxy_rdns, proxy_user, proxy_pass = self.proxy_info.astuple()
            host = proxy_host
            port = proxy_port
        else:
            use_proxy = False
            host = self.host
            port = self.port
        for res in socket.getaddrinfo(host, port, 0, socket.SOCK_STREAM):
            af, socktype, proto, canonname, sa = res
            try:
                if use_proxy:
                    self.sock = socks.socksocket(af, socktype, proto)
                    self.sock.setproxy(proxy_type, proxy_host, proxy_port, proxy_rdns, proxy_user, proxy_pass)
                else:
                    self.sock = socket.socket(af, socktype, proto)
                    self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                if has_timeout(self.timeout):
                    self.sock.settimeout(self.timeout)
                if self.debuglevel > 0:
                    print 'connect: (%s, %s) ************' % (self.host, self.port)
                    if use_proxy:
                        print 'proxy: %s ************' % str((proxy_host,
                         proxy_port,
                         proxy_rdns,
                         proxy_user,
                         proxy_pass))
                self.sock.connect((self.host, self.port) + sa[2:])
            except socket.error as msg:
                if self.debuglevel > 0:
                    print 'connect fail: (%s, %s)' % (self.host, self.port)
                    if use_proxy:
                        print 'proxy: %s' % str((proxy_host,
                         proxy_port,
                         proxy_rdns,
                         proxy_user,
                         proxy_pass))
                if self.sock:
                    self.sock.close()
                self.sock = None
                continue

            break

        if not self.sock:
            raise socket.error, msg


class HTTPSConnectionWithTimeout(httplib.HTTPSConnection):

    def __init__(self, host, port = None, key_file = None, cert_file = None, strict = None, timeout = None, proxy_info = None, ca_certs = None, disable_ssl_certificate_validation = False):
        httplib.HTTPSConnection.__init__(self, host, port=port, key_file=key_file, cert_file=cert_file, strict=strict)
        self.timeout = timeout
        self.proxy_info = proxy_info
        if ca_certs is None:
            ca_certs = CA_CERTS
        self.ca_certs = ca_certs
        self.disable_ssl_certificate_validation = disable_ssl_certificate_validation

    def _GetValidHostsForCert(self, cert):
        if 'subjectAltName' in cert:
            return [ x[1] for x in cert['subjectAltName'] if x[0].lower() == 'dns' ]
        else:
            return [ x[0][1] for x in cert['subject'] if x[0][0].lower() == 'commonname' ]

    def _ValidateCertificateHostname(self, cert, hostname):
        hosts = self._GetValidHostsForCert(cert)
        for host in hosts:
            host_re = host.replace('.', '\\.').replace('*', '[^.]*')
            if re.search('^%s$' % (host_re,), hostname, re.I):
                return True

        return False

    def connect(self):
        msg = 'getaddrinfo returns an empty list'
        if self.proxy_info and self.proxy_info.isgood():
            use_proxy = True
            proxy_type, proxy_host, proxy_port, proxy_rdns, proxy_user, proxy_pass = self.proxy_info.astuple()
            host = proxy_host
            port = proxy_port
        else:
            use_proxy = False
            host = self.host
            port = self.port
        address_info = socket.getaddrinfo(host, port, 0, socket.SOCK_STREAM)
        for family, socktype, proto, canonname, sockaddr in address_info:
            try:
                if use_proxy:
                    sock = socks.socksocket(family, socktype, proto)
                    sock.setproxy(proxy_type, proxy_host, proxy_port, proxy_rdns, proxy_user, proxy_pass)
                else:
                    sock = socket.socket(family, socktype, proto)
                    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                if has_timeout(self.timeout):
                    sock.settimeout(self.timeout)
                sock.connect((self.host, self.port))
                self.sock = _ssl_wrap_socket(sock, self.key_file, self.cert_file, self.disable_ssl_certificate_validation, self.ca_certs)
                if self.debuglevel > 0:
                    print 'connect: (%s, %s)' % (self.host, self.port)
                    if use_proxy:
                        print 'proxy: %s' % str((proxy_host,
                         proxy_port,
                         proxy_rdns,
                         proxy_user,
                         proxy_pass))
                if not self.disable_ssl_certificate_validation:
                    cert = self.sock.getpeercert()
                    hostname = self.host.split(':', 0)[0]
                    if not self._ValidateCertificateHostname(cert, hostname):
                        raise CertificateHostnameMismatch('Server presented certificate that does not match host %s: %s' % (hostname, cert), hostname, cert)
            except ssl_SSLError as e:
                if sock:
                    sock.close()
                if self.sock:
                    self.sock.close()
                self.sock = None
                if e.errno == ssl.SSL_ERROR_SSL:
                    raise SSLHandshakeError(e)
                else:
                    raise
            except (socket.timeout, socket.gaierror):
                raise
            except socket.error as msg:
                if self.debuglevel > 0:
                    print 'connect fail: (%s, %s)' % (self.host, self.port)
                    if use_proxy:
                        print 'proxy: %s' % str((proxy_host,
                         proxy_port,
                         proxy_rdns,
                         proxy_user,
                         proxy_pass))
                if self.sock:
                    self.sock.close()
                self.sock = None
                continue

            break

        if not self.sock:
            raise socket.error, msg


SCHEME_TO_CONNECTION = {'http': HTTPConnectionWithTimeout,
 'https': HTTPSConnectionWithTimeout}
try:
    try:
        from google.appengine.api import apiproxy_stub_map
        if apiproxy_stub_map.apiproxy.GetStub('urlfetch') is None:
            raise ImportError
        from google.appengine.api.urlfetch import fetch
        from google.appengine.api.urlfetch import InvalidURLError
    except (ImportError, AttributeError):
        from google3.apphosting.api import apiproxy_stub_map
        if apiproxy_stub_map.apiproxy.GetStub('urlfetch') is None:
            raise ImportError
        from google3.apphosting.api.urlfetch import fetch
        from google3.apphosting.api.urlfetch import InvalidURLError

    def _new_fixed_fetch(validate_certificate):

        def fixed_fetch(url, payload = None, method = 'GET', headers = {}, allow_truncated = False, follow_redirects = True, deadline = None):
            if deadline is None:
                deadline = socket.getdefaulttimeout() or 5
            return fetch(url, payload=payload, method=method, headers=headers, allow_truncated=allow_truncated, follow_redirects=follow_redirects, deadline=deadline, validate_certificate=validate_certificate)

        return fixed_fetch


    class AppEngineHttpConnection(httplib.HTTPConnection):

        def __init__(self, host, port = None, key_file = None, cert_file = None, strict = None, timeout = None, proxy_info = None, ca_certs = None, disable_ssl_certificate_validation = False):
            httplib.HTTPConnection.__init__(self, host, port=port, strict=strict, timeout=timeout)


    class AppEngineHttpsConnection(httplib.HTTPSConnection):

        def __init__(self, host, port = None, key_file = None, cert_file = None, strict = None, timeout = None, proxy_info = None, ca_certs = None, disable_ssl_certificate_validation = False):
            httplib.HTTPSConnection.__init__(self, host, port=port, key_file=key_file, cert_file=cert_file, strict=strict, timeout=timeout)
            self._fetch = _new_fixed_fetch(not disable_ssl_certificate_validation)


    SCHEME_TO_CONNECTION = {'http': AppEngineHttpConnection,
     'https': AppEngineHttpsConnection}
except (ImportError, AttributeError):
    pass

class Http(object):

    def __init__(self, cache = None, timeout = None, proxy_info = proxy_info_from_environment, ca_certs = None, disable_ssl_certificate_validation = False):
        self.proxy_info = proxy_info
        self.ca_certs = ca_certs
        self.disable_ssl_certificate_validation = disable_ssl_certificate_validation
        self.connections = {}
        if cache and isinstance(cache, basestring):
            self.cache = FileCache(cache)
        else:
            self.cache = cache
        self.credentials = Credentials()
        self.certificates = KeyCerts()
        self.authorizations = []
        self.follow_redirects = True
        self.optimistic_concurrency_methods = ['PUT', 'PATCH']
        self.follow_all_redirects = False
        self.ignore_etag = False
        self.force_exception_to_status_code = False
        self.timeout = timeout
        self.forward_authorization_headers = False

    def __getstate__(self):
        state_dict = copy.copy(self.__dict__)
        if 'request' in state_dict:
            del state_dict['request']
        if 'connections' in state_dict:
            del state_dict['connections']
        return state_dict

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.connections = {}

    def _auth_from_challenge(self, host, request_uri, headers, response, content):
        challenges = _parse_www_authenticate(response, 'www-authenticate')
        for cred in self.credentials.iter(host):
            for scheme in AUTH_SCHEME_ORDER:
                if challenges.has_key(scheme):
                    yield AUTH_SCHEME_CLASSES[scheme](cred, host, request_uri, headers, response, content, self)

    def add_credentials(self, name, password, domain = ''):
        self.credentials.add(name, password, domain)

    def add_certificate(self, key, cert, domain):
        self.certificates.add(key, cert, domain)

    def clear_credentials(self):
        self.credentials.clear()
        self.authorizations = []

    def _conn_request(self, conn, request_uri, method, body, headers):
        i = 0
        seen_bad_status_line = False
        while i < RETRIES:
            i += 1
            try:
                if hasattr(conn, 'sock') and conn.sock is None:
                    conn.connect()
                conn.request(method, request_uri, body, headers)
            except socket.timeout:
                raise
            except socket.gaierror:
                conn.close()
                raise ServerNotFoundError('Unable to find the server at %s' % conn.host)
            except ssl_SSLError:
                conn.close()
                raise
            except socket.error as e:
                err = 0
                if hasattr(e, 'args'):
                    err = getattr(e, 'args')[0]
                else:
                    err = e.errno
                if err in (errno.ENETUNREACH, errno.EADDRNOTAVAIL) and i < RETRIES:
                    continue
                raise
            except httplib.HTTPException:
                if hasattr(conn, 'sock') and conn.sock is None:
                    if i < RETRIES - 1:
                        conn.close()
                        conn.connect()
                        continue
                    else:
                        conn.close()
                        raise
                if i < RETRIES - 1:
                    conn.close()
                    conn.connect()
                    continue

            try:
                response = conn.getresponse()
            except httplib.BadStatusLine:
                if not seen_bad_status_line and i == 1:
                    i = 0
                    seen_bad_status_line = True
                    conn.close()
                    conn.connect()
                    continue
                else:
                    conn.close()
                    raise
            except (socket.error, httplib.HTTPException):
                if i < RETRIES - 1:
                    conn.close()
                    conn.connect()
                    continue
                else:
                    conn.close()
                    raise
            else:
                content = ''
                if method == 'HEAD':
                    conn.close()
                else:
                    content = response.read()
                response = Response(response)
                if method != 'HEAD':
                    content = _decompressContent(response, content)

            break

        return (response, content)

    def _request(self, conn, host, absolute_uri, request_uri, method, body, headers, redirections, cachekey):
        auths = [ (auth.depth(request_uri), auth) for auth in self.authorizations if auth.inscope(host, request_uri) ]
        auth = auths and sorted(auths)[0][1] or None
        if auth:
            auth.request(method, request_uri, headers, body)
        response, content = self._conn_request(conn, request_uri, method, body, headers)
        if auth:
            if auth.response(response, body):
                auth.request(method, request_uri, headers, body)
                response, content = self._conn_request(conn, request_uri, method, body, headers)
                response._stale_digest = 1
        if response.status == 401:
            for authorization in self._auth_from_challenge(host, request_uri, headers, response, content):
                authorization.request(method, request_uri, headers, body)
                response, content = self._conn_request(conn, request_uri, method, body, headers)
                if response.status != 401:
                    self.authorizations.append(authorization)
                    authorization.response(response, body)
                    break

        if self.follow_all_redirects or method in ('GET', 'HEAD') or response.status == 303:
            if self.follow_redirects and response.status in (300, 301, 302, 303, 307):
                if redirections:
                    if not response.has_key('location') and response.status != 300:
                        raise RedirectMissingLocation(_('Redirected but the response is missing a Location: header.'), response, content)
                    if response.has_key('location'):
                        location = response['location']
                        scheme, authority, path, query, fragment = parse_uri(location)
                        if authority == None:
                            response['location'] = urlparse.urljoin(absolute_uri, location)
                    if response.status == 301 and method in ('GET', 'HEAD'):
                        response['-x-permanent-redirect-url'] = response['location']
                        if not response.has_key('content-location'):
                            response['content-location'] = absolute_uri
                        _updateCache(headers, response, content, self.cache, cachekey)
                    if headers.has_key('if-none-match'):
                        del headers['if-none-match']
                    if headers.has_key('if-modified-since'):
                        del headers['if-modified-since']
                    if 'authorization' in headers and not self.forward_authorization_headers:
                        del headers['authorization']
                    if response.has_key('location'):
                        location = response['location']
                        old_response = copy.deepcopy(response)
                        if not old_response.has_key('content-location'):
                            old_response['content-location'] = absolute_uri
                        redirect_method = method
                        if response.status in (302, 303):
                            redirect_method = 'GET'
                            body = None
                        response, content = self.request(location, method=redirect_method, body=body, headers=headers, redirections=redirections - 1)
                        response.previous = old_response
                else:
                    raise RedirectLimit('Redirected more times than rediection_limit allows.', response, content)
            elif response.status in (200, 203) and method in ('GET', 'HEAD'):
                if not response.has_key('content-location'):
                    response['content-location'] = absolute_uri
                _updateCache(headers, response, content, self.cache, cachekey)
        return (response, content)

    def _normalize_headers(self, headers):
        return _normalize_headers(headers)

    def request(self, uri, method = 'GET', body = None, headers = None, redirections = DEFAULT_MAX_REDIRECTS, connection_type = None):
        try:
            if headers is None:
                headers = {}
            else:
                headers = self._normalize_headers(headers)
            if not headers.has_key('user-agent'):
                headers['user-agent'] = 'Python-httplib2/%s (gzip)' % __version__
            uri = iri2uri(uri)
            scheme, authority, request_uri, defrag_uri = urlnorm(uri)
            domain_port = authority.split(':')[0:2]
            if len(domain_port) == 2 and domain_port[1] == '443' and scheme == 'http':
                scheme = 'https'
                authority = domain_port[0]
            proxy_info = self._get_proxy_info(scheme, authority)
            conn_key = scheme + ':' + authority
            if conn_key in self.connections:
                conn = self.connections[conn_key]
            else:
                if not connection_type:
                    connection_type = SCHEME_TO_CONNECTION[scheme]
                certs = list(self.certificates.iter(authority))
                if scheme == 'https':
                    if certs:
                        conn = self.connections[conn_key] = connection_type(authority, key_file=certs[0][0], cert_file=certs[0][1], timeout=self.timeout, proxy_info=proxy_info, ca_certs=self.ca_certs, disable_ssl_certificate_validation=self.disable_ssl_certificate_validation)
                    else:
                        conn = self.connections[conn_key] = connection_type(authority, timeout=self.timeout, proxy_info=proxy_info, ca_certs=self.ca_certs, disable_ssl_certificate_validation=self.disable_ssl_certificate_validation)
                else:
                    conn = self.connections[conn_key] = connection_type(authority, timeout=self.timeout, proxy_info=proxy_info)
                conn.set_debuglevel(debuglevel)
            if 'range' not in headers and 'accept-encoding' not in headers:
                headers['accept-encoding'] = 'gzip, deflate'
            info = email.Message.Message()
            cached_value = None
            if self.cache:
                cachekey = defrag_uri.encode('utf-8')
                cached_value = self.cache.get(cachekey)
                if cached_value:
                    try:
                        info, content = cached_value.split('\r\n\r\n', 1)
                        feedparser = email.FeedParser.FeedParser()
                        feedparser.feed(info)
                        info = feedparser.close()
                        feedparser._parse = None
                    except (IndexError, ValueError):
                        self.cache.delete(cachekey)
                        cachekey = None
                        cached_value = None

            else:
                cachekey = None
            if method in self.optimistic_concurrency_methods and self.cache and info.has_key('etag') and not self.ignore_etag and 'if-match' not in headers:
                headers['if-match'] = info['etag']
            if method not in ('GET', 'HEAD') and self.cache and cachekey:
                self.cache.delete(cachekey)
            if method in ('GET', 'HEAD') and 'vary' in info:
                vary = info['vary']
                vary_headers = vary.lower().replace(' ', '').split(',')
                for header in vary_headers:
                    key = '-varied-%s' % header
                    value = info[key]
                    if headers.get(header, None) != value:
                        cached_value = None
                        break

            if cached_value and method in ('GET', 'HEAD') and self.cache and 'range' not in headers:
                if info.has_key('-x-permanent-redirect-url'):
                    if redirections <= 0:
                        raise RedirectLimit('Redirected more times than rediection_limit allows.', {}, '')
                    response, new_content = self.request(info['-x-permanent-redirect-url'], method='GET', headers=headers, redirections=redirections - 1)
                    response.previous = Response(info)
                    response.previous.fromcache = True
                else:
                    entry_disposition = _entry_disposition(info, headers)
                    if entry_disposition == 'FRESH':
                        if not cached_value:
                            info['status'] = '504'
                            content = ''
                        response = Response(info)
                        if cached_value:
                            response.fromcache = True
                        return (response, content)
                    if entry_disposition == 'STALE':
                        if info.has_key('etag') and not self.ignore_etag and 'if-none-match' not in headers:
                            headers['if-none-match'] = info['etag']
                        if info.has_key('last-modified') and 'last-modified' not in headers:
                            headers['if-modified-since'] = info['last-modified']
                    elif entry_disposition == 'TRANSPARENT':
                        pass
                    response, new_content = self._request(conn, authority, uri, request_uri, method, body, headers, redirections, cachekey)
                if response.status == 304 and method == 'GET':
                    for key in _get_end2end_headers(response):
                        info[key] = response[key]

                    merged_response = Response(info)
                    if hasattr(response, '_stale_digest'):
                        merged_response._stale_digest = response._stale_digest
                    _updateCache(headers, merged_response, content, self.cache, cachekey)
                    response = merged_response
                    response.status = 200
                    response.fromcache = True
                elif response.status == 200:
                    content = new_content
                else:
                    self.cache.delete(cachekey)
                    content = new_content
            else:
                cc = _parse_cache_control(headers)
                if cc.has_key('only-if-cached'):
                    info['status'] = '504'
                    response = Response(info)
                    content = ''
                else:
                    response, content = self._request(conn, authority, uri, request_uri, method, body, headers, redirections, cachekey)
        except Exception as e:
            if self.force_exception_to_status_code:
                if isinstance(e, HttpLib2ErrorWithResponse):
                    response = e.response
                    content = e.content
                    response.status = 500
                    response.reason = str(e)
                elif isinstance(e, socket.timeout):
                    content = 'Request Timeout'
                    response = Response({'content-type': 'text/plain',
                     'status': '408',
                     'content-length': len(content)})
                    response.reason = 'Request Timeout'
                else:
                    content = str(e)
                    response = Response({'content-type': 'text/plain',
                     'status': '400',
                     'content-length': len(content)})
                    response.reason = 'Bad Request'
            else:
                raise

        return (response, content)

    def _get_proxy_info(self, scheme, authority):
        hostname, port = urllib.splitport(authority)
        proxy_info = self.proxy_info
        if callable(proxy_info):
            proxy_info = proxy_info(scheme)
        if hasattr(proxy_info, 'applies_to') and not proxy_info.applies_to(hostname):
            proxy_info = None
        return proxy_info


class Response(dict):
    fromcache = False
    version = 11
    status = 200
    reason = 'Ok'
    previous = None

    def __init__(self, info):
        if isinstance(info, httplib.HTTPResponse):
            for key, value in info.getheaders():
                self[key.lower()] = value

            self.status = info.status
            self['status'] = str(self.status)
            self.reason = info.reason
            self.version = info.version
        elif isinstance(info, email.Message.Message):
            for key, value in info.items():
                self[key.lower()] = value

            self.status = int(self['status'])
        else:
            for key, value in info.iteritems():
                self[key.lower()] = value

            self.status = int(self.get('status', self.status))
            self.reason = self.get('reason', self.reason)

    def __getattr__(self, name):
        if name == 'dict':
            return self
        raise AttributeError, name
