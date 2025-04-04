#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\stdlib\urlparse.py
__all__ = ['urlparse',
 'urlunparse',
 'urljoin',
 'urldefrag',
 'urlsplit',
 'urlunsplit',
 'parse_qs',
 'parse_qsl']
uses_relative = ['ftp',
 'http',
 'gopher',
 'nntp',
 'imap',
 'wais',
 'file',
 'https',
 'shttp',
 'mms',
 'prospero',
 'rtsp',
 'rtspu',
 '',
 'sftp']
uses_netloc = ['ftp',
 'http',
 'gopher',
 'nntp',
 'telnet',
 'imap',
 'wais',
 'file',
 'mms',
 'https',
 'shttp',
 'snews',
 'prospero',
 'rtsp',
 'rtspu',
 'rsync',
 '',
 'svn',
 'svn+ssh',
 'sftp',
 'nfs',
 'git',
 'git+ssh']
non_hierarchical = ['gopher',
 'hdl',
 'mailto',
 'news',
 'telnet',
 'wais',
 'imap',
 'snews',
 'sip',
 'sips']
uses_params = ['ftp',
 'hdl',
 'prospero',
 'http',
 'imap',
 'https',
 'shttp',
 'rtsp',
 'rtspu',
 'sip',
 'sips',
 'mms',
 '',
 'sftp']
uses_query = ['http',
 'wais',
 'imap',
 'https',
 'shttp',
 'mms',
 'gopher',
 'rtsp',
 'rtspu',
 'sip',
 'sips',
 '']
uses_fragment = ['ftp',
 'hdl',
 'http',
 'gopher',
 'news',
 'nntp',
 'wais',
 'https',
 'shttp',
 'snews',
 'file',
 'prospero',
 '']
scheme_chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+-.'
MAX_CACHE_SIZE = 20
_parse_cache = {}

def clear_cache():
    _parse_cache.clear()


class ResultMixin(object):

    @property
    def username(self):
        netloc = self.netloc
        if '@' in netloc:
            userinfo = netloc.rsplit('@', 1)[0]
            if ':' in userinfo:
                userinfo = userinfo.split(':', 1)[0]
            return userinfo

    @property
    def password(self):
        netloc = self.netloc
        if '@' in netloc:
            userinfo = netloc.rsplit('@', 1)[0]
            if ':' in userinfo:
                return userinfo.split(':', 1)[1]

    @property
    def hostname(self):
        netloc = self.netloc.split('@')[-1]
        if '[' in netloc and ']' in netloc:
            return netloc.split(']')[0][1:].lower()
        elif ':' in netloc:
            return netloc.split(':')[0].lower()
        elif netloc == '':
            return None
        else:
            return netloc.lower()

    @property
    def port(self):
        netloc = self.netloc.split('@')[-1].split(']')[-1]
        if ':' in netloc:
            port = netloc.split(':')[1]
            return int(port, 10)
        else:
            return None


from collections import namedtuple

class SplitResult(namedtuple('SplitResult', 'scheme netloc path query fragment'), ResultMixin):
    __slots__ = ()

    def geturl(self):
        return urlunsplit(self)


class ParseResult(namedtuple('ParseResult', 'scheme netloc path params query fragment'), ResultMixin):
    __slots__ = ()

    def geturl(self):
        return urlunparse(self)


def urlparse(url, scheme = '', allow_fragments = True):
    tuple = urlsplit(url, scheme, allow_fragments)
    scheme, netloc, url, query, fragment = tuple
    if scheme in uses_params and ';' in url:
        url, params = _splitparams(url)
    else:
        params = ''
    return ParseResult(scheme, netloc, url, params, query, fragment)


def _splitparams(url):
    if '/' in url:
        i = url.find(';', url.rfind('/'))
        if i < 0:
            return (url, '')
    else:
        i = url.find(';')
    return (url[:i], url[i + 1:])


def _splitnetloc(url, start = 0):
    delim = len(url)
    for c in '/?#':
        wdelim = url.find(c, start)
        if wdelim >= 0:
            delim = min(delim, wdelim)

    return (url[start:delim], url[delim:])


def urlsplit(url, scheme = '', allow_fragments = True):
    allow_fragments = bool(allow_fragments)
    key = (url,
     scheme,
     allow_fragments,
     type(url),
     type(scheme))
    cached = _parse_cache.get(key, None)
    if cached:
        return cached
    if len(_parse_cache) >= MAX_CACHE_SIZE:
        clear_cache()
    netloc = query = fragment = ''
    i = url.find(':')
    if i > 0:
        if url[:i] == 'http':
            scheme = url[:i].lower()
            url = url[i + 1:]
            if url[:2] == '//':
                netloc, url = _splitnetloc(url, 2)
                if '[' in netloc and ']' not in netloc or ']' in netloc and '[' not in netloc:
                    raise ValueError('Invalid IPv6 URL')
            if allow_fragments and '#' in url:
                url, fragment = url.split('#', 1)
            if '?' in url:
                url, query = url.split('?', 1)
            v = SplitResult(scheme, netloc, url, query, fragment)
            _parse_cache[key] = v
            return v
        if url.endswith(':') or not url[i + 1].isdigit():
            for c in url[:i]:
                if c not in scheme_chars:
                    break
            else:
                scheme, url = url[:i].lower(), url[i + 1:]

    if url[:2] == '//':
        netloc, url = _splitnetloc(url, 2)
        if '[' in netloc and ']' not in netloc or ']' in netloc and '[' not in netloc:
            raise ValueError('Invalid IPv6 URL')
    if allow_fragments and scheme in uses_fragment and '#' in url:
        url, fragment = url.split('#', 1)
    if scheme in uses_query and '?' in url:
        url, query = url.split('?', 1)
    v = SplitResult(scheme, netloc, url, query, fragment)
    _parse_cache[key] = v
    return v


def urlunparse(data):
    scheme, netloc, url, params, query, fragment = data
    if params:
        url = '%s;%s' % (url, params)
    return urlunsplit((scheme,
     netloc,
     url,
     query,
     fragment))


def urlunsplit(data):
    scheme, netloc, url, query, fragment = data
    if netloc or scheme and scheme in uses_netloc and url[:2] != '//':
        if url and url[:1] != '/':
            url = '/' + url
        url = '//' + (netloc or '') + url
    if scheme:
        url = scheme + ':' + url
    if query:
        url = url + '?' + query
    if fragment:
        url = url + '#' + fragment
    return url


def urljoin(base, url, allow_fragments = True):
    if not base:
        return url
    if not url:
        return base
    bscheme, bnetloc, bpath, bparams, bquery, bfragment = urlparse(base, '', allow_fragments)
    scheme, netloc, path, params, query, fragment = urlparse(url, bscheme, allow_fragments)
    if scheme != bscheme or scheme not in uses_relative:
        return url
    if scheme in uses_netloc:
        if netloc:
            return urlunparse((scheme,
             netloc,
             path,
             params,
             query,
             fragment))
        netloc = bnetloc
    if path[:1] == '/':
        return urlunparse((scheme,
         netloc,
         path,
         params,
         query,
         fragment))
    if not path:
        path = bpath
        if not params:
            params = bparams
        else:
            path = path[:-1]
            return urlunparse((scheme,
             netloc,
             path,
             params,
             query,
             fragment))
        if not query:
            query = bquery
        return urlunparse((scheme,
         netloc,
         path,
         params,
         query,
         fragment))
    segments = bpath.split('/')[:-1] + path.split('/')
    if segments[-1] == '.':
        segments[-1] = ''
    while '.' in segments:
        segments.remove('.')

    while 1:
        i = 1
        n = len(segments) - 1
        while i < n:
            if segments[i] == '..' and segments[i - 1] not in ('', '..'):
                del segments[i - 1:i + 1]
                break
            i = i + 1
        else:
            break

    if segments == ['', '..']:
        segments[-1] = ''
    elif len(segments) >= 2 and segments[-1] == '..':
        segments[-2:] = ['']
    return urlunparse((scheme,
     netloc,
     '/'.join(segments),
     params,
     query,
     fragment))


def urldefrag(url):
    if '#' in url:
        s, n, p, a, q, frag = urlparse(url)
        defrag = urlunparse((s,
         n,
         p,
         a,
         q,
         ''))
        return (defrag, frag)
    else:
        return (url, '')


_hexdig = '0123456789ABCDEFabcdef'
_hextochr = dict(((a + b, chr(int(a + b, 16))) for a in _hexdig for b in _hexdig))

def unquote(s):
    res = s.split('%')
    if len(res) == 1:
        return s
    s = res[0]
    for item in res[1:]:
        try:
            s += _hextochr[item[:2]] + item[2:]
        except KeyError:
            s += '%' + item
        except UnicodeDecodeError:
            s += unichr(int(item[:2], 16)) + item[2:]

    return s


def parse_qs(qs, keep_blank_values = 0, strict_parsing = 0):
    dict = {}
    for name, value in parse_qsl(qs, keep_blank_values, strict_parsing):
        if name in dict:
            dict[name].append(value)
        else:
            dict[name] = [value]

    return dict


def parse_qsl(qs, keep_blank_values = 0, strict_parsing = 0):
    pairs = [ s2 for s1 in qs.split('&') for s2 in s1.split(';') ]
    r = []
    for name_value in pairs:
        if not name_value and not strict_parsing:
            continue
        nv = name_value.split('=', 1)
        if len(nv) != 2:
            if strict_parsing:
                raise ValueError, 'bad query field: %r' % (name_value,)
            if keep_blank_values:
                nv.append('')
            else:
                continue
        if len(nv[1]) or keep_blank_values:
            name = unquote(nv[0].replace('+', ' '))
            value = unquote(nv[1].replace('+', ' '))
            r.append((name, value))

    return r
