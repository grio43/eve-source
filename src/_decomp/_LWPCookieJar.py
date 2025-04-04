#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\stdlib\_LWPCookieJar.py
import time, re
from cookielib import _warn_unhandled_exception, FileCookieJar, LoadError, Cookie, MISSING_FILENAME_TEXT, join_header_words, split_header_words, iso2time, time2isoz

def lwp_cookie_str(cookie):
    h = [(cookie.name, cookie.value), ('path', cookie.path), ('domain', cookie.domain)]
    if cookie.port is not None:
        h.append(('port', cookie.port))
    if cookie.path_specified:
        h.append(('path_spec', None))
    if cookie.port_specified:
        h.append(('port_spec', None))
    if cookie.domain_initial_dot:
        h.append(('domain_dot', None))
    if cookie.secure:
        h.append(('secure', None))
    if cookie.expires:
        h.append(('expires', time2isoz(float(cookie.expires))))
    if cookie.discard:
        h.append(('discard', None))
    if cookie.comment:
        h.append(('comment', cookie.comment))
    if cookie.comment_url:
        h.append(('commenturl', cookie.comment_url))
    keys = cookie._rest.keys()
    keys.sort()
    for k in keys:
        h.append((k, str(cookie._rest[k])))

    h.append(('version', str(cookie.version)))
    return join_header_words([h])


class LWPCookieJar(FileCookieJar):

    def as_lwp_str(self, ignore_discard = True, ignore_expires = True):
        now = time.time()
        r = []
        for cookie in self:
            if not ignore_discard and cookie.discard:
                continue
            if not ignore_expires and cookie.is_expired(now):
                continue
            r.append('Set-Cookie3: %s' % lwp_cookie_str(cookie))

        return '\n'.join(r + [''])

    def save(self, filename = None, ignore_discard = False, ignore_expires = False):
        if filename is None:
            if self.filename is not None:
                filename = self.filename
            else:
                raise ValueError(MISSING_FILENAME_TEXT)
        f = open(filename, 'w')
        try:
            f.write('#LWP-Cookies-2.0\n')
            f.write(self.as_lwp_str(ignore_discard, ignore_expires))
        finally:
            f.close()

    def _really_load(self, f, filename, ignore_discard, ignore_expires):
        magic = f.readline()
        if not re.search(self.magic_re, magic):
            msg = '%r does not look like a Set-Cookie3 (LWP) format file' % filename
            raise LoadError(msg)
        now = time.time()
        header = 'Set-Cookie3:'
        boolean_attrs = ('port_spec', 'path_spec', 'domain_dot', 'secure', 'discard')
        value_attrs = ('version', 'port', 'path', 'domain', 'expires', 'comment', 'commenturl')
        try:
            while 1:
                line = f.readline()
                if line == '':
                    break
                if not line.startswith(header):
                    continue
                line = line[len(header):].strip()
                for data in split_header_words([line]):
                    name, value = data[0]
                    standard = {}
                    rest = {}
                    for k in boolean_attrs:
                        standard[k] = False

                    for k, v in data[1:]:
                        if k is not None:
                            lc = k.lower()
                        else:
                            lc = None
                        if lc in value_attrs or lc in boolean_attrs:
                            k = lc
                        if k in boolean_attrs:
                            if v is None:
                                v = True
                            standard[k] = v
                        elif k in value_attrs:
                            standard[k] = v
                        else:
                            rest[k] = v

                    h = standard.get
                    expires = h('expires')
                    discard = h('discard')
                    if expires is not None:
                        expires = iso2time(expires)
                    if expires is None:
                        discard = True
                    domain = h('domain')
                    domain_specified = domain.startswith('.')
                    c = Cookie(h('version'), name, value, h('port'), h('port_spec'), domain, domain_specified, h('domain_dot'), h('path'), h('path_spec'), h('secure'), expires, discard, h('comment'), h('commenturl'), rest)
                    if not ignore_discard and c.discard:
                        continue
                    if not ignore_expires and c.is_expired(now):
                        continue
                    self.set_cookie(c)

        except IOError:
            raise
        except Exception:
            _warn_unhandled_exception()
            raise LoadError('invalid Set-Cookie3 format file %r: %r' % (filename, line))
