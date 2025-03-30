#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\future\backports\urllib\error.py
from __future__ import absolute_import, division, unicode_literals
from future import standard_library
from future.backports.urllib import response as urllib_response
__all__ = [u'URLError', u'HTTPError', u'ContentTooShortError']

class URLError(IOError):

    def __init__(self, reason, filename = None):
        self.args = (reason,)
        self.reason = reason
        if filename is not None:
            self.filename = filename

    def __str__(self):
        return u'<urlopen error %s>' % self.reason


class HTTPError(URLError, urllib_response.addinfourl):
    __super_init = urllib_response.addinfourl.__init__

    def __init__(self, url, code, msg, hdrs, fp):
        self.code = code
        self.msg = msg
        self.hdrs = hdrs
        self.fp = fp
        self.filename = url
        if fp is not None:
            self.__super_init(fp, hdrs, url, code)

    def __str__(self):
        return u'HTTP Error %s: %s' % (self.code, self.msg)

    @property
    def reason(self):
        return self.msg

    def info(self):
        return self.hdrs


class ContentTooShortError(URLError):

    def __init__(self, message, content):
        URLError.__init__(self, message)
        self.content = content
